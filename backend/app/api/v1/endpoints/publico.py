from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from surrealdb import AsyncSurreal

from app.core.database import get_db
from app.schemas.categoria_veiculo import CategoriaVeiculoResponse
from app.schemas.filial import FilialResponse
from app.schemas.tarifa import BuscarTarifasResponse
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


@router.get("/buscar", response_model=BuscarTarifasResponse)
async def buscar_tarifas(
    db: DB,
    pickup_store_id: str = Query(...),
    dropoff_store_id: str = Query(...),
    category_id: str = Query(...),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    promo_code: str | None = Query(None),
):
    """Busca tarifas e disponibilidade sem autenticação."""
    company_id = await _get_company_from_store(pickup_store_id, db)
    return await tarifa_service.buscar_tarifas(
        company_id=company_id,
        pickup_store_id=pickup_store_id,
        dropoff_store_id=dropoff_store_id,
        category_id=category_id,
        pickup_time=pickup_time,
        dropoff_time=dropoff_time,
        customer_age=customer_age,
        promo_code=promo_code,
        db=db,
    )
