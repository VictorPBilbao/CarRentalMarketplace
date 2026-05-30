<script lang="ts">
  import { enhance } from '$app/forms';
  import type { Categoria } from '$lib/services/categoria.service';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  interface Props {
    form?:        Record<string, any> | null;
    categoria?:   Categoria | null;
    action:       string;
    acaoLabel:    string;
    cancelarHref?: string;
  }

  let {
    form        = null,
    categoria   = null,
    action,
    acaoLabel,
    cancelarHref = '/locadora/categorias',
  }: Props = $props();

  const erros      = $derived((form as any)?.erros  ?? {});
  const erroGlobal = $derived((form as any)?.erro   ?? null);
  const campos     = $derived((form as any)?.campos ?? {});

  function v(key: string, fallback?: string | null): string {
    return campos[key] ?? fallback ?? '';
  }

  function vn(key: string, fallback: number): number {
    const raw = campos[key] ?? fallback;
    return typeof raw === 'number' ? raw : (parseInt(String(raw), 10) || fallback);
  }

  // ── ar condicionado ──────────────────────────────────────────────────────────
  function initAirConditioning(): boolean {
    const raw = (form as any)?.campos?.airConditioning;
    if (raw !== undefined) return raw === 'true';
    return categoria?.features?.air_conditioning ?? true;
  }

  let arVal = $state(initAirConditioning());

  // ── modelos representativos ──────────────────────────────────────────────────
  function initModelos(): string[] {
    const raw = (form as any)?.campos?.modelosRaw;
    if (raw) { try { return JSON.parse(raw); } catch { /* fallthrough */ } }
    if (Array.isArray(categoria?.representative_models)) return [...categoria!.representative_models];
    return [];
  }

  let modelos      = $state<string[]>(initModelos());
  let novoModelo   = $state('');
  const modelosJSON = $derived(JSON.stringify(modelos));

  function adicionarModelo() {
    const m = novoModelo.trim();
    if (m && !modelos.includes(m)) modelos = [...modelos, m];
    novoModelo = '';
  }

  function removerModelo(i: number) {
    modelos = modelos.filter((_, idx) => idx !== i);
  }

  let enviando = $state(false);

  $effect(() => { const m = erroGlobal; if (m) notificacoes.erro(m); });

  const COMBUSTIVEIS = [
    { value: 'FLEX',     label: 'Flex'      },
    { value: 'GASOLINE', label: 'Gasolina'  },
    { value: 'DIESEL',   label: 'Diesel'    },
    { value: 'ELECTRIC', label: 'Elétrico'  },
    { value: 'HYBRID',   label: 'Híbrido'   },
  ];

  const TRANSMISSOES = [
    { value: 'AUTOMATIC', label: 'Automático' },
    { value: 'MANUAL',    label: 'Manual'     },
  ];

  // ── ACRISS ──────────────────────────────────────────────────────────────────
  const ACRISS_CAT: { value: string; label: string }[] = [
    { value: 'M', label: 'M — Mini' },
    { value: 'E', label: 'E — Economy' },
    { value: 'C', label: 'C — Compact' },
    { value: 'I', label: 'I — Intermediário' },
    { value: 'S', label: 'S — Standard' },
    { value: 'F', label: 'F — Full-size' },
    { value: 'P', label: 'P — Premium' },
    { value: 'L', label: 'L — Luxo' },
    { value: 'X', label: 'X — Especial' },
    { value: 'J', label: 'J — SUV' },
    { value: 'K', label: 'K — Pickup / Caminhonete' },
    { value: 'V', label: 'V — Van / Minivan' },
    { value: 'W', label: 'W — Perua / Station Wagon' },
  ];

  const ACRISS_TIPO: { value: string; label: string }[] = [
    { value: 'B', label: 'B — 2-3 Portas' },
    { value: 'C', label: 'C — 2/4 Portas' },
    { value: 'D', label: 'D — 4-5 Portas' },
    { value: 'W', label: 'W — Perua / Estate' },
    { value: 'V', label: 'V — Van de Passageiros' },
    { value: 'L', label: 'L — Limusine' },
    { value: 'S', label: 'S — Esportivo' },
    { value: 'T', label: 'T — Conversível' },
    { value: 'F', label: 'F — SUV / 4×4 Aberto' },
    { value: 'J', label: 'J — Aberto (Jipe)' },
    { value: 'X', label: 'X — Especial' },
    { value: 'P', label: 'P — Pickup Cabine Simples' },
    { value: 'Q', label: 'Q — Pickup 4×4' },
    { value: 'Z', label: 'Z — Especial 4×4' },
    { value: 'M', label: 'M — Monovolume' },
    { value: 'E', label: 'E — Cupê' },
    { value: 'H', label: 'H — Motorhome / Trailer' },
    { value: 'Y', label: 'Y — Pickup Cab. Regular' },
  ];

  const ACRISS_TRANS: { value: string; label: string }[] = [
    { value: 'M', label: 'M — Manual' },
    { value: 'N', label: 'N — Manual 4×4' },
    { value: 'C', label: 'C — Manual AWD' },
    { value: 'A', label: 'A — Automático' },
    { value: 'B', label: 'B — Automático 4×4' },
    { value: 'D', label: 'D — Automático AWD' },
  ];

  const ACRISS_COMB: { value: string; label: string }[] = [
    { value: 'R', label: 'R — Indefinido / Ar' },
    { value: 'N', label: 'N — Indefinido / Sem Ar' },
    { value: 'D', label: 'D — Diesel / Ar' },
    { value: 'Q', label: 'Q — Diesel / Sem Ar' },
    { value: 'H', label: 'H — Híbrido / Ar' },
    { value: 'I', label: 'I — Híbrido / Sem Ar' },
    { value: 'E', label: 'E — Elétrico / Ar' },
    { value: 'C', label: 'C — Elétrico / Sem Ar' },
    { value: 'L', label: 'L — GLP / Ar' },
    { value: 'S', label: 'S — GLP / Sem Ar' },
    { value: 'M', label: 'M — Etanol / Ar' },
    { value: 'F', label: 'F — Etanol / Sem Ar' },
    { value: 'A', label: 'A — Hidrogênio / Ar' },
    { value: 'B', label: 'B — Hidrogênio / Sem Ar' },
  ];

  const _acrissInit = ((form as any)?.campos?.acrissCode ?? categoria?.acriss_code ?? '') as string;
  let acrissP1 = $state(_acrissInit[0] ?? '');
  let acrissP2 = $state(_acrissInit[1] ?? '');
  let acrissP3 = $state(_acrissInit[2] ?? '');
  let acrissP4 = $state(_acrissInit[3] ?? '');
  const acrissCode = $derived(
    acrissP1 && acrissP2 && acrissP3 && acrissP4
      ? `${acrissP1}${acrissP2}${acrissP3}${acrissP4}`
      : ''
  );
</script>

<form method="POST" {action}
  use:enhance={() => {
    enviando = true;
    return async ({ update }) => { await update(); enviando = false; };
  }}
>
  <input type="hidden" name="modelos"          value={modelosJSON} />
  <input type="hidden" name="airConditioning"  value={arVal.toString()} />

  <!-- ── 1. Identificação ── -->
  <div class="secao">
    <p class="secao-titulo">Identificação</p>
    <div class="grid-4">

      <div class="campo col-span-3">
        <label for="groupName">Nome do Grupo <span class="obrigatorio">*</span></label>
        <input id="groupName" name="groupName" type="text"
          placeholder="Ex.: Econômico, SUV, Luxo"
          value={v('groupName', categoria?.group_name)}
          class={erros.groupName ? 'erro' : ''} />
        {#if erros.groupName}<span class="erro-msg">{erros.groupName}</span>{/if}
      </div>

      <div class="campo">
        <label for="code">Código <span class="obrigatorio">*</span></label>
        <input id="code" name="code" type="text"
          placeholder="Ex.: ECONOMY"
          value={v('code', categoria?.code)}
          class={erros.code ? 'erro' : ''}
          style="text-transform:uppercase" />
        {#if erros.code}<span class="erro-msg">{erros.code}</span>{/if}
      </div>

      <div class="campo col-span-4">
        <label>
          Código ACRISS
          <span class="campo-hint">4 posições — padrão internacional (opcional)</span>
        </label>
        <input type="hidden" name="acrissCode" value={acrissCode} />
        <div class="acriss-builder">
          <div class="acriss-selects">
            <div class="acriss-pos">
              <span class="acriss-pos-label">1 — Categoria</span>
              <select bind:value={acrissP1}>
                <option value="">—</option>
                {#each ACRISS_CAT as o}<option value={o.value}>{o.label}</option>{/each}
              </select>
            </div>
            <div class="acriss-pos">
              <span class="acriss-pos-label">2 — Carroceria</span>
              <select bind:value={acrissP2}>
                <option value="">—</option>
                {#each ACRISS_TIPO as o}<option value={o.value}>{o.label}</option>{/each}
              </select>
            </div>
            <div class="acriss-pos">
              <span class="acriss-pos-label">3 — Câmbio / Tração</span>
              <select bind:value={acrissP3}>
                <option value="">—</option>
                {#each ACRISS_TRANS as o}<option value={o.value}>{o.label}</option>{/each}
              </select>
            </div>
            <div class="acriss-pos">
              <span class="acriss-pos-label">4 — Combustível / Ar</span>
              <select bind:value={acrissP4}>
                <option value="">—</option>
                {#each ACRISS_COMB as o}<option value={o.value}>{o.label}</option>{/each}
              </select>
            </div>
          </div>
          <div class="acriss-preview {acrissCode ? 'acriss-ready' : ''}">
            <span class="acriss-char {acrissP1 ? 'acriss-set' : ''}">{acrissP1 || '?'}</span>
            <span class="acriss-char {acrissP2 ? 'acriss-set' : ''}">{acrissP2 || '?'}</span>
            <span class="acriss-char {acrissP3 ? 'acriss-set' : ''}">{acrissP3 || '?'}</span>
            <span class="acriss-char {acrissP4 ? 'acriss-set' : ''}">{acrissP4 || '?'}</span>
          </div>
        </div>
        {#if erros.acrissCode}<span class="erro-msg">{erros.acrissCode}</span>{/if}
      </div>

      <div class="campo col-span-4">
        <label for="description">Descrição</label>
        <textarea id="description" name="description"
          placeholder="Descreva as características gerais desta categoria..."
        >{v('description', categoria?.description)}</textarea>
      </div>

    </div>
  </div>

  <!-- ── 2. Características ── -->
  <div class="secao">
    <p class="secao-titulo">Características do Veículo</p>
    <div class="grid-4">

      <div class="campo">
        <label for="fuelType">Combustível <span class="obrigatorio">*</span></label>
        <select id="fuelType" name="fuelType" class={erros.fuelType ? 'erro' : ''}>
          <option value="">Selecione...</option>
          {#each COMBUSTIVEIS as c}
            <option value={c.value} selected={v('fuelType', categoria?.features?.fuel_type) === c.value}>{c.label}</option>
          {/each}
        </select>
        {#if erros.fuelType}<span class="erro-msg">{erros.fuelType}</span>{/if}
      </div>

      <div class="campo">
        <label for="transmission">Câmbio <span class="obrigatorio">*</span></label>
        <select id="transmission" name="transmission" class={erros.transmission ? 'erro' : ''}>
          <option value="">Selecione...</option>
          {#each TRANSMISSOES as t}
            <option value={t.value} selected={v('transmission', categoria?.features?.transmission) === t.value}>{t.label}</option>
          {/each}
        </select>
        {#if erros.transmission}<span class="erro-msg">{erros.transmission}</span>{/if}
      </div>

      <div class="campo">
        <label for="doors">Portas <span class="obrigatorio">*</span></label>
        <input id="doors" name="doors" type="number" min="2" max="6"
          value={vn('doors', categoria?.features?.doors ?? 4)}
          class={erros.doors ? 'erro' : ''} />
        {#if erros.doors}<span class="erro-msg">{erros.doors}</span>{/if}
      </div>

      <div class="campo">
        <label>Ar-condicionado</label>
        <button type="button" class="toggle {arVal ? 'toggle-on' : ''}"
          onclick={() => arVal = !arVal}>
          <span class="toggle-thumb"></span>
          <span class="toggle-label">{arVal ? 'Incluído' : 'Não incluso'}</span>
        </button>
      </div>

    </div>
  </div>

  <!-- ── 3. Capacidade ── -->
  <div class="secao">
    <p class="secao-titulo">Capacidade</p>
    <div class="grid-3">

      <div class="campo">
        <label for="passengers">Passageiros <span class="obrigatorio">*</span></label>
        <div class="input-icon-wrap">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="input-icon">
            <circle cx="7" cy="5" r="2.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M2 12c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          <input id="passengers" name="passengers" type="number" min="1" max="20"
            value={vn('passengers', categoria?.features?.capacity?.passengers ?? 5)}
            class={erros.passengers ? 'erro' : ''} />
        </div>
        {#if erros.passengers}<span class="erro-msg">{erros.passengers}</span>{/if}
      </div>

      <div class="campo">
        <label for="smallSuitcases">Malas Pequenas</label>
        <div class="input-icon-wrap">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="input-icon">
            <rect x="2" y="4" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.2"/>
            <path d="M5 4V3a1 1 0 011-1h2a1 1 0 011 1v1" stroke="currentColor" stroke-width="1.2"/>
          </svg>
          <input id="smallSuitcases" name="smallSuitcases" type="number" min="0" max="10"
            value={vn('smallSuitcases', categoria?.features?.capacity?.small_suitcases ?? 0)} />
        </div>
      </div>

      <div class="campo">
        <label for="largeSuitcases">Malas Grandes</label>
        <div class="input-icon-wrap">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="input-icon">
            <rect x="1.5" y="3.5" width="11" height="9" rx="1" stroke="currentColor" stroke-width="1.2"/>
            <path d="M5 3.5V2.5A1 1 0 016 1.5h2a1 1 0 011 1v1" stroke="currentColor" stroke-width="1.2"/>
          </svg>
          <input id="largeSuitcases" name="largeSuitcases" type="number" min="0" max="10"
            value={vn('largeSuitcases', categoria?.features?.capacity?.large_suitcases ?? 0)} />
        </div>
      </div>

    </div>
  </div>

  <!-- ── 4. Modelos Representativos ── -->
  <div class="secao">
    <p class="secao-titulo">Modelos Representativos</p>
    <p class="secao-desc">Exemplos de carros que se encaixam nesta categoria. Exibido ao cliente no momento da reserva.</p>

    <div class="modelos-input-row">
      <input type="text" placeholder="Ex.: Chevrolet Onix, Volkswagen Polo..."
        bind:value={novoModelo}
        onkeydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); adicionarModelo(); } }} />
      <button type="button" class="btn-add" onclick={adicionarModelo}>
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Adicionar
      </button>
    </div>

    {#if modelos.length > 0}
      <div class="modelos-chips">
        {#each modelos as m, i}
          <span class="chip">
            {m}
            <button type="button" onclick={() => removerModelo(i)} aria-label="Remover {m}">
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <path d="M2 2l6 6M8 2l-6 6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </button>
          </span>
        {/each}
      </div>
    {:else}
      <p class="modelos-vazio">Nenhum modelo adicionado ainda.</p>
    {/if}
  </div>

  <!-- ── 5. Imagem ── -->
  <div class="secao">
    <p class="secao-titulo">Imagem da Categoria</p>
    <div class="grid-1">
      <div class="campo">
        <label for="imageUrl">URL da Imagem <span class="campo-hint">opcional</span></label>
        <input id="imageUrl" name="imageUrl" type="url"
          placeholder="https://..."
          value={v('imageUrl', categoria?.image_url)}
          class={erros.imageUrl ? 'erro' : ''} />
        {#if erros.imageUrl}<span class="erro-msg">{erros.imageUrl}</span>{/if}
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
  .secao {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .secao-titulo {
    font-size: 12px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #475569; margin: 0 0 20px;
  }
  .secao-desc {
    font-size: 12px; color: #334155; margin: -12px 0 16px;
  }

  .grid-1 { display: grid; grid-template-columns: 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
  .col-span-2 { grid-column: span 2; }
  .col-span-3 { grid-column: span 3; }
  .col-span-4 { grid-column: span 4; }

  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo label { font-size: 12px; font-weight: 500; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
  .campo label .obrigatorio { color: #f87171; }
  .campo-hint { font-size: 11px; color: #334155; font-weight: 400; }

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
  .campo input::placeholder, .campo textarea::placeholder { color: #334155; }
  .campo input:focus, .campo select:focus, .campo textarea:focus {
    border-color: rgba(96,165,250,0.5);
    box-shadow: 0 0 0 3px rgba(96,165,250,0.08);
  }
  .campo select option { background: #0f172a; }
  .campo textarea { resize: vertical; min-height: 72px; }
  .campo input.erro, .campo select.erro { border-color: rgba(248,113,113,0.5); }
  .campo .erro-msg { font-size: 11px; color: #f87171; }

  /* ── input com ícone ── */
  .input-icon-wrap { position: relative; }
  .input-icon {
    position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
    color: #334155; pointer-events: none;
  }
  .input-icon-wrap input { padding-left: 32px; }

  /* ── toggle ar-condicionado ── */
  .toggle {
    display: inline-flex; align-items: center; gap: 10px;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    transition: border-color 0.14s;
    font-family: 'DM Sans', sans-serif;
    width: 100%;
  }
  .toggle:hover { border-color: rgba(255,255,255,0.18); }
  .toggle-on { border-color: rgba(96,165,250,0.4); background: rgba(96,165,250,0.06); }
  .toggle-thumb {
    width: 28px; height: 16px; border-radius: 8px;
    background: #1e293b;
    position: relative; flex-shrink: 0;
    transition: background 0.14s;
  }
  .toggle-thumb::after {
    content: '';
    position: absolute; top: 2px; left: 2px;
    width: 12px; height: 12px; border-radius: 50%;
    background: #475569;
    transition: left 0.14s, background 0.14s;
  }
  .toggle-on .toggle-thumb { background: rgba(96,165,250,0.25); }
  .toggle-on .toggle-thumb::after { left: 14px; background: #60a5fa; }
  .toggle-label { font-size: 13px; color: #64748b; }
  .toggle-on .toggle-label { color: #93c5fd; }

  /* ── modelos tag input ── */
  .modelos-input-row {
    display: flex; gap: 10px; margin-bottom: 14px;
  }
  .modelos-input-row input {
    flex: 1;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    color: #e2e8f0; font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    padding: 9px 12px; outline: none;
    transition: border-color 0.14s;
  }
  .modelos-input-row input:focus { border-color: rgba(96,165,250,0.4); }
  .modelos-input-row input::placeholder { color: #334155; }
  .btn-add {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 9px 16px; border-radius: 8px;
    border: 1px solid rgba(96,165,250,0.3);
    background: rgba(96,165,250,0.08); color: #60a5fa;
    font-size: 13px; font-family: 'DM Sans', sans-serif;
    cursor: pointer; white-space: nowrap;
    transition: border-color 0.14s, background 0.14s;
  }
  .btn-add:hover { border-color: rgba(96,165,250,0.5); background: rgba(96,165,250,0.12); }

  .modelos-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 10px; border-radius: 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    font-size: 12px; color: #94a3b8;
  }
  .chip button {
    display: flex; align-items: center;
    background: none; border: none;
    color: #475569; cursor: pointer; padding: 0;
    transition: color 0.12s;
  }
  .chip button:hover { color: #f87171; }
  .modelos-vazio { font-size: 12px; color: #334155; }

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

  /* ── ACRISS builder ── */
  .acriss-builder {
    display: flex;
    align-items: flex-end;
    gap: 16px;
  }
  .acriss-selects {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .acriss-pos {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  .acriss-pos-label {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .acriss-pos select {
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    padding: 8px 10px;
    outline: none;
    width: 100%;
    box-sizing: border-box;
    transition: border-color 0.14s;
    cursor: pointer;
  }
  .acriss-pos select:focus { border-color: rgba(96,165,250,0.5); }
  .acriss-pos select option { background: #0f172a; }
  .acriss-preview {
    display: flex;
    gap: 1px;
    padding: 8px 16px;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    align-items: center;
    flex-shrink: 0;
    transition: border-color 0.2s, background 0.2s;
  }
  .acriss-ready {
    border-color: rgba(52,211,153,0.35);
    background: rgba(52,211,153,0.04);
  }
  .acriss-char {
    font-size: 24px;
    font-weight: 700;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    color: #1e293b;
    width: 26px;
    text-align: center;
    transition: color 0.14s;
    line-height: 1;
  }
  .acriss-set { color: #34d399; }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
