<script lang="ts">
  import type { PageData } from './$types';
  import type { StatusReserva } from '$lib/services/dashboard.service';

  let { data }: { data: PageData } = $props();

  const frota            = $derived(data.dashboard.frota);
  const reservas         = $derived(data.dashboard.reservas);
  const reservasRecentes = $derived(data.dashboard.reservas_recentes);
  const filialData       = $derived((data as any).filial);

  const taxaUtilizacao = $derived(frota.total > 0 ? Math.round((frota.alugado / frota.total) * 100) : 0);

  function pct(v: number): string {
    if (frota.total === 0) return '0%';
    return Math.round((v / frota.total) * 100) + '%';
  }

  function saudacao(): string {
    const h = new Date().getHours();
    if (h < 12) return 'Bom dia';
    if (h < 18) return 'Boa tarde';
    return 'Boa noite';
  }

  const dataAtual = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });

  const statusConfig: Record<StatusReserva, { label: string; cor: string; bg: string }> = {
    PENDING:   { label: 'Pendente',       cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    CONFIRMED: { label: 'Confirmada',     cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    ACTIVE:    { label: 'Ativa',          cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    COMPLETED: { label: 'Concluída',      cor: '#64748b', bg: 'rgba(100,116,139,0.1)' },
    CANCELLED: { label: 'Cancelada',      cor: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    NO_SHOW:   { label: 'Não compareceu', cor: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
  };
</script>

<svelte:head>
  <title>Dashboard — {filialData?.name ?? 'Filial'}</title>
</svelte:head>

{#if data.erro}
  <div class="banner-erro">
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
      <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.2"/>
      <path d="M7 4.5V7.5M7 9.5h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    {data.erro}
  </div>
{/if}

<!-- Cabeçalho -->
<div class="cabecalho">
  <p class="data-atual">{dataAtual}</p>
  <h1 class="saudacao">{saudacao()}{#if filialData}, <em>{filialData.name}</em>{/if}</h1>
  <p class="subtitulo">Visão geral da operação — dados em tempo real</p>
</div>

<!-- KPIs -->
<div class="kpis">

  <div class="kpi-card">
    <div class="kpi-header">
      <p class="kpi-label">Frota Total</p>
      <div class="kpi-icon" style="background:rgba(59,130,246,0.1)">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="color:#60a5fa">
          <path d="M1.5 7L3 3.5h9L13.5 7M1.5 7v4a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V10.5h8v.5a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V7M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="4" cy="9" r="0.8" fill="currentColor"/>
          <circle cx="11" cy="9" r="0.8" fill="currentColor"/>
        </svg>
      </div>
    </div>
    <p class="kpi-valor">{frota.total}</p>
    <p class="kpi-desc">{frota.disponivel} disponíveis agora</p>
  </div>

  <div class="kpi-card">
    <div class="kpi-header">
      <p class="kpi-label">Em Aluguel</p>
      <div class="kpi-icon" style="background:rgba(16,185,129,0.1)">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="color:#34d399">
          <path d="M1.5 7.5l4 4 8-8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="kpi-valor">{frota.alugado}</p>
    <p class="kpi-desc">{taxaUtilizacao}% de utilização</p>
  </div>

  <div class="kpi-card">
    <div class="kpi-header">
      <p class="kpi-label">Reservas Ativas</p>
      <div class="kpi-icon" style="background:rgba(139,92,246,0.1)">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="color:#a78bfa">
          <rect x="2" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 1.5v2M10 1.5v2M2 6.5h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </div>
    </div>
    <p class="kpi-valor">{reservas.ativa}</p>
    <p class="kpi-desc">{reservas.pendente} pendentes</p>
  </div>

  <div class="kpi-card">
    <div class="kpi-header">
      <p class="kpi-label">Manutenção</p>
      <div class="kpi-icon" style="background:rgba(245,158,11,0.1)">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="color:#fbbf24">
          <path d="M10.5 1.5l-2 2 3 3 2-2-3-3zM8.5 3.5L2 10v3h3l6.5-6.5-3-3z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="kpi-valor">{frota.manutencao}</p>
    <p class="kpi-desc">{frota.em_transito} em trânsito</p>
  </div>

</div>

<!-- Status da Frota + Hoje -->
<div class="meio-linha">

  <!-- Status da Frota -->
  <div class="card card-lg">
    <h2 class="card-titulo">Status da Frota</h2>
    <div class="barras">

      {#each [
        { label: 'Disponível', val: frota.disponivel, cor: '#4ade80' },
        { label: 'Alugado',    val: frota.alugado,    cor: '#60a5fa' },
        { label: 'Manutenção', val: frota.manutencao, cor: '#fbbf24' },
        { label: 'Em Trânsito',val: frota.em_transito,cor: '#fb923c' },
      ] as item}
        <div>
          <div class="barra-label">
            <span class="barra-label-txt">
              <span class="dot" style="background:{item.cor}"></span>
              {item.label}
            </span>
            <span class="barra-count">{item.val} <span class="barra-pct">({pct(item.val)})</span></span>
          </div>
          <div class="barra-track">
            <div class="barra-fill" style="width:{pct(item.val)}; background:{item.cor}"></div>
          </div>
        </div>
      {/each}

    </div>
  </div>

  <!-- Hoje na Operação -->
  <div class="card card-sm">
    <h2 class="card-titulo">Hoje na Operação</h2>
    <div class="hoje-lista">

      {#each [
        { icon: '▲', cor: '#4ade80', bg: 'rgba(74,222,128,0.1)', label: 'Retiradas',   val: reservas.hoje_retirada  },
        { icon: '▼', cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)', label: 'Devoluções',  val: reservas.hoje_devolucao },
        { icon: '!', cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)', label: 'Pendentes',   val: reservas.pendente       },
        { icon: '✓', cor: '#a78bfa', bg: 'rgba(167,139,250,0.1)',label: 'Confirmadas', val: reservas.confirmada     },
      ] as item}
        <div class="hoje-item">
          <div class="hoje-icone" style="background:{item.bg}; color:{item.cor}">{item.icon}</div>
          <span class="hoje-label">{item.label}</span>
          <span class="hoje-valor">{item.val}</span>
        </div>
      {/each}

    </div>
  </div>

</div>

<!-- Reservas Recentes -->
{#if reservasRecentes.length > 0}
  <div class="card" style="margin-top: 0;">
    <div class="tabela-header">
      <h2 class="card-titulo" style="margin:0">Reservas Recentes</h2>
      <a href="/filial/reservas" class="ver-todas">Ver todas →</a>
    </div>
    <div style="overflow-x:auto; margin-top:16px;">
      <table class="tabela">
        <thead>
          <tr>
            <th>Cliente</th>
            <th>Categoria</th>
            <th>Período</th>
            <th>Status</th>
            <th style="text-align:right">Valor</th>
          </tr>
        </thead>
        <tbody>
          {#each reservasRecentes as r}
            <tr>
              <td>
                <p class="nome-cliente">{r.cliente}</p>
                <p class="id-reserva">#{r.id}</p>
              </td>
              <td class="texto-muted">{r.categoria}</td>
              <td>
                <p class="texto-xs">{r.retirada}</p>
                <p class="texto-xs-muted">{r.devolucao}</p>
              </td>
              <td>
                <span class="status-badge" style="color:{statusConfig[r.status].cor}; background:{statusConfig[r.status].bg}">
                  {statusConfig[r.status].label}
                </span>
              </td>
              <td style="text-align:right; font-weight:600; color:#e2e8f0;">
                {r.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}

<style>
  .cabecalho { margin-bottom: 28px; }
  .data-atual { font-size: 13px; color: #475569; margin: 0 0 4px; text-transform: capitalize; }
  .saudacao   { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .saudacao em { font-style: normal; color: #34d399; }
  .subtitulo  { font-size: 13px; color: #475569; margin: 0; }

  .kpis {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 14px; margin-bottom: 16px;
  }
  .kpi-card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px;
  }
  .kpi-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }
  .kpi-label  { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; color: #475569; margin: 0; }
  .kpi-icon   { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
  .kpi-valor  { font-size: 28px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .kpi-desc   { font-size: 12px; color: #334155; margin: 0; }

  .meio-linha {
    display: grid; grid-template-columns: 3fr 2fr;
    gap: 14px; margin-bottom: 16px;
  }
  .card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px;
  }
  .card-titulo {
    font-size: 13px; font-weight: 600; color: #e2e8f0;
    margin: 0 0 20px; text-transform: none; letter-spacing: 0;
  }

  .barras { display: flex; flex-direction: column; gap: 16px; }
  .barra-label {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 6px; font-size: 12px;
  }
  .barra-label-txt { display: flex; align-items: center; gap: 8px; color: #94a3b8; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .barra-count { font-weight: 500; color: #cbd5e1; }
  .barra-pct   { font-weight: 400; color: #334155; }
  .barra-track { height: 6px; border-radius: 3px; background: #1e293b; overflow: hidden; }
  .barra-fill  { height: 100%; border-radius: 3px; transition: width 0.3s; }

  .hoje-lista { display: flex; flex-direction: column; gap: 4px; }
  .hoje-item  {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 8px; border-radius: 8px;
    transition: background 0.12s;
  }
  .hoje-item:hover { background: rgba(255,255,255,0.03); }
  .hoje-icone {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .hoje-label { font-size: 13px; color: #94a3b8; flex: 1; }
  .hoje-valor { font-size: 18px; font-weight: 700; color: #f1f5f9; }

  .tabela-header { display: flex; align-items: center; justify-content: space-between; }
  .ver-todas { font-size: 12px; color: #34d399; text-decoration: none; }
  .ver-todas:hover { color: #6ee7b7; }

  .tabela { width: 100%; border-collapse: collapse; }
  .tabela th {
    text-align: left; padding: 10px 14px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em; color: #334155;
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .tabela td {
    padding: 12px 14px; font-size: 13px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .tabela tbody tr:last-child td { border-bottom: none; }
  .tabela tbody tr:hover td { background: rgba(255,255,255,0.015); }

  .nome-cliente  { font-weight: 600; color: #e2e8f0; margin: 0; }
  .id-reserva    { font-size: 11px; color: #334155; margin: 0; }
  .texto-muted   { color: #64748b; }
  .texto-xs      { font-size: 12px; color: #64748b; margin: 0; }
  .texto-xs-muted{ font-size: 12px; color: #334155; margin: 0; }

  .status-badge {
    display: inline-block;
    padding: 3px 9px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }

  .banner-erro {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.2);
    background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }
</style>
