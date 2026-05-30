from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

TipoCalculoAddon = Literal['PER_DAY', 'PER_TRIP', 'PERCENTAGE']
TipoCalculoFee = Literal['PERCENTAGE', 'FLAT_FEE']
TipoFeeOneWay = Literal['FREE', 'FIXED', 'PER_KM']
TipoAddon = Literal['INSURANCE', 'EQUIPMENT', 'SERVICE', 'FEE']


# ── Modelos de cotação (read) ─────────────────────────────────────────────────

class AddonSelecionado(BaseModel):
    addon_id: str
    quantity: int = 1


class RatePlanDisponivel(BaseModel):
    id: str
    name: str
    daily_rate: float
    total_days: int
    subtotal: float
    mileage_policy: str
    included_km_per_day: int
    extra_km_price: float
    currency: str
    included_protections: list[str]
    allow_one_way: bool


class AddonDisponivel(BaseModel):
    id: str
    name: str
    description: str
    type: str
    pricing_amount: float
    pricing_type: TipoCalculoAddon
    max_amount_per_trip: float | None


class FeeCalculado(BaseModel):
    id: str
    name: str
    amount: float
    calculation_type: TipoCalculoFee
    applies_after_time: str | None
    applies_before_time: str | None
    is_tax: bool = False


class TaxaOneWay(BaseModel):
    pickup_store: str
    dropoff_store: str
    fee_type: TipoFeeOneWay
    amount: float


class LojaAlternativa(BaseModel):
    store_id: str
    store_name: str
    transit_time_hours: int
    transfer_fee: float
    available_units: int


class BuscarTarifasResponse(BaseModel):
    total_days: int
    is_one_way: bool
    rate_plans: list[RatePlanDisponivel]
    available_addons: list[AddonDisponivel]
    store_fees: list[FeeCalculado]
    one_way_fee: TaxaOneWay | None
    disponibilidade: int = 0
    lojas_alternativas: list[LojaAlternativa] = []


class ResultadoCategoriaDisponivel(BaseModel):
    category_id: str
    category_name: str
    category_code: str
    image_url: str | None = None
    disponibilidade: int
    rate_plans: list[RatePlanDisponivel]
    store_fees: list[FeeCalculado]
    one_way_fee: TaxaOneWay | None
    lojas_alternativas: list[LojaAlternativa] = []
    available_addons: list[AddonDisponivel] = []


class BuscarTodasCategoriasResponse(BaseModel):
    total_days: int
    is_one_way: bool
    categorias: list[ResultadoCategoriaDisponivel]


class CotacaoRequest(BaseModel):
    pickup_store_id: str
    dropoff_store_id: str
    category_id: str
    pickup_time: datetime
    dropoff_time: datetime
    customer_age: int
    nationality: str | None = None
    promo_code: str | None = None
    rate_plan_id: str | None = None
    selected_addons: list[AddonSelecionado] = []

    @field_validator('dropoff_time')
    @classmethod
    def dropoff_after_pickup(cls, v: datetime, info) -> datetime:
        pickup = info.data.get('pickup_time')
        if pickup and v <= pickup:
            raise ValueError('dropoff_time deve ser posterior a pickup_time.')
        return v


class ProtecaoIncluida(BaseModel):
    id: str
    name: str
    code: str
    daily_rate: float
    deductible_amount: float


class ItemCotacao(BaseModel):
    type: str
    description: str
    amount: float


class CotacaoResponse(BaseModel):
    rate_plan_id: str
    rate_plan_name: str
    daily_rate: float
    total_days: int
    subtotal_base: float
    addons_total: float
    fees_total: float
    one_way_fee: float
    final_total: float
    breakdown: list[ItemCotacao]
    included_protections: list[ProtecaoIncluida]
    available_addons: list[AddonDisponivel]


# ── CRUD: Addon ───────────────────────────────────────────────────────────────

class AddonPricingRequest(BaseModel):
    amount: float
    calculation_type: TipoCalculoAddon
    max_amount_per_trip: float | None = None


class AddonRequest(BaseModel):
    name: str
    description: str = ''
    type: TipoAddon
    pricing: AddonPricingRequest
    stores: list[str] = []
    active: bool = True


class AddonResponse(BaseModel):
    id: str
    name: str
    description: str
    type: str
    active: bool
    stores: list[str]
    pricing: AddonPricingRequest
    created_at: str
    updated_at: str


# ── CRUD: Fee ─────────────────────────────────────────────────────────────────

class FeePricingRequest(BaseModel):
    amount: float
    calculation_type: TipoCalculoFee


class FeeConditionsRequest(BaseModel):
    applies_after_time: str | None = None
    applies_before_time: str | None = None


class FeeRequest(BaseModel):
    name: str
    store_id: str
    pricing: FeePricingRequest
    conditions: FeeConditionsRequest = FeeConditionsRequest()
    active: bool = True
    is_tax: bool = False


class FeeResponse(BaseModel):
    id: str
    name: str
    store: str
    store_name: str | None = None
    store_code: str | None = None
    active: bool
    pricing: FeePricingRequest
    conditions: FeeConditionsRequest
    is_tax: bool = False


# ── CRUD: One-Way ─────────────────────────────────────────────────────────────

class OneWayRequest(BaseModel):
    from_store_id: str
    fee_type: TipoFeeOneWay
    amount: float = 0.0
    active: bool = True


class OneWayResponse(BaseModel):
    id: str
    from_store_id: str
    from_store_name: str
    to_store_id: str
    fee_type: str
    amount: float
    active: bool


# ── CRUD: Rate Plan ───────────────────────────────────────────────────────────

class RatePlanPriceRequest(BaseModel):
    daily_rate: float
    currency: str = 'BRL'
    mileage_policy: str = 'UNLIMITED'
    included_km_per_day: int = 0
    extra_km_price: float = 0.0


class RatePlanConditionsRequest(BaseModel):
    categories: list[str]
    stores: list[str] = []
    min_days: int = 1
    max_days: int | None = None
    min_age: int = 18
    max_age: int | None = None
    advance_booking_days: int = 0
    allow_one_way: bool = True
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    promo_code: str | None = None
    allowed_nationalities: list[str] = []


class RatePlanRequest(BaseModel):
    name: str
    priority: int = 0
    active: bool = True
    price: RatePlanPriceRequest
    conditions: RatePlanConditionsRequest
    included_protections: list[str] = []


class RatePlanResponse(BaseModel):
    id: str
    name: str
    active: bool
    priority: int
    price: RatePlanPriceRequest
    conditions: RatePlanConditionsRequest
    included_protections: list[str]
    created_at: str
    updated_at: str


# ── CRUD: Proteção ────────────────────────────────────────────────────────────

class PricingMatrixItem(BaseModel):
    category: str
    daily_rate: float
    deductible_amount: float


class ProtecaoRequest(BaseModel):
    name: str
    code: str
    pricing_matrix: list[PricingMatrixItem] = []


class ProtecaoResponse(BaseModel):
    id: str
    name: str
    code: str
    pricing_matrix: list[PricingMatrixItem]
