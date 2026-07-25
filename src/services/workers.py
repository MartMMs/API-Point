from databases.interfaces import Record
import random
from datetime import date

from database import database
from models.workers import workers
from schemas.workers import WorkersIn, WorkersUpdate, WorkerStatus
from encryption import EncryptionService


class WorkersService:
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.sensitive_fields = ["name", "cpf", "address", "cep"]

    def _process_record(self, record: Record, decrypt: bool = False) -> dict:
        """Decriptografa os campos sensíveis de um registro do banco."""
        if not record:
            return None
        mutable_record = dict(record)
        for field in self.sensitive_fields:
            if field in mutable_record and mutable_record[field]:
                mutable_record[field] = self.encryption_service.decrypt(mutable_record[field]) if decrypt else mutable_record[field]
        return mutable_record

    def _encrypt_data(self, data: dict) -> dict:
        """Criptografa os campos sensíveis de um dicionário de dados de entrada."""
        encrypted_data = data.copy()
        for field in self.sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encryption_service.encrypt(encrypted_data[field])
        return encrypted_data

    async def _get_and_decrypt_worker(self, worker_id: int) -> dict | None:
        """Busca um funcionário pelo ID e retorna seus dados decriptografados."""
        query = workers.select().where(workers.c.id == worker_id)
        record = await database.fetch_one(query)
        if record:
            return self._process_record(record, decrypt=True)
        return None

    async def read_all(self, status: WorkerStatus | None, limit: int, skip: int = 0) -> list[Record]:
        """Busca funcionários, opcionalmente filtrando por status."""
        query = workers.select()
        # Se um status for fornecido, adiciona o filtro à query
        if status:
            query = query.where(workers.c.status == status.value)
        query = query.limit(limit).offset(skip)
        records = await database.fetch_all(query)
        return [self._process_record(r, decrypt=True) for r in records]

    async def create(self, worker_in: WorkersIn) -> Record:
        # 1. Gera a matrícula customizada
        # Pega a primeira letra do setor, ex: "Cozinha" -> "C"
        initial = worker_in.sector.value[0].upper()
        # Gera 6 números aleatórios
        random_part = "".join([str(random.randint(0, 9)) for _ in range(6)])
        registration_code = f"{initial}{random_part}"

        # Criptografa os dados antes de montar o comando
        encrypted_payload = self._encrypt_data(worker_in.model_dump())

        # 2. Prepara o comando de inserção com os dados corretos do RH
        command = workers.insert().values(
            **encrypted_payload,
            registration=registration_code,
            status=WorkerStatus.active.value,
            dismissal_date=None,
        )
        new_worker_id = await database.execute(command)

        # Retorna o funcionário recém-criado e decriptografado
        return await self._get_and_decrypt_worker(new_worker_id)

    async def read_by_id(self, worker_id: int) -> Record | None:
        return await self._get_and_decrypt_worker(worker_id)

    async def update(self, worker_id: int, worker_data: WorkersUpdate) -> Record | None:
        """Atualiza os dados de um funcionário."""
        update_data = worker_data.model_dump(exclude_unset=True)

        if not update_data:
            query_existing = workers.select().where(workers.c.id == worker_id)
            return await self._get_and_decrypt_worker(worker_id)

        # Criptografa os campos sensíveis antes de atualizar
        encrypted_payload = self._encrypt_data(update_data)
        command = workers.update().where(workers.c.id == worker_id).values(**encrypted_payload)
        await database.execute(command)

        return await self._get_and_decrypt_worker(worker_id)


    async def delete(self, worker_id: int) -> bool:
        """Deleta um funcionário fisicamente do banco de dados."""
        command = workers.delete().where(workers.c.id == worker_id)
        rows_affected = await database.execute(command)
        return rows_affected > 0

    async def set_status(self, worker_id: int, status: WorkerStatus) -> Record | None:
        """Altera o status de um funcionário (ex: para inativo)."""
        update_payload = {"status": status.value}

        if status == WorkerStatus.inactive:
            update_payload["dismissal_date"] = date.today()
        else:  # Se estiver reativando, limpa a data de demissão
            update_payload["dismissal_date"] = None

        command = workers.update().where(workers.c.id == worker_id).values(**update_payload)
        rows_affected = await database.execute(command)
        if rows_affected > 0:
            return await self._get_and_decrypt_worker(worker_id)
        return None