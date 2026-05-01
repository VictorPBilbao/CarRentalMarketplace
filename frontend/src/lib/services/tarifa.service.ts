import { api } from './api';

// ── Tipos compartilhados ──────────────────────────────────────────────────────

export type TipoCalculoAddon = 'PER_DAY' | 'PER_TRIP' | 'PERCENTAGE';
export type TipoCalculoFee   = 'PERCENTAGE' | 'FLAT_FEE';
export type TipoFeeOneWay    = 'FREE' | 'FIXED' | 'PER_KM';

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
  pricing_type: TipoCalculoAddon;
  max_amount_per_trip: number | null;
}

export interface FeeCalculado {
  id: string;
  name: string;
  amount: number;
  calculation_type: TipoCalculoFee;
  applies_after_time: string | null;
  applies_before_time: string | null;
}

export interface TaxaOneWay {
  pickup_store: string;
  dropoff_store: string;
  fee_type: TipoFeeOneWay;
  amount: number;
}

export interface BuscarTarifasResponse {
  total_days: number;
  is_one_way: boolean;
  rate_plans: RatePlanDisponivel[];
  available_addons: AddonDisponivel[];
  store_fees: FeeCalculado[];
  one_way_fee: TaxaOneWay | null;
}

export interface AddonSelecionado {
  addon_id: string;
  quantity: number;
}

export interface ProtecaoIncluida {
  id: string;
  name: string;
  code: string;
  daily_rate: number;
  deductible_amount: number;
}

export interface ItemCotacao {
  type: string;
  description: string;
  amount: number;
}

export interface CotacaoResponse {
  rate_plan_id: string;
  rate_plan_name: string;
  daily_rate: number;
  total_days: number;
  subtotal_base: number;
  addons_total: number;
  fees_total: number;
  one_way_fee: number;
  final_total: number;
  breakdown: ItemCotacao[];
  included_protections: ProtecaoIncluida[];
  available_addons: AddonDisponivel[];
}

// Tipos para listagem gerencial (locadora)
export interface RatePlanCompleto {
  id: string;
  name: string;
  active: boolean;
  priority: number;
  price: {
    daily_rate: number;
    currency: string;
    mileage_policy: string;
    included_km_per_day: number;
    extra_km_price: number;
  };
  conditions: {
    min_days: number;
    max_days: number | null;
    min_age: number;
    max_age: number | null;
    allow_one_way: boolean;
    advance_booking_days: number;
    promo_code: string | null;
    valid_from: string | null;
    valid_to: string | null;
    stores: string[];
    categories: string[];
  };
  included_protections: string[];
  created_at: string;
  updated_at: string;
}

export interface TaxaLoja {
  id: string;
  name: string;
  store: string;
  store_name?: string;
  store_code?: string;
  active: boolean;
  pricing: { amount: number; calculation_type: TipoCalculoFee };
  conditions: { applies_after_time: string | null; applies_before_time: string | null };
}

export interface AddonCompleto {
  id: string;
  name: string;
  description: string;
  type: string;
  active: boolean;
  stores: string[];
  pricing: { amount: number; calculation_type: TipoCalculoAddon; max_amount_per_trip: number | null };
  updated_at: string;
}

// ── Parâmetros de busca ───────────────────────────────────────────────────────

export interface BuscarTarifasParams {
  dropoff_store_id: string;
  category_id: string;
  pickup_time: string;
  dropoff_time: string;
  customer_age: number;
  promo_code?: string | null;
}

export interface CotacaoRequest {
  pickup_store_id: string;
  dropoff_store_id: string;
  category_id: string;
  pickup_time: string;
  dropoff_time: string;
  customer_age: number;
  promo_code?: string | null;
  rate_plan_id?: string | null;
  selected_addons?: AddonSelecionado[];
}

// ── Service ───────────────────────────────────────────────────────────────────

function buildParams(obj: Record<string, string | number | null | undefined>): string {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(obj)) {
    if (v !== null && v !== undefined && v !== '') p.set(k, String(v));
  }
  return p.toString();
}

export const tarifaService = {
  async buscarTarifasFilial(params: BuscarTarifasParams, token: string): Promise<BuscarTarifasResponse> {
    const qs = buildParams({
      dropoff_store_id: params.dropoff_store_id,
      category_id: params.category_id,
      pickup_time: params.pickup_time,
      dropoff_time: params.dropoff_time,
      customer_age: params.customer_age,
      promo_code: params.promo_code ?? null,
    });
    return api.get<BuscarTarifasResponse>(`/filial/tarifas?${qs}`, token);
  },

  async calcularCotacaoFilial(data: CotacaoRequest, token: string): Promise<CotacaoResponse> {
    return api.post<CotacaoResponse>('/filial/cotacao', data, token);
  },

  async buscarTarifasLocadora(
    params: BuscarTarifasParams & { pickup_store_id: string },
    token: string,
  ): Promise<BuscarTarifasResponse> {
    const qs = buildParams({ ...params, promo_code: params.promo_code ?? null });
    return api.get<BuscarTarifasResponse>(`/locadora/tarifas?${qs}`, token);
  },

  async calcularCotacaoLocadora(data: CotacaoRequest, token: string): Promise<CotacaoResponse> {
    return api.post<CotacaoResponse>('/locadora/cotacao', data, token);
  },

  async listarRatePlans(token: string): Promise<RatePlanCompleto[]> {
    return api.get<RatePlanCompleto[]>('/locadora/rate_plans', token);
  },

  async listarFees(token: string): Promise<TaxaLoja[]> {
    return api.get<TaxaLoja[]>('/locadora/fees', token);
  },

  async listarAddons(token: string): Promise<AddonCompleto[]> {
    return api.get<AddonCompleto[]>('/locadora/addons', token);
  },
};
