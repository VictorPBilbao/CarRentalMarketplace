from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Query
from surrealdb import AsyncSurreal

from app.core.database import get_db
from app.schemas.categoria_veiculo import CategoriaVeiculoResponse
from app.schemas.filial import CidadeResponse, FilialResponse
from app.schemas.tarifa import BuscarTarifasResponse, BuscarTodasCategoriasResponse
from app.services import categoria_veiculo_service, filial_service, tarifa_service
from app.services.reserva_service import _get_company_from_store

router = APIRouter(prefix="/publico", tags=["publico"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/lojas", response_model=list[FilialResponse])
async def listar_lojas(db: DB):
    """Lista todas as lojas ativas (single-tenant: sem autenticação necessária)."""
    return await filial_service.listar_todos(db)


@router.get("/categorias", response_model=list[CategoriaVeiculoResponse])
async def listar_categorias(db: DB):
    """Lista todas as categorias ativas (single-tenant: sem autenticação necessária)."""
    return await categoria_veiculo_service.listar_todos(db)


@router.get("/lojas-com-categoria", response_model=list[FilialResponse])
async def lojas_com_categoria(db: DB, category_id: str = Query(...)):
    """Lojas ativas que possuem frota da categoria informada (sem autenticação)."""
    return await filial_service.listar_com_categoria(category_id, db)


@router.get("/cidades", response_model=list[CidadeResponse])
async def listar_cidades(db: DB):
    """Cidades distintas com suas lojas ativas (sem autenticação)."""
    return await filial_service.listar_cidades(db)


@router.get("/buscar-categorias", response_model=BuscarTodasCategoriasResponse)
async def buscar_todas_categorias(
    db: DB,
    pickup_store_id: str = Query(...),
    dropoff_store_id: str = Query(...),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    nationality: str | None = Query(None),
    promo_code: str | None = Query(None),
):
    """Busca tarifas para todas as categorias disponíveis em uma loja (sem autenticação)."""
    company_id      = await _get_company_from_store(pickup_store_id, db)
    company_dropoff = await _get_company_from_store(dropoff_store_id, db)
    if company_id != company_dropoff:
        raise HTTPException(
            status_code=400,
            detail='Retirada e devolução devem ser da mesma locadora.',
        )
    return await tarifa_service.buscar_tarifas_todas_categorias(
        company_id=company_id,
        pickup_store_id=pickup_store_id,
        dropoff_store_id=dropoff_store_id,
        pickup_time=pickup_time,
        dropoff_time=dropoff_time,
        customer_age=customer_age,
        nationality=nationality,
        promo_code=promo_code,
        db=db,
    )


@router.get("/buscar", response_model=BuscarTarifasResponse)
async def buscar_tarifas(
    db: DB,
    pickup_store_id: str = Query(...),
    dropoff_store_id: str = Query(...),
    category_id: str = Query(...),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    nationality: str | None = Query(None),
    promo_code: str | None = Query(None),
):
    """Busca tarifas e disponibilidade sem autenticação."""
    company_id      = await _get_company_from_store(pickup_store_id, db)
    company_dropoff = await _get_company_from_store(dropoff_store_id, db)
    if company_id != company_dropoff:
        raise HTTPException(
            status_code=400,
            detail='Retirada e devolução devem ser da mesma locadora.',
        )
    return await tarifa_service.buscar_tarifas(
        company_id=company_id,
        pickup_store_id=pickup_store_id,
        dropoff_store_id=dropoff_store_id,
        category_id=category_id,
        pickup_time=pickup_time,
        dropoff_time=dropoff_time,
        customer_age=customer_age,
        nationality=nationality,
        promo_code=promo_code,
        db=db,
    )
