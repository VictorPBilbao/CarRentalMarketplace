import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { authService } from '$lib/services/auth.service';
import { decodeJwt } from '$lib/server/jwtDecoder.server';

export const actions: Actions = {
  entrar: async ({ request, cookies, url }) => {
    const data  = await request.formData();
    const email = String(data.get('email') ?? '').trim();
    const senha = String(data.get('senha') ?? '');

    const erros: Record<string, string> = {};
    if (!email)                                       erros.email = 'E-mail obrigatório.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) erros.email = 'E-mail inválido.';
    if (!senha)                                       erros.senha = 'Senha obrigatória.';

    if (Object.keys(erros).length > 0) return fail(422, { erros, email });

    let resposta;
    try {
      resposta = await authService.login({ email, senha });
    } catch (err: any) {
      return fail(401, { erro: err?.message ?? 'E-mail ou senha incorretos.', email });
    }

    const role = decodeJwt(resposta.token)?.role as string;
    if (role !== 'customer') {
      return fail(403, { erro: 'Esta conta não é de cliente. Use o login da área administrativa.', email });
    }

    cookies.set('token', resposta.token, {
      path: '/',
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24 * 7,
    });

    const redir = url.searchParams.get('redir') ?? '/cliente/dashboard';
    redirect(303, redir);
  },
};
