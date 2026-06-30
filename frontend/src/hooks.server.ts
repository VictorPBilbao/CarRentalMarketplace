import type { Handle } from '@sveltejs/kit';

const API_URL = import.meta.env.VITE_API_URL;

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('token');

  if (token) {
    event.locals.token = token;

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const usuario = await response.json();
        event.locals.usuario = {
          id:         usuario.id,
          nome:       usuario.nome,
          email:      usuario.email,
          role:       usuario.role,
          locadoraId: usuario.locadoraId,
          ...(usuario.locadoraNome ? { locadoraNome: usuario.locadoraNome } : {}),
          ...(usuario.matrizId    ? { matrizId:    usuario.matrizId    } : {}),
          ...(usuario.filialIds   ? { filialIds:   usuario.filialIds   } : {}),
          ...(usuario.filialNames ? { filialNames: usuario.filialNames } : {}),
        };
      } else {
        event.cookies.delete('token', { path: '/' });
        event.locals.token = undefined;
      }
    } catch {
      // API offline — mantém o cookie para tentar na próxima requisição
    }
  }

  return resolve(event);
};
