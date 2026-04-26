import { api } from './api';

export type StatusReserva = 'PENDING' | 'CONFIRMED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';

export interface ItemPricing {
  type: string;
  description: string;
  amount: number;
}

export interface ReservaPricing {
  daily_rate: number;
  total_days: number;
  fees: number;
  total_amount: number;
  breakdown: ItemPricing[];
}

export interface Reserva {
  id: string;
  customer: string;
  category: string;
  pickup_store: string;
  dropoff_store: string;
  pickup_time: string;
  dropoff_time: string;
  flight_number: string | null;
  notes: string | null;
  pricing: ReservaPricing;
  status: StatusReserva;
  created_at: string;
  updated_at: string;
}

export interface CriarReservaDTO {
  customer_id: string;
  category_id: string;
  pickup_store_id: string;
  dropoff_store_id: string;
  pickup_time: string;
  dropoff_time: string;
  flight_number?: string | null;
  notes?: string | null;
  pricing: {
    daily_rate: number;
    total_days: number;
    fees: number;
    breakdown: ItemPricing[];
  };
}

export const reservaService = {
  async listar(token: string, status?: string): Promise<Reserva[]> {
    const q = status ? `?status=${encodeURIComponent(status)}` : '';
    return api.get<Reserva[]>(`/locadora/reservas${q}`, token);
  },

  async buscarPorId(id: string, token: string): Promise<Reserva> {
    return api.get<Reserva>(`/locadora/reservas/${encodeURIComponent(id)}`, token);
  },

  async criar(dados: CriarReservaDTO, token: string): Promise<Reserva> {
    return api.post<Reserva>('/locadora/reservas', dados, token);
  },

  async atualizarStatus(id: string, status: StatusReserva, token: string): Promise<Reserva> {
    return api.patch<Reserva>(`/locadora/reservas/${encodeURIComponent(id)}/status`, { status }, token);
  },
};

export const filialReservaService = {
  async listar(token: string, status?: string): Promise<Reserva[]> {
    const q = status ? `?status=${encodeURIComponent(status)}` : '';
    return api.get<Reserva[]>(`/filial/reservas${q}`, token);
  },

  async buscarPorId(id: string, token: string): Promise<Reserva> {
    return api.get<Reserva>(`/filial/reservas/${encodeURIComponent(id)}`, token);
  },

  async atualizarStatus(id: string, status: StatusReserva, token: string): Promise<Reserva> {
    return api.patch<Reserva>(`/filial/reservas/${encodeURIComponent(id)}/status`, { status }, token);
  },
};
