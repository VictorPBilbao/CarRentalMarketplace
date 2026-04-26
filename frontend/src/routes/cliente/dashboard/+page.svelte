<script lang="ts">
  import type { PageData } from './$types';
  import { page } from '$app/state';

  let { data }: { data: PageData } = $props();

  const usuario = $derived((page.data as any).usuario);
  const primeiroNome = $derived(usuario?.nome?.split(' ')[0] ?? 'Cliente');

  const STATUS_CONFIG: Record<string, { label: string; cor: string; bg: string }> = {
    PENDING:   { label: 'Pendente',       cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    CONFIRMED: { label: 'Confirmada',     cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    ACTIVE:    { label: 'Ativa',          cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    COMPLETED: { label: 'Concluída',      cor: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
    CANCELLED: { label: 'Cancelada',      cor: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    NO_SHOW:   { label: 'Não Compareceu', cor: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
  };

  const total      = $derived(data.reservas.length);
  const pendentes  = $derived(data.reservas.filter((r: any) => r.status === 'PENDING').length);
  const confirmadas = $derived(data.reservas.filter((r: any) => r.status === 'CONFIRMED').length);
  const ativas     = $derived(data.reservas.filter((r: any) => r.status === 'ACTIVE').length);

  const proximas = $derived(
    [...data.reservas]
      .filter((r: any) => r.status === 'PENDING' || r.status === 'CONFIRMED' || r.status === 'ACTIVE')
      .sort((a: any, b: any) => new Date(a.pickup_time).getTime() - new Date(b.pickup_time).getTime())
      .slice(0, 5)
  );

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

  function statusCfg(s: string) {
    return STATUS_CONFIG[s] ?? { label: s, cor: '#64748b', bg: 'rgba(100,116,139,0.1)' };
  }
</script>

<svelte:head>
  <title>Dashboard — Área do Cliente</title>
</svelte:head>

<div class="page-header">
  <div>
    <h1>Olá, {primeiroNome}!</h1>
    <p>Aqui está um resumo das suas reservas</p>
  </div>
  <a href="/cliente/reservas" class="btn-ver-todas">
    Ver todas as reservas
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M2.5 6.5h8M7 3l3.5 3.5L7 10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </a>
</div>

<div class="stats-row">
  <div class="stat-card">
    <p class="stat-label">Total</p>
    <p class="stat-valor">{total}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Pendentes</p>
    <p class="stat-valor" style="color:#fbbf24">{pendentes}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Confirmadas</p>
    <p class="stat-valor" style="color:#60a5fa">{confirmadas}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Ativas</p>
    <p class="stat-valor" style="color:#4ade80">{ativas}</p>
  </div>
</div>

<div class="secao">
  <h2 class="secao-titulo">Próximas reservas</h2>

  {#if proximas.length === 0}
    <div class="empty">
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none" style="color:#1e293b; margin-bottom:12px">
        <rect x="4" y="6" width="28" height="25" rx="3" stroke="currentColor" stroke-width="1.4"/>
        <path d="M12 3v5M24 3v5M4 16h28" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
      <p class="empty-titulo">Sem reservas ativas</p>
      <p class="empty-desc">Suas reservas futuras aparecerão aqui.</p>
    </div>
  {:else}
    <div class="reservas-lista">
      {#each proximas as r (r.id)}
        {@const sc = statusCfg(r.status)}
        <a href="/cliente/reservas/{encodeURIComponent(r.id)}" class="reserva-card">
          <div class="reserva-id">
            <span class="id-mono">#{shortId(r.id)}</span>
            <span class="status-badge" style="color:{sc.cor}; background:{sc.bg}">{sc.label}</span>
          </div>
          <div class="reserva-datas">
            <div class="data-item">
              <span class="data-label">Retirada</span>
              <span class="data-val">{formatDate(r.pickup_time)}</span>
            </div>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="color:#334155; flex-shrink:0; margin-top:14px">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="data-item">
              <span class="data-label">Devolução</span>
              <span class="data-val">{formatDate(r.dropoff_time)}</span>
            </div>
          </div>
          <div class="reserva-valor">
            {r.pricing.total_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>

<style>
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 24px; gap: 16px;
  }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .page-header p  { font-size: 13px; color: #475569; margin: 0; }

  .btn-ver-todas {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 9px 16px; border-radius: 8px; flex-shrink: 0;
    border: 1px solid rgba(167,139,250,0.25);
    background: rgba(167,139,250,0.07); color: #a78bfa;
    font-size: 13px; font-weight: 500; text-decoration: none;
    transition: background 0.14s, border-color 0.14s;
  }
  .btn-ver-todas:hover {
    background: rgba(167,139,250,0.12);
    border-color: rgba(167,139,250,0.4);
  }

  .stats-row {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 28px;
  }
  .stat-card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px 20px;
  }
  .stat-label { font-size: 11px; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 8px; }
  .stat-valor { font-size: 24px; font-weight: 700; color: #f1f5f9; margin: 0; }

  .secao { }
  .secao-titulo { font-size: 13px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 14px; }

  .empty {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 48px 24px;
    text-align: center; display: flex; flex-direction: column; align-items: center;
  }
  .empty-titulo { font-size: 14px; font-weight: 600; color: #475569; margin: 0 0 4px; }
  .empty-desc   { font-size: 13px; color: #334155; margin: 0; }

  .reservas-lista { display: flex; flex-direction: column; gap: 8px; }

  .reserva-card {
    display: flex; align-items: center; gap: 20px;
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 18px;
    text-decoration: none; color: inherit;
    transition: border-color 0.14s, background 0.14s;
  }
  .reserva-card:hover {
    border-color: rgba(167,139,250,0.2);
    background: rgba(167,139,250,0.03);
  }

  .reserva-id { display: flex; flex-direction: column; gap: 5px; flex-shrink: 0; min-width: 90px; }
  .id-mono { font-family: monospace; font-size: 12px; font-weight: 600; color: #475569; letter-spacing: 0.05em; }

  .status-badge {
    display: inline-block; padding: 3px 8px; border-radius: 20px;
    font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
    width: fit-content;
  }

  .reserva-datas { display: flex; align-items: flex-start; gap: 12px; flex: 1; min-width: 0; }
  .data-item { display: flex; flex-direction: column; gap: 2px; }
  .data-label { font-size: 10px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.06em; }
  .data-val   { font-size: 12px; color: #94a3b8; white-space: nowrap; }

  .reserva-valor { font-size: 14px; font-weight: 700; color: #e2e8f0; flex-shrink: 0; margin-left: auto; }
</style>
