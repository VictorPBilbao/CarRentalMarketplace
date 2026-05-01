import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';
import { filialService } from '$lib/services/filial.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [rules, lojas] = await Promise.all([
    tarifaService.listarOneWay(token).catch(() => []),
    filialService.listarLojas(token).catch(() => []),
  ]);

  return { rules, lojas };
};

export const actions: Actions = {
  criar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const from_store_id = String(data.get('from_store_id') ?? '').trim();
    const fee_type      = String(data.get('fee_type') ?? 'FREE').trim();
    const amount        = parseFloat(String(data.get('amount') ?? '0'));
    const active        = data.get('active') !== 'false';

    if (!from_store_id) return fail(400, { erro: 'Selecione a loja de origem.' });

    try {
      await tarifaService.criarOneWay({ from_store_id, fee_type: fee_type as any, amount, active }, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao criar regra.' });
    }
  },

  atualizar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const id            = String(data.get('id') ?? '').trim();
    const from_store_id = String(data.get('from_store_id') ?? '').trim();
    const fee_type      = String(data.get('fee_type') ?? 'FREE').trim();
    const amount        = parseFloat(String(data.get('amount') ?? '0'));
    const active        = data.get('active') !== 'false';

    if (!id || !from_store_id) return fail(400, { erro: 'Dados inválidos.' });

    try {
      await tarifaService.atualizarOneWay(id, { from_store_id, fee_type: fee_type as any, amount, active }, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao atualizar regra.' });
    }
  },

  excluir: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { erro: 'ID inválido.' });
    try {
      await tarifaService.excluirOneWay(id, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao excluir regra.' });
    }
  },
};
