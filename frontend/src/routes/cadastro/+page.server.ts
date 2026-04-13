import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { authService } from '../../lib/services/auth.service';
import { setFlash } from '$lib/flash';

export const actions: Actions = {

  cadastrar: async ({ request, cookies }) => {

    const data = await request.formData();

    // ── coleta os campos ──
    const nomeEmpresa      = String(data.get('nomeEmpresa')      ?? '').trim();
    const cnpj             = String(data.get('cnpj')             ?? '').trim();
    const telefone         = String(data.get('telefone')         ?? '').trim();
    const cidade           = String(data.get('cidade')           ?? '').trim();
    const estado           = String(data.get('estado')           ?? '').trim();
    const nomeResponsavel  = String(data.get('nomeResponsavel')  ?? '').trim();
    const email            = String(data.get('email')            ?? '').trim();
    const senha            = String(data.get('senha')            ?? '');
    const confirmarSenha   = String(data.get('confirmarSenha')   ?? '');

    // ── validação server-side ──
    const erros: Record<string, string> = {};

    if (nomeEmpresa.length < 3)                        erros.nomeEmpresa     = 'Nome da empresa obrigatório';
    if (cnpj.replace(/\D/g, '').length !== 14)         erros.cnpj            = 'CNPJ inválido';
    if (telefone.replace(/\D/g, '').length < 10)       erros.telefone        = 'Telefone inválido';
    if (!cidade)                                        erros.cidade          = 'Cidade obrigatória';
    if (!estado)                                        erros.estado          = 'Selecione um estado';
    if (nomeResponsavel.length < 3)                    erros.nomeResponsavel = 'Nome do responsável obrigatório';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))    erros.email           = 'E-mail inválido';
    if (senha.length < 8)                              erros.senha           = 'Mínimo 8 caracteres';
    if (senha !== confirmarSenha)                      erros.confirmarSenha  = 'As senhas não coincidem';

    if (Object.keys(erros).length > 0) {
      return fail(422, { erros, campos: { nomeEmpresa, cnpj, telefone, cidade, estado, nomeResponsavel, email } });
    }

    // ── chama a service ──
    try {
      await authService.cadastrar({
        nomeEmpresa,
        cnpj,
        telefone,
        cidade,
        estado,
        nomeResponsavel,
        email,
        senha,
      });
    } catch (err: any) {
      return fail(400, {
        erro: err?.message ?? 'Erro ao cadastrar. Tente novamente.',
      });
    }

    // ── redireciona para login após sucesso ──
    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Cadastro realizado com sucesso. Faça login para continuar.' });
    redirect(303, '/login');
  },

};