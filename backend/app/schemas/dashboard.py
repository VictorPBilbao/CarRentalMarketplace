from pydantic import BaseModel


class FrotaStats(BaseModel):
    total: int
    disponivel: int
    alugado: int
    manutencao: int
    em_transito: int


class ReservasStats(BaseModel):
    pendente: int
    confirmada: int
    ativa: int
    hoje_retirada: int
    hoje_devolucao: int


class ContratosStats(BaseModel):
    aberto: int


class FiliaisStats(BaseModel):
    total: int
    ativas: int


class ReservaRecente(BaseModel):
    id: str
    cliente: str
    categoria: str
    filial: str
    retirada: str
    devolucao: str
    status: str
    valor: float


class DashboardResponse(BaseModel):
    frota: FrotaStats
    reservas: ReservasStats
    contratos: ContratosStats
    filiais: FiliaisStats
    reservas_recentes: list[ReservaRecente]
