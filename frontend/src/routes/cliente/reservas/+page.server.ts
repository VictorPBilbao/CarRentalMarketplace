import type { PageServerLoad } from './$types';
import { clienteReservaService } from '$lib/services/reserva.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals, url }) => {
  const token = locals.token!;
  const statusFiltro = url.searchParams.get('status') ?? undefined;

  const [reservas, categorias] = await Promise.all([
    clienteReservaService.listar(token, statusFiltro).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);

  return { reservas, categorias, statusFiltro: statusFiltro ?? null };
};
