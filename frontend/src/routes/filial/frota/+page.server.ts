import type { PageServerLoad } from './$types';
import { filialVeiculoService } from '$lib/services/veiculo.service';
import { categoriaService } from '$lib/services/categoria.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [veiculos, categorias] = await Promise.all([
    filialVeiculoService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
  ]);

  return { veiculos, categorias };
};
