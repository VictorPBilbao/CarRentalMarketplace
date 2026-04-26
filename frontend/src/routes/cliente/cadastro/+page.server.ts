import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { clienteAuthService } from '$lib/services/cliente.service';
import { setFlash } from '$lib/flash';

export const actions: Actions = {
  cadastrar: async ({ request, cookies }) => {
    const data         = await request.formData();
    const primeiroNome = String(data.get('primeiroNome') ?? '').trim();
    const sobrenome    = String(data.get('sobrenome')    ?? '').trim();
    const email        = String(data.get('email')        ?? '').trim();
    const telefone     = String(data.get('telefone')     ?? '').trim() || null;
    const senha        = String(data.get('senha')        ?? '');
    const confirmarSenha = String(data.get('confirmarSenha') ?? '');

    const erros: Record<string, string> = {};
    if (!primeiroNome)                erros.primeiroNome = 'Informe o primeiro nome.';
    if (!sobrenome)                   erros.sobrenome    = 'Informe o sobrenome.';
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
                                      erros.email        = 'E-mail inválido.';
    if (!senha || senha.length < 6)   erros.senha        = 'Senha deve ter ao menos 6 caracteres.';
    if (senha !== confirmarSenha)      erros.confirmarSenha = 'As senhas não coincidem.';

    const campos = { primeiroNome, sobrenome, email, telefone: telefone ?? '' };
    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    try {
      await clienteAuthService.cadastrar({ primeiroNome, sobrenome, email, telefone, senha });
    } catch (e: any) {
      return fail(400, { erros: {}, erro: e?.message ?? 'Erro ao criar conta.', campos });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Conta criada com sucesso! Faça login para continuar.' });
    redirect(303, '/cliente/login');
  },
};
