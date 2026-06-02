import type { PageServerLoad } from './$types';
import { adminService } from '$lib/services/admin.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const chaves = await adminService.listarChavesOta(token).catch(() => []);
  const ativas = chaves.filter(c => c.active).length;
  return { totalChaves: chaves.length, chavesAtivas: ativas };
};
