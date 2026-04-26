from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import LocadoraOnly, StaffOnly
from app.core.database import get_db
from app.schemas.categoria_veiculo import CategoriaVeiculoRequest, CategoriaVeiculoResponse
from app.services import categoria_veiculo_service

router = APIRouter(prefix="/locadora", tags=["categorias"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/categorias", response_model=list[CategoriaVeiculoResponse])
async def listar_categorias(usuario: StaffOnly, db: DB):
    return await categoria_veiculo_service.listar(usuario, db)


@router.get("/categorias/{categoria_id}", response_model=CategoriaVeiculoResponse)
async def buscar_categoria(categoria_id: str, usuario: StaffOnly, db: DB):
    return await categoria_veiculo_service.buscar_por_id(categoria_id, usuario, db)


@router.post("/categorias", response_model=CategoriaVeiculoResponse, status_code=201)
async def criar_categoria(payload: CategoriaVeiculoRequest, usuario: LocadoraOnly, db: DB):
    return await categoria_veiculo_service.criar(payload, usuario, db)


@router.put("/categorias/{categoria_id}", response_model=CategoriaVeiculoResponse)
async def atualizar_categoria(categoria_id: str, payload: CategoriaVeiculoRequest, usuario: LocadoraOnly, db: DB):
    return await categoria_veiculo_service.atualizar(categoria_id, payload, usuario, db)
