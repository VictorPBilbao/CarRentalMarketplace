from pydantic import BaseModel, EmailStr

from app.schemas.usuario import UsuarioPayload


class StoreOption(BaseModel):
    id:   str
    name: str


class LoginRequest(BaseModel):
    email:    EmailStr
    senha:    str
    store_id: str | None = None


class LoginResponse(BaseModel):
    token:  str | None = None
    stores: list[StoreOption] | None = None


class CadastroLocadoraRequest(BaseModel):
    nomeEmpresa: str
    cnpj: str
    telefone: str
    cidade: str
    estado: str
    nomeResponsavel: str
    email: EmailStr
    senha: str


class CadastroResponse(BaseModel):
    locadoraId: str
    mensagem: str


class CadastroClienteRequest(BaseModel):
    primeiroNome: str
    sobrenome: str
    email: EmailStr
    telefone: str | None = None
    senha: str


class CadastroClienteResponse(BaseModel):
    userId: str
    mensagem: str
