from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Query
from surrealdb import AsyncSurreal

from app.api.deps import OtaClient
from app.core.database import get_db
from app.schemas.filial import CidadeResponse
from app.schemas.reserva import AtualizarStatusRequest, CriarReservaRequest, ReservaResponse
from app.schemas.tarifa import BuscarTarifasResponse, BuscarTodasCategoriasResponse, CotacaoRequest, CotacaoResponse
from app.services import filial_service, reserva_service, tarifa_service
from app.services.reserva_service import _get_company_from_store

router = APIRouter(prefix="/ota", tags=["OTA — Parceiros"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/cidades", response_model=list[CidadeResponse])
async def ota_cidades(cliente: OtaClient, db: DB):
    """Lista cidades com lojas disponíveis."""
    return await filial_service.listar_cidades(db)


@router.get("/buscar", response_model=BuscarTodasCategoriasResponse)
async def ota_buscar(
    cliente: OtaClient,
    db: DB,
    pickup_store_id:  str      = Query(...),
    dropoff_store_id: str      = Query(...),
    pickup_time:      datetime = Query(...),
    dropoff_time:     datetime = Query(...),
    customer_age:     int      = Query(..., ge=18),
    nationality:      str | None = Query(None),
    promo_code:       str | None = Query(None),
):
    """Busca categorias disponíveis para o percurso e período informados."""
    company_id      = await _get_company_from_store(pickup_store_id, db)
    company_dropoff = await _get_company_from_store(dropoff_store_id, db)
    if company_id != company_dropoff:
        raise HTTPException(status_code=400, detail='Retirada e devolução devem ser da mesma locadora.')
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


@router.post("/cotacao", response_model=CotacaoResponse)
async def ota_cotacao(payload: CotacaoRequest, cliente: OtaClient, db: DB):
    """Cotação detalhada para uma categoria e período específicos."""
    company_id = await _get_company_from_store(payload.pickup_store_id, db)
    return await tarifa_service.cotar(company_id=company_id, payload=payload, db=db)


@router.post("/reservas", response_model=ReservaResponse, status_code=201)
async def ota_criar_reserva(payload: CriarReservaRequest, cliente: OtaClient, db: DB):
    """Cria uma reserva em nome de um cliente cadastrado no sistema."""
    company_id = await _get_company_from_store(payload.pickup_store_id, db)
    return await reserva_service.criar(payload, company_id, db)


@router.get("/reservas/{reserva_id}", response_model=ReservaResponse)
async def ota_buscar_reserva(reserva_id: str, cliente: OtaClient, db: DB):
    """Consulta o status e detalhes de uma reserva."""
    company_id = str((cliente.get('company') or {}).get('id', '') or '')
    if not company_id:
        raise HTTPException(status_code=403, detail='Chave OTA sem empresa associada não pode consultar reservas.')
    return await reserva_service.buscar_por_id(reserva_id, company_id, db)


@router.delete("/reservas/{reserva_id}", status_code=204)
async def ota_cancelar_reserva(reserva_id: str, cliente: OtaClient, db: DB):
    """Cancela uma reserva."""
    company_id = str((cliente.get('company') or {}).get('id', '') or '')
    if not company_id:
        raise HTTPException(status_code=403, detail='Chave OTA sem empresa associada não pode cancelar reservas.')
    await reserva_service.atualizar_status(
        reserva_id,
        AtualizarStatusRequest(status='CANCELLED'),
        company_id,
        db,
    )
