from typing import Annotated

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.auth import CadastroLocadoraRequest, CadastroResponse, LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioPayload
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

DB = Annotated[AsyncSurreal, Depends(get_db)]


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: DB):
    return await auth_service.login(payload, db)


@router.post("/cadastro", response_model=CadastroResponse, status_code=201)
async def cadastro(payload: CadastroLocadoraRequest, db: DB):
    return await auth_service.cadastrar(payload, db)


@router.get("/me", response_model=UsuarioPayload)
async def me(usuario: CurrentUser):
    """Retorna os dados do usuário autenticado a partir do token."""
    return usuario
