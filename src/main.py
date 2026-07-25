from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from controllers import auth, workers, point
from database import database, engine, metadata
from exceptions import UserNotFoundError, BusinessError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no banco de dados (caso ainda não existam) usando o motor síncrono
    metadata.create_all(engine)

    # Inicia a conexão de alta performance (assíncrona) da biblioteca databases
    await database.connect()
    yield
    await database.disconnect()

tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and access token generation operations.",
    },
    {
        "name": "workers",
        "description": "Operations for managing employee records and work schedules.",
    },
    {
        "name": "point",
        "description": "Operations for time tracking and calculating hours worked.",
    },
]
app = FastAPI(
    title="PointsExtras API",
    version="1.0.0",
    summary="Microservice for work schedule management and time tracking.",
    description="""
    PointsExtras is a microservice for HR time tracking. ⏰🏢

## Workers

* **Create Workers**
* **List Workers**.
* **List Workers transactions by ID**.

## Points
* **Clock in/out** (Clock-in, Lunch Out, Lunch In, Clock-out).
* **View daily log** with automatic overtime calculation.
""",
    openapi_tags=tags_metadata,
    redoc_url=None,
    lifespan=lifespan,
)

# Em produção, restrinja as origens para os domínios do seu frontend.
# Exemplo: origins = ["https://meufrontend.com", "https://www.meufrontend.com"]
origins = ["*"] # Manter assim para desenvolvimento

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


app.include_router(auth.router, tags=["auth"])
app.include_router(workers.router, tags=["workers"])
app.include_router(point.router, tags=["point"])

@ app.exception_handler(UserNotFoundError)
async def user_not_found_error_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Worker not found in the system."}
    )


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    # Mantive o 409 Conflict do seu projeto original, que faz muito sentido
    # para erros de lógica, como bater uma 'saída' sem ter uma 'entrada'.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc.message if hasattr(exc, 'message') else exc)}
    )