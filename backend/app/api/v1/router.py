from fastapi import APIRouter

from app.api.v1.endpoints import auth

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)

# Futuros routers — descomente conforme criar os módulos:
# from app.api.v1.endpoints import locadoras, filiais, veiculos, reservas
# router.include_router(locadoras.router)
# router.include_router(filiais.router)
# router.include_router(veiculos.router)
# router.include_router(reservas.router)
