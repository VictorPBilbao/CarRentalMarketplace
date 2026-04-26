import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { categoriaService } from '$lib/services/categoria.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ params, locals }) => {
  const categoria = await categoriaService.buscarPorId(
    decodeURIComponent(params.id),
    locals.token!,
  );
  return { categoria };
};

export const actions: Actions = {
  atualizar: async ({ request, params, locals, cookies }) => {
    const data = await request.formData();

    const groupName    = String(data.get('groupName')    ?? '').trim();
    const code         = String(data.get('code')         ?? '').trim().toUpperCase();
    const acrissCode   = String(data.get('acrissCode')   ?? '').trim().toUpperCase() || null;
    const description  = String(data.get('description')  ?? '').trim() || null;
    const fuelType     = String(data.get('fuelType')     ?? '').trim();
    const transmission = String(data.get('transmission') ?? '').trim();
    const doors        = parseInt(String(data.get('doors')        ?? '4'), 10);
    const airCond      = data.get('airConditioning') === 'true';
    const passengers   = parseInt(String(data.get('passengers')   ?? '5'), 10);
    const smallSuit    = parseInt(String(data.get('smallSuitcases') ?? '0'), 10);
    const largeSuit    = parseInt(String(data.get('largeSuitcases') ?? '0'), 10);
    const modelosRaw   = String(data.get('modelos') ?? '[]');
    const imageUrl     = String(data.get('imageUrl') ?? '').trim() || null;

    const erros: Record<string, string> = {};
    if (groupName.length < 2)                      erros.groupName    = 'Nome deve ter ao menos 2 caracteres.';
    if (code.length < 2)                           erros.code         = 'Código deve ter ao menos 2 caracteres.';
    if (acrissCode && acrissCode.length !== 4)     erros.acrissCode   = 'Código ACRISS deve ter exatamente 4 letras.';
    if (!fuelType)                                 erros.fuelType     = 'Selecione o tipo de combustível.';
    if (!transmission)                             erros.transmission = 'Selecione o câmbio.';
    if (isNaN(doors) || doors < 2)                 erros.doors        = 'Número de portas deve ser pelo menos 2.';
    if (isNaN(passengers) || passengers < 1)       erros.passengers   = 'Mínimo de 1 passageiro.';

    const campos = {
      groupName, code, acrissCode, description, fuelType, transmission,
      doors: String(doors), passengers: String(passengers),
      smallSuitcases: String(smallSuit), largeSuitcases: String(largeSuit),
      airConditioning: String(airCond),
      modelosRaw, imageUrl,
    };

    if (Object.keys(erros).length > 0) return fail(422, { erros, campos });

    let modelos: string[] = [];
    try { modelos = JSON.parse(modelosRaw); } catch { /* ignore */ }

    try {
      await categoriaService.atualizar(
        decodeURIComponent(params.id),
        {
          group_name:            groupName,
          code,
          acriss_code:           acrissCode,
          description,
          features: {
            fuel_type:        fuelType as any,
            transmission:     transmission as any,
            doors,
            air_conditioning: airCond,
            capacity: {
              passengers,
              small_suitcases: smallSuit,
              large_suitcases: largeSuit,
            },
          },
          representative_models: modelos,
          image_url:             imageUrl,
        },
        locals.token!,
      );
    } catch (e: any) {
      return fail(400, { erros: {}, erro: e?.message ?? 'Erro ao atualizar categoria.', campos });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: `Categoria "${groupName}" atualizada com sucesso.` });
    redirect(303, '/locadora/categorias');
  },
};
