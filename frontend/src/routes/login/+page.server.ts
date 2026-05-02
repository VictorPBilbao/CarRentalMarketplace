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

    const email   = String(data.get('email')   ?? '').trim();
    const senha   = String(data.get('senha')   ?? '');
    const storeId = String(data.get('storeId') ?? '').trim() || null;

    // ── validação server-side (skip quando é re-submit de seleção de filial) ──
    if (!storeId) {
      const erros: Record<string, string> = {};
      if (!email)                                          erros.email = 'E-mail obrigatório';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) erros.email = 'E-mail inválido';
      if (!senha)                                          erros.senha = 'Senha obrigatória';
      else if (senha.length < 6)                           erros.senha = 'Mínimo 6 caracteres';
      if (Object.keys(erros).length > 0) return fail(422, { erros, email });
    }

    let resposta;
    try {
      resposta = await authService.login({ email, senha, store_id: storeId });
    } catch (err: any) {
      return fail(401, { erro: err?.message ?? 'E-mail ou senha incorretos.', email });
    }

    // ── funcionário com múltiplas filiais → pede seleção ──────────────────────
    if (resposta.stores && !resposta.token) {
      return { stores: resposta.stores, email, senha };
    }

    if (!resposta.token) {
      return fail(500, { erro: 'Resposta inesperada do servidor.', email });
    }

    cookies.set('token', resposta.token, {
      path: '/',
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24 * 7,
    });

    const destinoPorRole: Record<string, string> = {
      locadora: '/locadora/dashboard',
      admin:    '/admin/dashboard',
      filial:   '/filial/dashboard',
      customer: '/cliente/dashboard',
    };

    const role = decodeJwt(resposta.token)?.role as string;
    throw redirect(303, destinoPorRole[role] ?? '/');
  },
};