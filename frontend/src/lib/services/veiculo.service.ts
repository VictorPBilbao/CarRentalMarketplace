import { api } from './api';

export type StatusVeiculo = 'AVAILABLE' | 'RENTED' | 'MAINTENANCE' | 'IN_TRANSIT' | 'DECOMMISSIONED';

export interface CriarVeiculoDTO {
  make:           string;
  model:          string;
  year:           number;
  color:          string;
  plate:          string;
  chassis_number: string;
  mileage_km:     number;
  status:         StatusVeiculo;
  category:       string;
  current_store:  string;
}

export interface Veiculo extends CriarVeiculoDTO {
  id:         string;
  company:    string;
  created_at: string;
  updated_at: string;
}

export const filialVeiculoService = {
  async listar(token: string): Promise<Veiculo[]> {
    return api.get<Veiculo[]>('/filial/veiculos', token);
  },

  async buscarPorId(id: string, token: string): Promise<Veiculo> {
    return api.get<Veiculo>(`/filial/veiculos/${id}`, token);
  },

  async criar(dados: CriarVeiculoDTO, token: string): Promise<Veiculo> {
    return api.post<Veiculo>('/filial/veiculos', dados, token);
  },

  async atualizar(id: string, dados: Partial<CriarVeiculoDTO>, token: string): Promise<Veiculo> {
    return api.put<Veiculo>(`/filial/veiculos/${id}`, dados, token);
  },
};

export const veiculoService = {
  async listar(token: string): Promise<Veiculo[]> {
    return api.get<Veiculo[]>('/locadora/veiculos', token);
  },

  async buscarPorId(id: string, token: string): Promise<Veiculo> {
    return api.get<Veiculo>(`/locadora/veiculos/${id}`, token);
  },

  async criar(dados: CriarVeiculoDTO, token: string): Promise<Veiculo> {
    return api.post<Veiculo>('/locadora/veiculos', dados, token);
  },

  async atualizar(id: string, dados: Partial<CriarVeiculoDTO>, token: string): Promise<Veiculo> {
    return api.put<Veiculo>(`/locadora/veiculos/${id}`, dados, token);
  },
};
