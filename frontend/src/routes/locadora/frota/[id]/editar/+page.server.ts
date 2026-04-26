import { fail, redirect, error } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { veiculoService } from '$lib/services/veiculo.service';
import { categoriaService } from '$lib/services/categoria.service';
import { filialService } from '$lib/services/filial.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ params, locals }) => {
  const token = locals.token!;
  const id    = decodeURIComponent(params.id);

  const [veiculo, categorias, lojas] = await Promise.all([
    veiculoService.buscarPorId(id, token).catch(() => null),
    categoriaService.listar(token).catch(() => []),
    filialService.listar(token).catch(() => []),
  ]);

  if (!veiculo) error(404, 'Veículo não encontrado.');

  return { veiculo, categorias, lojas };
};

export const actions: Actions = {
  atualizar: async ({ params, request, locals, cookies }) => {
    const token = locals.token!;
    const id    = decodeURIComponent(params.id);
    const data  = await request.formData();

    const make          = String(data.get('make')          ?? '').trim();
    const model         = String(data.get('model')         ?? '').trim();
    const year          = parseInt(String(data.get('year')          ?? '0'), 10);
    const color         = String(data.get('color')         ?? '').trim();
    const plate         = String(data.get('plate')         ?? '').trim().toUpperCase();
    const chassisNumber = String(data.get('chassisNumber') ?? '').trim().toUpperCase();
    const mileageKm     = parseInt(String(data.get('mileageKm')     ?? '0'), 10);
    const category      = String(data.get('category')      ?? '').trim();
    const currentStore  = String(data.get('currentStore')  ?? '').trim();
    const status        = String(data.get('status')        ?? 'AVAILABLE').trim();

    const erros: Record<string, string> = {};
    if (!make)                              erros.make          = 'Informe a marca.';
    if (!model)                             erros.model         = 'Informe o modelo.';
    if (isNaN(year) || year < 2000)         erros.year          = 'Ano inválido (mínimo 2000).';
    if (!color)                             erros.color         = 'Informe a cor.';
    if (plate.length < 6)                   erros.plate         = 'Placa deve ter ao menos 6 caracteres.';
    if (chassisNumber.length !== 17)        erros.chassisNumber = 'Chassi deve ter exatamente 17 caracteres.';
    if (isNaN(mileageKm) || mileageKm < 0) erros.mileageKm     = 'Quilometragem inválida.';
    if (!category)                          erros.category      = 'Selecione uma categoria.';
    if (!currentStore)                      erros.currentStore  = 'Selecione uma loja.';

    const campos = {
      make, model, year: String(year), color, plate, chassisNumber,
      mileageKm: String(mileageKm), category, currentStore, status,
    };

    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    try {
      await veiculoService.atualizar(
        id,
        {
          make,
          model,
          year,
          color,
          plate,
          chassis_number: chassisNumber,
          mileage_km:     mileageKm,
          category,
          current_store:  currentStore,
          status:         status as any,
        },
        token,
      );
    } catch (e: any) {
      return fail(400, { erros: {}, erro: e?.message ?? 'Erro ao atualizar veículo.', campos });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: `${make} ${model} atualizado com sucesso.` });
    redirect(303, '/locadora/frota');
  },
};
