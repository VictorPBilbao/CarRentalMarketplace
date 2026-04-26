<script lang="ts">
  import type { PageData } from './$types';
  import type { TipoCombustivel, TipoTransmissao } from '$lib/services/categoria.service';

  let { data }: { data: PageData } = $props();

  const categorias = $derived(data.categorias ?? []);
  const totalAtivas = $derived(categorias.filter((c: any) => c.active).length);

  const COMBUSTIVEL_LABEL: Record<TipoCombustivel, string> = {
    FLEX:     'Flex',
    GASOLINE: 'Gasolina',
    DIESEL:   'Diesel',
    ELECTRIC: 'Elétrico',
    HYBRID:   'Híbrido',
  };

  const TRANSMISSAO_LABEL: Record<TipoTransmissao, string> = {
    AUTOMATIC: 'Automático',
    MANUAL:    'Manual',
  };

  const COMBUSTIVEL_COR: Record<TipoCombustivel, string> = {
    FLEX:     'bg-emerald-400/10 text-emerald-400',
    GASOLINE: 'bg-amber-400/10 text-amber-400',
    DIESEL:   'bg-slate-400/10 text-slate-400',
    ELECTRIC: 'bg-blue-400/10 text-blue-400',
    HYBRID:   'bg-cyan-400/10 text-cyan-400',
  };
</script>

<svelte:head>
  <title>Categorias de Veículos — CarRental</title>
</svelte:head>

<!-- ── cabeçalho ── -->
<div class="page-header">
  <div class="page-header-info">
    <h1>Categorias de Veículos</h1>
    <p>Defina os grupos de veículos disponíveis na sua frota</p>
  </div>
  <a href="/locadora/categorias/nova" class="btn-novo">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Nova Categoria
  </a>
</div>

<!-- ── stats ── -->
<div class="stats-row">
  <div class="stat-card">
    <p class="stat-label">Total de Categorias</p>
    <p class="stat-valor">{categorias.length}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Ativas</p>
    <p class="stat-valor" style="color:#34d399">{totalAtivas}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Inativas</p>
    <p class="stat-valor" style="color:#475569">{categorias.length - totalAtivas}</p>
  </div>
</div>

{#if data.erro}
  <div class="banner-erro">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
      <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    {data.erro}
  </div>
{/if}

<!-- ── tabela ── -->
<div class="tabela-container">
  <div class="tabela-header">
    <h2>Todas as Categorias</h2>
  </div>

  {#if categorias.length === 0 && !data.erro}
    <div class="vazio">
      <div class="vazio-icone">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M3 18L7 8h14l4 10M3 18h22M3 18v4h22v-4" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <circle cx="9" cy="22" r="1.5" fill="currentColor"/>
          <circle cx="19" cy="22" r="1.5" fill="currentColor"/>
        </svg>
      </div>
      <p class="vazio-titulo">Nenhuma categoria cadastrada</p>
      <p class="vazio-desc">Crie categorias para organizar os veículos da sua frota.</p>
      <a href="/locadora/categorias/nova" class="btn-novo" style="margin-top:16px">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Criar primeira categoria
      </a>
    </div>
  {:else}
    <div class="overflow-x">
      <table>
        <thead>
          <tr>
            <th>Categoria</th>
            <th>Combustível</th>
            <th>Câmbio</th>
            <th>Capacidade</th>
            <th>Modelos</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each categorias as c}
            <tr>
              <!-- Nome + código -->
              <td>
                <p class="td-nome">{c.group_name}</p>
                <div class="td-badges">
                  <span class="badge badge-code">{c.code}</span>
                  {#if c.acriss_code}
                    <span class="badge badge-acriss">ACRISS: {c.acriss_code}</span>
                  {/if}
                </div>
              </td>

              <!-- Combustível -->
              <td>
                <span class="badge {COMBUSTIVEL_COR[c.features.fuel_type as TipoCombustivel] ?? 'bg-slate-400/10 text-slate-400'}">
                  {COMBUSTIVEL_LABEL[c.features.fuel_type as TipoCombustivel] ?? c.features.fuel_type}
                </span>
              </td>

              <!-- Câmbio -->
              <td>
                <p class="td-principal">{TRANSMISSAO_LABEL[c.features.transmission as TipoTransmissao] ?? c.features.transmission}</p>
                <p class="td-sub">{c.features.doors} portas</p>
              </td>

              <!-- Capacidade -->
              <td>
                <div class="capacidade-row">
                  <span class="cap-item" title="Passageiros">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <circle cx="6" cy="4" r="2" stroke="currentColor" stroke-width="1.2"/>
                      <path d="M2 10c0-2.21 1.79-4 4-4s4 1.79 4 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                    {c.features.capacity.passengers}
                  </span>
                  <span class="cap-item" title="Malas pequenas">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <rect x="1.5" y="3.5" width="9" height="7" rx="1" stroke="currentColor" stroke-width="1.2"/>
                      <path d="M4 3.5V3a1 1 0 011-1h2a1 1 0 011 1v.5" stroke="currentColor" stroke-width="1.2"/>
                    </svg>
                    {c.features.capacity.small_suitcases}+{c.features.capacity.large_suitcases}
                  </span>
                  {#if c.features.air_conditioning}
                    <span class="cap-item cap-ac" title="Ar-condicionado">AC</span>
                  {/if}
                </div>
              </td>

              <!-- Modelos -->
              <td>
                {#if c.representative_models?.length > 0}
                  <p class="td-principal">{c.representative_models.slice(0, 2).join(', ')}{c.representative_models.length > 2 ? '...' : ''}</p>
                {:else}
                  <p class="td-sub">—</p>
                {/if}
              </td>

              <!-- Status -->
              <td>
                {#if c.active}
                  <span class="badge bg-emerald-400/10 text-emerald-400">Ativa</span>
                {:else}
                  <span class="badge bg-slate-400/10 text-slate-500">Inativa</span>
                {/if}
              </td>

              <!-- Ações -->
              <td class="td-acoes">
                <a href="/locadora/categorias/{encodeURIComponent(c.id)}/editar" class="btn-editar">
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path d="M9 2l2 2-7 7H2V9l7-7z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
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
</div>

<style>
  .page-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px;
  }
  .page-header-info h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 0 0 4px; }
  .page-header-info p  { font-size: 13px; color: #475569; margin: 0; }

  .btn-novo {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 9px 16px; border-radius: 8px;
    background: #3b82f6; color: #fff;
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    text-decoration: none; cursor: pointer; border: none;
    transition: background 0.14s; white-space: nowrap;
  }
  .btn-novo:hover { background: #2563eb; }

  .stats-row {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 12px; margin-bottom: 20px;
  }
  .stat-card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px 20px;
  }
  .stat-label { font-size: 11px; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 6px; }
  .stat-valor { font-size: 22px; font-weight: 700; color: #e2e8f0; margin: 0; }

  .banner-erro {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.2);
    background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }

  .tabela-container {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; overflow: hidden;
  }
  .tabela-header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .tabela-header h2 { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }

  .overflow-x { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
  th {
    padding: 11px 16px; text-align: left;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em; color: #475569;
  }
  td { padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.03); vertical-align: middle; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.015); }

  .td-nome { font-size: 13px; font-weight: 500; color: #e2e8f0; margin: 0 0 4px; }
  .td-badges { display: flex; gap: 6px; flex-wrap: wrap; }
  .td-principal { font-size: 13px; color: #94a3b8; margin: 0; }
  .td-sub { font-size: 11px; color: #475569; margin: 2px 0 0; }
  .td-acoes { text-align: right; }

  .badge {
    display: inline-flex; align-items: center;
    padding: 3px 8px; border-radius: 5px;
    font-size: 11px; font-weight: 600;
  }
  .badge-code { background: rgba(99,102,241,0.1); color: #a5b4fc; }
  .badge-acriss { background: rgba(255,255,255,0.05); color: #475569; font-weight: 500; }

  /* utility color classes used dynamically */
  :global(.bg-emerald-400\/10) { background: rgba(52,211,153,0.1); }
  :global(.text-emerald-400)   { color: #34d399; }
  :global(.bg-amber-400\/10)   { background: rgba(251,191,36,0.1); }
  :global(.text-amber-400)     { color: #fbbf24; }
  :global(.bg-slate-400\/10)   { background: rgba(148,163,184,0.1); }
  :global(.text-slate-400)     { color: #94a3b8; }
  :global(.text-slate-500)     { color: #64748b; }
  :global(.bg-blue-400\/10)    { background: rgba(96,165,250,0.1); }
  :global(.text-blue-400)      { color: #60a5fa; }
  :global(.bg-cyan-400\/10)    { background: rgba(34,211,238,0.1); }
  :global(.text-cyan-400)      { color: #22d3ee; }

  /* capacidade */
  .capacidade-row { display: flex; align-items: center; gap: 10px; }
  .cap-item {
    display: inline-flex; align-items: center; gap: 3px;
    font-size: 12px; color: #64748b;
  }
  .cap-ac {
    font-size: 10px; font-weight: 700;
    padding: 1px 5px; border-radius: 4px;
    background: rgba(96,165,250,0.1); color: #60a5fa;
  }

  /* botão editar */
  .btn-editar {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 6px 12px; border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent; color: #64748b;
    font-size: 12px; font-family: 'DM Sans', sans-serif;
    text-decoration: none;
    transition: border-color 0.14s, color 0.14s, background 0.14s;
  }
  .btn-editar:hover {
    border-color: rgba(96,165,250,0.4); color: #60a5fa;
    background: rgba(96,165,250,0.05);
  }

  /* vazio */
  .vazio {
    display: flex; flex-direction: column; align-items: center;
    padding: 48px 24px; gap: 10px;
  }
  .vazio-icone {
    width: 56px; height: 56px; border-radius: 14px;
    background: rgba(255,255,255,0.04);
    display: flex; align-items: center; justify-content: center;
    color: #334155; margin-bottom: 4px;
  }
  .vazio-titulo { font-size: 14px; font-weight: 600; color: #475569; margin: 0; }
  .vazio-desc   { font-size: 13px; color: #334155; margin: 0; }
</style>
