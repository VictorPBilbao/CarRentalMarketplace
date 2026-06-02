from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from surrealdb import AsyncSurreal

from app.core.database import extract_records, get_db
from app.core.security import decodificar_token
from app.schemas.usuario import RoleEnum, UsuarioPayload

bearer     = HTTPBearer()
ota_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> UsuarioPayload:
    try:
        payload = decodificar_token(credentials.credentials)
        return UsuarioPayload(**payload)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )


def require_role(*roles: RoleEnum):
    """Dependency factory que restringe acesso por role."""
    def _check(usuario: Annotated[UsuarioPayload, Depends(get_current_user)]) -> UsuarioPayload:
        if usuario.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado para este perfil.",
            )
        return usuario
    return _check


async def get_ota_client(
    api_key: Annotated[str, Depends(ota_header)],
    db: Annotated[AsyncSurreal, Depends(get_db)],
) -> dict:
    result = await db.query(
        "SELECT *, company FROM ota_key WHERE key = $k AND active = true FETCH company LIMIT 1",
        {'k': api_key},
    )
    records = extract_records(result)
    if not records:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida ou inativa.")
    return records[0]


# ── Aliases prontos para usar nos routers ─────────────────────────────────────
CurrentUser      = Annotated[UsuarioPayload, Depends(get_current_user)]
OtaClient        = Annotated[dict, Depends(get_ota_client)]
AdminOnly        = Annotated[UsuarioPayload, Depends(require_role("admin"))]
LocadoraOnly     = Annotated[UsuarioPayload, Depends(require_role("locadora"))]
FilialOnly       = Annotated[UsuarioPayload, Depends(require_role("filial"))]
StaffOnly        = Annotated[UsuarioPayload, Depends(require_role("admin", "locadora"))]
LocadoraOrFilial = Annotated[UsuarioPayload, Depends(require_role("locadora", "filial"))]
CustomerOnly     = Annotated[UsuarioPayload, Depends(require_role("customer"))]
