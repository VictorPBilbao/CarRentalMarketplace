import { api } from './api';

export type RoleFuncionario = 'MANAGER' | 'CLERK' | 'MECHANIC';

export interface CriarFuncionarioDTO {
  first_name: string;
  last_name:  string;
  email:      string;
  senha:      string;
  role:       RoleFuncionario;
}

export interface Funcionario {
  id:         string;
  first_name: string;
  last_name:  string;
  email:      string;
  role:       string;
  active:     boolean;
  created_at: string;
}

export const funcionarioService = {
  async listar(filialId: string, token: string): Promise<Funcionario[]> {
    return api.get<Funcionario[]>(`/locadora/filiais/${filialId}/funcionarios`, token);
  },

  async criar(filialId: string, dados: CriarFuncionarioDTO, token: string): Promise<Funcionario> {
    return api.post<Funcionario>(`/locadora/filiais/${filialId}/funcionarios`, dados, token);
  },

  async remover(filialId: string, userId: string, token: string): Promise<void> {
    return api.delete<void>(`/locadora/filiais/${filialId}/funcionarios/${userId}`, token);
  },
};
