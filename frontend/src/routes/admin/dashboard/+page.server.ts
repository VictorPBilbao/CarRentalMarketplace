import type { PageServerLoad } from './$types';
import { adminService } from '$lib/services/admin.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;
  const stats = await adminService.getDashboard(token).catch(() => null);
  return { stats };
};
