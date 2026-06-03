from pydantic import BaseModel


class EmpresasStats(BaseModel):
    total: int


class LojasStats(BaseModel):
    total: int
    ativas: int


class StatusCount(BaseModel):
    status: str
    qty: int


class VeiculosStats(BaseModel):
    total: int
    por_status: list[StatusCount]


class ReservasAdminStats(BaseModel):
    total: int
    por_status: list[StatusCount]


class OtaKeyEmpresa(BaseModel):
    empresa: str
    total: int


class OtaKeysStats(BaseModel):
    total: int
    ativas: int
    por_empresa: list[OtaKeyEmpresa]


class AdminDashboardResponse(BaseModel):
    empresas: EmpresasStats
    lojas: LojasStats
    veiculos: VeiculosStats
    reservas: ReservasAdminStats
    ota_keys: OtaKeysStats
