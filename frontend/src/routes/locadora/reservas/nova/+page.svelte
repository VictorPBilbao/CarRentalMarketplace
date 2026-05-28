<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const etapa   = $derived((form as any)?.etapa ?? 'cotar');
  const cotacao = $derived((form as any)?.cotacao ?? null);

  const campos = $state({
    customerId:     (form as any)?.campos?.customerId     ?? '',
    categoryId:     (form as any)?.campos?.categoryId     ?? '',
    pickupStoreId:  (form as any)?.campos?.pickupStoreId  ?? '',
    dropoffStoreId: (form as any)?.campos?.dropoffStoreId ?? '',
    pickupTime:     (form as any)?.campos?.pickupTime     ?? '',
    dropoffTime:    (form as any)?.campos?.dropoffTime    ?? '',
    customerAge:    (form as any)?.campos?.customerAge    ?? '25',
    nationality:    (form as any)?.campos?.nationality    ?? '',
    promoCode:      (form as any)?.campos?.promoCode      ?? '',
    flightNumber:   (form as any)?.campos?.flightNumber   ?? '',
    notes:          (form as any)?.campos?.notes          ?? '',
  });

  let carregando = $state(false);

  function err(campo: string): string {
    return (form as any)?.erros?.[campo] ?? '';
  }

  function formatMoeda(v: number): string {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  const tipoLabel: Record<string, string> = {
    BASE_RATE:     'Diária',
    FEE:           'Taxa',
    ADDON:         'Adicional',
    LOGISTICS_FEE: 'Taxa de Retorno',
    INSURANCE:     'Proteção',
    DISCOUNT:      'Desconto',
    TAX:           'Imposto',
  };
</script>

<svelte:head>
  <title>Nova Reserva — Locadora</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/reservas" class="breadcrumb">Reservas</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">Nova</span>
    <h1>{etapa === 'confirmar' ? 'Confirmar Reserva' : 'Nova Reserva'}</h1>
  </div>
</div>

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<!-- ── Etapa 1: Parâmetros ────────────────────────────────────────────── -->
{#if etapa === 'cotar'}
  <form
    method="POST"
    action="?/cotar"
    use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}
  >
    <div class="section-card">
      <h2 class="section-title">Cliente</h2>
      <div class="campo-group">
        <div class="campo">
          <label for="customerId">ID do Cliente <span class="req">*</span></label>
          <input id="customerId" name="customerId" type="text" placeholder="user:abc123"
            bind:value={campos.customerId} class:erro={!!err('customerId')} />
          {#if err('customerId')}<span class="erro-msg">{err('customerId')}</span>{/if}
        </div>
      </div>
    </div>

    <div class="section-card">
      <h2 class="section-title">Veículo e Lojas</h2>
      <div class="campo-group campo-2col">
        <div class="campo">
          <label for="categoryId">Categoria <span class="req">*</span></label>
          <select id="categoryId" name="categoryId" bind:value={campos.categoryId} class:erro={!!err('categoryId')}>
            <option value="">Selecione...</option>
            {#each data.categorias as c}
              <option value={c.id}>{c.group_name} ({c.code})</option>
            {/each}
          </select>
          {#if err('categoryId')}<span class="erro-msg">{err('categoryId')}</span>{/if}
        </div>

        <div class="campo">
          <!-- espaço intencional -->
        </div>

        <div class="campo">
          <label for="pickupStoreId">Loja de Retirada <span class="req">*</span></label>
          <select id="pickupStoreId" name="pickupStoreId" bind:value={campos.pickupStoreId} class:erro={!!err('pickupStoreId')}>
            <option value="">Selecione...</option>
            {#each data.lojas as l}
              <option value={l.id}>{l.name} ({l.code})</option>
            {/each}
          </select>
          {#if err('pickupStoreId')}<span class="erro-msg">{err('pickupStoreId')}</span>{/if}
        </div>

        <div class="campo">
          <label for="dropoffStoreId">Loja de Devolução <span class="req">*</span></label>
          <select id="dropoffStoreId" name="dropoffStoreId" bind:value={campos.dropoffStoreId} class:erro={!!err('dropoffStoreId')}>
            <option value="">Selecione...</option>
            {#each data.lojas as l}
              <option value={l.id}>{l.name} ({l.code})</option>
            {/each}
          </select>
          {#if err('dropoffStoreId')}<span class="erro-msg">{err('dropoffStoreId')}</span>{/if}
        </div>
      </div>
    </div>

    <div class="section-card">
      <h2 class="section-title">Período</h2>
      <div class="campo-group campo-2col">
        <div class="campo">
          <label for="pickupTime">Retirada <span class="req">*</span></label>
          <input id="pickupTime" name="pickupTime" type="datetime-local"
            bind:value={campos.pickupTime} class:erro={!!err('pickupTime')} />
          {#if err('pickupTime')}<span class="erro-msg">{err('pickupTime')}</span>{/if}
        </div>
        <div class="campo">
          <label for="dropoffTime">Devolução <span class="req">*</span></label>
          <input id="dropoffTime" name="dropoffTime" type="datetime-local"
            bind:value={campos.dropoffTime} class:erro={!!err('dropoffTime')} />
          {#if err('dropoffTime')}<span class="erro-msg">{err('dropoffTime')}</span>{/if}
        </div>
      </div>
    </div>

    <div class="section-card">
      <h2 class="section-title">Perfil do Cliente</h2>
      <div class="campo-group campo-2col">
        <div class="campo">
          <label for="customerAge">Idade <span class="req">*</span></label>
          <input id="customerAge" name="customerAge" type="number" min="18" max="99"
            bind:value={campos.customerAge} class:erro={!!err('customerAge')} />
          {#if err('customerAge')}<span class="erro-msg">{err('customerAge')}</span>{/if}
        </div>
        <div class="campo">
          <label for="nationality">Nacionalidade</label>
          <input id="nationality" name="nationality" type="text" placeholder="BR, US, EU..."
            bind:value={campos.nationality} />
        </div>
      </div>
    </div>

    <div class="section-card">
      <h2 class="section-title">Opcionais</h2>
      <div class="campo-group campo-2col">
        <div class="campo">
          <label for="promoCode">Código Promocional</label>
          <input id="promoCode" name="promoCode" type="text" placeholder="PROMO2024"
            bind:value={campos.promoCode} />
        </div>
        <div class="campo">
          <label for="flightNumber">Número do Voo</label>
          <input id="flightNumber" name="flightNumber" type="text" placeholder="LA1234"
            bind:value={campos.flightNumber} />
        </div>
        <div class="campo campo-full">
          <label for="notes">Observações</label>
          <textarea id="notes" name="notes" rows="2" bind:value={campos.notes}></textarea>
        </div>
      </div>
    </div>

    <div class="form-acoes">
      <a href="/locadora/reservas" class="btn-cancelar">Cancelar</a>
      <button type="submit" class="btn-calcular" disabled={carregando}>
        {carregando ? 'Calculando...' : 'Calcular Cotação'}
      </button>
    </div>
  </form>
{/if}

<!-- ── Etapa 2: Confirmar ─────────────────────────────────────────────── -->
{#if etapa === 'confirmar' && cotacao}
  <div class="resumo-card">
    <h3 class="card-title">Resumo</h3>
    <div class="resumo-grid">
      <div class="resumo-item">
        <span class="resumo-label">Tarifa</span>
        <span class="resumo-val">{cotacao.rate_plan_name}</span>
        <span class="resumo-sub">{formatMoeda(cotacao.daily_rate)}/dia × {cotacao.total_days} dia(s)</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Retirada</span>
        <span class="resumo-val">{formatDate(campos.pickupTime)}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Devolução</span>
        <span class="resumo-val">{formatDate(campos.dropoffTime)}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Total</span>
        <span class="resumo-val total-destaque">{formatMoeda(cotacao.final_total)}</span>
      </div>
    </div>
  </div>

  <div class="section-card" style="margin-bottom:16px">
    <h2 class="section-title">Composição do Preço</h2>
    <div class="breakdown-lista">
      {#each cotacao.breakdown as item}
        <div class="breakdown-item">
          <span class="breakdown-tipo {item.type.toLowerCase()}">{tipoLabel[item.type] ?? item.type}</span>
          <span class="breakdown-desc">{item.description}</span>
          <span class="breakdown-valor">{formatMoeda(item.amount)}</span>
        </div>
      {/each}
    </div>
    <div class="total-linha">
      <span>Total</span>
      <span class="total-valor">{formatMoeda(cotacao.final_total)}</span>
    </div>
  </div>

  {#if cotacao.available_addons.length > 0}
    <div class="section-card" style="margin-bottom:16px">
      <h2 class="section-title">Adicionais Opcionais</h2>
      <div class="addons-lista">
        {#each cotacao.available_addons as addon}
          <label class="addon-item">
            <input type="checkbox" form="form-confirmar" name="addon_id" value={addon.id} />
            <input type="hidden"   form="form-confirmar" name="addon_qty" value="1" />
            <div class="addon-info">
              <span class="addon-nome">{addon.name}</span>
              <span class="addon-desc">{addon.description}</span>
            </div>
            <span class="addon-preco">
              {formatMoeda(addon.pricing_amount)}
              <span class="addon-tipo">/{addon.pricing_type === 'PER_DAY' ? 'dia' : addon.pricing_type === 'PER_TRIP' ? 'viagem' : '%'}</span>
            </span>
          </label>
        {/each}
      </div>
    </div>
  {/if}

  {#if cotacao.included_protections.length > 0}
    <div class="section-card" style="margin-bottom:16px">
      <h2 class="section-title">Proteções Incluídas</h2>
      {#each cotacao.included_protections as prot}
        <div class="protecao-item">
          <span class="prot-nome">{prot.name}</span>
          <span class="prot-detalhe">{formatMoeda(prot.daily_rate)}/dia · Franquia {formatMoeda(prot.deductible_amount)}</span>
        </div>
      {/each}
    </div>
  {/if}

  <form id="form-confirmar" method="POST" action="?/confirmar"
    use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}
  >
    <input type="hidden" name="customerId"     value={campos.customerId} />
    <input type="hidden" name="categoryId"     value={campos.categoryId} />
    <input type="hidden" name="pickupStoreId"  value={campos.pickupStoreId} />
    <input type="hidden" name="dropoffStoreId" value={campos.dropoffStoreId} />
    <input type="hidden" name="pickupTime"     value={campos.pickupTime} />
    <input type="hidden" name="dropoffTime"    value={campos.dropoffTime} />
    <input type="hidden" name="customerAge"    value={campos.customerAge} />
    <input type="hidden" name="nationality"    value={campos.nationality} />
    <input type="hidden" name="promoCode"      value={campos.promoCode} />
    <input type="hidden" name="flightNumber"   value={campos.flightNumber} />
    <input type="hidden" name="notes"          value={campos.notes} />

    <div class="form-acoes">
      <a href="/locadora/reservas/nova" class="btn-cancelar">Voltar</a>
      <button type="submit" class="btn-confirmar" disabled={carregando}>
        {carregando ? 'Criando...' : `Confirmar — ${formatMoeda(cotacao.final_total)}`}
      </button>
    </div>
  </form>
{/if}

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }

  .banner-erro {
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px; border: 1px solid rgba(248,113,113,0.3);
    background: rgba(248,113,113,0.07); font-size: 13px; color: #f87171;
  }

  .section-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; max-width: 780px; margin-bottom: 16px;
  }
  .section-title {
    font-size: 11px; font-weight: 600; color: #475569;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 16px;
  }
  .card-title {
    font-size: 11px; font-weight: 600; color: #475569;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 16px;
  }

  .campo-group { display: flex; flex-direction: column; gap: 14px; }
  .campo-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo-full { grid-column: 1 / -1; }

  label { font-size: 12px; font-weight: 500; color: #64748b; }
  .req { color: #f87171; }

  input, select, textarea {
    background: #0a0f1a; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 12px;
    font-size: 13px; color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
    outline: none; width: 100%; box-sizing: border-box;
    transition: border-color 0.14s;
  }
  input:focus, select:focus, textarea:focus { border-color: rgba(96,165,250,0.4); }
  select option { background: #0f172a; }
  textarea { resize: vertical; }
  input.erro, select.erro { border-color: rgba(248,113,113,0.5); }
  .erro-msg { font-size: 11px; color: #f87171; }

  .form-acoes {
    display: flex; justify-content: flex-end; gap: 10px;
    margin-top: 4px; max-width: 780px;
  }
  .btn-cancelar {
    padding: 9px 20px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent; color: #64748b;
    font-size: 13px; font-family: 'DM Sans', sans-serif; text-decoration: none;
    display: inline-flex; align-items: center; transition: all 0.14s;
  }
  .btn-cancelar:hover { border-color: rgba(255,255,255,0.15); color: #94a3b8; }
  .btn-calcular {
    padding: 9px 24px; border-radius: 8px; border: none;
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    color: #fff; font-size: 13px; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: opacity 0.14s;
  }
  .btn-calcular:hover:not(:disabled) { opacity: 0.88; }
  .btn-calcular:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-confirmar {
    padding: 9px 24px; border-radius: 8px; border: none;
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff; font-size: 13px; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: opacity 0.14s;
  }
  .btn-confirmar:hover:not(:disabled) { opacity: 0.88; }
  .btn-confirmar:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Resumo */
  .resumo-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; max-width: 780px; margin-bottom: 16px;
  }
  .resumo-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .resumo-item { display: flex; flex-direction: column; gap: 3px; }
  .resumo-label { font-size: 10px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.07em; }
  .resumo-val   { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .resumo-sub   { font-size: 11px; color: #475569; }
  .total-destaque { font-size: 16px; color: #60a5fa; }

  /* Breakdown */
  .breakdown-lista { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
  .breakdown-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: 7px;
    background: rgba(255,255,255,0.02);
  }
  .breakdown-tipo {
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; padding: 2px 7px; border-radius: 4px; flex-shrink: 0;
  }
  .breakdown-tipo.base_rate { background: rgba(96,165,250,0.1); color: #60a5fa; }
  .breakdown-tipo.fee       { background: rgba(251,191,36,0.1);  color: #fbbf24; }
  .breakdown-tipo.addon     { background: rgba(167,139,250,0.1); color: #a78bfa; }
  .breakdown-tipo.logistics_fee { background: rgba(52,211,153,0.1); color: #34d399; }
  .breakdown-tipo.insurance { background: rgba(96,165,250,0.08); color: #93c5fd; }
  .breakdown-tipo.discount  { background: rgba(248,113,113,0.1); color: #f87171; }
  .breakdown-desc { flex: 1; font-size: 13px; color: #94a3b8; }
  .breakdown-valor { font-size: 13px; font-weight: 600; color: #e2e8f0; flex-shrink: 0; }
  .total-linha {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.07);
    font-size: 13px; font-weight: 600; color: #64748b;
  }
  .total-valor { font-size: 16px; color: #60a5fa; }

  /* Addons */
  .addons-lista { display: flex; flex-direction: column; gap: 6px; }
  .addon-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px; border-radius: 8px; cursor: pointer;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    transition: border-color 0.14s, background 0.14s;
  }
  .addon-item:has(input:checked) {
    border-color: rgba(96,165,250,0.35);
    background: rgba(96,165,250,0.05);
  }
  .addon-item input[type="checkbox"] { width: 14px; height: 14px; flex-shrink: 0; accent-color: #60a5fa; }
  .addon-info { flex: 1; display: flex; flex-direction: column; gap: 1px; }
  .addon-nome { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .addon-desc { font-size: 11px; color: #475569; }
  .addon-preco { font-size: 13px; font-weight: 600; color: #94a3b8; flex-shrink: 0; }
  .addon-tipo  { font-size: 11px; font-weight: 400; color: #475569; }

  /* Proteções */
  .protecao-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .protecao-item:last-child { border-bottom: none; }
  .prot-nome { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .prot-detalhe { font-size: 11px; color: #475569; }
</style>
