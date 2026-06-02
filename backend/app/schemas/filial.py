from typing import Literal

from pydantic import BaseModel

TipoLocalizacao = Literal['AIRPORT', 'TRAIN_STATION', 'CITY_CENTER', 'HOTEL', 'PORT', 'MALL', 'OTHER']
MetodoRetirada  = Literal['IN_TERMINAL', 'SHUTTLE', 'MEET_AND_GREET', 'WALK', 'DELIVERY']
DiaSemana       = Literal['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', 'HOLIDAY']


class Endereco(BaseModel):
    street:       str
    number:       str
    complement:   str | None = None
    neighborhood: str
    city:         str
    state:        str
    postal_code:  str
    country:      str = 'BR'


class Contato(BaseModel):
    phone:        str
    email:        str
    manager_name: str | None = None


class Localizacao(BaseModel):
    latitude:  float
    longitude: float


class Instrucoes(BaseModel):
    pickup:  str | None = None
    dropoff: str | None = None
    extra:   str | None = None


class HorarioFuncionamento(BaseModel):
    day_of_week: DiaSemana
    open:        str | None = None
    close:       str | None = None
    is_closed:   bool = False


class CidadeStore(BaseModel):
    id:            str
    name:          str
    code:          str
    location_type: str
    company_id:    str
    company_name:  str = ''


class CidadeResponse(BaseModel):
    city:   str
    state:  str
    stores: list[CidadeStore]


class FilialRequest(BaseModel):
    """Payload para criar ou substituir completamente uma filial (POST / PUT)."""
    name:            str
    code:            str
    location_type:   TipoLocalizacao
    pickup_method:   MetodoRetirada
    address:         Endereco
    contact:         Contato
    location:        Localizacao
    instructions:    Instrucoes = Instrucoes()
    operating_hours: list[HorarioFuncionamento] = []
    amenities:       list[str] = []


class FilialResponse(BaseModel):
    id:              str
    name:            str
    code:            str
    location_type:   str
    pickup_method:   str
    address:         Endereco
    contact:         Contato
    location:        Localizacao
    instructions:    Instrucoes
    operating_hours: list[HorarioFuncionamento]
    amenities:       list[str]
    active:          bool
    created_at:      str
    updated_at:      str
