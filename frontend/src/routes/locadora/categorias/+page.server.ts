import type { PageServerLoad } from './$types';
import { categoriaService } from '$lib/services/categoria.service';
import type { Categoria } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals }) => {
  try {
    const categorias = await categoriaService.listar(locals.token!);
    return { categorias, erro: null };
  } catch {
    return { categorias: [] as Categoria[], erro: 'Não foi possível carregar as categorias.' };
  }
};
