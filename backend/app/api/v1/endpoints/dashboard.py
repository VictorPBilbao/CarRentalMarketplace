from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from surrealdb import AsyncSurreal

from app.api.deps import LocadoraOnly
from app.core.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/locadora", tags=["locadora"])

DB: TypeAlias = Annotated[AsyncSurreal, Depends(get_db)]


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(usuario: LocadoraOnly, db: DB):
    return await dashboard_service.get_dashboard(usuario, db)
