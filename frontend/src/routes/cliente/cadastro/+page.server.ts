import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { clienteAuthService } from '$lib/services/cliente.service';
import { setFlash } from '$lib/flash';

function validarCPF(cpf: string): boolean {
  const nums = cpf.replace(/\D/g, '');
  if (nums.length !== 11 || /^(\d)\1{10}$/.test(nums)) return false;
  let soma = 0;
  for (let i = 0; i < 9; i++) soma += parseInt(nums[i]) * (10 - i);
  let dig1 = (soma * 10) % 11; if (dig1 === 10 || dig1 === 11) dig1 = 0;
  if (dig1 !== parseInt(nums[9])) return false;
  soma = 0;
  for (let i = 0; i < 10; i++) soma += parseInt(nums[i]) * (11 - i);
  let dig2 = (soma * 10) % 11; if (dig2 === 10 || dig2 === 11) dig2 = 0;
  return dig2 === parseInt(nums[10]);
}

function calcularIdade(dataNascimento: string): number {
  const nascimento = new Date(dataNascimento);
  const hoje = new Date();
  let idade = hoje.getFullYear() - nascimento.getFullYear();
  const m = hoje.getMonth() - nascimento.getMonth();
  if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) idade--;
  return idade;
}

export const actions: Actions = {
  cadastrar: async ({ request, cookies }) => {
    const data           = await request.formData();
    const primeiroNome   = String(data.get('primeiroNome')   ?? '').trim();
    const sobrenome      = String(data.get('sobrenome')      ?? '').trim();
    const email          = String(data.get('email')          ?? '').trim();
    const telefone       = String(data.get('telefone')       ?? '').trim() || null;
    const cpf            = String(data.get('cpf')            ?? '').trim();
    const dataNascimento = String(data.get('dataNascimento') ?? '').trim();
    const senha          = String(data.get('senha')          ?? '');
    const confirmarSenha = String(data.get('confirmarSenha') ?? '');

    const erros: Record<string, string> = {};
    if (!primeiroNome)  erros.primeiroNome = 'Informe o primeiro nome.';
    if (!sobrenome)     erros.sobrenome    = 'Informe o sobrenome.';
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
                        erros.email        = 'E-mail inválido.';
    if (!cpf || !validarCPF(cpf))
                        erros.cpf          = 'CPF inválido.';
    if (!dataNascimento)
                        erros.dataNascimento = 'Informe a data de nascimento.';
    else if (calcularIdade(dataNascimento) < 18)
                        erros.dataNascimento = 'É necessário ter pelo menos 18 anos.';
    if (!senha || senha.length < 6)
                        erros.senha        = 'Senha deve ter ao menos 6 caracteres.';
    if (senha !== confirmarSenha)
                        erros.confirmarSenha = 'As senhas não coincidem.';

    const campos = { primeiroNome, sobrenome, email, telefone: telefone ?? '', cpf, dataNascimento };
    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    try {
      await clienteAuthService.cadastrar({ primeiroNome, sobrenome, email, telefone, cpf, dataNascimento, senha });
    } catch (e: any) {
      return fail(400, { erros: {}, erro: e?.message ?? 'Erro ao criar conta.', campos });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Conta criada com sucesso! Faça login para continuar.' });
    redirect(303, '/cliente/login');
  },
};
