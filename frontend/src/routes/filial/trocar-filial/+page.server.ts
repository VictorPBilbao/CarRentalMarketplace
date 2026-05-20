import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { setFlash } from '$lib/flash';

const API_URL = import.meta.env.VITE_API_URL;

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
