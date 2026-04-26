import type { PageServerLoad } from './$types';
import { clienteReservaService } from '$lib/services/reserva.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const reservas = await clienteReservaService.listar(token).catch(() => []);

  return { reservas };
};
