import type { PageServerLoad } from './$types';
import { tarifaService } from '$lib/services/tarifa.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [ratePlans, fees, addons] = await Promise.all([
    tarifaService.listarRatePlans(token).catch(() => []),
    tarifaService.listarFees(token).catch(() => []),
    tarifaService.listarAddons(token).catch(() => []),
  ]);

  return { ratePlans, fees, addons };
};
