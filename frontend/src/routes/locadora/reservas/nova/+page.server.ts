import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { reservaService } from '$lib/services/reserva.service';
import { filialService } from '$lib/services/filial.service';
import { categoriaService } from '$lib/services/categoria.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const [lojas, categorias] = await Promise.all([
    filialService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);
  return { lojas, categorias };
};

export const actions: Actions = {
  criar: async ({ request, locals, cookies }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const customerId     = String(data.get('customerId')     ?? '').trim();
    const categoryId     = String(data.get('categoryId')     ?? '').trim();
    const pickupStoreId  = String(data.get('pickupStoreId')  ?? '').trim();
    const dropoffStoreId = String(data.get('dropoffStoreId') ?? '').trim();
    const pickupTime     = String(data.get('pickupTime')     ?? '').trim();
    const dropoffTime    = String(data.get('dropoffTime')    ?? '').trim();
    const flightNumber   = String(data.get('flightNumber')   ?? '').trim() || null;
    const notes          = String(data.get('notes')          ?? '').trim() || null;
    const dailyRate      = parseFloat(String(data.get('dailyRate') ?? '0'));
    const fees           = parseFloat(String(data.get('fees')      ?? '0')) || 0;

    const erros: Record<string, string> = {};
    if (!customerId)                          erros.customerId     = 'Informe o ID do cliente.';
    if (!categoryId)                          erros.categoryId     = 'Selecione uma categoria.';
    if (!pickupStoreId)                       erros.pickupStoreId  = 'Selecione a loja de retirada.';
    if (!dropoffStoreId)                      erros.dropoffStoreId = 'Selecione a loja de devolução.';
    if (!pickupTime)                          erros.pickupTime     = 'Informe a data de retirada.';
    if (!dropoffTime)                         erros.dropoffTime    = 'Informe a data de devolução.';
    if (isNaN(dailyRate) || dailyRate <= 0)   erros.dailyRate      = 'Informe a diária (valor > 0).';

    let totalDays = 1;
    if (pickupTime && dropoffTime && !erros.pickupTime && !erros.dropoffTime) {
      const pickup  = new Date(pickupTime);
      const dropoff = new Date(dropoffTime);
      if (dropoff <= pickup) {
        erros.dropoffTime = 'Devolução deve ser posterior à retirada.';
      } else {
        totalDays = Math.max(1, Math.ceil((dropoff.getTime() - pickup.getTime()) / 86_400_000));
      }
    }

    const campos = {
      customerId, categoryId, pickupStoreId, dropoffStoreId,
      pickupTime, dropoffTime,
      flightNumber: flightNumber ?? '',
      notes: notes ?? '',
      dailyRate: String(dailyRate),
      fees: String(fees),
    };

    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    try {
      const reserva = await reservaService.criar(
        {
          customer_id:      customerId,
          category_id:      categoryId,
          pickup_store_id:  pickupStoreId,
          dropoff_store_id: dropoffStoreId,
          pickup_time:      new Date(pickupTime).toISOString(),
          dropoff_time:     new Date(dropoffTime).toISOString(),
          flight_number:    flightNumber,
          notes:            notes,
          pricing: {
            daily_rate: dailyRate,
            total_days: totalDays,
            fees,
            breakdown: [],
          },
        },
        token,
      );

      setFlash(cookies, { tipo: 'sucesso', mensagem: 'Reserva criada com sucesso.' });
      redirect(303, `/locadora/reservas/${encodeURIComponent(reserva.id)}`);
    } catch (e: any) {
      return fail(400, { erros: {}, erro: e?.message ?? 'Erro ao criar reserva.', campos });
    }
  },
};
