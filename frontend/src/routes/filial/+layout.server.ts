import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { setFlash } from '$lib/flash';
import { filialService } from '$lib/services/filial.service';

export const load: LayoutServerLoad = async ({ locals, cookies }) => {
  if (!locals.usuario) {
    setFlash(cookies, { tipo: 'erro', mensagem: 'Usuário não autenticado.' });
    redirect(303, '/login');
  }

  if (locals.usuario.role !== 'filial') {
    setFlash(cookies, { tipo: 'erro', mensagem: 'Você não tem permissão para acessar esta área.' });
    redirect(303, '/login');
  }

  const filial = await filialService.minhaLoja(locals.token!).catch(() => null);

  return { usuario: locals.usuario, filial };
};
