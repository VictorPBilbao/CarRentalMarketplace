import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { filialService } from '$lib/services/filial.service';
import { setFlash } from '$lib/flash';

export const actions: Actions = {

  criar: async ({ request, locals, cookies }) => {

    const data = await request.formData();

    // ── dados gerais ──
    const nome           = String(data.get('nome')          ?? '').trim();
    const codigo         = String(data.get('codigo')        ?? '').trim().toUpperCase();
    const tipoLocalizacao = String(data.get('tipoLocalizacao') ?? '').trim();
    const metodoRetirada  = String(data.get('metodoRetirada')  ?? '').trim();

    // ── endereço ──
    const cep            = String(data.get('cep')           ?? '').trim();
    const logradouro     = String(data.get('logradouro')    ?? '').trim();
    const numero         = String(data.get('numero')        ?? '').trim();
    const complemento    = String(data.get('complemento')   ?? '').trim() || null;
    const bairro         = String(data.get('bairro')        ?? '').trim();
    const cidade         = String(data.get('cidade')        ?? '').trim();
    const estado         = String(data.get('estado')        ?? '').trim();

    // ── contato ──
    const telefone       = String(data.get('telefone')      ?? '').trim();
    const email          = String(data.get('email')         ?? '').trim();
    const gerente        = String(data.get('gerente')       ?? '').trim() || null;

    // ── coordenadas ──
    const latitudeRaw    = String(data.get('latitude')      ?? '').trim();
    const longitudeRaw   = String(data.get('longitude')     ?? '').trim();

    // ── instruções ──
    const instrRetirada  = String(data.get('instrRetirada') ?? '').trim() || null;
    const instrDevolucao = String(data.get('instrDevolucao') ?? '').trim() || null;
    const instrExtra     = String(data.get('instrExtra')    ?? '').trim() || null;

    // ── horários: recebe JSON serializado do cliente ──
    const horariosRaw    = String(data.get('horarios')      ?? '[]');

    // ── comodidades: checkboxes com name="amenidades" ──
    const amenidades     = data.getAll('amenidades').map(String);

    // ── validação ──
    const erros: Record<string, string> = {};

    if (nome.length < 3)                                    erros.nome           = 'Nome deve ter ao menos 3 caracteres';
    if (codigo.length < 3)                                  erros.codigo         = 'Código deve ter ao menos 3 caracteres';
    if (!tipoLocalizacao)                                   erros.tipoLocalizacao = 'Selecione o tipo de localização';
    if (!metodoRetirada)                                    erros.metodoRetirada  = 'Selecione o método de retirada';
    if (cep.replace(/\D/g, '').length !== 8)               erros.cep            = 'CEP inválido';
    if (!logradouro)                                        erros.logradouro     = 'Logradouro obrigatório';
    if (!numero)                                            erros.numero         = 'Número obrigatório';
    if (!bairro)                                            erros.bairro         = 'Bairro obrigatório';
    if (!cidade)                                            erros.cidade         = 'Cidade obrigatória';
    if (!estado)                                            erros.estado         = 'Estado obrigatório';
    if (telefone.replace(/\D/g, '').length < 10)           erros.telefone       = 'Telefone inválido';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))        erros.email          = 'E-mail inválido';

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
      await filialService.criar(
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
          contact: {
            phone:        telefone,
            email,
            manager_name: gerente,
          },
          location: { latitude, longitude },
          instructions: {
            pickup:  instrRetirada,
            dropoff: instrDevolucao,
            extra:   instrExtra,
          },
          operating_hours: horarios as any,
          amenities:       amenidades,
        },
        locals.token!,
      );
    } catch (err: any) {
      return fail(400, {
        erro: err?.message ?? 'Erro ao cadastrar filial. Tente novamente.',
      });
    }

    setFlash(cookies, { tipo: 'sucesso', mensagem: `Filial "${nome}" cadastrada com sucesso.` });
    redirect(303, '/locadora/filiais');
  },

};
