import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { authService } from '$lib/services/auth.service';
import { decodeJwt } from '$lib/server/jwtDecoder.server';

export const actions: Actions = {

  sair: async ({ cookies }) => {
    const token = cookies.get('token');
    if (token) {
      try {
        await authService.logout(token);
      } catch {
        // mesmo se o backend falhar, limpa o cookie
      }
    }
    cookies.delete('token', { path: '/' });
    throw redirect(303, '/login');
  },

  entrar: async ({ request, cookies }) => {

    const data = await request.formData();

    const email = String(data.get('email') ?? '').trim();
    const senha = String(data.get('senha') ?? '');

    // ── validação server-side ──
    const erros: Record<string, string> = {};

    if (!email)                                       erros.email = 'E-mail obrigatório';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) erros.email = 'E-mail inválido';
    if (!senha)                                       erros.senha = 'Senha obrigatória';
    else if (senha.length < 6)                        erros.senha = 'Mínimo 6 caracteres';

    if (Object.keys(erros).length > 0) {
      return fail(422, { erros, email });
    }

    let resposta;
    // ── chama a service ──
    try {
      resposta = await authService.login({ email, senha });
    } catch (err: any) {
      return fail(401, {
        erro: err?.message ?? 'E-mail ou senha incorretos.',
        email
      });
    }

    // salva o token em cookie httpOnly (mais seguro que localStorage)
    cookies.set('token', resposta.token, {
      path: '/',
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24 * 7, // 7 dias
    });

    const destinoPorRole: Record<string, string> = {
      locadora: '/locadora/dashboard',
      admin: '/admin/dashboard',
      filial: '/filial/dashboard',
    };

    const role = decodeJwt(resposta.token)?.role as string;
    const destino = destinoPorRole[role] ?? '/';
    throw redirect(303, destino);
  },
};