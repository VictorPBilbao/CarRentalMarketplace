import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { clienteReservaService } from '$lib/services/reserva.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ params, locals }) => {
  const token = locals.token!;
  const id    = decodeURIComponent(params.id);

  const [reserva, categorias] = await Promise.all([
    clienteReservaService.buscarPorId(id, token).catch(() => null),
    categoriaService.listar(token).catch(() => []),
  ]);

  if (!reserva) error(404, 'Reserva não encontrada.');
  return { reserva, categorias };
};

export const actions: Actions = {
  cancelar: async ({ params, locals }) => {
    const token = locals.token!;
    const id    = decodeURIComponent(params.id);
    try {
      await clienteReservaService.cancelar(id, token);
    } catch (e) {
      return fail(422, { erro: e instanceof Error ? e.message : 'Erro ao cancelar reserva.' });
    }
    return { sucesso: true };
  },
};
