import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';
import { categoriaService } from '$lib/services/categoria.service';
import { filialService } from '$lib/services/filial.service';

export const load: PageServerLoad = async ({ locals, url }) => {
  const token = locals.token!;

  const [categorias, todasLojas] = await Promise.all([
    categoriaService.listar(token).catch(() => []),
    filialService.listar(token).catch(() => []),
  ]);

  const dropoffStoreId = url.searchParams.get('dropoff_store') ?? '';
  const categoryId     = url.searchParams.get('category') ?? '';
  const pickupTime     = url.searchParams.get('pickup_time') ?? '';
  const dropoffTime    = url.searchParams.get('dropoff_time') ?? '';
  const customerAge    = url.searchParams.get('customer_age') ?? '';
  const promoCode      = url.searchParams.get('promo_code') ?? '';

  const paramsPreenchidos =
    dropoffStoreId && categoryId && pickupTime && dropoffTime && customerAge;

  let tarifas = null;
  let buscarErro: string | null = null;

  if (paramsPreenchidos) {
    try {
      tarifas = await tarifaService.buscarTarifasFilial(
        {
          dropoff_store_id: dropoffStoreId,
          category_id:      categoryId,
          pickup_time:      pickupTime,
          dropoff_time:     dropoffTime,
          customer_age:     parseInt(customerAge),
          promo_code:       promoCode || null,
        },
        token,
      );
    } catch (e: any) {
      buscarErro = e?.message ?? 'Erro ao buscar tarifas.';
    }
  }

  return {
    categorias,
    todasLojas,
    tarifas,
    buscarErro,
    params: { dropoffStoreId, categoryId, pickupTime, dropoffTime, customerAge, promoCode },
  };
};

export const actions: Actions = {
  cotar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const pickup_store_id  = String(data.get('pickup_store_id')  ?? '').trim();
    const dropoff_store_id = String(data.get('dropoff_store_id') ?? '').trim();
    const category_id      = String(data.get('category_id')      ?? '').trim();
    const pickup_time      = String(data.get('pickup_time')       ?? '').trim();
    const dropoff_time     = String(data.get('dropoff_time')      ?? '').trim();
    const customer_age     = parseInt(String(data.get('customer_age') ?? '0'));
    const promo_code       = String(data.get('promo_code') ?? '').trim() || null;
    const rate_plan_id     = String(data.get('rate_plan_id') ?? '').trim() || null;

    const addonIds  = data.getAll('addon_id').map(String).filter(Boolean);
    const addonQtys = data.getAll('addon_qty').map(String);
    const selected_addons = addonIds.map((id, i) => ({
      addon_id: id,
      quantity: parseInt(addonQtys[i] ?? '1') || 1,
    }));

    if (!pickup_store_id || !dropoff_store_id || !category_id || !pickup_time || !dropoff_time) {
      return fail(400, { erro: 'Parâmetros incompletos para calcular cotação.' });
    }

    try {
      const cotacao = await tarifaService.calcularCotacaoFilial(
        {
          pickup_store_id,
          dropoff_store_id,
          category_id,
          pickup_time:   new Date(pickup_time).toISOString(),
          dropoff_time:  new Date(dropoff_time).toISOString(),
          customer_age,
          promo_code,
          rate_plan_id,
          selected_addons,
        },
        token,
      );
      return { cotacao };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao calcular cotação.' });
    }
  },
};
