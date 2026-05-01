import { api } from './api';

// ── tipos ──
export type TipoLocalizacao = 'AIRPORT' | 'TRAIN_STATION' | 'CITY_CENTER' | 'HOTEL' | 'PORT' | 'MALL' | 'OTHER';
export type MetodoRetirada  = 'IN_TERMINAL' | 'SHUTTLE' | 'MEET_AND_GREET' | 'WALK' | 'DELIVERY';
export type DiaSemana       = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY' | 'SUNDAY' | 'HOLIDAY';

export interface HorarioFuncionamento {
  day_of_week: DiaSemana;
  open:        string | null;
  close:       string | null;
  is_closed:   boolean;
}

export interface CriarFilialDTO {
  name:            string;
  code:            string;
  location_type:   TipoLocalizacao;
  pickup_method:   MetodoRetirada;
  address: {
    street:        string;
    number:        string;
    complement:    string | null;
    neighborhood:  string;
    city:          string;
    state:         string;
    postal_code:   string;
    country:       string;
  };
  contact: {
    phone:         string;
    email:         string;
    manager_name:  string | null;
  };
  location: {
    latitude:      number;
    longitude:     number;
  };
  instructions: {
    pickup:        string | null;
    dropoff:       string | null;
    extra:         string | null;
  };
  operating_hours: HorarioFuncionamento[];
  amenities:       string[];
}

export interface Filial extends CriarFilialDTO {
  id:         string;
  active:     boolean;
  created_at: string;
  updated_at: string;
}

// ── service ──
export const filialService = {
  async minhaLoja(token: string): Promise<Filial> {
    return api.get<Filial>('/filial/minha-loja', token);
  },


  async criar(dados: CriarFilialDTO, token: string): Promise<Filial> {
    return api.post<Filial>('/locadora/filiais', dados, token);
  },

  async listar(token: string): Promise<Filial[]> {
    return api.get<Filial[]>('/locadora/filiais', token);
  },

  async listarLojas(token: string): Promise<Filial[]> {
    return api.get<Filial[]>('/locadora/lojas', token);
  },

  async buscarPorId(id: string, token: string): Promise<Filial> {
    return api.get<Filial>(`/locadora/filiais/${id}`, token);
  },

  async atualizar(id: string, dados: Partial<CriarFilialDTO>, token: string): Promise<Filial> {
    return api.put<Filial>(`/locadora/filiais/${id}`, dados, token);
  },
};
