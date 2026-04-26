import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
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
