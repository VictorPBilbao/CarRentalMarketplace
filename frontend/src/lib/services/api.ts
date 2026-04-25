const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8080/api/v1';

async function request<T>(method: string, path: string, body?: unknown, overrideToken?: string): Promise<T> {
  const token = overrideToken ?? (typeof localStorage !== 'undefined'
    ? localStorage.getItem('token')
    : null);

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const erro = await res.json().catch(() => ({}));
    
    // APIs como o FastAPI geralmente retornam os erros na propriedade "detail"
    let mensagemErro = erro?.mensagem || erro?.error;
    if (!mensagemErro && erro?.detail) {
      // Se for validação do FastAPI, o detail vem como um Array
      mensagemErro = typeof erro.detail === 'string' ? erro.detail : JSON.stringify(erro.detail);
    }
    
    throw new Error(mensagemErro || `Erro de conexão com o servidor (Status HTTP: ${res.status})`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  get:    <T>(path: string, token?: string)                  => request<T>('GET',    path, undefined, token),
  post:   <T>(path: string, body: unknown, token?: string)   => request<T>('POST',   path, body,      token),
  put:    <T>(path: string, body: unknown, token?: string)   => request<T>('PUT',    path, body,      token),
  patch:  <T>(path: string, body: unknown, token?: string)   => request<T>('PATCH',  path, body,      token),
  delete: <T>(path: string, token?: string)                  => request<T>('DELETE', path, undefined, token),
};