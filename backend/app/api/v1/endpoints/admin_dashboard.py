from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import AdminOnly
from app.core.database import get_db
from app.schemas.admin_dashboard import AdminDashboardResponse
from app.services import admin_dashboard_service

router = APIRouter(prefix="/admin", tags=["Admin"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(usuario: AdminOnly, db: DB):
    """Retorna estatísticas globais do sistema para o painel administrativo."""
    return await admin_dashboard_service.get_admin_dashboard(db)
