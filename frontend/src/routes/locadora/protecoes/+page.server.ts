import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const [protecoes, categorias] = await Promise.all([
    tarifaService.listarProtecoes(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);
  return { protecoes, categorias };
};

export const actions: Actions = {
  criar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const name = String(data.get('name') ?? '').trim();
    const code = String(data.get('code') ?? '').trim();

    const cat_ids = data.getAll('cat_id').map(String).filter(Boolean);
    const cat_rates = data.getAll('cat_rate').map(String);
    const cat_deductibles = data.getAll('cat_deductible').map(String);

    const pricing_matrix = cat_ids.map((category, i) => ({
      category,
      daily_rate: parseFloat(cat_rates[i] ?? '0') || 0,
      deductible_amount: parseFloat(cat_deductibles[i] ?? '0') || 0,
    }));

    if (!name || !code) return fail(400, { erro: 'Nome e código são obrigatórios.' });

    try {
      await tarifaService.criarProtecao({ name, code, pricing_matrix }, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao criar proteção.' });
    }
  },

  atualizar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const id   = String(data.get('id')   ?? '').trim();
    const name = String(data.get('name') ?? '').trim();
    const code = String(data.get('code') ?? '').trim();

    const cat_ids = data.getAll('cat_id').map(String).filter(Boolean);
    const cat_rates = data.getAll('cat_rate').map(String);
    const cat_deductibles = data.getAll('cat_deductible').map(String);

    const pricing_matrix = cat_ids.map((category, i) => ({
      category,
      daily_rate: parseFloat(cat_rates[i] ?? '0') || 0,
      deductible_amount: parseFloat(cat_deductibles[i] ?? '0') || 0,
    }));

    if (!id || !name || !code) return fail(400, { erro: 'Dados inválidos.' });

    try {
      await tarifaService.atualizarProtecao(id, { name, code, pricing_matrix }, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao atualizar proteção.' });
    }
  },

  excluir: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { erro: 'ID inválido.' });
    try {
      await tarifaService.excluirProtecao(id, token);
      return { sucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao excluir proteção.' });
    }
  },
};
