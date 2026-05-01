import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';
import { filialService } from '$lib/services/filial.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [ratePlans, fees, addons, lojas] = await Promise.all([
    tarifaService.listarRatePlans(token).catch(() => []),
    tarifaService.listarFees(token).catch(() => []),
    tarifaService.listarAddons(token).catch(() => []),
    filialService.listarLojas(token).catch(() => []),
  ]);

  return { ratePlans, fees, addons, lojas };
};

export const actions: Actions = {
  // ── Addon ──────────────────────────────────────────────────────────────────
  criarAddon: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const name        = String(data.get('name') ?? '').trim();
    const description = String(data.get('description') ?? '').trim();
    const type        = String(data.get('type') ?? '').trim();
    const amount      = parseFloat(String(data.get('amount') ?? '0'));
    const calc_type   = String(data.get('calc_type') ?? '').trim();
    const max_per_trip_raw = String(data.get('max_per_trip') ?? '').trim();
    const max_per_trip = max_per_trip_raw ? parseFloat(max_per_trip_raw) : null;
    const active      = data.get('active') === 'true';
    const stores      = data.getAll('stores').map(String).filter(Boolean);

    if (!name || !type || !calc_type) {
      return fail(400, { addonErro: 'Preencha nome, tipo e tipo de cálculo.' });
    }

    try {
      await tarifaService.criarAddon({ name, description, type: type as any, pricing: { amount, calculation_type: calc_type as any, max_amount_per_trip: max_per_trip }, stores, active }, token);
      return { addonSucesso: true };
    } catch (e: any) {
      return fail(400, { addonErro: e?.message ?? 'Erro ao criar adicional.' });
    }
  },

  atualizarAddon: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const id          = String(data.get('id') ?? '').trim();
    const name        = String(data.get('name') ?? '').trim();
    const description = String(data.get('description') ?? '').trim();
    const type        = String(data.get('type') ?? '').trim();
    const amount      = parseFloat(String(data.get('amount') ?? '0'));
    const calc_type   = String(data.get('calc_type') ?? '').trim();
    const max_per_trip_raw = String(data.get('max_per_trip') ?? '').trim();
    const max_per_trip = max_per_trip_raw ? parseFloat(max_per_trip_raw) : null;
    const active      = data.get('active') === 'true';
    const stores      = data.getAll('stores').map(String).filter(Boolean);

    if (!id || !name) return fail(400, { addonErro: 'Dados inválidos.' });

    try {
      await tarifaService.atualizarAddon(id, { name, description, type: type as any, pricing: { amount, calculation_type: calc_type as any, max_amount_per_trip: max_per_trip }, stores, active }, token);
      return { addonSucesso: true };
    } catch (e: any) {
      return fail(400, { addonErro: e?.message ?? 'Erro ao atualizar adicional.' });
    }
  },

  desativarAddon: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { addonErro: 'ID inválido.' });
    try {
      await tarifaService.desativarAddon(id, token);
      return { addonSucesso: true };
    } catch (e: any) {
      return fail(400, { addonErro: e?.message ?? 'Erro ao desativar adicional.' });
    }
  },

  // ── Fee ────────────────────────────────────────────────────────────────────
  criarFee: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const name        = String(data.get('name') ?? '').trim();
    const store_id    = String(data.get('store_id') ?? '').trim();
    const amount      = parseFloat(String(data.get('amount') ?? '0'));
    const calc_type   = String(data.get('calc_type') ?? '').trim();
    const after_time  = String(data.get('after_time') ?? '').trim() || null;
    const before_time = String(data.get('before_time') ?? '').trim() || null;
    const active      = data.get('active') === 'true';

    if (!name || !store_id || !calc_type) {
      return fail(400, { feeErro: 'Preencha nome, loja e tipo de cálculo.' });
    }

    try {
      await tarifaService.criarFee({ name, store_id, pricing: { amount, calculation_type: calc_type as any }, conditions: { applies_after_time: after_time, applies_before_time: before_time }, active }, token);
      return { feeSucesso: true };
    } catch (e: any) {
      return fail(400, { feeErro: e?.message ?? 'Erro ao criar taxa.' });
    }
  },

  atualizarFee: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const id          = String(data.get('id') ?? '').trim();
    const name        = String(data.get('name') ?? '').trim();
    const store_id    = String(data.get('store_id') ?? '').trim();
    const amount      = parseFloat(String(data.get('amount') ?? '0'));
    const calc_type   = String(data.get('calc_type') ?? '').trim();
    const after_time  = String(data.get('after_time') ?? '').trim() || null;
    const before_time = String(data.get('before_time') ?? '').trim() || null;
    const active      = data.get('active') === 'true';

    if (!id || !name || !store_id) return fail(400, { feeErro: 'Dados inválidos.' });

    try {
      await tarifaService.atualizarFee(id, { name, store_id, pricing: { amount, calculation_type: calc_type as any }, conditions: { applies_after_time: after_time, applies_before_time: before_time }, active }, token);
      return { feeSucesso: true };
    } catch (e: any) {
      return fail(400, { feeErro: e?.message ?? 'Erro ao atualizar taxa.' });
    }
  },

  desativarFee: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { feeErro: 'ID inválido.' });
    try {
      await tarifaService.desativarFee(id, token);
      return { feeSucesso: true };
    } catch (e: any) {
      return fail(400, { feeErro: e?.message ?? 'Erro ao desativar taxa.' });
    }
  },
};
