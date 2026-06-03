import { api } from './api';

export interface StatusCount {
  status: string;
  qty: number;
}

export interface OtaKeyEmpresa {
  empresa: string;
  total: number;
}

export interface AdminDashboardStats {
  empresas: { total: number };
  lojas: { total: number; ativas: number };
  veiculos: { total: number; por_status: StatusCount[] };
  reservas: { total: number; por_status: StatusCount[] };
  ota_keys: { total: number; ativas: number; por_empresa: OtaKeyEmpresa[] };
}

export interface OtaKeyListItem {
  id: string;
  name: string;
  key_preview: string;
  company_id: string | null;
  company_name: string;
  active: boolean;
  created_at: string;
}

export interface OtaKeyResponse {
  id: string;
  name: string;
  key: string;
  company_id: string | null;
  company_name: string;
  active: boolean;
  created_at: string;
}

export interface OtaKeyRequest {
  name: string;
  company_id?: string | null;
}

export const adminService = {
  getDashboard: (token: string) =>
    api.get<AdminDashboardStats>('/admin/dashboard', token),

  listarChavesOta: (token: string) =>
    api.get<OtaKeyListItem[]>('/admin/ota-keys', token),

  criarChaveOta: (payload: OtaKeyRequest, token: string) =>
    api.post<OtaKeyResponse>('/admin/ota-keys', payload, token),

  revogarChaveOta: (id: string, token: string) =>
    api.delete<void>(`/admin/ota-keys/${encodeURIComponent(id)}`, token),
};
