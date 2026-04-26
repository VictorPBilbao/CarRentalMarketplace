import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { reservaService } from '$lib/services/reserva.service';
import { filialService } from '$lib/services/filial.service';
import { categoriaService } from '$lib/services/categoria.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ params, locals }) => {
  const token = locals.token!;
  const id    = decodeURIComponent(params.id);

  const [reserva, lojas, categorias] = await Promise.all([
    reservaService.buscarPorId(id, token).catch(() => null),
    filialService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);

  if (!reserva) error(404, 'Reserva não encontrada.');
  return { reserva, lojas, categorias };
};

export const actions: Actions = {
  atualizarStatus: async ({ params, request, locals, cookies }) => {
    const token = locals.token!;
    const id    = decodeURIComponent(params.id);
    const data  = await request.formData();
    const status = String(data.get('status') ?? '').trim();

    if (!status) return fail(422, { erro: 'Status inválido.' });

    try {
      await reservaService.atualizarStatus(id, status as any, token);
    } catch (e: any) {
      return fail(400, { erro: e?.message ?? 'Erro ao atualizar status.' });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: 'Status da reserva atualizado.' });
    redirect(303, `/locadora/reservas/${encodeURIComponent(id)}`);
  },
};
