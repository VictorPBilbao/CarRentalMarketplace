<script lang="ts">
  import type { PageData } from './$types';
  import type { StatusVeiculo } from '$lib/services/veiculo.service';
  import { page } from '$app/state';

  let { data }: { data: PageData } = $props();

  const flash = $derived((page.data as any)?.flash ?? null);

  // maps for display
  const categoriaMap = $derived(
    Object.fromEntries(data.categorias.map((c: any) => [c.id, c]))
  );
  const lojaMap = $derived(
    Object.fromEntries(data.lojas.map((l: any) => [l.id, l]))
  );

  const STATUS_CONFIG: Record<StatusVeiculo, { label: string; cor: string; bg: string }> = {
    AVAILABLE:      { label: 'Disponível',   cor: '#4ade80', bg: 'rgba(74,222,128,0.1)'  },
    RENTED:         { label: 'Alugado',      cor: '#60a5fa', bg: 'rgba(96,165,250,0.1)'  },
    MAINTENANCE:    { label: 'Manutenção',   cor: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    IN_TRANSIT:     { label: 'Em trânsito',  cor: '#a78bfa', bg: 'rgba(167,139,250,0.1)' },
    DECOMMISSIONED: { label: 'Desativado',   cor: '#64748b', bg: 'rgba(100,116,139,0.1)' },
  };

  function statusCfg(s: string) {
    return STATUS_CONFIG[s as StatusVeiculo] ?? { label: s, cor: '#64748b', bg: 'rgba(100,116,139,0.1)' };
  }

  // stats
  const total        = $derived(data.veiculos.length);
  const disponiveis  = $derived(data.veiculos.filter((v: any) => v.status === 'AVAILABLE').length);
  const alugados     = $derived(data.veiculos.filter((v: any) => v.status === 'RENTED').length);
  const manutencao   = $derived(data.veiculos.filter((v: any) => v.status === 'MAINTENANCE').length);
</script>

<svelte:head>
  <title>Frota — CarRental</title>
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

<!-- Header -->
<div class="page-header">
  <div>
    <h1>Frota</h1>
    <p>Gerencie os veículos cadastrados na sua locadora</p>
  </div>
  <a href="/locadora/frota/novo" class="btn-novo">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Novo Veículo
  </a>
</div>

<!-- Stats -->
<div class="stats-row">
  <div class="stat-card">
    <p class="stat-label">Total</p>
    <p class="stat-valor">{total}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Disponíveis</p>
    <p class="stat-valor" style="color:#4ade80">{disponiveis}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Alugados</p>
    <p class="stat-valor" style="color:#60a5fa">{alugados}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Manutenção</p>
    <p class="stat-valor" style="color:#fbbf24">{manutencao}</p>
  </div>
</div>

<!-- Tabela -->
{#if data.veiculos.length === 0}
  <div class="empty-state">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" style="color:#1e293b; margin-bottom:16px">
      <path d="M5 25L10 10h20l5 15M5 25h30M5 25v5a1 1 0 001 1h3a1 1 0 001-1v-1.5h20V31a1 1 0 001 1h3a1 1 0 001-1v-6"
        stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
      <circle cx="12" cy="28" r="2" fill="currentColor"/>
      <circle cx="28" cy="28" r="2" fill="currentColor"/>
    </svg>
    <p class="empty-titulo">Nenhum veículo cadastrado</p>
    <p class="empty-desc">Adicione o primeiro veículo da sua frota.</p>
    <a href="/locadora/frota/novo" class="btn-novo" style="margin-top:16px">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
        <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      Cadastrar Veículo
    </a>
  </div>
{:else}
  <div class="tabela-wrap">
    <table>
      <thead>
        <tr>
          <th>Veículo</th>
          <th>Placa</th>
          <th>Categoria</th>
          <th>Loja</th>
          <th>Quilometragem</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each data.veiculos as v (v.id)}
          {@const cat  = categoriaMap[v.category]}
          {@const loja = lojaMap[v.current_store]}
          {@const sc   = statusCfg(v.status)}
          <tr>
            <td>
              <div class="veiculo-info">
                <span class="veiculo-nome">{v.make} {v.model}</span>
                <span class="veiculo-detalhe">{v.year} · {v.color}</span>
              </div>
            </td>
            <td>
              <span class="placa-badge">{v.plate.toUpperCase()}</span>
            </td>
            <td>
              {#if cat}
                <div class="cat-info">
                  <span class="cat-nome">{cat.group_name}</span>
                  <span class="cat-code">{cat.code}</span>
                </div>
              {:else}
                <span class="texto-muted">—</span>
              {/if}
            </td>
            <td>
              {#if loja}
                <div class="loja-info">
                  <span class="loja-nome">{loja.name}</span>
                  <span class="loja-code">{loja.code}</span>
                </div>
              {:else}
                <span class="texto-muted">—</span>
              {/if}
            </td>
            <td>
              <span class="km-val">{v.mileage_km.toLocaleString('pt-BR')} km</span>
            </td>
            <td>
              <span class="status-badge" style="color:{sc.cor}; background:{sc.bg}">
                {sc.label}
              </span>
            </td>
            <td class="td-acoes">
              <a href="/locadora/frota/{encodeURIComponent(v.id)}/editar" class="btn-editar">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <path d="M9.5 1.5l2 2-8 8H1.5v-2l8-8z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                </svg>
                Editar
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
    background: #3b82f6; color: #fff;
    font-size: 13px; font-weight: 600; text-decoration: none;
    font-family: 'DM Sans', sans-serif;
    transition: background 0.14s;
    flex-shrink: 0;
  }
  .btn-novo:hover { background: #2563eb; }

  .stats-row {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 20px;
  }
  .stat-card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 16px 20px;
  }
  .stat-label { font-size: 11px; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 8px; }
  .stat-valor { font-size: 24px; font-weight: 700; color: #f1f5f9; margin: 0; }

  .tabela-wrap {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    overflow: hidden;
  }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
  th {
    text-align: left;
    padding: 13px 16px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: #334155;
  }
  td {
    padding: 14px 16px;
    font-size: 13px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.015); }

  .veiculo-info { display: flex; flex-direction: column; gap: 2px; }
  .veiculo-nome { font-weight: 600; color: #e2e8f0; }
  .veiculo-detalhe { font-size: 12px; color: #475569; }

  .placa-badge {
    display: inline-block;
    padding: 3px 9px; border-radius: 5px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    font-size: 12px; font-weight: 600; color: #94a3b8;
    font-family: monospace; letter-spacing: 0.05em;
  }

  .cat-info, .loja-info { display: flex; flex-direction: column; gap: 2px; }
  .cat-nome, .loja-nome { font-size: 13px; color: #cbd5e1; }
  .cat-code, .loja-code { font-size: 11px; color: #334155; }

  .km-val { font-size: 13px; color: #94a3b8; }
  .texto-muted { color: #334155; }

  .status-badge {
    display: inline-block;
    padding: 3px 9px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }

  .td-acoes { text-align: right; }
  .btn-editar {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 6px 12px; border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent; color: #64748b;
    font-size: 12px; font-family: 'DM Sans', sans-serif;
    text-decoration: none;
    transition: border-color 0.14s, color 0.14s;
  }
  .btn-editar:hover { border-color: rgba(96,165,250,0.4); color: #60a5fa; }

  .empty-state {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 60px 24px;
    text-align: center;
    display: flex; flex-direction: column; align-items: center;
  }
  .empty-titulo { font-size: 15px; font-weight: 600; color: #475569; margin: 0 0 6px; }
  .empty-desc   { font-size: 13px; color: #334155; margin: 0; }

  .banner-sucesso {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid rgba(74,222,128,0.2);
    background: rgba(74,222,128,0.07);
    font-size: 13px; color: #4ade80;
  }
</style>
