import { api } from './api';

export type TipoTransmissao = 'MANUAL' | 'AUTOMATIC';
export type TipoCombustivel = 'GASOLINE' | 'DIESEL' | 'ELECTRIC' | 'HYBRID' | 'FLEX';

export interface CategoriaFeatures {
  air_conditioning: boolean;
  capacity: {
    passengers:      number;
    small_suitcases: number;
    large_suitcases: number;
  };
  doors:        number;
  fuel_type:    TipoCombustivel;
  transmission: TipoTransmissao;
}

export interface CriarCategoriaDTO {
  code:                  string;
  group_name:            string;
  acriss_code?:          string | null;
  description?:          string | null;
  features:              CategoriaFeatures;
  representative_models: string[];
  image_url?:            string | null;
}

export interface Categoria extends CriarCategoriaDTO {
  id:         string;
  active:     boolean;
  created_at: string;
  updated_at: string;
}

export const categoriaService = {
  async listar(token: string): Promise<Categoria[]> {
    return api.get<Categoria[]>('/locadora/categorias', token);
  },

  async buscarPorId(id: string, token: string): Promise<Categoria> {
    return api.get<Categoria>(`/locadora/categorias/${id}`, token);
  },

  async criar(dados: CriarCategoriaDTO, token: string): Promise<Categoria> {
    return api.post<Categoria>('/locadora/categorias', dados, token);
  },

  async atualizar(id: string, dados: CriarCategoriaDTO, token: string): Promise<Categoria> {
    return api.put<Categoria>(`/locadora/categorias/${id}`, dados, token);
  },
};
