<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const lojaMap   = $derived(Object.fromEntries(data.lojas.map((l: any) => [l.id, l])));
  const catMap    = $derived(Object.fromEntries(data.categorias.map((c: any) => [c.id, c])));

  const STATUS_CONFIG: Record<string, { label: string; cor: string; bg: string }> = {
    PENDING:   { label: 'Pendente',       cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    CONFIRMED: { label: 'Confirmada',     cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    ACTIVE:    { label: 'Ativa',          cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    COMPLETED: { label: 'Concluída',      cor: '#94a3b8', bg: 'rgba(148,163,184,0.1)' },
    CANCELLED: { label: 'Cancelada',      cor: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    NO_SHOW:   { label: 'Não Compareceu', cor: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
  };

  const FILTROS = [
    { valor: null,        label: 'Todos'        },
    { valor: 'PENDING',   label: 'Pendente'     },
    { valor: 'CONFIRMED', label: 'Confirmada'   },
    { valor: 'ACTIVE',    label: 'Ativa'        },
    { valor: 'COMPLETED', label: 'Concluída'    },
    { valor: 'CANCELLED', label: 'Cancelada'    },
    { valor: 'NO_SHOW',   label: 'Não Compar.'  },
  ];

  function statusCfg(s: string) {
    return STATUS_CONFIG[s] ?? { label: s, cor: '#64748b', bg: 'rgba(100,116,139,0.1)' };
  }

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

  function nomeLoja(id: string): string {
    return lojaMap[id]?.name ?? shortId(id);
  }

  function nomeCategoria(id: string): string {
    const c = catMap[id];
    return c ? `${c.group_name} (${c.code})` : shortId(id);
  }

  const total     = $derived(data.reservas.length);
  const pendentes = $derived(data.reservas.filter((r: any) => r.status === 'PENDING').length);
  const confirmadas = $derived(data.reservas.filter((r: any) => r.status === 'CONFIRMED').length);
  const ativas    = $derived(data.reservas.filter((r: any) => r.status === 'ACTIVE').length);
</script>

<svelte:head>
  <title>Reservas — Locadora</title>
</svelte:head>

<div class="page-header">
  <div>
    <h1>Reservas</h1>
    <p>Gerencie todas as reservas da sua locadora</p>
  </div>
  <a href="/locadora/reservas/nova" class="btn-novo">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Nova Reserva
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

<div class="filtros-wrap">
  {#each FILTROS as f}
    <a
      href={f.valor ? `/locadora/reservas?status=${f.valor}` : '/locadora/reservas'}
      class="filtro-btn"
      class:filtro-ativo={data.statusFiltro === f.valor}
    >{f.label}</a>
  {/each}
</div>

{#if data.reservas.length === 0}
  <div class="empty-state">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" style="color:#1e293b; margin-bottom:16px">
      <rect x="5" y="7" width="30" height="27" rx="3" stroke="currentColor" stroke-width="1.5"/>
      <path d="M13 3v7M27 3v7M5 18h30" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <p class="empty-titulo">Nenhuma reserva encontrada</p>
    <p class="empty-desc">
      {data.statusFiltro ? 'Nenhuma reserva com este status.' : 'Crie a primeira reserva da sua locadora.'}
    </p>
    {#if !data.statusFiltro}
      <a href="/locadora/reservas/nova" class="btn-novo" style="margin-top:16px">Nova Reserva</a>
    {/if}
  </div>
{:else}
  <div class="tabela-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Cliente</th>
          <th>Categoria</th>
          <th>Lojas</th>
          <th>Período</th>
          <th>Valor</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each data.reservas as r (r.id)}
          {@const sc = statusCfg(r.status)}
          <tr>
            <td><span class="id-badge">{shortId(r.id)}</span></td>
            <td><span class="cliente-nome">{r.customer_name}</span></td>
            <td><span style="font-size:12px; color:#cbd5e1">{r.category_name ? `${r.category_name} (${r.category_code})` : nomeCategoria(r.category)}</span></td>
            <td>
              <div class="lojas-cell">
                <span>{nomeLoja(r.pickup_store)}</span>
                <span class="seta">→</span>
                <span>{nomeLoja(r.dropoff_store)}</span>
              </div>
            </td>
            <td>
              <div class="periodo-cell">
                <span>{formatDate(r.pickup_time)}</span>
                <span class="periodo-sep">até</span>
                <span>{formatDate(r.dropoff_time)}</span>
              </div>
            </td>
            <td>
              <span class="valor-cell">
                {r.pricing.total_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </span>
            </td>
            <td>
              <span class="status-badge" style="color:{sc.cor}; background:{sc.bg}">
                {sc.label}
              </span>
            </td>
            <td class="td-acoes">
              <a href="/locadora/reservas/{encodeURIComponent(r.id)}" class="btn-ver">
                Ver
              </a>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 24px;
  }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .page-header p  { font-size: 13px; color: #475569; margin: 0; }

  .btn-novo {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 9px 18px; border-radius: 8px;
    background: #60a5fa; color: #fff;
    font-size: 13px; font-weight: 600; text-decoration: none;
    font-family: 'DM Sans', sans-serif; flex-shrink: 0;
    transition: background 0.14s;
  }
  .btn-novo:hover { background: #3b82f6; }

  .stats-row {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 16px;
  }
  .stat-card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px 20px;
  }
  .stat-label { font-size: 11px; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 8px; }
  .stat-valor { font-size: 24px; font-weight: 700; color: #f1f5f9; margin: 0; }

  .filtros-wrap {
    display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap;
  }
  .filtro-btn {
    padding: 6px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 500; text-decoration: none;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    color: #64748b;
    transition: all 0.14s;
  }
  .filtro-btn:hover { color: #94a3b8; border-color: rgba(255,255,255,0.12); }
  .filtro-ativo {
    background: rgba(96,165,250,0.12) !important;
    border-color: rgba(96,165,250,0.3) !important;
    color: #60a5fa !important;
  }

  .tabela-wrap {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; overflow: hidden;
  }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
  th {
    text-align: left; padding: 13px 16px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em; color: #334155;
  }
  td {
    padding: 13px 16px; font-size: 13px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.015); }

  .id-badge {
    font-family: monospace; font-size: 11px; font-weight: 600;
    color: #475569; letter-spacing: 0.05em;
  }
  .cliente-nome {
    font-size: 13px; color: #cbd5e1;
  }
  .lojas-cell { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #94a3b8; flex-wrap: wrap; }
  .seta { color: #334155; font-size: 10px; }
  .periodo-cell { display: flex; flex-direction: column; gap: 2px; font-size: 12px; color: #94a3b8; }
  .periodo-sep  { font-size: 10px; color: #334155; }
  .valor-cell   { font-size: 13px; font-weight: 600; color: #e2e8f0; }

  .status-badge {
    display: inline-block; padding: 3px 9px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }
  .td-acoes { text-align: right; }
  .btn-ver {
    display: inline-flex; align-items: center;
    padding: 6px 14px; border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent; color: #64748b;
    font-size: 12px; font-family: 'DM Sans', sans-serif; text-decoration: none;
    transition: border-color 0.14s, color 0.14s;
  }
  .btn-ver:hover { border-color: rgba(96,165,250,0.4); color: #60a5fa; }

  .empty-state {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 60px 24px;
    text-align: center; display: flex; flex-direction: column; align-items: center;
  }
  .empty-titulo { font-size: 15px; font-weight: 600; color: #475569; margin: 0 0 6px; }
  .empty-desc   { font-size: 13px; color: #334155; margin: 0; }

</style>
