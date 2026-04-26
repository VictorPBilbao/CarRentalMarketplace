import type { PageServerLoad } from './$types';
import { dashboardService, type DashboardData } from '$lib/services/dashboard.service';

const VAZIO: DashboardData = {
  frota:     { total: 0, disponivel: 0, alugado: 0, manutencao: 0, em_transito: 0 },
  reservas:  { pendente: 0, confirmada: 0, ativa: 0, hoje_retirada: 0, hoje_devolucao: 0 },
  contratos: { aberto: 0 },
  filiais:   { total: 0, ativas: 0 },
  reservas_recentes: [],
};

export const load: PageServerLoad = async ({ locals }) => {
  try {
    const dashboard = await dashboardService.getDashboard(locals.token!);
    return { dashboard, erro: null };
  } catch {
    return { dashboard: VAZIO, erro: 'Não foi possível carregar os dados do painel.' };
  }
};
