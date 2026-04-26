from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

StatusReserva = Literal['PENDING', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'NO_SHOW']
TipoItemPricing = Literal['BASE_RATE', 'ADDON', 'INSURANCE', 'LOGISTICS_FEE', 'DRIVER_FEE', 'TAX', 'DISCOUNT', 'FEE']


class ItemPricingRequest(BaseModel):
    type: TipoItemPricing
    description: str
    amount: float


class PricingRequest(BaseModel):
    daily_rate: float
    total_days: int
    fees: float = 0.0
    breakdown: list[ItemPricingRequest] = []


class CriarReservaRequest(BaseModel):
    customer_id: str
    category_id: str
    pickup_store_id: str
    dropoff_store_id: str
    pickup_time: datetime
    dropoff_time: datetime
    flight_number: str | None = None
    notes: str | None = None
    pricing: PricingRequest

    @field_validator('dropoff_time')
    @classmethod
    def dropoff_after_pickup(cls, v: datetime, info) -> datetime:
        pickup = info.data.get('pickup_time')
        if pickup and v <= pickup:
            raise ValueError('dropoff_time deve ser posterior a pickup_time.')
        return v


class AtualizarStatusRequest(BaseModel):
    status: StatusReserva


class ItemPricingResponse(BaseModel):
    type: str
    description: str
    amount: float


class PricingResponse(BaseModel):
    daily_rate: float
    total_days: int
    fees: float
    total_amount: float
    breakdown: list[ItemPricingResponse]


class ReservaResponse(BaseModel):
    id: str
    customer: str
    category: str
    pickup_store: str
    dropoff_store: str
    pickup_time: str
    dropoff_time: str
    flight_number: str | None
    notes: str | None
    pricing: PricingResponse
    status: str
    created_at: str
    updated_at: str
