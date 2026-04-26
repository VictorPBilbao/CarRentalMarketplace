<script lang="ts">
  import type { ActionData, PageData } from './$types';
  import { page } from '$app/state';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const flash  = $derived((page.data as any)?.flash ?? null);
  const catMap = $derived(Object.fromEntries(data.categorias.map((c: any) => [c.id, c])));

  const STATUS_CONFIG: Record<string, { label: string; cor: string; bg: string }> = {
    PENDING:   { label: 'Pendente',       cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    CONFIRMED: { label: 'Confirmada',     cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    ACTIVE:    { label: 'Ativa',          cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    COMPLETED: { label: 'Concluída',      cor: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
    CANCELLED: { label: 'Cancelada',      cor: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    NO_SHOW:   { label: 'Não Compareceu', cor: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
  };

  // Filial só pode executar transições operacionais: confirmar retirada/devolução
  const TRANSICOES: Record<string, Array<{ status: string; label: string; cor: string }>> = {
    PENDING:   [
      { status: 'CONFIRMED', label: 'Confirmar',       cor: '#60a5fa' },
      { status: 'CANCELLED', label: 'Cancelar',        cor: '#f87171' },
    ],
    CONFIRMED: [
      { status: 'ACTIVE',    label: 'Marcar Retirada', cor: '#4ade80' },
      { status: 'NO_SHOW',   label: 'Não Compareceu',  cor: '#fb923c' },
      { status: 'CANCELLED', label: 'Cancelar',        cor: '#f87171' },
    ],
    ACTIVE: [
      { status: 'COMPLETED', label: 'Concluir',        cor: '#94a3b8' },
    ],
    COMPLETED: [],
    CANCELLED: [],
    NO_SHOW:   [],
  };

  function shortId(recordId: string): string {
    const parts = recordId.split(':');
    return (parts[parts.length - 1] ?? recordId).slice(0, 8).toUpperCase();
  }

  function formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  const sc         = $derived(STATUS_CONFIG[data.reserva.status] ?? STATUS_CONFIG['PENDING']);
  const transicoes = $derived(TRANSICOES[data.reserva.status] ?? []);
  const cat        = $derived(catMap[data.reserva.category]);
</script>

<svelte:head>
  <title>Reserva {shortId(data.reserva.id)} — Filial</title>
</svelte:head>

{#if flash?.tipo === 'sucesso'}
  <div class="banner-sucesso">
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
      <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.2"/>
      <path d="M4.5 7l2 2 3.5-4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    {flash.mensagem}
  </div>
{/if}

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<div class="page-header">
  <div>
    <a href="/filial/reservas" class="breadcrumb">Reservas</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">#{shortId(data.reserva.id)}</span>
    <div class="header-row">
      <h1>Reserva #{shortId(data.reserva.id)}</h1>
      <span class="status-badge" style="color:{sc.cor}; background:{sc.bg}">{sc.label}</span>
    </div>
    <p>Criada em {formatDate(data.reserva.created_at)}</p>
  </div>

  {#if transicoes.length > 0}
    <div class="acoes-wrap">
      {#each transicoes as t}
        <form method="POST" action="?/atualizarStatus">
          <input type="hidden" name="status" value={t.status} />
          <button
            type="submit"
            class="btn-acao"
            style="--cor: {t.cor};"
          >{t.label}</button>
        </form>
      {/each}
    </div>
  {/if}
</div>

<div class="detail-grid">

  <div class="col-info">
    <div class="info-card">
      <h3 class="card-title">Detalhes</h3>
      <dl class="info-list">
        <div class="info-item">
          <dt>Cliente</dt>
          <dd><span class="mono">{data.reserva.customer}</span></dd>
        </div>
        <div class="info-item">
          <dt>Categoria</dt>
          <dd>
            {#if cat}
              {cat.group_name} <span class="cat-code">{cat.code}</span>
            {:else}
              <span class="mono">{data.reserva.category}</span>
            {/if}
          </dd>
        </div>
        <div class="info-item">
          <dt>Retirada</dt>
          <dd>
            <span class="bold">{formatDate(data.reserva.pickup_time)}</span>
          </dd>
        </div>
        <div class="info-item">
          <dt>Devolução</dt>
          <dd>
            <span class="bold">{formatDate(data.reserva.dropoff_time)}</span>
            {#if data.reserva.pickup_store !== data.reserva.dropoff_store}
              <span class="loja-tag warn">Devolução em loja diferente</span>
            {/if}
          </dd>
        </div>
        {#if data.reserva.flight_number}
          <div class="info-item">
            <dt>Voo</dt>
            <dd>{data.reserva.flight_number}</dd>
          </div>
        {/if}
        {#if data.reserva.notes}
          <div class="info-item">
            <dt>Observações</dt>
            <dd class="notes">{data.reserva.notes}</dd>
          </div>
        {/if}
      </dl>
    </div>
  </div>

  <div class="col-pricing">
    <div class="info-card">
      <h3 class="card-title">Precificação</h3>
      <div class="pricing-row">
        <span class="pricing-label">Diária</span>
        <span class="pricing-val">
          {data.reserva.pricing.daily_rate.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      </div>
      <div class="pricing-row">
        <span class="pricing-label">Dias</span>
        <span class="pricing-val">{data.reserva.pricing.total_days}</span>
      </div>
      {#if data.reserva.pricing.fees > 0}
        <div class="pricing-row">
          <span class="pricing-label">Taxas</span>
          <span class="pricing-val">
            {data.reserva.pricing.fees.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
        </div>
      {/if}

      {#if data.reserva.pricing.breakdown.length > 0}
        <div class="breakdown-sep"></div>
        <p class="breakdown-titulo">Composição</p>
        {#each data.reserva.pricing.breakdown as item}
          <div class="breakdown-item">
            <span class="breakdown-tipo">{item.type}</span>
            <span class="breakdown-desc">{item.description}</span>
            <span class="breakdown-val">
              {item.amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </span>
          </div>
        {/each}
      {/if}

      <div class="total-row">
        <span>Total</span>
        <span class="total-val">
          {data.reserva.pricing.total_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      </div>
    </div>
  </div>

</div>

<style>
  .page-header { margin-bottom: 28px; display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; }
  .page-header p { font-size: 12px; color: #334155; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }

  .header-row { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
  .header-row h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0; }

  .status-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }

  .acoes-wrap { display: flex; gap: 8px; flex-wrap: wrap; flex-shrink: 0; }
  .btn-acao {
    padding: 8px 16px; border-radius: 8px;
    border: 1px solid color-mix(in srgb, var(--cor) 40%, transparent);
    background: color-mix(in srgb, var(--cor) 10%, transparent);
    color: var(--cor);
    font-size: 12px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background 0.14s; white-space: nowrap;
  }
  .btn-acao:hover { background: color-mix(in srgb, var(--cor) 20%, transparent); }

  .detail-grid { display: grid; grid-template-columns: 1fr 380px; gap: 16px; align-items: start; }

  .info-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px;
  }
  .card-title {
    font-size: 11px; font-weight: 600; color: #475569;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 16px;
  }

  .info-list { margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
  .info-item { display: flex; flex-direction: column; gap: 3px; }
  dt { font-size: 11px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.06em; }
  dd { margin: 0; font-size: 13px; color: #94a3b8; display: flex; flex-direction: column; gap: 3px; }
  .mono { font-family: monospace; font-size: 12px; color: #64748b; word-break: break-all; }
  .bold { font-weight: 600; color: #e2e8f0; }
  .loja-tag {
    font-size: 11px; color: #475569; background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 4px;
    padding: 2px 7px; display: inline-block; width: fit-content;
  }
  .loja-tag.warn { color: #fb923c; border-color: rgba(251,146,60,0.3); background: rgba(251,146,60,0.07); }
  .cat-code { font-size: 11px; color: #475569; margin-left: 6px; background: rgba(255,255,255,0.04); border-radius: 4px; padding: 2px 6px; }
  .notes { color: #64748b; font-size: 12px; white-space: pre-wrap; }

  .pricing-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .pricing-label { font-size: 13px; color: #64748b; }
  .pricing-val   { font-size: 13px; color: #e2e8f0; font-weight: 500; }

  .breakdown-sep  { height: 1px; background: rgba(255,255,255,0.07); margin: 12px 0; }
  .breakdown-titulo { font-size: 11px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 8px; }
  .breakdown-item {
    display: grid; grid-template-columns: auto 1fr auto;
    gap: 8px; align-items: center; padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }
  .breakdown-tipo { font-size: 10px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
  .breakdown-desc { font-size: 12px; color: #475569; }
  .breakdown-val  { font-size: 12px; color: #94a3b8; text-align: right; white-space: nowrap; }

  .total-row {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 14px; margin-top: 4px;
    border-top: 1px solid rgba(255,255,255,0.1);
  }
  .total-row span { font-size: 14px; font-weight: 600; color: #94a3b8; }
  .total-val { font-size: 18px; font-weight: 700; color: #34d399 !important; }

  .banner-sucesso {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; padding: 12px 16px; border-radius: 10px;
    border: 1px solid rgba(74,222,128,0.2); background: rgba(74,222,128,0.07);
    font-size: 13px; color: #4ade80;
  }
  .banner-erro {
    margin-bottom: 20px; padding: 12px 16px; border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.3); background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }
</style>
