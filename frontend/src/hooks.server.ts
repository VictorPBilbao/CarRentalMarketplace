import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('token');

  if (token) {
    try {
      // TODO: trocar pela validação real do seu backend
      const resposta = await fetch(`${process.env.API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (resposta.ok) {
        event.locals.token = token;
        event.locals.usuario = await resposta.json();
      } else {
        // token inválido ou expirado — limpa o cookie
        event.cookies.delete('token', { path: '/' });
      }
    } catch {
      event.cookies.delete('token', { path: '/' });
    }
  }

  return resolve(event);
};