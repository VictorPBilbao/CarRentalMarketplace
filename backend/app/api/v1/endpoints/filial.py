from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import FilialOnly, LocadoraOrFilial, StaffOnly
from app.core.database import get_db
from app.schemas.filial import FilialRequest, FilialResponse
from app.services import filial_service

router = APIRouter(prefix="/locadora", tags=["filiais"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/filiais", response_model=list[FilialResponse])
async def listar_filiais(usuario: StaffOnly, db: DB):
    return await filial_service.listar(usuario, db)


@router.get("/lojas", response_model=list[FilialResponse])
async def listar_lojas_empresa(usuario: LocadoraOrFilial, db: DB):
    """Lista todas as lojas da empresa — acessível por filial e locadora (ex: seleção de devolução)."""
    return await filial_service.listar(usuario, db)


@router.get("/filiais/{filial_id}", response_model=FilialResponse)
async def buscar_filial(filial_id: str, usuario: StaffOnly, db: DB):
    return await filial_service.buscar_por_id(filial_id, usuario, db)


@router.post("/filiais", response_model=FilialResponse, status_code=201)
async def criar_filial(payload: FilialRequest, usuario: StaffOnly, db: DB):
    return await filial_service.criar(payload, usuario, db)


@router.put("/filiais/{filial_id}", response_model=FilialResponse)
async def atualizar_filial(filial_id: str, payload: FilialRequest, usuario: StaffOnly, db: DB):
    return await filial_service.atualizar(filial_id, payload, usuario, db)


