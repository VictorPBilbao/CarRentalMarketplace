from typing import Literal

from pydantic import BaseModel

StatusVeiculo = Literal['AVAILABLE', 'RENTED', 'MAINTENANCE', 'IN_TRANSIT', 'DECOMMISSIONED']


class VeiculoRequest(BaseModel):
    make:           str
    model:          str
    year:           int
    color:          str
    plate:          str
    chassis_number: str
    mileage_km:     int = 0
    status:         StatusVeiculo = 'AVAILABLE'
    category:       str  # record ID: vehicle_category:xxx
    current_store:  str  # record ID: store:xxx — obrigatório para locadora; ignorado para filial (usa token)


class VeiculoResponse(BaseModel):
    id:             str
    make:           str
    model:          str
    year:           int
    color:          str
    plate:          str
    chassis_number: str
    mileage_km:     int
    status:         StatusVeiculo
    category:       str
    current_store:  str
    company:        str
    created_at:     str
    updated_at:     str
