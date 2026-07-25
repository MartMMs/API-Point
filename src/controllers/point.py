from fastapi import APIRouter, Depends, status

from schemas.point import PointIn
from security import login_required
from services.point import PointService

# O prefixo será /points e, como passamos o Depends aqui em cima,
# todas as rotas deste arquivo exigirão o Token JWT obrigatoriamente.
router = APIRouter(prefix="/points", dependencies=[Depends(login_required)])


@router.post("/", status_code=status.HTTP_200_OK)
async def create_point(
        data: PointIn,
        current_user: dict = Depends(login_required),
        point_service: PointService = Depends()
):
    """
    Registra uma batida de ponto (Entrada, Saídas ou Retorno).
    O ID do funcionário é extraído de forma segura do Token JWT.
    """
    # 1. Pega o user_id que o security.py validou e extraiu do token
    user_id =int(current_user["user_id"])

    # 2. Envia para o serviço processar as regras de negócio
    # O PointService fará as validações de sequência e salvará no banco
    result = await point_service.register_point(
        user_id=user_id,
        point_type=data.type
    )

    # 3. Retorna o dicionário que o serviço gerou (com o resumo do dia, se for saída)
    return result