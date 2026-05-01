from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from surrealdb import AsyncSurreal

from app.api.deps import FilialOnly, LocadoraOnly, LocadoraOrFilial
from app.core.database import get_db
from app.schemas.tarifa import (
    AddonRequest,
    AddonResponse,
    BuscarTarifasResponse,
    CotacaoRequest,
    CotacaoResponse,
    FeeRequest,
    FeeResponse,
    OneWayRequest,
    OneWayResponse,
)
from app.services import tarifa_service

router = APIRouter(tags=["tarifas"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


# ── Filial: busca e cotação ───────────────────────────────────────────────────

@router.get("/filial/tarifas", response_model=BuscarTarifasResponse)
async def buscar_tarifas_filial(
    usuario: FilialOnly,
    db: DB,
    dropoff_store_id: str = Query(...),
    category_id: str = Query(...),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    promo_code: str | None = Query(None),
):
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
async def calcular_cotacao_filial(payload: CotacaoRequest, usuario: FilialOnly, db: DB):
    payload.pickup_store_id = usuario.matrizId
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)


# ── Filial: one-way config ────────────────────────────────────────────────────

@router.get("/filial/one-way", response_model=list[OneWayResponse])
async def listar_one_way(usuario: FilialOnly, db: DB):
    """Lista regras de devolução one-way para a loja da filial."""
    return await tarifa_service.listar_one_way_filial(usuario.matrizId, db)


@router.post("/filial/one-way", response_model=OneWayResponse, status_code=201)
async def criar_one_way(payload: OneWayRequest, usuario: FilialOnly, db: DB):
    """Cria regra: cobra X quando um veículo de outra loja é devolvido aqui."""
    return await tarifa_service.criar_one_way(payload, usuario.matrizId, db)


@router.put("/filial/one-way/{rule_id}", response_model=OneWayResponse)
async def atualizar_one_way(rule_id: str, payload: OneWayRequest, usuario: FilialOnly, db: DB):
    return await tarifa_service.atualizar_one_way(rule_id, payload, usuario.matrizId, db)


@router.delete("/filial/one-way/{rule_id}", status_code=204)
async def excluir_one_way(rule_id: str, usuario: FilialOnly, db: DB):
    await tarifa_service.excluir_one_way(rule_id, usuario.matrizId, db)


# ── Locadora: busca e cotação ─────────────────────────────────────────────────

@router.get("/locadora/tarifas", response_model=BuscarTarifasResponse)
async def buscar_tarifas_locadora(
    usuario: LocadoraOrFilial,
    db: DB,
    pickup_store_id: str = Query(...),
    dropoff_store_id: str = Query(...),
    category_id: str = Query(...),
    pickup_time: datetime = Query(...),
    dropoff_time: datetime = Query(...),
    customer_age: int = Query(..., ge=18),
    promo_code: str | None = Query(None),
):
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


@router.post("/locadora/cotacao", response_model=CotacaoResponse)
async def calcular_cotacao_locadora(payload: CotacaoRequest, usuario: LocadoraOrFilial, db: DB):
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)


# ── Locadora: listagem gerencial ──────────────────────────────────────────────

@router.get("/locadora/rate_plans")
async def listar_rate_plans(usuario: LocadoraOrFilial, db: DB):
    return await tarifa_service.listar_rate_plans_empresa(usuario.locadoraId, db)


@router.get("/locadora/fees", response_model=list[FeeResponse])
async def listar_fees(usuario: LocadoraOrFilial, db: DB):
    return await tarifa_service.listar_fees_empresa(usuario.locadoraId, db)


@router.get("/locadora/addons", response_model=list[AddonResponse])
async def listar_addons(usuario: LocadoraOrFilial, db: DB):
    return await tarifa_service.listar_addons_empresa(usuario.locadoraId, db)


# ── Locadora: CRUD addons ─────────────────────────────────────────────────────

@router.post("/locadora/addons", response_model=AddonResponse, status_code=201)
async def criar_addon(payload: AddonRequest, usuario: LocadoraOnly, db: DB):
    return await tarifa_service.criar_addon(payload, usuario.locadoraId, db)


@router.put("/locadora/addons/{addon_id}", response_model=AddonResponse)
async def atualizar_addon(addon_id: str, payload: AddonRequest, usuario: LocadoraOnly, db: DB):
    return await tarifa_service.atualizar_addon(addon_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/addons/{addon_id}", status_code=204)
async def desativar_addon(addon_id: str, usuario: LocadoraOnly, db: DB):
    await tarifa_service.desativar_addon(addon_id, usuario.locadoraId, db)


# ── Locadora: CRUD fees ───────────────────────────────────────────────────────

@router.post("/locadora/fees", response_model=FeeResponse, status_code=201)
async def criar_fee(payload: FeeRequest, usuario: LocadoraOnly, db: DB):
    return await tarifa_service.criar_fee(payload, usuario.locadoraId, db)


@router.put("/locadora/fees/{fee_id}", response_model=FeeResponse)
async def atualizar_fee(fee_id: str, payload: FeeRequest, usuario: LocadoraOnly, db: DB):
    return await tarifa_service.atualizar_fee(fee_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/fees/{fee_id}", status_code=204)
async def desativar_fee(fee_id: str, usuario: LocadoraOnly, db: DB):
    await tarifa_service.desativar_fee(fee_id, usuario.locadoraId, db)
