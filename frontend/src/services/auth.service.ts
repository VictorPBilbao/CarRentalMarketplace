import { api } from './api';

export interface LoginPayload {
  email: string;
  senha: string;
}

export interface LoginResponse {
  token: string;
  usuario: {
    id: string;
    nome: string;
    email: string;
    locadoraId: string;
  };
}

export const authService = {

  async login(payload: LoginPayload): Promise<LoginResponse> {
    const data = await api.post<LoginResponse>('/auth/login', payload);

    // salva o token para as próximas requisições
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('token', data.token);
    }

    return data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout', {});
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('token');
    }
  },

  getToken(): string | null {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem('token');
  },

  isAutenticado(): boolean {
    return !!this.getToken();
  },

};