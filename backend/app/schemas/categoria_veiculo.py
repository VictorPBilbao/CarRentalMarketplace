from typing import Literal

from pydantic import BaseModel

TipoCombustivel = Literal['GASOLINE', 'DIESEL', 'ELECTRIC', 'HYBRID', 'FLEX']
TipoTransmissao = Literal['MANUAL', 'AUTOMATIC']


class Capacidade(BaseModel):
    passengers:      int
    small_suitcases: int = 0
    large_suitcases: int = 0


class Features(BaseModel):
    air_conditioning: bool = True
    capacity:         Capacidade
    doors:            int
    fuel_type:        TipoCombustivel
    transmission:     TipoTransmissao


class CategoriaVeiculoRequest(BaseModel):
    code:                  str
    group_name:            str
    acriss_code:           str | None = None
    description:           str | None = None
    features:              Features
    representative_models: list[str] = []
    image_url:             str | None = None


class CategoriaVeiculoResponse(BaseModel):
    id:                    str
    code:                  str
    group_name:            str
    acriss_code:           str | None
    description:           str | None
    features:              Features
    representative_models: list[str]
    image_url:             str | None
    active:                bool
    created_at:            str
    updated_at:            str
