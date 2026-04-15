import type { Handle } from '@sveltejs/kit';
import { decodeJwt } from '$lib/server/jwtDecoder.server';

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