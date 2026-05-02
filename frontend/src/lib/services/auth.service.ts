import { api } from './api';

// ── tipos ──
export interface LoginPayload {
  email:    string;
  senha:    string;
  store_id?: string | null;
}

export interface StoreOption {
  id:   string;
  name: string;
}

export interface CadastroPayload {
  nomeEmpresa:     string;
  cnpj:            string;
  telefone:        string;
  cidade:          string;
  estado:          string;
  nomeResponsavel: string;
  email:           string;
  senha:           string;
}

export interface LoginResponse {
  token:  string | null;
  stores: StoreOption[] | null;
}

export interface CadastroResponse {
  locadoraId: string;
  mensagem:   string;
}

// ── service ──
export const authService = {

  async login(payload: LoginPayload): Promise<LoginResponse> {
    return api.post<LoginResponse>('/auth/login', payload);
  },

  async cadastrar(payload: CadastroPayload): Promise<CadastroResponse> {
    return api.post<CadastroResponse>('/auth/cadastro', payload);
  },

  async logout(token: string): Promise<void> {
    await api.post('/auth/logout', {}, token);
  },
};