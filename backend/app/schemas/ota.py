from pydantic import BaseModel


class OtaKeyRequest(BaseModel):
    name:       str
    company_id: str | None = None  # None = acesso global a todas as locadoras


class OtaKeyResponse(BaseModel):
    id:           str
    name:         str
    key:          str        # UUID completo — retornado APENAS na criação
    company_id:   str | None
    company_name: str
    active:       bool
    created_at:   str


class OtaKeyListItem(BaseModel):
    id:           str
    name:         str
    key_preview:  str        # primeiros 8 chars + "…" — nunca expõe a chave completa
    company_id:   str | None
    company_name: str
    active:       bool
    created_at:   str
