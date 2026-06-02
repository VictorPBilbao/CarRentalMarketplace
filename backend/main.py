from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.router import router
from app.api.v1.endpoints.ota import router as ota_router
from app.core.config import settings
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    await init_db()
    yield
    await close_db()
    logger.info("Servidor encerrado")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# ── Sub-app OTA: documentação pública para parceiros ─────────────────────────
ota_api = FastAPI(
    title="CarRental OTA API",
    description="""
API pública para integração com **OTAs (Online Travel Agencies)**.

## Autenticação
Todos os endpoints requerem uma **API Key** no header `X-API-Key`.
Solicite sua chave ao administrador do sistema.

## Fluxo típico de integração
1. `GET /ota/cidades` — listar cidades e lojas disponíveis
2. `GET /ota/buscar` — pesquisar categorias disponíveis para o percurso e período
3. `POST /ota/cotacao` — obter cotação detalhada de uma categoria
4. `POST /ota/reservas` — criar reserva em nome do cliente
5. `GET /ota/reservas/{id}` — consultar status da reserva
6. `DELETE /ota/reservas/{id}` — cancelar reserva
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "CarRental Marketplace", "email": "api@carrental.com"},
)

ota_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

ota_api.include_router(ota_router)

app.mount("/ota-api", ota_api)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
