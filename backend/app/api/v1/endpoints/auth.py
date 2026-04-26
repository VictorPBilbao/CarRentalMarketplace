from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.auth import (
    CadastroClienteRequest,
    CadastroClienteResponse,
    CadastroLocadoraRequest,
    CadastroResponse,
    LoginRequest,
    LoginResponse,
)
from app.schemas.usuario import UsuarioPayload
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: DB):
    return await auth_service.login(payload, db)


@router.post("/cadastro", response_model=CadastroResponse, status_code=201)
async def cadastro(payload: CadastroLocadoraRequest, db: DB):
    return await auth_service.cadastrar(payload, db)


@router.get("/me", response_model=UsuarioPayload)
async def me(usuario: CurrentUser, db: DB):
    return await auth_service.me(usuario, db)


@router.post("/cadastro/cliente", response_model=CadastroClienteResponse, status_code=201)
async def cadastro_cliente(payload: CadastroClienteRequest, db: DB):
    return await auth_service.cadastrar_cliente(payload, db)


@router.post("/logout")
async def logout(_usuario: CurrentUser):
    return {"mensagem": "Logout realizado com sucesso."}
