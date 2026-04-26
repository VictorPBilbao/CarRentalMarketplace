import type { PageServerLoad } from './$types';
import { veiculoService } from '$lib/services/veiculo.service';
import { categoriaService } from '$lib/services/categoria.service';
import { filialService } from '$lib/services/filial.service';

export const load: PageServerLoad = async ({ locals }) => {
  const token = locals.token!;

  const [veiculos, categorias, lojas] = await Promise.all([
    veiculoService.listar(token).catch(() => []),
    categoriaService.listar(token).catch(() => []),
    filialService.listar(token).catch(() => []),
  ]);

  return { veiculos, categorias, lojas };
};
