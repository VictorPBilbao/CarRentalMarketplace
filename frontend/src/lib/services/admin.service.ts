import { api } from './api';

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
  listarChavesOta: (token: string) =>
    api.get<OtaKeyListItem[]>('/admin/ota-keys', token),

  criarChaveOta: (payload: OtaKeyRequest, token: string) =>
    api.post<OtaKeyResponse>('/admin/ota-keys', payload, token),

  revogarChaveOta: (id: string, token: string) =>
    api.delete<void>(`/admin/ota-keys/${encodeURIComponent(id)}`, token),
};
