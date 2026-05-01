from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from surrealdb import AsyncSurreal

from app.api.deps import FilialOnly, LocadoraOrFilial
from app.core.database import get_db
from app.schemas.tarifa import BuscarTarifasResponse, CotacaoRequest, CotacaoResponse
from app.services import tarifa_service

router = APIRouter(tags=["tarifas"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


# ── Filial ────────────────────────────────────────────────────────────────────

@router.get("/filial/tarifas", response_model=BuscarTarifasResponse)
async def buscar_tarifas_filial(
    usuario: FilialOnly,
    db: DB,
    dropoff_store_id: str = Query(..., description="ID da loja de devolução (ex: store:gru_localiza)"),
    category_id: str = Query(..., description="ID da categoria do veículo"),
    pickup_time: datetime = Query(..., description="Data/hora de retirada (ISO 8601)"),
    dropoff_time: datetime = Query(..., description="Data/hora de devolução (ISO 8601)"),
    customer_age: int = Query(..., ge=18, description="Idade do condutor principal"),
    promo_code: str | None = Query(None, description="Código promocional (opcional)"),
):
    """
    Busca planos tarifários aplicáveis, taxas obrigatórias da loja e adicionais
    disponíveis para a filial do usuário autenticado.

    Planos são retornados em ordem crescente de diária (mais barato primeiro).
    """
    return await tarifa_service.buscar_tarifas(
        company_id=usuario.locadoraId,
        pickup_store_id=usuario.matrizId,
        dropoff_store_id=dropoff_store_id,
        category_id=category_id,
        pickup_time=pickup_time,
        dropoff_time=dropoff_time,
        customer_age=customer_age,
        promo_code=promo_code,
        db=db,
    )


@router.post("/filial/cotacao", response_model=CotacaoResponse)
async def calcular_cotacao_filial(
    payload: CotacaoRequest,
    usuario: FilialOnly,
    db: DB,
):
    """
    Calcula uma cotação completa (breakdown detalhado) para a filial do usuário.

    - Aplica taxas obrigatórias da loja de retirada
    - Soma adicionais selecionados com cálculo PER_DAY / PER_TRIP / PERCENTAGE
    - Inclui taxa de retorno one-way quando aplicável
    - Lista proteções incluídas no plano

    O resultado pode ser usado diretamente para criar uma reserva.
    """
    payload.pickup_store_id = usuario.matrizId
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)


# ── Locadora ──────────────────────────────────────────────────────────────────

@router.get("/locadora/tarifas", response_model=BuscarTarifasResponse)
async def buscar_tarifas_locadora(
    usuario: LocadoraOrFilial,
    db: DB,
    pickup_store_id: str = Query(..., description="ID da loja de retirada"),
    dropoff_store_id: str = Query(..., description="ID da loja de devolução"),
    category_id: str = Query(..., description="ID da categoria do veículo"),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    promo_code: str | None = Query(None),
):
    """
    Busca planos tarifários para qualquer loja da locadora (visão gerencial).
    """
    return await tarifa_service.buscar_tarifas(
        company_id=usuario.locadoraId,
        pickup_store_id=pickup_store_id,
        dropoff_store_id=dropoff_store_id,
        category_id=category_id,
        pickup_time=pickup_time,
        dropoff_time=dropoff_time,
        customer_age=customer_age,
        promo_code=promo_code,
        db=db,
    )


@router.get("/locadora/rate_plans")
async def listar_rate_plans(usuario: LocadoraOrFilial, db: DB):
    """Lista todos os planos tarifários da locadora."""
    return await tarifa_service.listar_rate_plans_empresa(usuario.locadoraId, db)


@router.get("/locadora/fees")
async def listar_fees(usuario: LocadoraOrFilial, db: DB):
    """Lista todas as taxas de todas as lojas da locadora."""
    return await tarifa_service.listar_fees_empresa(usuario.locadoraId, db)


@router.get("/locadora/addons")
async def listar_addons(usuario: LocadoraOrFilial, db: DB):
    """Lista todos os adicionais da locadora."""
    return await tarifa_service.listar_addons_empresa(usuario.locadoraId, db)


@router.post("/locadora/cotacao", response_model=CotacaoResponse)
async def calcular_cotacao_locadora(
    payload: CotacaoRequest,
    usuario: LocadoraOrFilial,
    db: DB,
):
    """
    Calcula cotação completa para qualquer loja da locadora.
    O `pickup_store_id` deve ser informado no body.
    """
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)
