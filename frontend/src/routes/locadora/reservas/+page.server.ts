import type { PageServerLoad } from './$types';
import { reservaService } from '$lib/services/reserva.service';
import { filialService } from '$lib/services/filial.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals, url }) => {
  const token = locals.token!;
  const statusFiltro = url.searchParams.get('status') ?? undefined;

  const [reservas, lojas, categorias] = await Promise.all([
    reservaService.listar(token, statusFiltro).catch(() => []),
    filialService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);

  return { reservas, lojas, categorias, statusFiltro: statusFiltro ?? null };
};
