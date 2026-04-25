from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import StaffOnly
from app.core.database import get_db
from app.schemas.funcionario import FuncionarioRequest, FuncionarioResponse
from app.services import funcionario_service

router = APIRouter(prefix="/locadora", tags=["funcionarios"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/filiais/{filial_id}/funcionarios", response_model=list[FuncionarioResponse])
async def listar_funcionarios(filial_id: str, usuario: StaffOnly, db: DB):
    return await funcionario_service.listar(filial_id, usuario, db)


@router.post("/filiais/{filial_id}/funcionarios", response_model=FuncionarioResponse, status_code=201)
async def criar_funcionario(filial_id: str, payload: FuncionarioRequest, usuario: StaffOnly, db: DB):
    return await funcionario_service.criar(filial_id, payload, usuario, db)


@router.delete("/filiais/{filial_id}/funcionarios/{user_id}", status_code=204)
async def remover_funcionario(filial_id: str, user_id: str, usuario: StaffOnly, db: DB):
    await funcionario_service.remover(filial_id, user_id, usuario, db)
