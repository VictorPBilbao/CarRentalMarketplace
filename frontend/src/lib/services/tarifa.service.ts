import { api } from './api';

// ── Tipos compartilhados ──────────────────────────────────────────────────────

export type TipoCalculoAddon = 'PER_DAY' | 'PER_TRIP' | 'PERCENTAGE';
export type TipoCalculoFee   = 'PERCENTAGE' | 'FLAT_FEE';
export type TipoFeeOneWay    = 'FREE' | 'FIXED' | 'PER_KM';
export type TipoAddon        = 'INSURANCE' | 'EQUIPMENT' | 'SERVICE' | 'FEE';

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

export interface LojaAlternativa {
  store_id: string;
  store_name: string;
  transit_time_hours: number;
  transfer_fee: number;
  available_units: number;
}

export interface BuscarTarifasResponse {
  total_days: number;
  is_one_way: boolean;
  rate_plans: RatePlanDisponivel[];
  available_addons: AddonDisponivel[];
  store_fees: FeeCalculado[];
  one_way_fee: TaxaOneWay | null;
  disponibilidade: number;
  lojas_alternativas: LojaAlternativa[];
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

// Tipos gerenciais (locadora)
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

export interface AddonPricing {
  amount: number;
  calculation_type: TipoCalculoAddon;
  max_amount_per_trip: number | null;
}

export interface AddonCompleto {
  id: string;
  name: string;
  description: string;
  type: string;
  active: boolean;
  stores: string[];
  pricing: AddonPricing;
  updated_at: string;
}

export interface FeePricing {
  amount: number;
  calculation_type: TipoCalculoFee;
}

export interface FeeConditions {
  applies_after_time: string | null;
  applies_before_time: string | null;
}

export interface TaxaLoja {
  id: string;
  name: string;
  store: string;
  store_name?: string;
  store_code?: string;
  active: boolean;
  is_tax: boolean;
  pricing: FeePricing;
  conditions: FeeConditions;
}

export interface OneWayRule {
  id: string;
  from_store_id: string;
  from_store_name: string;
  to_store_id: string;
  fee_type: TipoFeeOneWay;
  amount: number;
  active: boolean;
}

// ── Parâmetros de busca ───────────────────────────────────────────────────────

export interface BuscarTarifasParams {
  dropoff_store_id: string;
  category_id: string;
  pickup_time: string;
  dropoff_time: string;
  customer_age: number;
  nationality?: string | null;
  promo_code?: string | null;
}

export interface CotacaoRequest {
  pickup_store_id: string;
  dropoff_store_id: string;
  category_id: string;
  pickup_time: string;
  dropoff_time: string;
  customer_age: number;
  nationality?: string | null;
  promo_code?: string | null;
  rate_plan_id?: string | null;
  selected_addons?: AddonSelecionado[];
}

// ── CRUD requests ─────────────────────────────────────────────────────────────

export interface RatePlanRequest {
  name: string;
  priority: number;
  active: boolean;
  price: {
    daily_rate: number;
    currency: string;
    mileage_policy: string;
    included_km_per_day: number;
    extra_km_price: number;
  };
  conditions: {
    categories: string[];
    stores: string[];
    min_days: number;
    max_days: number | null;
    min_age: number;
    max_age: number | null;
    advance_booking_days: number;
    allow_one_way: boolean;
    valid_from: string | null;
    valid_to: string | null;
    promo_code: string | null;
    allowed_nationalities: string[];
  };
  included_protections: string[];
}

export interface PricingMatrixItem {
  category: string;
  daily_rate: number;
  deductible_amount: number;
}

export interface ProtecaoItem {
  id: string;
  name: string;
  code: string;
  pricing_matrix: PricingMatrixItem[];
}

export interface ProtecaoRequest {
  name: string;
  code: string;
  pricing_matrix: PricingMatrixItem[];
}

export interface AddonRequest {
  name: string;
  description: string;
  type: TipoAddon;
  pricing: AddonPricing;
  stores: string[];
  active: boolean;
}

export interface FeeRequest {
  name: string;
  store_id: string;
  pricing: FeePricing;
  conditions: FeeConditions;
  active: boolean;
  is_tax: boolean;
}

export interface OneWayRequest {
  from_store_id: string;
  fee_type: TipoFeeOneWay;
  amount: number;
  active: boolean;
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
  // Busca/cotação
  async buscarTarifasFilial(params: BuscarTarifasParams, token: string): Promise<BuscarTarifasResponse> {
    const qs = buildParams({ ...params, promo_code: params.promo_code ?? null });
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

  // Listagem gerencial
  async listarRatePlans(token: string): Promise<RatePlanCompleto[]> {
    return api.get<RatePlanCompleto[]>('/locadora/rate_plans', token);
  },

  async listarFees(token: string): Promise<TaxaLoja[]> {
    return api.get<TaxaLoja[]>('/locadora/fees', token);
  },

  async listarAddons(token: string): Promise<AddonCompleto[]> {
    return api.get<AddonCompleto[]>('/locadora/addons', token);
  },

  // CRUD addons
  async criarAddon(data: AddonRequest, token: string): Promise<AddonCompleto> {
    return api.post<AddonCompleto>('/locadora/addons', data, token);
  },

  async atualizarAddon(id: string, data: AddonRequest, token: string): Promise<AddonCompleto> {
    return api.put<AddonCompleto>(`/locadora/addons/${id}`, data, token);
  },

  async desativarAddon(id: string, token: string): Promise<void> {
    return api.delete(`/locadora/addons/${id}`, token);
  },

  // CRUD fees
  async criarFee(data: FeeRequest, token: string): Promise<TaxaLoja> {
    return api.post<TaxaLoja>('/locadora/fees', data, token);
  },

  async atualizarFee(id: string, data: FeeRequest, token: string): Promise<TaxaLoja> {
    return api.put<TaxaLoja>(`/locadora/fees/${id}`, data, token);
  },

  async desativarFee(id: string, token: string): Promise<void> {
    return api.delete(`/locadora/fees/${id}`, token);
  },

  // One-Way (filial)
  async listarOneWay(token: string): Promise<OneWayRule[]> {
    return api.get<OneWayRule[]>('/filial/one-way', token);
  },

  async criarOneWay(data: OneWayRequest, token: string): Promise<OneWayRule> {
    return api.post<OneWayRule>('/filial/one-way', data, token);
  },

  async atualizarOneWay(id: string, data: OneWayRequest, token: string): Promise<OneWayRule> {
    return api.put<OneWayRule>(`/filial/one-way/${id}`, data, token);
  },

  async excluirOneWay(id: string, token: string): Promise<void> {
    return api.delete(`/filial/one-way/${id}`, token);
  },

  // CRUD rate_plans (locadora)
  async criarRatePlan(data: RatePlanRequest, token: string): Promise<RatePlanCompleto> {
    return api.post<RatePlanCompleto>('/locadora/rate_plans', data, token);
  },

  async atualizarRatePlan(id: string, data: RatePlanRequest, token: string): Promise<RatePlanCompleto> {
    return api.put<RatePlanCompleto>(`/locadora/rate_plans/${id}`, data, token);
  },

  async desativarRatePlan(id: string, token: string): Promise<void> {
    return api.delete(`/locadora/rate_plans/${id}`, token);
  },

  // CRUD rate_plans (filial)
  async listarRatePlansFilial(token: string): Promise<RatePlanCompleto[]> {
    return api.get<RatePlanCompleto[]>('/filial/rate_plans', token);
  },

  async criarRatePlanFilial(data: RatePlanRequest, token: string): Promise<RatePlanCompleto> {
    return api.post<RatePlanCompleto>('/filial/rate_plans', data, token);
  },

  async atualizarRatePlanFilial(id: string, data: RatePlanRequest, token: string): Promise<RatePlanCompleto> {
    return api.put<RatePlanCompleto>(`/filial/rate_plans/${id}`, data, token);
  },

  async desativarRatePlanFilial(id: string, token: string): Promise<void> {
    return api.delete(`/filial/rate_plans/${id}`, token);
  },

  // CRUD proteções
  async listarProtecoes(token: string): Promise<ProtecaoItem[]> {
    return api.get<ProtecaoItem[]>('/locadora/protecoes', token);
  },

  async criarProtecao(data: ProtecaoRequest, token: string): Promise<ProtecaoItem> {
    return api.post<ProtecaoItem>('/locadora/protecoes', data, token);
  },

  async atualizarProtecao(id: string, data: ProtecaoRequest, token: string): Promise<ProtecaoItem> {
    return api.put<ProtecaoItem>(`/locadora/protecoes/${id}`, data, token);
  },

  async excluirProtecao(id: string, token: string): Promise<void> {
    return api.delete(`/locadora/protecoes/${id}`, token);
  },
};
