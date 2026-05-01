from fastapi import APIRouter

from app.api.v1.endpoints import auth, categoria_veiculo, dashboard, filial, funcionario, publico, reserva, tarifa, veiculo

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(publico.router)
router.include_router(dashboard.router)
router.include_router(filial.router)
router.include_router(funcionario.router)
router.include_router(categoria_veiculo.router)
router.include_router(veiculo.router)
router.include_router(reserva.router)
router.include_router(tarifa.router)
