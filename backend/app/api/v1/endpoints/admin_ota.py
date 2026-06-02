from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import AdminOnly
from app.core.database import get_db
from app.schemas.ota import OtaKeyListItem, OtaKeyRequest, OtaKeyResponse
from app.services import ota_service

router = APIRouter(prefix="/admin", tags=["Admin"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/ota-keys", response_model=list[OtaKeyListItem])
async def listar_chaves_ota(usuario: AdminOnly, db: DB):
    """Lista todas as chaves OTA cadastradas (prévia — chave completa não é exposta)."""
    return await ota_service.listar_chaves(db)


@router.post("/ota-keys", response_model=OtaKeyResponse, status_code=201)
async def criar_chave_ota(payload: OtaKeyRequest, usuario: AdminOnly, db: DB):
    """Cria uma nova chave OTA. A chave completa é retornada **apenas nesta resposta**."""
    return await ota_service.criar_chave(payload, db)


@router.delete("/ota-keys/{key_id}", status_code=204)
async def revogar_chave_ota(key_id: str, usuario: AdminOnly, db: DB):
    """Revoga (desativa) uma chave OTA."""
    await ota_service.revogar_chave(key_id, db)
