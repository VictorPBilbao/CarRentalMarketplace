import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const PUBLIC_PATHS = ['/cliente/login', '/cliente/cadastro'];

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (PUBLIC_PATHS.some(p => url.pathname.startsWith(p))) {
    return { usuario: locals.usuario ?? null };
  }

  if (!locals.usuario) {
    redirect(303, `/cliente/login?redir=${encodeURIComponent(url.pathname)}`);
  }

  if (locals.usuario.role !== 'customer') {
    redirect(303, '/login');
  }

  return { usuario: locals.usuario };
};
