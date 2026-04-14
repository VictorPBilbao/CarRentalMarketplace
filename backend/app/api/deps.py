from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decodificar_token
from app.schemas.usuario import RoleEnum, UsuarioPayload

bearer = HTTPBearer()


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


# ── Aliases prontos para usar nos routers ─────────────────────────────────────
CurrentUser   = Annotated[UsuarioPayload, Depends(get_current_user)]
AdminOnly     = Annotated[UsuarioPayload, Depends(require_role("admin"))]
LocadoraOnly  = Annotated[UsuarioPayload, Depends(require_role("locadora"))]
FilialOnly    = Annotated[UsuarioPayload, Depends(require_role("filial"))]
StaffOnly     = Annotated[UsuarioPayload, Depends(require_role("admin", "locadora"))]
