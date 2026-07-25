import os
import logging
import time
from typing import Annotated, Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
if not SECRET:
    raise ValueError("A variável de ambiente JWT_SECRET não foi definida.")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str

class JWTToken(BaseModel):
    access_token: AccessToken

def sign_jwt(user_id: int) -> dict[str, Any]:
    now = time.time()
    payload = {
        "iss": "api-ponto.local",
        "sub": str (user_id),
        "aud": "api-ponto",
        "exp": now + (60 * 60 * 8),
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return {"access_token": token}

async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_token = jwt.decode(token, SECRET, audience="api-ponto", algorithms=[ALGORITHM])
        _token = JWTToken.model_validate({"access_token": decoded_token})
        return _token
    except Exception as e:
        logging.error(f"Erro ao decodificar o token: {e}")
        return None

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )

            payload = await decode_jwt(credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                )
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
            )

async def get_current_user(
    token: Annotated[JWTToken, Depends(JWTBearer())],
) -> dict[str, int]:
    return {"user_id": int(token.access_token.sub)}

def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user