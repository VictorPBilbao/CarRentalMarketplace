import { api } from './api';
import type { Filial } from './filial.service';
import type { Categoria } from './categoria.service';

export interface BuscarTarifasParams {
  pickup_store_id: string;
  dropoff_store_id: string;
  category_id: string;
  pickup_time: string;
  dropoff_time: string;
  customer_age: number;
  nationality?: string | null;
  promo_code?: string | null;
}

export interface RatePlanDisponivel {
  id: string;
  name: string;
  daily_rate: number;
  total_days: number;
  subtotal: number;
  mileage_policy: string;
  included_km_per_day: number;
  extra_km_price: number;
  currency: string;
  included_protections: string[];
  allow_one_way: boolean;
}

export interface AddonDisponivel {
  id: string;
  name: string;
  description: string;
  type: string;
  pricing_amount: number;
  pricing_type: string;
  max_amount_per_trip: number | null;
}

export interface BuscarTarifasResponse {
  total_days: number;
  is_one_way: boolean;
  rate_plans: RatePlanDisponivel[];
  available_addons: AddonDisponivel[];
  store_fees: { id: string; name: string; amount: number }[];
  one_way_fee: { fee_type: string; amount: number } | null;
  disponibilidade: number;
  lojas_alternativas: { store_id: string; store_name: string; available_units: number }[];
}

export const publicoService = {
  async listarLojas(): Promise<Filial[]> {
    return api.get<Filial[]>('/publico/lojas');
  },

  async listarCategorias(): Promise<Categoria[]> {
    return api.get<Categoria[]>('/publico/categorias');
  },

  async buscar(params: BuscarTarifasParams): Promise<BuscarTarifasResponse> {
    const q = new URLSearchParams({
      pickup_store_id:  params.pickup_store_id,
      dropoff_store_id: params.dropoff_store_id,
      category_id:      params.category_id,
      pickup_time:      params.pickup_time,
      dropoff_time:     params.dropoff_time,
      customer_age:     String(params.customer_age),
      ...(params.nationality  ? { nationality:  params.nationality  } : {}),
      ...(params.promo_code   ? { promo_code:   params.promo_code   } : {}),
    });
    return api.get<BuscarTarifasResponse>(`/publico/buscar?${q}`);
  },
};
