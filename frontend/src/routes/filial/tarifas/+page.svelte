<script lang="ts">
  import { page } from '$app/state';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const filial     = $derived((page.data as any)?.filial ?? null);
  const cotacao    = $derived((form as any)?.cotacao ?? null);
  const erroCotar  = $derived((form as any)?.erro ?? null);

  // Controle de abas de resultado
  let planSelecionado = $state('');
  let addonsQty: Record<string, number> = $state({});

  function brl(v: number) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function shortId(id: string) {
    return id.split(':').pop() ?? id;
  }

  function nomeLoja(id: string) {
    const l = data.todasLojas?.find((x: any) => x.id === id);
    return l ? `${l.name} (${l.code})` : shortId(id);
  }

  function nomeCategoria(id: string) {
    const c = data.categorias?.find((x: any) => x.id === id);
    return c ? `${c.group_name} – ${c.code}` : shortId(id);
  }

  // Inicia planSelecionado quando chegam os resultados de busca
  $effect(() => {
    if (data.tarifas?.rate_plans?.length && !planSelecionado) {
      planSelecionado = data.tarifas.rate_plans[0].id;
    }
  });

  const MILEAGE: Record<string, string> = {
    UNLIMITED: 'Km ilimitado',
    LIMITED:   'Km limitado',
  };

  const TIPO_ADDON: Record<string, string> = {
    INSURANCE:  'Seguro',
    EQUIPMENT:  'Equipamento',
    SERVICE:    'Serviço',
    FEE:        'Taxa',
  };

  const TIPO_CALC: Record<string, string> = {
    PER_DAY:    '/dia',
    PER_TRIP:   '/viagem',
    PERCENTAGE: '%',
  };

  function addonPreco(addon: any, totalDays: number): string {
    const p = addon.pricing_type;
    if (p === 'PER_DAY') {
      const raw = addon.pricing_amount * totalDays;
      const cap = addon.max_amount_per_trip;
      return brl(cap ? Math.min(raw, cap) : raw);
    }
    if (p === 'PER_TRIP') return brl(addon.pricing_amount);
    return `${addon.pricing_amount}% da diária`;
  }
</script>

<svelte:head>
  <title>Tarifas — Filial</title>
</svelte:head>

<!-- ── Cabeçalho ─────────────────────────────────────────────────────────── -->
<div class="page-header">
  <div>
    <h1>Consulta de Tarifas</h1>
    <p>Pesquise planos disponíveis e calcule cotações para clientes</p>
  </div>
</div>

<!-- ── Formulário de Busca (GET) ─────────────────────────────────────────── -->
<form method="GET" class="search-card">
  <h2 class="section-title">Parâmetros da Locação</h2>

  <div class="grid-4">
    <div class="campo">
      <label for="category">Categoria</label>
      <select id="category" name="category" required>
        <option value="">Selecione...</option>
        {#each data.categorias as cat (cat.id)}
          <option value={cat.id} selected={data.params.categoryId === cat.id}>
            {cat.group_name} – {cat.code}
          </option>
        {/each}
      </select>
    </div>

    <div class="campo">
      <label for="dropoff_store">Loja de Devolução</label>
      <select id="dropoff_store" name="dropoff_store" required>
        <option value="">Selecione...</option>
        {#each data.todasLojas as loja (loja.id)}
          <option value={loja.id} selected={data.params.dropoffStoreId === loja.id}>
            {loja.name} ({loja.code})
          </option>
        {/each}
      </select>
    </div>

    <div class="campo">
      <label for="pickup_time">Retirada</label>
      <input
        id="pickup_time" name="pickup_time" type="datetime-local"
        value={data.params.pickupTime}
        required
      />
    </div>

    <div class="campo">
      <label for="dropoff_time">Devolução</label>
      <input
        id="dropoff_time" name="dropoff_time" type="datetime-local"
        value={data.params.dropoffTime}
        required
      />
    </div>
  </div>

  <div class="grid-2" style="margin-top:12px">
    <div class="campo">
      <label for="customer_age">Idade do Condutor</label>
      <input
        id="customer_age" name="customer_age" type="number"
        min="18" max="99" placeholder="Ex: 30"
        value={data.params.customerAge}
        required
      />
    </div>
    <div class="campo">
      <label for="promo_code">Código Promocional <span class="opcional">(opcional)</span></label>
      <input
        id="promo_code" name="promo_code" type="text"
        placeholder="Ex: VERAO2024"
        value={data.params.promoCode}
      />
    </div>
  </div>

  <div class="search-footer">
    <button type="submit" class="btn-buscar">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
        <circle cx="5.5" cy="5.5" r="4" stroke="currentColor" stroke-width="1.3"/>
        <path d="M8.5 8.5L11 11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      Buscar Tarifas
    </button>
  </div>
</form>

<!-- ── Erro de busca ─────────────────────────────────────────────────────── -->
{#if data.buscarErro}
  <div class="banner-erro">{data.buscarErro}</div>
{/if}

<!-- ── Resultados ────────────────────────────────────────────────────────── -->
{#if data.tarifas}
  {@const t = data.tarifas}

  <!-- Resumo -->
  <div class="resumo-bar">
    <span class="resumo-item">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
        <rect x="1.5" y="2" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
        <path d="M4 1v2M9 1v2M1.5 5.5h10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
      <strong>{t.total_days} dia{t.total_days !== 1 ? 's' : ''}</strong>
    </span>
    <span class="resumo-item">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
        <path d="M1.5 6.5L6.5 2 11.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3 5.5V11H10V5.5" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
      </svg>
      Retirada: <strong>{nomeLoja(filial?.id ?? '')}</strong>
    </span>
    {#if t.is_one_way}
      <span class="resumo-item resumo-oneway">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
          <path d="M2 6.5h9M8 3.5l3 3-3 3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        One Way
        {#if t.one_way_fee}
          — {t.one_way_fee.fee_type === 'FREE' ? 'Gratuito' : brl(t.one_way_fee.amount)}
        {/if}
      </span>
    {/if}
    <span class="resumo-item" style="margin-left:auto; color:#475569; font-size:11px;">
      {t.rate_plans.length} plano{t.rate_plans.length !== 1 ? 's' : ''} disponível{t.rate_plans.length !== 1 ? 'is' : ''}
    </span>
  </div>

  <!-- Layout em duas colunas: planos (esq) + lateral (dir) -->
  <div class="resultado-grid">

    <!-- ── Planos ── -->
    <div class="col-planos">
      {#if t.rate_plans.length === 0}
        <div class="empty-small">
          <p>Nenhum plano tarifário aplicável para estes parâmetros.</p>
          <p class="empty-sub">Verifique a idade, as datas ou o código promocional.</p>
        </div>
      {:else}
        <h3 class="col-titulo">Planos Tarifários</h3>
        {#each t.rate_plans as plan (plan.id)}
          <label
            class="plan-card"
            class:plan-selecionado={planSelecionado === plan.id}
            for="plan_{plan.id}"
          >
            <input
              id="plan_{plan.id}" type="radio"
              bind:group={planSelecionado} value={plan.id}
              style="display:none"
            />
            <div class="plan-top">
              <div>
                <p class="plan-nome">{plan.name}</p>
                <p class="plan-detalhe">{MILEAGE[plan.mileage_policy] ?? plan.mileage_policy}</p>
                {#if plan.included_protections.length > 0}
                  <p class="plan-detalhe" style="color:#34d399">
                    ✓ Proteção incluída
                  </p>
                {/if}
              </div>
              <div class="plan-preco">
                <p class="plan-diaria">{brl(plan.daily_rate)}<span>/dia</span></p>
                <p class="plan-subtotal">{brl(plan.subtotal)} total</p>
              </div>
            </div>
            {#if plan.included_km_per_day > 0}
              <p class="plan-km">{plan.included_km_per_day} km/dia incluídos · km extra: {brl(plan.extra_km_price)}</p>
            {/if}
            {#if planSelecionado === plan.id}
              <div class="plan-badge-sel">Selecionado</div>
            {/if}
          </label>
        {/each}
      {/if}
    </div>

    <!-- ── Lateral: Taxas + Adicionais ── -->
    <div class="col-lateral">

      <!-- Taxas da Loja -->
      {#if t.store_fees.length > 0}
        <div class="lateral-card">
          <h3 class="col-titulo">Taxas da Loja</h3>
          {#each t.store_fees as fee (fee.id)}
            <div class="fee-row">
              <span class="fee-nome">{fee.name}</span>
              <span class="fee-valor">
                {#if fee.calculation_type === 'PERCENTAGE'}
                  {fee.amount}%
                {:else}
                  {brl(fee.amount)}
                {/if}
              </span>
            </div>
          {/each}
        </div>
      {/if}

      <!-- Adicionais Disponíveis -->
      {#if t.available_addons.length > 0}
        <div class="lateral-card">
          <h3 class="col-titulo">Adicionais Disponíveis</h3>
          {#each t.available_addons as addon (addon.id)}
            <div class="addon-row">
              <div class="addon-info">
                <div style="display:flex; align-items:center; gap:6px">
                  <span class="addon-type-badge">{TIPO_ADDON[addon.type] ?? addon.type}</span>
                  <span class="addon-nome">{addon.name}</span>
                </div>
                <p class="addon-desc">{addon.description}</p>
              </div>
              <div class="addon-preco">
                <span>{brl(addon.pricing_amount)}</span>
                <span class="addon-calc">{TIPO_CALC[addon.pricing_type]}</span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- ── Formulário de Cotação ─────────────────────────────────────────── -->
  {#if t.rate_plans.length > 0}
    <div class="cotar-card">
      <h3 class="col-titulo" style="margin-bottom:16px">Calcular Cotação</h3>

      <form method="POST" action="?/cotar">
        <!-- Campos ocultos com contexto da busca -->
        <input type="hidden" name="pickup_store_id"  value={filial?.id ?? ''} />
        <input type="hidden" name="dropoff_store_id" value={data.params.dropoffStoreId} />
        <input type="hidden" name="category_id"      value={data.params.categoryId} />
        <input type="hidden" name="pickup_time"      value={data.params.pickupTime} />
        <input type="hidden" name="dropoff_time"     value={data.params.dropoffTime} />
        <input type="hidden" name="customer_age"     value={data.params.customerAge} />
        <input type="hidden" name="promo_code"       value={data.params.promoCode} />
        <input type="hidden" name="rate_plan_id"     value={planSelecionado} />

        <!-- Adicionais selecionáveis -->
        {#if t.available_addons.length > 0}
          <div class="addons-select-wrap">
            <p class="addons-select-titulo">Incluir adicionais:</p>
            <div class="addons-select-grid">
              {#each t.available_addons as addon (addon.id)}
                <label class="addon-check-card">
                  <input
                    type="checkbox" name="addon_id"
                    value={addon.id}
                    onchange={(e) => {
                      if (!(e.currentTarget as HTMLInputElement).checked) {
                        const { [addon.id]: _, ...rest } = addonsQty;
                        addonsQty = rest;
                      } else {
                        addonsQty = { ...addonsQty, [addon.id]: 1 };
                      }
                    }}
                  />
                  <div class="addon-check-info">
                    <span class="addon-nome">{addon.name}</span>
                    <span class="addon-preco-small">{addonPreco(addon, t.total_days)}</span>
                  </div>
                  {#if addonsQty[addon.id]}
                    <input
                      type="number" name="addon_qty"
                      min="1" max="5"
                      bind:value={addonsQty[addon.id]}
                      class="addon-qty-input"
                      onclick={(e) => e.stopPropagation()}
                    />
                  {:else}
                    <input type="hidden" name="addon_qty" value="1" />
                  {/if}
                </label>
              {/each}
            </div>
          </div>
        {/if}

        <div class="cotar-footer">
          <div class="cotar-plan-info">
            <span>Plano selecionado:</span>
            <strong style="color:#f1f5f9">
              {t.rate_plans.find(p => p.id === planSelecionado)?.name ?? '—'}
            </strong>
          </div>
          <button type="submit" class="btn-cotar">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M1.5 6.5h10M7.5 2.5l4 4-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Calcular Cotação
          </button>
        </div>
      </form>
    </div>
  {/if}
{/if}

<!-- ── Resultado da Cotação ──────────────────────────────────────────────── -->
{#if erroCotar}
  <div class="banner-erro" style="margin-top:16px">{erroCotar}</div>
{/if}

{#if cotacao}
  <div class="cotacao-resultado">
    <div class="cotacao-header">
      <div>
        <h3 class="cotacao-titulo">Cotação Calculada</h3>
        <p class="cotacao-plano">{cotacao.rate_plan_name} · {cotacao.total_days} dia{cotacao.total_days !== 1 ? 's' : ''}</p>
      </div>
      <div class="cotacao-total">{brl(cotacao.final_total)}</div>
    </div>

    <!-- Breakdown -->
    <div class="breakdown-wrap">
      {#each cotacao.breakdown as item (item.description)}
        <div class="breakdown-row">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="breakdown-type" data-type={item.type}>{item.type.replace('_', ' ')}</span>
            <span class="breakdown-desc">{item.description}</span>
          </div>
          <span class="breakdown-valor">{brl(item.amount)}</span>
        </div>
      {/each}
    </div>

    <!-- Totalizadores -->
    <div class="cotacao-subtotais">
      <div class="subtotal-row">
        <span>Subtotal base</span>
        <span>{brl(cotacao.subtotal_base)}</span>
      </div>
      {#if cotacao.fees_total > 0}
        <div class="subtotal-row">
          <span>Taxas da loja</span>
          <span>{brl(cotacao.fees_total)}</span>
        </div>
      {/if}
      {#if cotacao.addons_total > 0}
        <div class="subtotal-row">
          <span>Adicionais</span>
          <span>{brl(cotacao.addons_total)}</span>
        </div>
      {/if}
      {#if cotacao.one_way_fee > 0}
        <div class="subtotal-row">
          <span>Taxa de retorno</span>
          <span>{brl(cotacao.one_way_fee)}</span>
        </div>
      {/if}
      <div class="subtotal-row subtotal-total">
        <span>Total Final</span>
        <span>{brl(cotacao.final_total)}</span>
      </div>
    </div>

    <!-- Proteções incluídas -->
    {#if cotacao.included_protections.length > 0}
      <div class="protecoes-wrap">
        <p class="protecoes-titulo">Proteções incluídas no plano:</p>
        {#each cotacao.included_protections as p (p.id)}
          <div class="protecao-row">
            <span class="protecao-nome">{p.name}</span>
            <span class="protecao-detalhe">Franquia: {brl(p.deductible_amount)} · {brl(p.daily_rate)}/dia</span>
          </div>
        {/each}
      </div>
    {/if}

    <!-- Ação -->
    <div class="cotacao-acoes">
      <a href="/filial/reservas" class="btn-ghost">Ver Reservas</a>
      <a
        href="/locadora/reservas/nova?category={encodeURIComponent(data.params.categoryId)}&pickup_store={encodeURIComponent(filial?.id ?? '')}&dropoff_store={encodeURIComponent(data.params.dropoffStoreId)}&pickup={encodeURIComponent(data.params.pickupTime)}&dropoff={encodeURIComponent(data.params.dropoffTime)}"
        class="btn-criar"
      >
        Criar Reserva com esta Cotação →
      </a>
    </div>
  </div>
{/if}

<!-- ── Estado inicial ────────────────────────────────────────────────────── -->
{#if !data.tarifas && !data.buscarErro}
  <div class="empty-state">
    <svg width="44" height="44" viewBox="0 0 44 44" fill="none" style="color:#1e293b; margin-bottom:16px">
      <path d="M4 22L22 4 40 22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M9 17v23h26V17" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
      <rect x="16" y="28" width="12" height="12" rx="1" stroke="currentColor" stroke-width="1.5"/>
      <path d="M15 10h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <p class="empty-titulo">Consulte tarifas para uma locação</p>
    <p class="empty-desc">Preencha os dados acima para ver os planos disponíveis, taxas e adicionais.</p>
  </div>
{/if}

<style>
  .page-header { margin-bottom: 24px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .page-header p  { font-size: 13px; color: #475569; margin: 0; }

  /* Search card */
  .search-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
  }
  .section-title {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #334155; margin: 0 0 14px;
  }
  .grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; }
  .grid-2 { display: grid; grid-template-columns: repeat(2,1fr); gap: 12px; }
  .campo { display: flex; flex-direction: column; gap: 5px; }
  label { font-size: 12px; font-weight: 500; color: #64748b; }
  .opcional { font-weight: 400; color: #334155; }
  input, select {
    background: #0a0f1a; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 8px 12px; font-size: 13px;
    color: #e2e8f0; font-family: 'DM Sans', sans-serif;
    outline: none; transition: border-color 0.14s;
  }
  input:focus, select:focus { border-color: rgba(96,165,250,0.4); }
  select option { background: #0f172a; }
  .search-footer { display: flex; justify-content: flex-end; margin-top: 14px; }
  .btn-buscar {
    display: flex; align-items: center; gap: 7px;
    padding: 9px 20px; border-radius: 8px;
    background: #60a5fa; color: #fff; border: none;
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background 0.14s;
  }
  .btn-buscar:hover { background: #3b82f6; }

  /* Resumo */
  .resumo-bar {
    display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 10px 16px; margin-bottom: 16px;
    font-size: 13px; color: #94a3b8;
  }
  .resumo-item { display: flex; align-items: center; gap: 6px; }
  .resumo-item strong { color: #e2e8f0; }
  .resumo-oneway { color: #fbbf24; }

  /* Grid resultado */
  .resultado-grid { display: grid; grid-template-columns: 1fr 320px; gap: 16px; margin-bottom: 16px; }
  .col-titulo { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #475569; margin: 0 0 10px; }
  .col-planos { display: flex; flex-direction: column; gap: 8px; }
  .col-lateral { display: flex; flex-direction: column; gap: 12px; }

  /* Plan card */
  .plan-card {
    display: block; position: relative;
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 16px; cursor: pointer;
    transition: border-color 0.14s;
  }
  .plan-card:hover { border-color: rgba(255,255,255,0.14); }
  .plan-selecionado { border-color: rgba(96,165,250,0.5) !important; background: rgba(96,165,250,0.04) !important; }
  .plan-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
  .plan-nome { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0 0 3px; }
  .plan-detalhe { font-size: 11px; color: #475569; margin: 0 0 2px; }
  .plan-preco { text-align: right; flex-shrink: 0; }
  .plan-diaria { font-size: 20px; font-weight: 700; color: #60a5fa; margin: 0; }
  .plan-diaria span { font-size: 12px; font-weight: 400; color: #475569; }
  .plan-subtotal { font-size: 12px; color: #94a3b8; margin: 2px 0 0; }
  .plan-km { font-size: 11px; color: #334155; margin: 8px 0 0; }
  .plan-badge-sel {
    position: absolute; top: 10px; right: 42px;
    font-size: 10px; font-weight: 600; color: #60a5fa;
    background: rgba(96,165,250,0.12); padding: 2px 8px; border-radius: 20px;
  }

  /* Lateral card */
  .lateral-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 16px;
  }
  .fee-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .fee-row:last-child { border-bottom: none; }
  .fee-nome { font-size: 12px; color: #94a3b8; }
  .fee-valor { font-size: 12px; font-weight: 600; color: #fbbf24; }
  .addon-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .addon-row:last-child { border-bottom: none; }
  .addon-info { flex: 1; }
  .addon-type-badge {
    font-size: 9px; font-weight: 600; text-transform: uppercase;
    color: #475569; background: rgba(255,255,255,0.05); padding: 1px 5px; border-radius: 4px;
  }
  .addon-nome { font-size: 12px; color: #cbd5e1; }
  .addon-desc { font-size: 11px; color: #334155; margin: 2px 0 0; }
  .addon-preco { text-align: right; flex-shrink: 0; }
  .addon-preco span:first-child { font-size: 12px; font-weight: 600; color: #34d399; display: block; }
  .addon-calc { font-size: 10px; color: #334155; }

  /* Cotação form */
  .cotar-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
  }
  .addons-select-titulo { font-size: 12px; color: #64748b; margin: 0 0 10px; }
  .addons-select-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; margin-bottom: 16px; }
  .addon-check-card {
    display: flex; align-items: center; gap: 10px;
    background: #0a0f1a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 9px 12px; cursor: pointer;
    transition: border-color 0.14s;
    position: relative;
  }
  .addon-check-card:has(input:checked) { border-color: rgba(52,211,153,0.4); }
  .addon-check-info { flex: 1; }
  .addon-preco-small { font-size: 11px; color: #475569; display: block; margin-top: 1px; }
  .addon-qty-input {
    width: 44px; text-align: center; padding: 4px 6px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px; font-size: 12px; color: #e2e8f0;
  }
  .cotar-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06); }
  .cotar-plan-info { font-size: 13px; color: #475569; display: flex; align-items: center; gap: 8px; }
  .btn-cotar {
    display: flex; align-items: center; gap: 7px;
    padding: 9px 20px; border-radius: 8px;
    background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.3);
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: all 0.14s;
  }
  .btn-cotar:hover { background: rgba(52,211,153,0.2); }

  /* Resultado da cotação */
  .cotacao-resultado {
    background: #0f172a; border: 1px solid rgba(52,211,153,0.2);
    border-radius: 12px; overflow: hidden; margin-top: 4px;
  }
  .cotacao-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 24px; border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(52,211,153,0.04);
  }
  .cotacao-titulo { font-size: 15px; font-weight: 700; color: #f1f5f9; margin: 0 0 3px; }
  .cotacao-plano { font-size: 12px; color: #475569; margin: 0; }
  .cotacao-total { font-size: 28px; font-weight: 800; color: #34d399; }
  .breakdown-wrap { padding: 14px 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .breakdown-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; }
  .breakdown-type {
    font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em;
    padding: 2px 6px; border-radius: 4px;
    background: rgba(255,255,255,0.05); color: #475569;
  }
  .breakdown-type[data-type="BASE_RATE"]    { background: rgba(96,165,250,0.1); color: #60a5fa; }
  .breakdown-type[data-type="FEE"]          { background: rgba(251,191,36,0.1); color: #fbbf24; }
  .breakdown-type[data-type="ADDON"]        { background: rgba(52,211,153,0.1); color: #34d399; }
  .breakdown-type[data-type="LOGISTICS_FEE"]{ background: rgba(251,146,60,0.1); color: #fb923c; }
  .breakdown-desc { font-size: 12px; color: #94a3b8; }
  .breakdown-valor { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .cotacao-subtotais { padding: 14px 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .subtotal-row { display: flex; justify-content: space-between; font-size: 12px; color: #475569; padding: 4px 0; }
  .subtotal-total { font-size: 14px; font-weight: 700; color: #f1f5f9; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 6px; padding-top: 10px; }
  .protecoes-wrap { padding: 14px 24px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .protecoes-titulo { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; color: #334155; margin: 0 0 8px; }
  .protecao-row { display: flex; align-items: center; justify-content: space-between; padding: 5px 0; }
  .protecao-nome { font-size: 12px; color: #94a3b8; }
  .protecao-detalhe { font-size: 11px; color: #475569; }
  .cotacao-acoes { display: flex; align-items: center; justify-content: flex-end; gap: 10px; padding: 14px 24px; }
  .btn-ghost {
    padding: 8px 18px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08); background: transparent;
    color: #64748b; font-size: 13px; font-family: 'DM Sans', sans-serif;
    text-decoration: none; transition: all 0.14s;
  }
  .btn-ghost:hover { border-color: rgba(255,255,255,0.15); color: #94a3b8; }
  .btn-criar {
    padding: 9px 20px; border-radius: 8px;
    background: #60a5fa; color: #fff; border: none;
    font-size: 13px; font-weight: 600; text-decoration: none;
    transition: background 0.14s;
  }
  .btn-criar:hover { background: #3b82f6; }

  /* Empty states */
  .empty-state {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 60px 24px;
    text-align: center; display: flex; flex-direction: column; align-items: center;
  }
  .empty-titulo { font-size: 15px; font-weight: 600; color: #475569; margin: 0 0 6px; }
  .empty-desc   { font-size: 13px; color: #334155; margin: 0; }
  .empty-small {
    background: #0f172a; border: 1px dashed rgba(255,255,255,0.07);
    border-radius: 10px; padding: 28px; text-align: center;
  }
  .empty-small p  { font-size: 13px; color: #475569; margin: 0 0 4px; }
  .empty-sub      { font-size: 12px; color: #334155 !important; }
  .banner-erro {
    padding: 12px 16px; border-radius: 10px; font-size: 13px;
    border: 1px solid rgba(248,113,113,0.3); background: rgba(248,113,113,0.07);
    color: #f87171; margin-bottom: 16px;
  }
  .col-titulo { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #475569; margin: 0 0 10px; }
</style>
