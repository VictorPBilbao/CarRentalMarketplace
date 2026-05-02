from typing import Literal

from pydantic import BaseModel

RoleFuncionario = Literal['MANAGER', 'CLERK', 'MECHANIC']


class FuncionarioRequest(BaseModel):
    first_name:      str
    last_name:       str
    email:           str
    senha:           str
    role:            RoleFuncionario = 'CLERK'
    extra_store_ids: list[str] = []


class FuncionarioResponse(BaseModel):
    id:         str
    first_name: str
    last_name:  str
    email:      str
    role:       str
    active:     bool
    created_at: str
