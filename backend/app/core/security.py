import jwt
import pendulum
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

pwd_hash = PasswordHash([Argon2Hasher()])


# ── Senha ──────────────────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    return pwd_hash.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    return pwd_hash.verify(senha, hash_)


# ── JWT ────────────────────────────────────────────────────────────────────────

def criar_token(payload: dict) -> str:
    agora = pendulum.now("UTC")
    dados = {
        **payload,
        "iat": agora.int_timestamp,
        "exp": agora.add(minutes=settings.JWT_EXPIRE_MINUTES).int_timestamp,
    }
    return jwt.encode(dados, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
