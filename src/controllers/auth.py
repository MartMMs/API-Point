from fastapi import APIRouter

from schemas.auth import LoginIn, LoginOut
from config import settings
from security import sign_jwt

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=LoginOut)
async def login(data: LoginIn):
    return sign_jwt(user_id=data.user_id)


# --- Endpoint de Teste ---
# Este bloco de código só será executado se o ambiente não for 'production'.
if settings.environment != "production":
    @router.get("/test-token/{user_id}", response_model=LoginOut, include_in_schema=False)
    async def get_test_token(user_id: int):
        """
        [TESTING ONLY] Generates an access token for any user_id.
        This endpoint will not be available in production.
        """
        return sign_jwt(user_id=user_id)