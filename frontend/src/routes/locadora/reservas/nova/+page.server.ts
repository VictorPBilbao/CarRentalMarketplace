import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { reservaService } from '$lib/services/reserva.service';
import { tarifaService } from '$lib/services/tarifa.service';
import { filialService } from '$lib/services/filial.service';
import { categoriaService } from '$lib/services/categoria.service';
import { authService } from '$lib/services/auth.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const [lojas, categorias, clientes] = await Promise.all([
    filialService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
    authService.listarClientes(token).catch(() => []),
  ]);
  return { lojas, categorias, clientes };
};

export const actions: Actions = {
  cotar: async ({ request, locals }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const customerId     = String(data.get('customerId')     ?? '').trim();
    const categoryId     = String(data.get('categoryId')     ?? '').trim();
    const pickupStoreId  = String(data.get('pickupStoreId')  ?? '').trim();
    const dropoffStoreId = String(data.get('dropoffStoreId') ?? '').trim();
    const pickupTime     = String(data.get('pickupTime')     ?? '').trim();
    const dropoffTime    = String(data.get('dropoffTime')    ?? '').trim();
    const customerAge    = parseInt(String(data.get('customerAge') ?? '25'));
    const nationality    = String(data.get('nationality')    ?? '').trim() || null;
    const promoCode      = String(data.get('promoCode')      ?? '').trim() || null;
    const flightNumber   = String(data.get('flightNumber')   ?? '').trim() || null;
    const notes          = String(data.get('notes')          ?? '').trim() || null;

    const erros: Record<string, string> = {};
    if (!customerId)     erros.customerId     = 'Selecione o cliente.';
    if (!categoryId)     erros.categoryId     = 'Selecione uma categoria.';
    if (!pickupStoreId)  erros.pickupStoreId  = 'Selecione a loja de retirada.';
    if (!dropoffStoreId) erros.dropoffStoreId = 'Selecione a loja de devolução.';
    if (!pickupTime)     erros.pickupTime     = 'Informe a data de retirada.';
    if (!dropoffTime)    erros.dropoffTime    = 'Informe a data de devolução.';
    if (isNaN(customerAge) || customerAge < 18) erros.customerAge = 'Idade mínima de 18 anos.';

    if (pickupTime && dropoffTime && !erros.pickupTime && !erros.dropoffTime) {
      if (new Date(dropoffTime) <= new Date(pickupTime))
        erros.dropoffTime = 'Devolução deve ser posterior à retirada.';
    }

    const campos = {
      customerId, categoryId, pickupStoreId, dropoffStoreId,
      pickupTime, dropoffTime, customerAge: String(customerAge),
      nationality: nationality ?? '', promoCode: promoCode ?? '',
      flightNumber: flightNumber ?? '', notes: notes ?? '',
    };

    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    try {
      const cotacao = await tarifaService.calcularCotacaoLocadora(
        {
          pickup_store_id:  pickupStoreId,
          dropoff_store_id: dropoffStoreId,
          category_id:      categoryId,
          pickup_time:      new Date(pickupTime).toISOString(),
          dropoff_time:     new Date(dropoffTime).toISOString(),
          customer_age:     customerAge,
          nationality,
          promo_code:       promoCode,
          selected_addons:  [],
        },
        token,
      );
      return { etapa: 'confirmar' as const, cotacao, campos };
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Sem tarifas aplicáveis para os parâmetros informados.', campos });
    }
  },

  confirmar: async ({ request, locals, cookies }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const customerId     = String(data.get('customerId')     ?? '').trim();
    const categoryId     = String(data.get('categoryId')     ?? '').trim();
    const pickupStoreId  = String(data.get('pickupStoreId')  ?? '').trim();
    const dropoffStoreId = String(data.get('dropoffStoreId') ?? '').trim();
    const pickupTime     = String(data.get('pickupTime')     ?? '').trim();
    const dropoffTime    = String(data.get('dropoffTime')    ?? '').trim();
    const customerAge    = parseInt(String(data.get('customerAge') ?? '25'));
    const nationality    = String(data.get('nationality')    ?? '').trim() || null;
    const promoCode      = String(data.get('promoCode')      ?? '').trim() || null;
    const flightNumber   = String(data.get('flightNumber')   ?? '').trim() || null;
    const notes          = String(data.get('notes')          ?? '').trim() || null;

    const addonIds  = data.getAll('addon_id').map(String).filter(Boolean);
    const addonQtys = data.getAll('addon_qty').map(String);
    const selectedAddons = addonIds.map((id, i) => ({
      addon_id: id,
      quantity: parseInt(addonQtys[i] ?? '1') || 1,
    }));

    let cotacao;
    try {
      cotacao = await tarifaService.calcularCotacaoLocadora(
        {
          pickup_store_id:  pickupStoreId,
          dropoff_store_id: dropoffStoreId,
          category_id:      categoryId,
          pickup_time:      new Date(pickupTime).toISOString(),
          dropoff_time:     new Date(dropoffTime).toISOString(),
          customer_age:     customerAge,
          nationality,
          promo_code:       promoCode,
          selected_addons:  selectedAddons,
        },
        token,
      );
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao recalcular cotação.' });
    }

    const breakdown = cotacao.breakdown.map((item) => ({
      type:        item.type,
      description: item.description,
      amount:      item.amount,
    }));

    let reserva;
    try {
      reserva = await reservaService.criar(
        {
          customer_id:      customerId,
          category_id:      categoryId,
          pickup_store_id:  pickupStoreId,
          dropoff_store_id: dropoffStoreId,
          pickup_time:      new Date(pickupTime).toISOString(),
          dropoff_time:     new Date(dropoffTime).toISOString(),
          flight_number:    flightNumber,
          notes,
          pricing: {
            daily_rate: cotacao.daily_rate,
            total_days: cotacao.total_days,
            fees:       cotacao.fees_total,
            breakdown,
          },
        },
        token,
      );
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao criar reserva.' });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Reserva criada com sucesso.' });
    redirect(303, `/locadora/reservas/${encodeURIComponent(reserva.id)}`);
  },
};
