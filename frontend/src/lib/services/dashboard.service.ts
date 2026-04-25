import { api } from './api';

// ── tipos ──
export type StatusReserva = 'PENDING' | 'CONFIRMED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';

export interface ReservaRecente {
  id:        string;
  cliente:   string;
  categoria: string;
  filial:    string;
  retirada:  string;
  devolucao: string;
  status:    StatusReserva;
  valor:     number;
}

export interface DashboardData {
  frota: {
    total:       number;
    disponivel:  number;
    alugado:     number;
    manutencao:  number;
    em_transito: number;
  };
  reservas: {
    pendente:       number;
    confirmada:     number;
    ativa:          number;
    hoje_retirada:  number;
    hoje_devolucao: number;
  };
  contratos: {
    aberto: number;
  };
  filiais: {
    total:  number;
    ativas: number;
  };
  reservas_recentes: ReservaRecente[];
}

// ── service ──
export const dashboardService = {
  async getDashboard(token: string): Promise<DashboardData> {
    return api.get<DashboardData>('/locadora/dashboard', token);
  },
};
