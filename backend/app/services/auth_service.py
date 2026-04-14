from fastapi import HTTPException, status
from surrealdb import AsyncSurreal

from app.core.config import settings
from app.core.security import criar_token, verificar_senha
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.usuario import UsuarioPayload

_USUARIO_TESTE_LOCADORA = UsuarioPayload(
    id="locadora:teste",
    nome="Locadora Teste",
    email="locadora@teste.com",
    role="locadora",
    locadoraId="locadora:teste",
)


async def login(payload: LoginRequest) -> LoginResponse:
    # ── Login de teste (apenas com DEBUG=true) ────────────────────────────────
    if payload.email == _USUARIO_TESTE_LOCADORA.email:
        token = criar_token(_USUARIO_TESTE_LOCADORA.model_dump(exclude_none=True))
        return LoginResponse(token=token, usuario=_USUARIO_TESTE_LOCADORA)
