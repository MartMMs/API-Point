import sqlalchemy as sa
from datetime import date, datetime, timedelta
from collections import defaultdict
from database import database

# Ajuste os imports de acordo com a sua estrutura de pastas
from models.point import points, PointType
from models.workers import workers
from exceptions import BusinessError, UserNotFoundError


class PointService:
    def _parse_duration(self, value: str) -> timedelta:
        if "day" in value:
            day_part, time_part = value.split(", ")
            day_count = int(day_part.split()[0])
        else:
            day_count = 0
            time_part = value

        hours, minutes, seconds = map(int, time_part.split(":"))
        return timedelta(days=day_count, hours=hours, minutes=minutes, seconds=seconds)

    async def read_all_by_worker(self, worker_id: int, limit: int = 10, skip: int = 0):
        """
        Returns the clock-in history for a specific worker, with pagination.
        """
        query = sa.select(points).where(points.c.worker_id == worker_id).limit(limit).offset(skip).order_by(
            points.c.created_at.desc(), points.c.id.desc())
        return await database.fetch_all(query)

    async def register_point(self, user_id: int, point_type: PointType):
        """
        Main logic for point registration called by the Controller.
        """
        # 1. Busca os dados do funcionário (precisamos saber se ele tem auto_lunch e a carga horária)
        query_worker = sa.select(workers).where(workers.c.user_id == user_id)
        worker = await database.fetch_one(query_worker)

        if not worker:
            raise UserNotFoundError("Worker not found or not linked to this user.")

        # 2. Busca todas as batidas que ele já fez hoje
        hoje = date.today()
        query_points = sa.select(points).where(
            sa.and_(
                points.c.worker_id == worker["id"],
                sa.func.date(points.c.created_at) == hoje.isoformat()
            )
        ).order_by(points.c.created_at.asc(), points.c.id.asc())

        batidas_hoje = await database.fetch_all(query_points)

        # 3. Valida se a sequência da batida está correta
        self._validate_sequence(batidas_hoje, point_type, worker["auto_lunch"])

        # 4. Usa uma transação para garantir a atomicidade da operação
        async with database.transaction():
            # 4.1. Insere a batida no banco
            query_insert = points.insert().values(
                worker_id=int(worker["id"]),
                type=point_type,
                created_at=datetime.now(),
            )
            await database.execute(query_insert)

            # 4.2. Se for o fim do expediente, processa o cálculo diário
            if point_type == PointType.check_out:
                # Puxamos as batidas novamente para incluir a saída que acabamos de registrar
                batidas_completas = await database.fetch_all(query_points)
                resumo = await self.calculate_daily_hours(worker, batidas_completas)
                return {"detail": "Shift ended.", "summary": resumo}

        return {"detail": f"Point '{point_type.value}' registered successfully."}

    def _validate_sequence(self, batidas: list, novo_tipo: PointType, auto_lunch: bool):
        """
        Defines the logical rules for which buttons the employee can press.
        """
        ultima_batida = batidas[-1]["type"] if batidas else None

        # Se a última batida foi a saída final, não pode registrar mais nada hoje
        if ultima_batida == PointType.check_out:
            raise BusinessError("Today's shift has already been closed.")

        if auto_lunch:
            # Fluxo simplificado: Entrada -> Saída
            ordem = {
                None: PointType.check_in,
                PointType.check_in: PointType.check_out
            }
        else:
            # Fluxo completo: Entrada -> Almoço -> Retorno -> Saída
            ordem = {
                None: PointType.check_in,
                PointType.check_in: PointType.lunch_out,
                PointType.lunch_out: PointType.lunch_in,
                PointType.lunch_in: PointType.check_out
            }

        tipo_esperado = ordem.get(ultima_batida)

        if novo_tipo != tipo_esperado:
            raise BusinessError(
                f"Invalid sequence. The system expected '{tipo_esperado}', "
                f"but received '{novo_tipo}'."
            )

    async def calculate_daily_hours(self, worker: dict, batidas_do_dia: list):
        """
        Calculates net hours and overtime based on the employee's lunch rule.
        """
        # A biblioteca databases retorna "Records", podemos acessar os campos por chave
        check_in = batidas_do_dia[0]["created_at"]
        check_out = batidas_do_dia[-1]["created_at"]

        if worker["auto_lunch"]:
            # Duração total menos os minutos de almoço fixados
            gross_time = check_out - check_in
            lunch_time = timedelta(minutes=worker["lunch_duration_minutes"])
            net_time = gross_time - lunch_time
        else:
            # Se não for automático, a validação garantiu que temos 4 batidas exatas
            lunch_out = batidas_do_dia[1]["created_at"]
            lunch_in = batidas_do_dia[2]["created_at"]

            turno_manha = lunch_out - check_in
            turno_tarde = check_out - lunch_in
            net_time = turno_manha + turno_tarde

        # Carga horária esperada
        expected_time = timedelta(hours=worker["daily_hours"])

        # Matemática de Horas Extras
        overtime = timedelta(0)
        negative_time = timedelta(0)

        if net_time > expected_time:
            overtime = net_time - expected_time
        elif net_time < expected_time:
            negative_time = expected_time - net_time

        return {
            "worked_hours": str(net_time).split(".")[0],
            "expected_hours": str(expected_time).split(".")[0],
            "overtime": str(overtime).split(".")[0],
            "negative_time": str(negative_time).split(".")[0]
        }

    async def generate_report(self, worker_id: int, start_date: date, end_date: date) -> dict | None:
        """Generates an hours report for a worker over a period."""
        # 1. Busca os dados do funcionário
        query_worker = sa.select(workers).where(workers.c.id == worker_id)
        worker = await database.fetch_one(query_worker)
        if not worker:
            raise UserNotFoundError("Worker not found.")

        # 2. Busca todas as batidas de ponto no período especificado
        query_points = sa.select(points).where(
            sa.and_(
                points.c.worker_id == worker_id,
                sa.func.date(points.c.created_at) >= start_date.isoformat(),
                sa.func.date(points.c.created_at) <= end_date.isoformat()
            )
        ).order_by(points.c.created_at.asc(), points.c.id.asc())
        all_points = await database.fetch_all(query_points)

        if not all_points:
            return None

        # 3. Agrupa as batidas por dia
        points_by_day = defaultdict(list)
        for point in all_points:
            points_by_day[point.created_at.date()].append(point)

        # 4. Calcula o resumo de cada dia e os totais
        daily_summaries = []
        total_worked = timedelta()
        total_expected = timedelta()
        total_overtime = timedelta()
        total_negative = timedelta()

        for day, day_points in sorted(points_by_day.items()):
            # Só calcula se o dia teve o expediente encerrado (última batida é check_out)
            if day_points and day_points[-1].type == PointType.check_out:
                summary = await self.calculate_daily_hours(worker, day_points)
                summary["date"] = day
                daily_summaries.append(summary)

                # Soma os totais (convertendo de string para timedelta)
                total_worked += self._parse_duration(summary["worked_hours"])
                total_expected += self._parse_duration(summary["expected_hours"])
                total_overtime += self._parse_duration(summary["overtime"])
                total_negative += self._parse_duration(summary["negative_time"])

        # 5. Formata a resposta final
        return {
            "worker_id": worker_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_worked_hours": str(total_worked).split(".")[0],
            "total_expected_hours": str(total_expected).split(".")[0],
            "total_overtime": str(total_overtime).split(".")[0],
            "total_negative_time": str(total_negative).split(".")[0],
            "daily_summaries": daily_summaries,
        }