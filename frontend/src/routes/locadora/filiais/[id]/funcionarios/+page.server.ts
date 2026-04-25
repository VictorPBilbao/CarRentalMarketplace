import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { filialService } from '$lib/services/filial.service';
import { funcionarioService } from '$lib/services/funcionario.service';
import type { RoleFuncionario } from '$lib/services/funcionario.service';

export const load: PageServerLoad = async ({ params, locals }) => {
  const filialId = decodeURIComponent(params.id);

  try {
    const [filial, funcionarios] = await Promise.all([
      filialService.buscarPorId(filialId, locals.token!),
      funcionarioService.listar(filialId, locals.token!),
    ]);
    return { filial, funcionarios, erro: null };
  } catch (e: any) {
    return { filial: null, funcionarios: [], erro: e?.message ?? 'Erro ao carregar dados.' };
  }
};

export const actions: Actions = {

  criar: async ({ request, params, locals }) => {
    const filialId = decodeURIComponent(params.id);
    const data = await request.formData();

    const firstName = String(data.get('firstName') ?? '').trim();
    const lastName  = String(data.get('lastName')  ?? '').trim();
    const email     = String(data.get('email')     ?? '').trim();
    const senha     = String(data.get('senha')     ?? '');
    const role      = String(data.get('role')      ?? 'CLERK') as RoleFuncionario;

    const erros: Record<string, string> = {};
    if (firstName.length < 2)                          erros.firstName = 'Nome deve ter ao menos 2 caracteres.';
    if (lastName.length < 2)                           erros.lastName  = 'Sobrenome deve ter ao menos 2 caracteres.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))    erros.email     = 'E-mail inválido.';
    if (senha.length < 6)                              erros.senha     = 'Senha deve ter ao menos 6 caracteres.';

    if (Object.keys(erros).length > 0) {
      return fail(422, { erros, campos: { firstName, lastName, email, role } });
    }

    try {
      await funcionarioService.criar(
        filialId,
        { first_name: firstName, last_name: lastName, email, senha, role },
        locals.token!,
      );
      return { sucesso: true };
    } catch (e: any) {
      return fail(422, { erros: {}, erro: e?.message ?? 'Erro ao cadastrar funcionário.' });
    }
  },

  remover: async ({ request, params, locals }) => {
    const filialId = decodeURIComponent(params.id);
    const data = await request.formData();
    const userId = String(data.get('userId') ?? '');

    try {
      await funcionarioService.remover(filialId, userId, locals.token!);
      return { removido: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao remover funcionário.' });
    }
  },

};
