<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const STATUS_CONFIG: Record<string, { label: string; cor: string; bg: string }> = {
    PENDING:   { label: 'Pendente',       cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    CONFIRMED: { label: 'Confirmada',     cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    ACTIVE:    { label: 'Ativa',          cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    COMPLETED: { label: 'Concluída',      cor: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
    CANCELLED: { label: 'Cancelada',      cor: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    NO_SHOW:   { label: 'Não Compareceu', cor: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
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

  const sc = $derived(STATUS_CONFIG[data.reserva.status] ?? STATUS_CONFIG['PENDING']);
</script>

<svelte:head>
  <title>Reserva {shortId(data.reserva.id)} — Área do Cliente</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/cliente/reservas" class="breadcrumb">Minhas Reservas</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">#{shortId(data.reserva.id)}</span>
    <div class="header-row">
      <h1>Reserva #{shortId(data.reserva.id)}</h1>
      <span class="status-badge" style="color:{sc.cor}; background:{sc.bg}">{sc.label}</span>
    </div>
    <p>Criada em {formatDate(data.reserva.created_at)}</p>
  </div>
</div>

<div class="detail-grid">

  <div class="col-info">
    <div class="info-card">
      <h3 class="card-title">Detalhes da Reserva</h3>
      <dl class="info-list">

        <div class="info-item">
          <dt>Categoria</dt>
          <dd>
            {data.reserva.category_name || data.reserva.category}
            {#if data.reserva.category_code}
              <span class="cat-code">{data.reserva.category_code}</span>
            {/if}
          </dd>
        </div>

        <div class="info-item">
          <dt>Retirada</dt>
          <dd>
            <span class="bold">{formatDate(data.reserva.pickup_time)}</span>
            <span class="loja-tag">{data.reserva.pickup_store_name || shortId(data.reserva.pickup_store)}</span>
          </dd>
        </div>

        <div class="info-item">
          <dt>Devolução</dt>
          <dd>
            <span class="bold">{formatDate(data.reserva.dropoff_time)}</span>
            <span class="loja-tag">{data.reserva.dropoff_store_name || shortId(data.reserva.dropoff_store)}</span>
          </dd>
        </div>

        <div class="info-item">
          <dt>Duração</dt>
          <dd>{data.reserva.pricing.total_days} {data.reserva.pricing.total_days === 1 ? 'dia' : 'dias'}</dd>
        </div>

        {#if data.reserva.flight_number}
          <div class="info-item">
            <dt>Número do Voo</dt>
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
  .page-header { margin-bottom: 28px; }
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

  .detail-grid {
    display: grid; grid-template-columns: 1fr 380px; gap: 16px; align-items: start;
  }

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
  .cat-code {
    font-size: 11px; color: #475569; margin-left: 6px;
    background: rgba(255,255,255,0.04); border-radius: 4px; padding: 2px 6px;
  }
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
  .total-val { font-size: 18px; font-weight: 700; color: #a78bfa !important; }
</style>
