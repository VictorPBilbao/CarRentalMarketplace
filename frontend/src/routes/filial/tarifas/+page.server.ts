import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [ratePlans, protecoes, categorias] = await Promise.all([
    tarifaService.listarRatePlansFilial(token).catch(() => []),
    tarifaService.listarProtecoes(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);

  return { ratePlans, protecoes, categorias };
};

export const actions: Actions = {
  criarRatePlan: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const name                 = String(data.get('name')                 ?? '').trim();
    const priority             = parseInt(String(data.get('priority')    ?? '0'));
    const active               = data.get('active') !== 'false';
    const daily_rate           = parseFloat(String(data.get('daily_rate')           ?? '0'));
    const currency             = String(data.get('currency')             ?? 'BRL').trim();
    const mileage_policy       = String(data.get('mileage_policy')       ?? 'UNLIMITED').trim();
    const included_km_per_day  = parseInt(String(data.get('included_km_per_day')   ?? '0'));
    const extra_km_price       = parseFloat(String(data.get('extra_km_price')       ?? '0'));
    const min_days             = parseInt(String(data.get('min_days')    ?? '1'));
    const max_days_raw         = String(data.get('max_days')             ?? '').trim();
    const max_days             = max_days_raw ? parseInt(max_days_raw)   : null;
    const min_age              = parseInt(String(data.get('min_age')     ?? '18'));
    const max_age_raw          = String(data.get('max_age')              ?? '').trim();
    const max_age              = max_age_raw ? parseInt(max_age_raw)     : null;
    const advance_booking_days = parseInt(String(data.get('advance_booking_days')  ?? '0'));
    const allow_one_way        = data.get('allow_one_way') === 'true';
    const valid_from_raw       = String(data.get('valid_from')           ?? '').trim();
    const valid_to_raw         = String(data.get('valid_to')             ?? '').trim();
    const valid_from           = valid_from_raw || null;
    const valid_to             = valid_to_raw   || null;
    const promo_code_raw       = String(data.get('promo_code')           ?? '').trim();
    const promo_code           = promo_code_raw || null;
    const nationalities_raw    = String(data.get('allowed_nationalities') ?? '').trim();
    const allowed_nationalities = nationalities_raw
      ? nationalities_raw.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean)
      : [];
    const categories           = data.getAll('categories').map(String).filter(Boolean);
    const included_protections = data.getAll('included_protections').map(String).filter(Boolean);

    if (!name) return fail(400, { ratePlanErro: 'Informe o nome do plano.' });
    if (categories.length === 0) return fail(400, { ratePlanErro: 'Selecione ao menos uma categoria.' });

    try {
      await tarifaService.criarRatePlanFilial({
        name, priority, active,
        price: { daily_rate, currency, mileage_policy, included_km_per_day, extra_km_price },
        conditions: { categories, stores: [], min_days, max_days, min_age, max_age, advance_booking_days, allow_one_way, valid_from, valid_to, promo_code, allowed_nationalities },
        included_protections,
      }, token);
      return { ratePlanSucesso: true };
    } catch (e: any) {
      return fail(400, { ratePlanErro: e?.message ?? 'Erro ao criar plano tarifário.' });
    }
  },

  atualizarRatePlan: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const id                   = String(data.get('id')                   ?? '').trim();
    const name                 = String(data.get('name')                 ?? '').trim();
    const priority             = parseInt(String(data.get('priority')    ?? '0'));
    const active               = data.get('active') !== 'false';
    const daily_rate           = parseFloat(String(data.get('daily_rate')           ?? '0'));
    const currency             = String(data.get('currency')             ?? 'BRL').trim();
    const mileage_policy       = String(data.get('mileage_policy')       ?? 'UNLIMITED').trim();
    const included_km_per_day  = parseInt(String(data.get('included_km_per_day')   ?? '0'));
    const extra_km_price       = parseFloat(String(data.get('extra_km_price')       ?? '0'));
    const min_days             = parseInt(String(data.get('min_days')    ?? '1'));
    const max_days_raw         = String(data.get('max_days')             ?? '').trim();
    const max_days             = max_days_raw ? parseInt(max_days_raw)   : null;
    const min_age              = parseInt(String(data.get('min_age')     ?? '18'));
    const max_age_raw          = String(data.get('max_age')              ?? '').trim();
    const max_age              = max_age_raw ? parseInt(max_age_raw)     : null;
    const advance_booking_days = parseInt(String(data.get('advance_booking_days')  ?? '0'));
    const allow_one_way        = data.get('allow_one_way') === 'true';
    const valid_from_raw       = String(data.get('valid_from')           ?? '').trim();
    const valid_to_raw         = String(data.get('valid_to')             ?? '').trim();
    const valid_from           = valid_from_raw || null;
    const valid_to             = valid_to_raw   || null;
    const promo_code_raw       = String(data.get('promo_code')           ?? '').trim();
    const promo_code           = promo_code_raw || null;
    const nationalities_raw    = String(data.get('allowed_nationalities') ?? '').trim();
    const allowed_nationalities = nationalities_raw
      ? nationalities_raw.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean)
      : [];
    const categories           = data.getAll('categories').map(String).filter(Boolean);
    const included_protections = data.getAll('included_protections').map(String).filter(Boolean);

    if (!id || !name) return fail(400, { ratePlanErro: 'Dados inválidos.' });
    if (categories.length === 0) return fail(400, { ratePlanErro: 'Selecione ao menos uma categoria.' });

    try {
      await tarifaService.atualizarRatePlanFilial(id, {
        name, priority, active,
        price: { daily_rate, currency, mileage_policy, included_km_per_day, extra_km_price },
        conditions: { categories, stores: [], min_days, max_days, min_age, max_age, advance_booking_days, allow_one_way, valid_from, valid_to, promo_code, allowed_nationalities },
        included_protections,
      }, token);
      return { ratePlanSucesso: true };
    } catch (e: any) {
      return fail(400, { ratePlanErro: e?.message ?? 'Erro ao atualizar plano tarifário.' });
    }
  },

  desativarRatePlan: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();
    const id    = String(data.get('id') ?? '').trim();
    if (!id) return fail(400, { ratePlanErro: 'ID inválido.' });
    try {
      await tarifaService.desativarRatePlanFilial(id, token);
      return { ratePlanSucesso: true };
    } catch (e: any) {
      return fail(400, { ratePlanErro: e?.message ?? 'Erro ao desativar plano tarifário.' });
    }
  },
};
