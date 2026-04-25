<script lang="ts">
  import { enhance } from '$app/forms';
  import type { Filial } from '$lib/services/filial.service';

  interface Props {
    form?:         Record<string, any> | null;
    filial?:       Filial | null;
    action:        string;
    acaoLabel:     string;
    cancelarHref?: string;
  }

  let {
    form        = null,
    filial      = null,
    action,
    acaoLabel,
    cancelarHref = '/locadora/filiais',
  }: Props = $props();

  const erros      = $derived((form as any)?.erros   ?? {});
  const erroGlobal = $derived((form as any)?.erro    ?? null);
  const campos     = $derived((form as any)?.campos  ?? {});

  // campos[key] > filialVal > ''
  function v(key: string, filialVal?: string | null): string {
    return campos[key] ?? filialVal ?? '';
  }

  // ── horários ──
  type DiaSemana = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY' | 'SUNDAY' | 'HOLIDAY';

  interface Horario {
    day_of_week: DiaSemana;
    label:       string;
    open:        string;
    close:       string;
    is_closed:   boolean;
  }

  const DIAS_CONFIG: { day_of_week: DiaSemana; label: string; defaultOpen: string; defaultClose: string; defaultClosed: boolean }[] = [
    { day_of_week: 'MONDAY',    label: 'Segunda-feira', defaultOpen: '08:00', defaultClose: '18:00', defaultClosed: false },
    { day_of_week: 'TUESDAY',   label: 'Terça-feira',   defaultOpen: '08:00', defaultClose: '18:00', defaultClosed: false },
    { day_of_week: 'WEDNESDAY', label: 'Quarta-feira',  defaultOpen: '08:00', defaultClose: '18:00', defaultClosed: false },
    { day_of_week: 'THURSDAY',  label: 'Quinta-feira',  defaultOpen: '08:00', defaultClose: '18:00', defaultClosed: false },
    { day_of_week: 'FRIDAY',    label: 'Sexta-feira',   defaultOpen: '08:00', defaultClose: '18:00', defaultClosed: false },
    { day_of_week: 'SATURDAY',  label: 'Sábado',        defaultOpen: '08:00', defaultClose: '13:00', defaultClosed: false },
    { day_of_week: 'SUNDAY',    label: 'Domingo',       defaultOpen: '08:00', defaultClose: '12:00', defaultClosed: true  },
    { day_of_week: 'HOLIDAY',   label: 'Feriado',       defaultOpen: '08:00', defaultClose: '12:00', defaultClosed: true  },
  ];

  function buildHorarios(): Horario[] {
    // 1. horariosRaw preservados após erro de validação
    const raw = (form as any)?.campos?.horariosRaw;
    if (raw) {
      try {
        const parsed: any[] = JSON.parse(raw);
        return DIAS_CONFIG.map(d => {
          const h = parsed.find(p => p.day_of_week === d.day_of_week);
          return { day_of_week: d.day_of_week, label: d.label, open: h?.open ?? d.defaultOpen, close: h?.close ?? d.defaultClose, is_closed: h?.is_closed ?? d.defaultClosed };
        });
      } catch { /* fallthrough */ }
    }
    // 2. dados da filial (modo edição)
    if (filial?.operating_hours?.length) {
      return DIAS_CONFIG.map(d => {
        const h = filial!.operating_hours.find(oh => oh.day_of_week === d.day_of_week);
        return { day_of_week: d.day_of_week, label: d.label, open: h?.open ?? d.defaultOpen, close: h?.close ?? d.defaultClose, is_closed: h?.is_closed ?? d.defaultClosed };
      });
    }
    // 3. defaults
    return DIAS_CONFIG.map(d => ({ day_of_week: d.day_of_week, label: d.label, open: d.defaultOpen, close: d.defaultClose, is_closed: d.defaultClosed }));
  }

  let horarios: Horario[] = $state(buildHorarios());

  const horariosJSON = $derived(
    JSON.stringify(horarios.map(h => ({
      day_of_week: h.day_of_week,
      open:        h.is_closed ? null : h.open,
      close:       h.is_closed ? null : h.close,
      is_closed:   h.is_closed,
    })))
  );

  // ── comodidades ──
  const AMENIDADES = [
    'WiFi gratuito', 'Estacionamento próprio', 'Atendimento 24h',
    'Aceita cartão', 'Serviço de entrega', 'Área de espera',
    'Cafeteria', 'Guarda-volumes', 'Acessibilidade',
  ];

  function initAmenidades(): string[] {
    const fromCampos = (form as any)?.campos?.amenidades;
    if (Array.isArray(fromCampos)) return fromCampos;
    if (Array.isArray(filial?.amenities)) return [...filial!.amenities];
    return [];
  }

  let amenidadesSelecionadas = $state<string[]>(initAmenidades());

  function toggleAmenidade(item: string) {
    if (amenidadesSelecionadas.includes(item)) {
      amenidadesSelecionadas = amenidadesSelecionadas.filter(a => a !== item);
    } else {
      amenidadesSelecionadas = [...amenidadesSelecionadas, item];
    }
  }

  let enviando = $state(false);

  // ── endereço reativo (busca por CEP) ──────────────────────────────────────
  let cepVal        = $state(v('cep',        filial?.address?.postal_code));
  let logradouroVal = $state(v('logradouro', filial?.address?.street));
  let bairroVal     = $state(v('bairro',     filial?.address?.neighborhood));
  let cidadeVal     = $state(v('cidade',     filial?.address?.city));
  let estadoVal     = $state(v('estado',     filial?.address?.state));

  let buscandoCep = $state(false);
  let erroCepApi  = $state<string | null>(null);

  async function buscarCep() {
    const limpo = cepVal.replace(/\D/g, '');
    if (limpo.length !== 8) return;
    buscandoCep = true;
    erroCepApi  = null;
    try {
      const res   = await fetch(`https://viacep.com.br/ws/${limpo}/json/`);
      if (!res.ok) throw new Error();
      const dados = await res.json();
      if (dados.erro) { erroCepApi = 'CEP não encontrado.'; return; }
      if (dados.logradouro) logradouroVal = dados.logradouro;
      if (dados.bairro)     bairroVal     = dados.bairro;
      if (dados.localidade) cidadeVal     = dados.localidade;
      if (dados.uf)         estadoVal     = dados.uf;
    } catch {
      erroCepApi = 'Não foi possível buscar o endereço.';
    } finally {
      buscandoCep = false;
    }
  }

  const TIPOS_LOCALIZACAO = [
    { value: 'AIRPORT',       label: 'Aeroporto'          },
    { value: 'TRAIN_STATION', label: 'Estação de Trem'    },
    { value: 'CITY_CENTER',   label: 'Centro da Cidade'   },
    { value: 'HOTEL',         label: 'Hotel'              },
    { value: 'PORT',          label: 'Porto'              },
    { value: 'MALL',          label: 'Shopping'           },
    { value: 'OTHER',         label: 'Outro'              },
  ];

  const METODOS_RETIRADA = [
    { value: 'IN_TERMINAL',    label: 'No Terminal'        },
    { value: 'SHUTTLE',        label: 'Transfer (Shuttle)' },
    { value: 'MEET_AND_GREET', label: 'Meet & Greet'       },
    { value: 'WALK',           label: 'A Pé'               },
    { value: 'DELIVERY',       label: 'Entrega no Local'   },
  ];
</script>

{#if erroGlobal}
  <div class="banner-erro">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
      <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    {erroGlobal}
  </div>
{/if}

<form method="POST" {action}
  use:enhance={() => {
    enviando = true;
    return async ({ update }) => { await update(); enviando = false; };
  }}
>
  <input type="hidden" name="horarios" value={horariosJSON} />

  <!-- ── 1. Identificação ── -->
  <div class="secao">
    <p class="secao-titulo">Identificação</p>
    <div class="grid-3">

      <div class="campo col-span-2">
        <label for="nome">Nome da Filial <span class="obrigatorio">*</span></label>
        <input id="nome" name="nome" type="text" placeholder="Ex.: Filial Aeroporto Guarulhos"
          value={v('nome', filial?.name)} class={erros.nome ? 'erro' : ''} />
        {#if erros.nome}<span class="erro-msg">{erros.nome}</span>{/if}
      </div>

      <div class="campo">
        <label for="codigo">Código <span class="obrigatorio">*</span></label>
        <input id="codigo" name="codigo" type="text" placeholder="Ex.: GRU-01"
          value={v('codigo', filial?.code)} class={erros.codigo ? 'erro' : ''}
          style="text-transform:uppercase" />
        {#if erros.codigo}<span class="erro-msg">{erros.codigo}</span>{/if}
      </div>

      <div class="campo">
        <label for="tipoLocalizacao">Tipo de Localização <span class="obrigatorio">*</span></label>
        <select id="tipoLocalizacao" name="tipoLocalizacao" class={erros.tipoLocalizacao ? 'erro' : ''}>
          <option value="">Selecione...</option>
          {#each TIPOS_LOCALIZACAO as t}
            <option value={t.value} selected={v('tipoLocalizacao', filial?.location_type) === t.value}>{t.label}</option>
          {/each}
        </select>
        {#if erros.tipoLocalizacao}<span class="erro-msg">{erros.tipoLocalizacao}</span>{/if}
      </div>

      <div class="campo col-span-2">
        <label for="metodoRetirada">Método de Retirada do Veículo <span class="obrigatorio">*</span></label>
        <select id="metodoRetirada" name="metodoRetirada" class={erros.metodoRetirada ? 'erro' : ''}>
          <option value="">Selecione...</option>
          {#each METODOS_RETIRADA as m}
            <option value={m.value} selected={v('metodoRetirada', filial?.pickup_method) === m.value}>{m.label}</option>
          {/each}
        </select>
        {#if erros.metodoRetirada}<span class="erro-msg">{erros.metodoRetirada}</span>{/if}
      </div>

    </div>
  </div>

  <!-- ── 2. Endereço ── -->
  <div class="secao">
    <p class="secao-titulo">Endereço</p>
    <div class="grid-4">

      <div class="campo">
        <label for="cep">CEP <span class="obrigatorio">*</span></label>
        <input id="cep" name="cep" type="text" placeholder="00000-000" maxlength="9"
          bind:value={cepVal} oninput={buscarCep}
          class={erros.cep ? 'erro' : ''} />
        {#if buscandoCep}
          <span class="cep-hint">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="animation:spin 0.8s linear infinite">
              <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.3" stroke-dasharray="16 8"/>
            </svg>
            Buscando endereço...
          </span>
        {:else if erroCepApi}
          <span class="erro-msg">{erroCepApi}</span>
        {:else if erros.cep}
          <span class="erro-msg">{erros.cep}</span>
        {/if}
      </div>

      <div class="campo col-span-3">
        <label for="logradouro">Logradouro <span class="obrigatorio">*</span></label>
        <input id="logradouro" name="logradouro" type="text" placeholder="Rua, Avenida, Rodovia..."
          bind:value={logradouroVal} class={erros.logradouro ? 'erro' : ''} />
        {#if erros.logradouro}<span class="erro-msg">{erros.logradouro}</span>{/if}
      </div>

      <div class="campo">
        <label for="numero">Número <span class="obrigatorio">*</span></label>
        <input id="numero" name="numero" type="text" placeholder="123"
          value={v('numero', filial?.address.number)} class={erros.numero ? 'erro' : ''} />
        {#if erros.numero}<span class="erro-msg">{erros.numero}</span>{/if}
      </div>

      <div class="campo">
        <label for="complemento">Complemento</label>
        <input id="complemento" name="complemento" type="text" placeholder="Sala, Terminal..."
          value={v('complemento', filial?.address.complement)} />
      </div>

      <div class="campo col-span-2">
        <label for="bairro">Bairro <span class="obrigatorio">*</span></label>
        <input id="bairro" name="bairro" type="text" placeholder="Nome do bairro"
          bind:value={bairroVal} class={erros.bairro ? 'erro' : ''} />
        {#if erros.bairro}<span class="erro-msg">{erros.bairro}</span>{/if}
      </div>

      <div class="campo col-span-3">
        <label for="cidade">Cidade <span class="obrigatorio">*</span></label>
        <input id="cidade" name="cidade" type="text" placeholder="Nome da cidade"
          bind:value={cidadeVal} class={erros.cidade ? 'erro' : ''} />
        {#if erros.cidade}<span class="erro-msg">{erros.cidade}</span>{/if}
      </div>

      <div class="campo">
        <label for="estado">Estado <span class="obrigatorio">*</span></label>
        <select id="estado" name="estado" bind:value={estadoVal} class={erros.estado ? 'erro' : ''}>
          <option value="">UF</option>
          {#each ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'] as uf}
            <option value={uf}>{uf}</option>
          {/each}
        </select>
        {#if erros.estado}<span class="erro-msg">{erros.estado}</span>{/if}
      </div>

    </div>
  </div>

  <!-- ── 3. Contato ── -->
  <div class="secao">
    <p class="secao-titulo">Contato</p>
    <div class="grid-3">

      <div class="campo">
        <label for="telefone">Telefone <span class="obrigatorio">*</span></label>
        <input id="telefone" name="telefone" type="tel" placeholder="(11) 99999-9999"
          value={v('telefone', filial?.contact.phone)} class={erros.telefone ? 'erro' : ''} />
        {#if erros.telefone}<span class="erro-msg">{erros.telefone}</span>{/if}
      </div>

      <div class="campo">
        <label for="email">E-mail <span class="obrigatorio">*</span></label>
        <input id="email" name="email" type="email" placeholder="filial@empresa.com.br"
          value={v('email', filial?.contact.email)} class={erros.email ? 'erro' : ''} />
        {#if erros.email}<span class="erro-msg">{erros.email}</span>{/if}
      </div>

      <div class="campo">
        <label for="gerente">Nome do Gerente</label>
        <input id="gerente" name="gerente" type="text" placeholder="Nome completo"
          value={v('gerente', filial?.contact.manager_name)} />
      </div>

    </div>
  </div>

  <!-- ── 4. Localização Geográfica ── -->
  <div class="secao">
    <p class="secao-titulo">Localização Geográfica</p>
    <div class="grid-2">

      <div class="campo">
        <label for="latitude">Latitude <span class="obrigatorio">*</span></label>
        <input id="latitude" name="latitude" type="number" placeholder="-23.4322"
          step="any" min="-90" max="90"
          value={v('latitudeRaw', filial?.location?.latitude?.toString())}
          class={erros.latitude ? 'erro' : ''} />
        {#if erros.latitude}<span class="erro-msg">{erros.latitude}</span>{/if}
      </div>

      <div class="campo">
        <label for="longitude">Longitude <span class="obrigatorio">*</span></label>
        <input id="longitude" name="longitude" type="number" placeholder="-46.9297"
          step="any" min="-180" max="180"
          value={v('longitudeRaw', filial?.location?.longitude?.toString())}
          class={erros.longitude ? 'erro' : ''} />
        {#if erros.longitude}<span class="erro-msg">{erros.longitude}</span>{/if}
      </div>

    </div>
  </div>

  <!-- ── 5. Horários de Funcionamento ── -->
  <div class="secao">
    <p class="secao-titulo">Horários de Funcionamento</p>
    <div class="horarios-grid">
      {#each horarios as h}
        <div class="horario-row">
          <span class="horario-dia">{h.label}</span>
          <input type="time" value={h.open} disabled={h.is_closed}
            oninput={(e) => { h.open = (e.currentTarget as HTMLInputElement).value; }} />
          <input type="time" value={h.close} disabled={h.is_closed}
            oninput={(e) => { h.close = (e.currentTarget as HTMLInputElement).value; }} />
          <label class="toggle-fechado">
            <input type="checkbox" checked={h.is_closed}
              onchange={() => { h.is_closed = !h.is_closed; }} />
            Fechado
          </label>
        </div>
      {/each}
    </div>
  </div>

  <!-- ── 6. Comodidades ── -->
  <div class="secao">
    <p class="secao-titulo">Comodidades</p>
    <div class="amenidades-grid">
      {#each AMENIDADES as item}
        {@const sel = amenidadesSelecionadas.includes(item)}
        <label class="amenidade-item {sel ? 'selecionada' : ''}">
          <input type="checkbox" name="amenidades" value={item}
            checked={sel} onchange={() => toggleAmenidade(item)} />
          <span>{item}</span>
        </label>
      {/each}
    </div>
  </div>

  <!-- ── 7. Instruções ao Cliente ── -->
  <div class="secao">
    <p class="secao-titulo">Instruções ao Cliente</p>
    <div class="grid-3">

      <div class="campo">
        <label for="instrRetirada">Retirada do Veículo</label>
        <textarea id="instrRetirada" name="instrRetirada"
          placeholder="Como o cliente deve proceder para retirar o veículo..."
        >{v('instrRetirada', filial?.instructions.pickup)}</textarea>
      </div>

      <div class="campo">
        <label for="instrDevolucao">Devolução do Veículo</label>
        <textarea id="instrDevolucao" name="instrDevolucao"
          placeholder="Como o cliente deve proceder para devolver o veículo..."
        >{v('instrDevolucao', filial?.instructions.dropoff)}</textarea>
      </div>

      <div class="campo">
        <label for="instrExtra">Informações Extras</label>
        <textarea id="instrExtra" name="instrExtra"
          placeholder="Outras informações relevantes para o cliente..."
        >{v('instrExtra', filial?.instructions.extra)}</textarea>
      </div>

    </div>
  </div>

  <!-- ── Ações ── -->
  <div class="acoes">
    <a href={cancelarHref} class="btn-cancelar">Cancelar</a>
    <button type="submit" class="btn-salvar" disabled={enviando}>
      {#if enviando}
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="animation:spin 0.8s linear infinite">
          <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" stroke-width="1.5" stroke-dasharray="20 12"/>
        </svg>
        Salvando...
      {:else}
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M2 7l3.5 3.5 5.5-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {acaoLabel}
      {/if}
    </button>
  </div>

</form>

<style>
  /* ── seções ── */
  .secao {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .secao-titulo {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    margin: 0 0 20px;
  }

  /* ── grids ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
  .col-span-2 { grid-column: span 2; }
  .col-span-3 { grid-column: span 3; }

  /* ── campo ── */
  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo label { font-size: 12px; font-weight: 500; color: #94a3b8; }
  .campo label .obrigatorio { color: #f87171; margin-left: 2px; }

  .campo input,
  .campo select,
  .campo textarea {
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    padding: 9px 12px;
    transition: border-color 0.14s, box-shadow 0.14s;
    outline: none;
    width: 100%;
    box-sizing: border-box;
  }
  .campo input::placeholder,
  .campo textarea::placeholder { color: #334155; }
  .campo input:focus,
  .campo select:focus,
  .campo textarea:focus {
    border-color: rgba(96,165,250,0.5);
    box-shadow: 0 0 0 3px rgba(96,165,250,0.08);
  }
  .campo select option { background: #0f172a; }
  .campo textarea { resize: vertical; min-height: 72px; }

  .campo .erro-msg { font-size: 11px; color: #f87171; }
  .campo input.erro,
  .campo select.erro,
  .campo textarea.erro { border-color: rgba(248,113,113,0.5); }

  /* ── horários ── */
  .horarios-grid { display: flex; flex-direction: column; gap: 8px; }
  .horario-row {
    display: grid;
    grid-template-columns: 140px 1fr 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
  }
  .horario-dia { font-size: 13px; font-weight: 500; color: #94a3b8; }
  .horario-row input[type="time"] {
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 6px;
    color: #e2e8f0;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    padding: 6px 10px;
    outline: none;
    width: 100%;
    box-sizing: border-box;
    color-scheme: dark;
  }
  .horario-row input[type="time"]:focus { border-color: rgba(96,165,250,0.5); }
  .horario-row input[type="time"]:disabled { opacity: 0.3; cursor: not-allowed; }
  .toggle-fechado {
    display: flex; align-items: center; gap: 6px;
    font-size: 12px; color: #64748b; cursor: pointer; white-space: nowrap;
  }
  .toggle-fechado input[type="checkbox"] { width: 14px; height: 14px; accent-color: #f87171; }

  /* ── comodidades ── */
  .amenidades-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .amenidade-item {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    cursor: pointer;
    transition: border-color 0.14s;
  }
  .amenidade-item:hover { border-color: rgba(255,255,255,0.12); }
  .amenidade-item.selecionada {
    border-color: rgba(96,165,250,0.4);
    background: rgba(96,165,250,0.05);
  }
  .amenidade-item input[type="checkbox"] { width: 14px; height: 14px; accent-color: #60a5fa; flex-shrink: 0; }
  .amenidade-item span { font-size: 13px; color: #94a3b8; }

  /* ── ações ── */
  .acoes {
    display: flex; align-items: center; justify-content: flex-end;
    gap: 12px; margin-top: 8px; padding-bottom: 40px;
  }
  .btn-cancelar {
    padding: 9px 18px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: transparent; color: #64748b;
    font-size: 13px; font-family: 'DM Sans', sans-serif;
    cursor: pointer; text-decoration: none;
    display: inline-flex; align-items: center;
    transition: border-color 0.14s, color 0.14s;
  }
  .btn-cancelar:hover { border-color: rgba(255,255,255,0.2); color: #94a3b8; }

  .btn-salvar {
    padding: 9px 22px; border-radius: 8px; border: none;
    background: #3b82f6; color: #fff;
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
    transition: background 0.14s, opacity 0.14s;
  }
  .btn-salvar:hover { background: #2563eb; }
  .btn-salvar:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── banner de erro global ── */
  .banner-erro {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.2);
    background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }

  .cep-hint {
    font-size: 11px; color: #60a5fa;
    display: flex; align-items: center; gap: 4px;
    margin-top: 2px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
