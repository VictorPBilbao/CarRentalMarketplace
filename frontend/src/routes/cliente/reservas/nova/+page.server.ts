import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { clienteReservaService } from '$lib/services/reserva.service';
import { publicoService } from '$lib/services/publico.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async () => {
  const cidades = await publicoService.listarCidades().catch(() => []);
  return { cidades };
};

export const actions: Actions = {
  buscar: async ({ request }) => {
    const data = await request.formData();

    const pickupStoreId   = String(data.get('pickupStoreId')   ?? '').trim();
    const dropoffStoreId  = String(data.get('dropoffStoreId')  ?? '').trim();
    const pickupTime      = String(data.get('pickupTime')      ?? '').trim();
    const dropoffTime     = String(data.get('dropoffTime')     ?? '').trim();
    const customerAge     = parseInt(String(data.get('customerAge') ?? '25'));
    const pickupCity      = String(data.get('pickupCity')      ?? '').trim();
    const dropoffCity     = String(data.get('dropoffCity')     ?? '').trim();
    const pickupStoreName  = String(data.get('pickupStoreName')  ?? '').trim();
    const dropoffStoreName = String(data.get('dropoffStoreName') ?? '').trim();
    const nationality      = String(data.get('nationality')      ?? '').trim() || null;

    const campos = { pickupStoreId, dropoffStoreId, pickupTime, dropoffTime, customerAge: String(customerAge), pickupCity, dropoffCity, pickupStoreName, dropoffStoreName, nationality: nationality ?? '' };

    const erros: Record<string, string> = {};
    if (!pickupStoreId)  erros.pickupStoreId  = 'Selecione a loja de retirada.';
    if (!dropoffStoreId) erros.dropoffStoreId = 'Selecione a loja de devolução.';
    if (!pickupTime)     erros.pickupTime     = 'Informe a data de retirada.';
    if (!dropoffTime)    erros.dropoffTime    = 'Informe a data de devolução.';

    if (Object.keys(erros).length > 0) {
      return fail(422, { erros, campos });
    }

    try {
      const resultado = await publicoService.buscarCategorias({
        pickup_store_id:  pickupStoreId,
        dropoff_store_id: dropoffStoreId,
        pickup_time:      new Date(pickupTime).toISOString(),
        dropoff_time:     new Date(dropoffTime).toISOString(),
        customer_age:     customerAge,
        nationality,
      });

      return { etapa: 'categorias' as const, resultado, campos };
    } catch (e: any) {
      return fail(400, {
        erro: e?.message ?? 'Erro ao buscar veículos.',
        campos,
      });
    }
  },

  confirmar: async ({ request, locals, cookies }) => {
    const token = locals.token!;
    const data  = await request.formData();

    const pickupStoreId  = String(data.get('pickupStoreId')  ?? '').trim();
    const dropoffStoreId = String(data.get('dropoffStoreId') ?? '').trim();
    const categoryId     = String(data.get('categoryId')     ?? '').trim();
    const pickupTime     = String(data.get('pickupTime')     ?? '').trim();
    const dropoffTime    = String(data.get('dropoffTime')    ?? '').trim();
    const dailyRate      = parseFloat(String(data.get('dailyRate')  ?? '0'));
    const totalDays      = parseInt(String(data.get('totalDays')    ?? '1'));
    const fees           = parseFloat(String(data.get('fees')       ?? '0'));
    const ratePlanId     = String(data.get('ratePlanId')    ?? '').trim() || null;
    const feesJson       = String(data.get('feesJson')      ?? '[]');
    const flightNumber   = String(data.get('flightNumber')  ?? '').trim() || null;
    const notes          = String(data.get('notes')         ?? '').trim() || null;

    const selected_addons: { addon_id: string; quantity: number }[] = [];
    for (const [key, val] of data.entries()) {
      if (key.startsWith('addon_')) {
        const qty = parseInt(String(val));
        if (qty > 0) selected_addons.push({ addon_id: key.slice(6), quantity: qty });
      }
    }

    let reserva;
    try {
      reserva = await clienteReservaService.criar(
        {
          category_id:      categoryId,
          pickup_store_id:  pickupStoreId,
          dropoff_store_id: dropoffStoreId,
          pickup_time:      pickupTime,
          dropoff_time:     dropoffTime,
          flight_number:    flightNumber,
          notes:            notes,
          selected_addons,
          pricing: {
            daily_rate: dailyRate,
            total_days: totalDays,
            fees,
            breakdown: [
              ...(ratePlanId ? [{ type: 'BASE_RATE', description: `${totalDays} dia(s) × R$ ${dailyRate.toFixed(2)}`, amount: dailyRate * totalDays }] : []),
              ...(() => { try { return (JSON.parse(feesJson) as { name: string; amount: number; is_tax: boolean }[]).map(f => ({ type: f.is_tax ? 'TAX' : 'FEE', description: f.name, amount: f.amount })); } catch { return []; } })(),
            ],
          },
        },
        token,
      );
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao criar reserva.' });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Reserva criada com sucesso!' });
    redirect(303, `/cliente/reservas/${encodeURIComponent(reserva.id)}`);
  },
};
