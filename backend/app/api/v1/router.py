from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, filial, funcionario

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(filial.router)
router.include_router(funcionario.router)
