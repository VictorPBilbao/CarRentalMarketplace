import { api } from './api';

// ── tipos ──
export interface LoginPayload {
  email: string;
  senha: string;
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
  token: string;
  usuario: {
    id:         string;
    nome:       string;
    email:      string;
    role:       'admin' | 'locadora' | 'filial';
    locadoraId: string;
  };
}

export interface CadastroResponse {
  locadoraId: string;
  mensagem:   string;
}

// ── service ──
export const authService = {

  async login(payload: LoginPayload): Promise<LoginResponse> {
    const data = await api.post<LoginResponse>('/auth/login', payload);
    return data;
  },

  async cadastrar(payload: CadastroPayload): Promise<CadastroResponse> {
    return api.post<CadastroResponse>('/auth/cadastro', payload);
  },

  async logout(token: string): Promise<void> {
    await api.post('/auth/logout', {}, token);
  },
};