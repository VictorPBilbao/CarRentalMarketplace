import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { adminService } from '$lib/services/admin.service';
import { publicoService } from '$lib/services/publico.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const [chaves, cidades] = await Promise.all([
    adminService.listarChavesOta(token).catch(() => []),
    publicoService.listarCidades().catch(() => []),
  ]);
  // Extrai empresas únicas das cidades (para o select de locadora)
  const empresasMap = new Map<string, string>();
  for (const cidade of cidades) {
    for (const loja of cidade.stores) {
      if (loja.company_id && loja.company_name && !empresasMap.has(loja.company_id)) {
        empresasMap.set(loja.company_id, loja.company_name);
      }
    }
  }
  const empresas = [...empresasMap.entries()].map(([id, nome]) => ({ id, nome }));
  return { chaves, empresas };
};

export const actions: Actions = {
  criar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const name       = String(data.get('name')       ?? '').trim();
    const company_id = String(data.get('company_id') ?? '').trim() || null;

    if (!name) return fail(400, { erro: 'Informe o nome do parceiro.' });

    try {
      const nova = await adminService.criarChaveOta({ name, company_id }, token);
      return { chaveGerada: nova.key, chaveName: nova.name };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao criar chave.' });
    }
  },

  revogar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { erro: 'ID inválido.' });
    try {
      await adminService.revogarChaveOta(id, token);
      return { revogadoSucesso: true };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao revogar chave.' });
    }
  },
};
