<script lang="ts">
  import { enhance } from '$app/forms';
  import type { Veiculo, StatusVeiculo } from '$lib/services/veiculo.service';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  interface LojaOpcao {
    id:   string;
    name: string;
    code: string;
  }

  interface CategoriaOpcao {
    id:         string;
    group_name: string;
    code:       string;
  }

  interface Props {
    form?:         Record<string, any> | null;
    veiculo?:      Veiculo | null;
    action:        string;
    acaoLabel:     string;
    cancelarHref?: string;
    lojas:         LojaOpcao[];
    categorias:    CategoriaOpcao[];
    lojaFixaId?:   string | null;
    lojaFixaNome?: string | null;
  }

  let {
    form        = null,
    veiculo     = null,
    action,
    acaoLabel,
    cancelarHref = '/locadora/frota',
    lojas,
    categorias,
    lojaFixaId  = null,
    lojaFixaNome = null,
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

  let enviando = $state(false);

  $effect(() => { const m = erroGlobal; if (m) notificacoes.erro(m); });

  const STATUS_OPTIONS: { value: StatusVeiculo; label: string }[] = [
    { value: 'AVAILABLE',      label: 'Disponível'  },
    { value: 'RENTED',         label: 'Alugado'     },
    { value: 'MAINTENANCE',    label: 'Manutenção'  },
    { value: 'IN_TRANSIT',     label: 'Em trânsito' },
    { value: 'DECOMMISSIONED', label: 'Desativado'  },
  ];

  const currentStoreId = $derived(lojaFixaId ?? v('currentStore', veiculo?.current_store));
</script>

<form method="POST" {action}
  use:enhance={() => {
    enviando = true;
    return async ({ update }) => { await update(); enviando = false; };
  }}
>
  {#if lojaFixaId}
    <input type="hidden" name="currentStore" value={lojaFixaId} />
  {/if}

  <!-- ── 1. Informações do Veículo ── -->
  <div class="secao">
    <p class="secao-titulo">Informações do Veículo</p>
    <div class="grid-4">

      <div class="campo col-span-2">
        <label for="make">Marca <span class="obrigatorio">*</span></label>
        <input id="make" name="make" type="text"
          placeholder="Ex.: Chevrolet, Volkswagen, Toyota"
          value={v('make', veiculo?.make)}
          class={erros.make ? 'erro' : ''} />
        {#if erros.make}<span class="erro-msg">{erros.make}</span>{/if}
      </div>

      <div class="campo col-span-2">
        <label for="model">Modelo <span class="obrigatorio">*</span></label>
        <input id="model" name="model" type="text"
          placeholder="Ex.: Onix, Polo, Corolla"
          value={v('model', veiculo?.model)}
          class={erros.model ? 'erro' : ''} />
        {#if erros.model}<span class="erro-msg">{erros.model}</span>{/if}
      </div>

      <div class="campo">
        <label for="year">Ano <span class="obrigatorio">*</span></label>
        <input id="year" name="year" type="number" min="2000" max="2030"
          value={vn('year', veiculo?.year ?? new Date().getFullYear())}
          class={erros.year ? 'erro' : ''} />
        {#if erros.year}<span class="erro-msg">{erros.year}</span>{/if}
      </div>

      <div class="campo">
        <label for="color">Cor <span class="obrigatorio">*</span></label>
        <input id="color" name="color" type="text"
          placeholder="Ex.: Prata, Preto, Branco"
          value={v('color', veiculo?.color)}
          class={erros.color ? 'erro' : ''} />
        {#if erros.color}<span class="erro-msg">{erros.color}</span>{/if}
      </div>

      <div class="campo col-span-2">
        <label for="mileageKm">Quilometragem <span class="obrigatorio">*</span></label>
        <div class="input-suffix-wrap">
          <input id="mileageKm" name="mileageKm" type="number" min="0"
            value={vn('mileageKm', veiculo?.mileage_km ?? 0)}
            class={erros.mileageKm ? 'erro' : ''} />
          <span class="input-suffix">km</span>
        </div>
        {#if erros.mileageKm}<span class="erro-msg">{erros.mileageKm}</span>{/if}
      </div>

    </div>
  </div>

  <!-- ── 2. Identificação Legal ── -->
  <div class="secao">
    <p class="secao-titulo">Identificação Legal</p>
    <div class="grid-2">

      <div class="campo">
        <label for="plate">Placa <span class="obrigatorio">*</span></label>
        <input id="plate" name="plate" type="text"
          placeholder="Ex.: ABC1234 ou ABC1D23"
          maxlength="8"
          value={v('plate', veiculo?.plate)}
          class={erros.plate ? 'erro' : ''}
          style="text-transform:uppercase" />
        {#if erros.plate}<span class="erro-msg">{erros.plate}</span>{/if}
      </div>

      <div class="campo">
        <label for="chassisNumber">
          Chassi <span class="obrigatorio">*</span>
          <span class="campo-hint">17 caracteres</span>
        </label>
        <input id="chassisNumber" name="chassisNumber" type="text"
          placeholder="Ex.: 9BWZZZ377VT004251"
          maxlength="17"
          value={v('chassisNumber', veiculo?.chassis_number)}
          class={erros.chassisNumber ? 'erro' : ''}
          style="text-transform:uppercase; font-family: monospace; letter-spacing: 0.05em;" />
        {#if erros.chassisNumber}<span class="erro-msg">{erros.chassisNumber}</span>{/if}
      </div>

    </div>
  </div>

  <!-- ── 3. Classificação ── -->
  <div class="secao">
    <p class="secao-titulo">Classificação</p>
    <div class="grid-2">

      <div class="campo">
        <label for="categoryId">Categoria <span class="obrigatorio">*</span></label>
        <select id="categoryId" name="category" class={erros.category ? 'erro' : ''}>
          <option value="">Selecione uma categoria...</option>
          {#each categorias as cat}
            <option value={cat.id}
              selected={v('category', veiculo?.category) === cat.id}>
              {cat.group_name} — {cat.code}
            </option>
          {/each}
        </select>
        {#if erros.category}<span class="erro-msg">{erros.category}</span>{/if}
      </div>

      {#if lojaFixaId}
        <div class="campo">
          <label>Loja <span class="campo-hint">fixada pelo perfil</span></label>
          <div class="campo-fixo">
            <svg width="14" height="14" viewBox="0 0 15 15" fill="none" style="flex-shrink:0; color:#475569">
              <path d="M2 13V6.5L7.5 2 13 6.5V13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
              <rect x="5.5" y="9" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            {lojaFixaNome ?? lojaFixaId}
          </div>
        </div>
      {:else}
        <div class="campo">
          <label for="currentStore">Loja <span class="obrigatorio">*</span></label>
          <select id="currentStore" name="currentStore" class={erros.currentStore ? 'erro' : ''}>
            <option value="">Selecione uma loja...</option>
            {#each lojas as loja}
              <option value={loja.id}
                selected={currentStoreId === loja.id}>
                {loja.name} — {loja.code}
              </option>
            {/each}
          </select>
          {#if erros.currentStore}<span class="erro-msg">{erros.currentStore}</span>{/if}
        </div>
      {/if}

    </div>
  </div>

  <!-- ── 4. Status ── -->
  <div class="secao">
    <p class="secao-titulo">Status</p>
    <div class="grid-2">

      <div class="campo">
        <label for="status">Status do Veículo <span class="obrigatorio">*</span></label>
        <select id="status" name="status" class={erros.status ? 'erro' : ''}>
          {#each STATUS_OPTIONS as opt}
            <option value={opt.value}
              selected={v('status', veiculo?.status ?? 'AVAILABLE') === opt.value}>
              {opt.label}
            </option>
          {/each}
        </select>
        {#if erros.status}<span class="erro-msg">{erros.status}</span>{/if}
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

  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
  .col-span-2 { grid-column: span 2; }

  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo label { font-size: 12px; font-weight: 500; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
  .campo label .obrigatorio { color: #f87171; }
  .campo-hint { font-size: 11px; color: #334155; font-weight: 400; }

  .campo input,
  .campo select {
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
  .campo input::placeholder { color: #334155; }
  .campo input:focus, .campo select:focus {
    border-color: rgba(96,165,250,0.5);
    box-shadow: 0 0 0 3px rgba(96,165,250,0.08);
  }
  .campo select option { background: #0f172a; }
  .campo input.erro, .campo select.erro { border-color: rgba(248,113,113,0.5); }
  .campo .erro-msg { font-size: 11px; color: #f87171; }

  /* ── input com sufixo ── */
  .input-suffix-wrap { position: relative; }
  .input-suffix {
    position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
    font-size: 12px; color: #334155; pointer-events: none;
  }
  .input-suffix-wrap input { padding-right: 36px; }

  /* ── campo fixo (loja fixada) ── */
  .campo-fixo {
    display: flex; align-items: center; gap: 8px;
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px; color: #475569;
  }

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

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
