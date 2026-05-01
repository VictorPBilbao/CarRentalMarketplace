from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from surrealdb import AsyncSurreal

from app.api.deps import CustomerOnly, FilialOnly, LocadoraOnly, StaffOnly
from app.core.database import get_db
from app.schemas.reserva import AtualizarStatusRequest, CriarReservaClienteRequest, CriarReservaRequest, ReservaResponse
from app.services import reserva_service

router = APIRouter(tags=["reservas"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]

# ── Locadora ──────────────────────────────────────────────────────────────────

@router.get("/locadora/reservas", response_model=list[ReservaResponse])
async def listar_reservas_locadora(
    usuario: StaffOnly,
    db: DB,
    status: str | None = Query(None),
):
    return await reserva_service.listar(usuario.locadoraId, db, status=status)


@router.get("/locadora/reservas/{reserva_id}", response_model=ReservaResponse)
async def buscar_reserva_locadora(reserva_id: str, usuario: StaffOnly, db: DB):
    return await reserva_service.buscar_por_id(reserva_id, usuario.locadoraId, db)


@router.post("/locadora/reservas", response_model=ReservaResponse, status_code=201)
async def criar_reserva_locadora(
    payload: CriarReservaRequest,
    usuario: LocadoraOnly,
    db: DB,
):
    return await reserva_service.criar(payload, usuario.locadoraId, db)


@router.patch("/locadora/reservas/{reserva_id}/status", response_model=ReservaResponse)
async def atualizar_status_locadora(
    reserva_id: str,
    payload: AtualizarStatusRequest,
    usuario: LocadoraOnly,
    db: DB,
):
    return await reserva_service.atualizar_status(reserva_id, payload, usuario.locadoraId, db)


# ── Filial ────────────────────────────────────────────────────────────────────

@router.get("/filial/reservas", response_model=list[ReservaResponse])
async def listar_reservas_filial(
    usuario: FilialOnly,
    db: DB,
    status: str | None = Query(None),
):
    return await reserva_service.listar(
        usuario.locadoraId, db, store_id=usuario.matrizId, status=status
    )


@router.get("/filial/reservas/{reserva_id}", response_model=ReservaResponse)
async def buscar_reserva_filial(reserva_id: str, usuario: FilialOnly, db: DB):
    return await reserva_service.buscar_por_id(
        reserva_id, usuario.locadoraId, db, store_id=usuario.matrizId
    )


@router.post("/filial/reservas", response_model=ReservaResponse, status_code=201)
async def criar_reserva_filial(
    payload: CriarReservaRequest,
    usuario: FilialOnly,
    db: DB,
):
    return await reserva_service.criar(payload, usuario.locadoraId, db)


@router.patch("/filial/reservas/{reserva_id}/status", response_model=ReservaResponse)
async def atualizar_status_filial(
    reserva_id: str,
    payload: AtualizarStatusRequest,
    usuario: FilialOnly,
    db: DB,
):
    return await reserva_service.atualizar_status(
        reserva_id, payload, usuario.locadoraId, db, store_id=usuario.matrizId
    )


# ── Cliente ───────────────────────────────────────────────────────────────────

@router.post("/cliente/reservas", response_model=ReservaResponse, status_code=201)
async def criar_reserva_cliente(
    payload: CriarReservaClienteRequest,
    usuario: CustomerOnly,
    db: DB,
):
    return await reserva_service.criar_cliente(payload, usuario.id, db)


@router.get("/cliente/reservas", response_model=list[ReservaResponse])
async def listar_reservas_cliente(
    usuario: CustomerOnly,
    db: DB,
    status: str | None = Query(None),
):
    return await reserva_service.listar_cliente(usuario.id, db, status=status)


@router.get("/cliente/reservas/{reserva_id}", response_model=ReservaResponse)
async def buscar_reserva_cliente(reserva_id: str, usuario: CustomerOnly, db: DB):
    return await reserva_service.buscar_por_id_cliente(reserva_id, usuario.id, db)
