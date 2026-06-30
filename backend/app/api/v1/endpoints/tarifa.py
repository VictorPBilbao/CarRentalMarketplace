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
    ProtecaoRequest,
    ProtecaoResponse,
    RatePlanRequest,
    RatePlanResponse,
)
from app.services import (
    addon_service,
    fee_service,
    one_way_service,
    protecao_service,
    rate_plan_service,
    tarifa_service,
)

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
    nationality: str | None = Query(None),
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
        nationality=nationality,
        promo_code=promo_code,
        db=db,
    )


@router.post("/filial/cotacao", response_model=CotacaoResponse)
async def calcular_cotacao_filial(payload: CotacaoRequest, usuario: FilialOnly, db: DB):
    payload.pickup_store_id = usuario.matrizId
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)


# ── Filial: rate plans ───────────────────────────────────────────────────────

@router.get("/filial/rate_plans")
async def listar_rate_plans_filial(usuario: FilialOnly, db: DB):
    return await rate_plan_service.listar_rate_plans_filial(usuario.locadoraId, usuario.matrizId, db)


@router.post("/filial/rate_plans", response_model=RatePlanResponse, status_code=201)
async def criar_rate_plan_filial(payload: RatePlanRequest, usuario: FilialOnly, db: DB):
    return await rate_plan_service.criar_rate_plan_filial(payload, usuario.locadoraId, usuario.matrizId, db)


@router.put("/filial/rate_plans/{plan_id}", response_model=RatePlanResponse)
async def atualizar_rate_plan_filial(plan_id: str, payload: RatePlanRequest, usuario: FilialOnly, db: DB):
    return await rate_plan_service.atualizar_rate_plan_filial(plan_id, payload, usuario.locadoraId, usuario.matrizId, db)


@router.delete("/filial/rate_plans/{plan_id}", status_code=204)
async def desativar_rate_plan_filial(plan_id: str, usuario: FilialOnly, db: DB):
    await rate_plan_service.desativar_rate_plan_filial(plan_id, usuario.locadoraId, usuario.matrizId, db)


# ── Filial: one-way config ────────────────────────────────────────────────────

@router.get("/filial/one-way", response_model=list[OneWayResponse])
async def listar_one_way(usuario: FilialOnly, db: DB):
    return await one_way_service.listar_one_way_filial(usuario.matrizId, db)


@router.post("/filial/one-way", response_model=OneWayResponse, status_code=201)
async def criar_one_way(payload: OneWayRequest, usuario: FilialOnly, db: DB):
    return await one_way_service.criar_one_way(payload, usuario.matrizId, db)


@router.put("/filial/one-way/{rule_id}", response_model=OneWayResponse)
async def atualizar_one_way(rule_id: str, payload: OneWayRequest, usuario: FilialOnly, db: DB):
    return await one_way_service.atualizar_one_way(rule_id, payload, usuario.matrizId, db)


@router.delete("/filial/one-way/{rule_id}", status_code=204)
async def excluir_one_way(rule_id: str, usuario: FilialOnly, db: DB):
    await one_way_service.excluir_one_way(rule_id, usuario.matrizId, db)


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
    nationality: str | None = Query(None),
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
        nationality=nationality,
        promo_code=promo_code,
        db=db,
    )


@router.post("/locadora/cotacao", response_model=CotacaoResponse)
async def calcular_cotacao_locadora(payload: CotacaoRequest, usuario: LocadoraOrFilial, db: DB):
    return await tarifa_service.calcular_cotacao(payload, usuario.locadoraId, db)


# ── Locadora: rate plans ──────────────────────────────────────────────────────

@router.get("/locadora/rate_plans")
async def listar_rate_plans(usuario: LocadoraOrFilial, db: DB):
    return await rate_plan_service.listar_rate_plans_empresa(usuario.locadoraId, db)


@router.post("/locadora/rate_plans", response_model=RatePlanResponse, status_code=201)
async def criar_rate_plan(payload: RatePlanRequest, usuario: LocadoraOnly, db: DB):
    return await rate_plan_service.criar_rate_plan(payload, usuario.locadoraId, db)


@router.put("/locadora/rate_plans/{plan_id}", response_model=RatePlanResponse)
async def atualizar_rate_plan(plan_id: str, payload: RatePlanRequest, usuario: LocadoraOnly, db: DB):
    return await rate_plan_service.atualizar_rate_plan(plan_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/rate_plans/{plan_id}", status_code=204)
async def desativar_rate_plan(plan_id: str, usuario: LocadoraOnly, db: DB):
    await rate_plan_service.desativar_rate_plan(plan_id, usuario.locadoraId, db)


# ── Locadora: proteções ───────────────────────────────────────────────────────

@router.get("/locadora/protecoes", response_model=list[ProtecaoResponse])
async def listar_protecoes(usuario: LocadoraOrFilial, db: DB):
    return await protecao_service.listar_protecoes_empresa(usuario.locadoraId, db)


@router.post("/locadora/protecoes", response_model=ProtecaoResponse, status_code=201)
async def criar_protecao(payload: ProtecaoRequest, usuario: LocadoraOnly, db: DB):
    return await protecao_service.criar_protecao(payload, usuario.locadoraId, db)


@router.put("/locadora/protecoes/{prot_id}", response_model=ProtecaoResponse)
async def atualizar_protecao(prot_id: str, payload: ProtecaoRequest, usuario: LocadoraOnly, db: DB):
    return await protecao_service.atualizar_protecao(prot_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/protecoes/{prot_id}", status_code=204)
async def excluir_protecao(prot_id: str, usuario: LocadoraOnly, db: DB):
    await protecao_service.excluir_protecao(prot_id, usuario.locadoraId, db)


# ── Locadora: fees ────────────────────────────────────────────────────────────

@router.get("/locadora/fees", response_model=list[FeeResponse])
async def listar_fees(usuario: LocadoraOrFilial, db: DB):
    return await fee_service.listar_fees_empresa(usuario.locadoraId, db)


@router.post("/locadora/fees", response_model=FeeResponse, status_code=201)
async def criar_fee(payload: FeeRequest, usuario: LocadoraOnly, db: DB):
    return await fee_service.criar_fee(payload, usuario.locadoraId, db)


@router.put("/locadora/fees/{fee_id}", response_model=FeeResponse)
async def atualizar_fee(fee_id: str, payload: FeeRequest, usuario: LocadoraOnly, db: DB):
    return await fee_service.atualizar_fee(fee_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/fees/{fee_id}", status_code=204)
async def desativar_fee(fee_id: str, usuario: LocadoraOnly, db: DB):
    await fee_service.desativar_fee(fee_id, usuario.locadoraId, db)


# ── Locadora: addons ──────────────────────────────────────────────────────────

@router.get("/locadora/addons", response_model=list[AddonResponse])
async def listar_addons(usuario: LocadoraOrFilial, db: DB):
    return await addon_service.listar_addons_empresa(usuario.locadoraId, db)


@router.post("/locadora/addons", response_model=AddonResponse, status_code=201)
async def criar_addon(payload: AddonRequest, usuario: LocadoraOnly, db: DB):
    return await addon_service.criar_addon(payload, usuario.locadoraId, db)


@router.put("/locadora/addons/{addon_id}", response_model=AddonResponse)
async def atualizar_addon(addon_id: str, payload: AddonRequest, usuario: LocadoraOnly, db: DB):
    return await addon_service.atualizar_addon(addon_id, payload, usuario.locadoraId, db)


@router.delete("/locadora/addons/{addon_id}", status_code=204)
async def desativar_addon(addon_id: str, usuario: LocadoraOnly, db: DB):
    await addon_service.desativar_addon(addon_id, usuario.locadoraId, db)
