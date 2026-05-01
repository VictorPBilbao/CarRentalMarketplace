from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

TipoCalculoAddon = Literal['PER_DAY', 'PER_TRIP', 'PERCENTAGE']
TipoCalculoFee = Literal['PERCENTAGE', 'FLAT_FEE']
TipoFeeOneWay = Literal['FREE', 'FIXED', 'PER_KM']


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


class TaxaOneWay(BaseModel):
    pickup_store: str
    dropoff_store: str
    fee_type: TipoFeeOneWay
    amount: float


class BuscarTarifasResponse(BaseModel):
    total_days: int
    is_one_way: bool
    rate_plans: list[RatePlanDisponivel]
    available_addons: list[AddonDisponivel]
    store_fees: list[FeeCalculado]
    one_way_fee: TaxaOneWay | None


class CotacaoRequest(BaseModel):
    pickup_store_id: str
    dropoff_store_id: str
    category_id: str
    pickup_time: datetime
    dropoff_time: datetime
    customer_age: int
    promo_code: str | None = None
    rate_plan_id: str | None = None  # None = usar o mais barato aplicável
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
