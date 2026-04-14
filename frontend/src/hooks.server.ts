import type { Handle } from '@sveltejs/kit';

function decodeJwt(token: string): Record<string, unknown> | null {
  try {
    const payloadBase64 = token.split('.')[1];
    if (!payloadBase64) return null;

    // Base64URL → Base64
    const base64 = payloadBase64.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(Buffer.from(base64, 'base64').toString('utf-8'));
  } catch {
    return null;
  }
}

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('token');

  if (token) {
    const payload = decodeJwt(token);

    if (payload && typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()) {
      event.locals.token = token;
      event.locals.usuario = {
        id:         payload.id         as string,
        nome:       payload.nome       as string,
        email:      payload.email      as string,
        role:       payload.role       as 'admin' | 'locadora' | 'filial',
        locadoraId: payload.locadoraId as string,
        ...(payload.matrizId ? { matrizId: payload.matrizId as string } : {}),
      };
    } else {
      // token ausente, malformado ou expirado — limpa o cookie
      event.cookies.delete('token', { path: '/' });
    }
  }

  return resolve(event);
};