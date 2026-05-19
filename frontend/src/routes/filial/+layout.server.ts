import { fail, redirect } from '@sveltejs/kit';
import type { Actions, LayoutServerLoad } from './$types';
import { setFlash } from '$lib/flash';
import { filialService } from '$lib/services/filial.service';

const API_URL = import.meta.env.VITE_API_URL;

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

  const filialIds   = locals.usuario.filialIds   ?? [];
  const filialNames = locals.usuario.filialNames ?? [];
  const lojas = filialIds.map((id, i) => ({ id, name: filialNames[i] ?? id }));

  return { usuario: locals.usuario, filial, lojas };
};

export const actions: Actions = {
  trocarFilial: async ({ request, locals, cookies }) => {
    const form    = await request.formData();
    const storeId = String(form.get('store_id') ?? '').trim();

    if (!storeId) return fail(400, { erro: 'Filial não informada.' });

    const res = await fetch(`${API_URL}/auth/troca-filial`, {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization:  `Bearer ${locals.token}`,
      },
      body: JSON.stringify({ store_id: storeId }),
    });

    if (!res.ok) {
      setFlash(cookies, { tipo: 'erro', mensagem: 'Não foi possível trocar de filial.' });
      return fail(res.status, { erro: 'Troca de filial falhou.' });
    }

    const { token } = await res.json();
    cookies.set('token', token, {
      path:     '/',
      httpOnly: true,
      sameSite: 'lax',
      secure:   process.env.NODE_ENV === 'production',
      maxAge:   60 * 60 * 24 * 7,
    });

    redirect(303, '/filial/dashboard');
  },
};
