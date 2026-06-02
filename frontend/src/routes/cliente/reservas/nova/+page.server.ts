import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { clienteReservaService } from '$lib/services/reserva.service';
import { publicoService } from '$lib/services/publico.service';
import type { CidadeStore, ResultadoPorLocadora } from '$lib/services/publico.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async () => {
  const cidades = await publicoService.listarCidades().catch(() => []);
  return { cidades };
};

export const actions: Actions = {
  buscar: async ({ request }) => {
    const data = await request.formData();

    const pickupCity   = String(data.get('pickupCity')   ?? '').trim();
    const dropoffCity  = String(data.get('dropoffCity')  ?? '').trim();
    const pickupTime   = String(data.get('pickupTime')   ?? '').trim();
    const dropoffTime  = String(data.get('dropoffTime')  ?? '').trim();
    const customerAge  = parseInt(String(data.get('customerAge') ?? '25'));
    const nationality  = String(data.get('nationality')  ?? '').trim() || null;

    const campos = { pickupCity, dropoffCity, pickupTime, dropoffTime, customerAge: String(customerAge), nationality: nationality ?? '' };

    const erros: Record<string, string> = {};
    if (!pickupCity)  erros.pickupCity  = 'Selecione a cidade de retirada.';
    if (!dropoffCity) erros.dropoffCity = 'Selecione a cidade de devolução.';
    if (!pickupTime)  erros.pickupTime  = 'Informe a data de retirada.';
    if (!dropoffTime) erros.dropoffTime = 'Informe a data de devolução.';

    if (Object.keys(erros).length > 0) {
      return fail(422, { erros, campos });
    }

    // Carrega cidades para montar o mapeamento empresa → lojas
    const cidades = await publicoService.listarCidades().catch(() => []);

    const storesByCity = (city: string): CidadeStore[] =>
      cidades.find(c => c.city === city)?.stores ?? [];

    const pickupStores  = storesByCity(pickupCity);
    const dropoffStores = storesByCity(dropoffCity);

    // Agrupa por empresa
    const pickupByCompany  = new Map<string, CidadeStore[]>();
    const dropoffByCompany = new Map<string, CidadeStore[]>();

    for (const s of pickupStores) {
      if (!pickupByCompany.has(s.company_id)) pickupByCompany.set(s.company_id, []);
      pickupByCompany.get(s.company_id)!.push(s);
    }
    for (const s of dropoffStores) {
      if (!dropoffByCompany.has(s.company_id)) dropoffByCompany.set(s.company_id, []);
      dropoffByCompany.get(s.company_id)!.push(s);
    }

    // Empresas presentes nas duas cidades
    const empresasComuns = [...pickupByCompany.keys()].filter(id => dropoffByCompany.has(id));

    if (empresasComuns.length === 0) {
      return fail(400, {
        erro: `Nenhuma locadora possui filiais em ${pickupCity} e ${dropoffCity} ao mesmo tempo.`,
        campos,
      });
    }

    // Para cada empresa e cada filial de retirada, busca categorias disponíveis
    const empresas: ResultadoPorLocadora[] = [];
    for (const companyId of empresasComuns) {
      const pStores = pickupByCompany.get(companyId)!;
      const dStore  = dropoffByCompany.get(companyId)![0];
      for (const pStore of pStores) {
        try {
          const resultado = await publicoService.buscarCategorias({
            pickup_store_id:  pStore.id,
            dropoff_store_id: dStore.id,
            pickup_time:      new Date(pickupTime).toISOString(),
            dropoff_time:     new Date(dropoffTime).toISOString(),
            customer_age:     customerAge,
            nationality,
          });
          if (resultado.categorias.length > 0) {
            empresas.push({
              company_id:    companyId,
              company_name:  pStore.company_name || companyId,
              pickup_store:  pStore,
              dropoff_store: dStore,
              total_days:    resultado.total_days,
              is_one_way:    resultado.is_one_way,
              categorias:    resultado.categorias,
            });
          }
        } catch {
          // Filial sem tarifas configuradas — pula silenciosamente
        }
      }
    }

    if (empresas.length === 0) {
      return { etapa: 'categorias' as const, empresas: [], campos };
    }

    return { etapa: 'categorias' as const, empresas, campos };
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
