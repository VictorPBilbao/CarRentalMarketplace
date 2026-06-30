import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { setFlash } from '$lib/flash';

export const load: LayoutServerLoad = async ({ locals, cookies }) => {
  if (!locals.usuario) {
    if (!locals.token) {
      setFlash(cookies, { tipo: 'erro', mensagem: 'Usuário não autenticado.' });
    }
    redirect(303, '/login');
  }

  if (locals.usuario.role !== 'locadora') {
    setFlash(cookies, { tipo: 'erro', mensagem: 'Você não tem permissão para acessar esta área.' });
    redirect(303, '/login');
  }

  return { usuario: locals.usuario };
};