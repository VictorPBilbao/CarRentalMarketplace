from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException
from surrealdb import AsyncSurreal

from app.api.deps import FilialOnly, LocadoraOnly, StaffOnly
from app.core.database import get_db
from app.schemas.filial import FilialResponse
from app.schemas.veiculo import VeiculoRequest, VeiculoResponse
from app.services import filial_service, veiculo_service

router = APIRouter(tags=["veiculos"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


# ── Rotas da Locadora (/locadora/veiculos) ────────────────────────────────────
# Acesso: locadora vê toda a frota da empresa; pode especificar qualquer loja.

@router.get("/locadora/veiculos", response_model=list[VeiculoResponse])
async def listar_veiculos(usuario: StaffOnly, db: DB):
    return await veiculo_service.listar(usuario.locadoraId, db)


@router.get("/locadora/veiculos/{veiculo_id}", response_model=VeiculoResponse)
async def buscar_veiculo(veiculo_id: str, usuario: StaffOnly, db: DB):
    return await veiculo_service.buscar_por_id(veiculo_id, usuario.locadoraId, db)


@router.post("/locadora/veiculos", response_model=VeiculoResponse, status_code=201)
async def criar_veiculo(payload: VeiculoRequest, usuario: LocadoraOnly, db: DB):
    if not payload.current_store:
        raise HTTPException(status_code=422, detail='Informe a loja vinculada ao veículo.')
    return await veiculo_service.criar(payload, usuario.locadoraId, payload.current_store, db)


@router.put("/locadora/veiculos/{veiculo_id}", response_model=VeiculoResponse)
async def atualizar_veiculo(veiculo_id: str, payload: VeiculoRequest, usuario: LocadoraOnly, db: DB):
    if not payload.current_store:
        raise HTTPException(status_code=422, detail='Informe a loja vinculada ao veículo.')
    return await veiculo_service.atualizar(veiculo_id, payload, usuario.locadoraId, payload.current_store, db)


# ── Dados da loja (filial) ───────────────────────────────────────────────────

@router.get("/filial/minha-loja", response_model=FilialResponse)
async def minha_loja(usuario: FilialOnly, db: DB):
    """Retorna os dados da loja do usuário filial logado."""
    if not usuario.matrizId:
        raise HTTPException(status_code=403, detail='Filial não identificada no token.')
    return await filial_service.buscar_por_id(usuario.matrizId, usuario, db)


# ── Rotas da Filial (/filial/veiculos) ────────────────────────────────────────
# Acesso: filial vê e gerencia apenas veículos da própria loja (matrizId).

@router.get("/filial/veiculos", response_model=list[VeiculoResponse])
async def listar_veiculos_filial(usuario: FilialOnly, db: DB):
    if not usuario.matrizId:
        raise HTTPException(status_code=403, detail='Filial não identificada no token.')
    return await veiculo_service.listar(usuario.locadoraId, db, store_id=usuario.matrizId)


@router.get("/filial/veiculos/{veiculo_id}", response_model=VeiculoResponse)
async def buscar_veiculo_filial(veiculo_id: str, usuario: FilialOnly, db: DB):
    if not usuario.matrizId:
        raise HTTPException(status_code=403, detail='Filial não identificada no token.')
    return await veiculo_service.buscar_por_id(veiculo_id, usuario.locadoraId, db, store_id=usuario.matrizId)


@router.post("/filial/veiculos", response_model=VeiculoResponse, status_code=201)
async def criar_veiculo_filial(payload: VeiculoRequest, usuario: FilialOnly, db: DB):
    if not usuario.matrizId:
        raise HTTPException(status_code=403, detail='Filial não identificada no token.')
    # A loja é sempre a própria filial — ignora current_store do payload por segurança
    return await veiculo_service.criar(payload, usuario.locadoraId, usuario.matrizId, db)


@router.put("/filial/veiculos/{veiculo_id}", response_model=VeiculoResponse)
async def atualizar_veiculo_filial(veiculo_id: str, payload: VeiculoRequest, usuario: FilialOnly, db: DB):
    if not usuario.matrizId:
        raise HTTPException(status_code=403, detail='Filial não identificada no token.')
    # Filial só edita veículos que estão na sua loja; loja permanece a mesma
    return await veiculo_service.atualizar(
        veiculo_id, payload,
        company_id=usuario.locadoraId,
        store_id=usuario.matrizId,
        db=db,
        store_restrito=usuario.matrizId,
    )
