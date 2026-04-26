from pydantic import BaseModel, EmailStr

from app.schemas.usuario import UsuarioPayload


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class LoginResponse(BaseModel):
    token: str


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
