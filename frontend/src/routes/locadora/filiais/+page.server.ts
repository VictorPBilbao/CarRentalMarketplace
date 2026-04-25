import type { PageServerLoad } from './$types';
import { filialService, type Filial } from '$lib/services/filial.service';

export const load: PageServerLoad = async ({ locals }) => {
  try {
    const filiais = await filialService.listar(locals.token!);
    return { filiais, erro: null };
  } catch {
    return { filiais: [] as Filial[], erro: 'Não foi possível carregar as filiais. Verifique sua conexão ou tente novamente.' };
  }
};
