import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { filialService } from '$lib/services/filial.service';
import { setFlash } from '$lib/flash';

export const load: PageServerLoad = async ({ params, locals }) => {
  const filial = await filialService.buscarPorId(params.id, locals.token!);
  return { filial };
};

export const actions: Actions = {

  atualizar: async ({ request, params, locals, cookies }) => {

    const data = await request.formData();

    const nome            = String(data.get('nome')             ?? '').trim();
    const codigo          = String(data.get('codigo')           ?? '').trim().toUpperCase();
    const tipoLocalizacao = String(data.get('tipoLocalizacao')  ?? '').trim();
    const metodoRetirada  = String(data.get('metodoRetirada')   ?? '').trim();

    const cep             = String(data.get('cep')              ?? '').trim();
    const logradouro      = String(data.get('logradouro')       ?? '').trim();
    const numero          = String(data.get('numero')           ?? '').trim();
    const complemento     = String(data.get('complemento')      ?? '').trim() || null;
    const bairro          = String(data.get('bairro')           ?? '').trim();
    const cidade          = String(data.get('cidade')           ?? '').trim();
    const estado          = String(data.get('estado')           ?? '').trim();

    const telefone        = String(data.get('telefone')         ?? '').trim();
    const email           = String(data.get('email')            ?? '').trim();
    const gerente         = String(data.get('gerente')          ?? '').trim() || null;

    const latitudeRaw     = String(data.get('latitude')         ?? '').trim();
    const longitudeRaw    = String(data.get('longitude')        ?? '').trim();

    const instrRetirada   = String(data.get('instrRetirada')    ?? '').trim() || null;
    const instrDevolucao  = String(data.get('instrDevolucao')   ?? '').trim() || null;
    const instrExtra      = String(data.get('instrExtra')       ?? '').trim() || null;

    const horariosRaw     = String(data.get('horarios')         ?? '[]');
    const amenidades      = data.getAll('amenidades').map(String);

    const erros: Record<string, string> = {};

    if (nome.length < 3)                                    erros.nome            = 'Nome deve ter ao menos 3 caracteres';
    if (codigo.length < 3)                                  erros.codigo          = 'Código deve ter ao menos 3 caracteres';
    if (!tipoLocalizacao)                                   erros.tipoLocalizacao = 'Selecione o tipo de localização';
    if (!metodoRetirada)                                    erros.metodoRetirada  = 'Selecione o método de retirada';
    if (cep.replace(/\D/g, '').length !== 8)               erros.cep             = 'CEP inválido';
    if (!logradouro)                                        erros.logradouro      = 'Logradouro obrigatório';
    if (!numero)                                            erros.numero          = 'Número obrigatório';
    if (!bairro)                                            erros.bairro          = 'Bairro obrigatório';
    if (!cidade)                                            erros.cidade          = 'Cidade obrigatória';
    if (!estado)                                            erros.estado          = 'Estado obrigatório';
    if (telefone.replace(/\D/g, '').length < 10)           erros.telefone        = 'Telefone inválido';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))        erros.email           = 'E-mail inválido';

    const latitude  = parseFloat(latitudeRaw);
    const longitude = parseFloat(longitudeRaw);
    if (isNaN(latitude)  || latitude  < -90  || latitude  > 90)  erros.latitude  = 'Latitude inválida (-90 a 90)';
    if (isNaN(longitude) || longitude < -180 || longitude > 180) erros.longitude = 'Longitude inválida (-180 a 180)';

    let horarios: unknown[] = [];
    try { horarios = JSON.parse(horariosRaw); } catch { erros.horarios = 'Horários inválidos'; }

    if (Object.keys(erros).length > 0) {
      return fail(422, {
        erros,
        campos: { nome, codigo, tipoLocalizacao, metodoRetirada, cep, logradouro, numero, complemento, bairro, cidade, estado, telefone, email, gerente, latitudeRaw, longitudeRaw, instrRetirada, instrDevolucao, instrExtra, horariosRaw, amenidades },
      });
    }

    try {
      await filialService.atualizar(
        params.id,
        {
          name:          nome,
          code:          codigo,
          location_type: tipoLocalizacao as any,
          pickup_method: metodoRetirada as any,
          address: {
            street:       logradouro,
            number:       numero,
            complement:   complemento,
            neighborhood: bairro,
            city:         cidade,
            state:        estado,
            postal_code:  cep.replace(/\D/g, ''),
            country:      'BR',
          },
          contact: { phone: telefone, email, manager_name: gerente },
          location: { latitude, longitude },
          instructions: { pickup: instrRetirada, dropoff: instrDevolucao, extra: instrExtra },
          operating_hours: horarios as any,
          amenities: amenidades,
        },
        locals.token!,
      );
    } catch (err: any) {
      return fail(400, { erro: err?.message ?? 'Erro ao atualizar filial. Tente novamente.' });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: `Filial "${nome}" atualizada com sucesso.` });
    redirect(303, '/locadora/filiais');
  },

};
