from typing import Literal

from pydantic import BaseModel

RoleEnum = Literal["admin", "locadora", "filial", "customer"]


class UsuarioPayload(BaseModel):
    """Dados do usuário presentes no JWT e retornados após login."""
    id: str
    nome: str
    email: str
    role: RoleEnum
    locadoraId: str = ""
    locadoraNome: str | None = None   # nome da empresa, preenchido para role == "locadora"
    matrizId: str | None = None       # preenchido apenas para role == "filial"
    filialIds: list[str] | None = None    # todas as filiais em que o funcionário trabalha
    filialNames: list[str] | None = None  # nomes correspondentes
