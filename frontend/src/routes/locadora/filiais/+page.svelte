<script lang="ts">
  import type { PageData } from './$types';
  import type { TipoLocalizacao } from '$lib/services/filial.service';
  import './filiais.css';

  let { data }: { data: PageData } = $props();

  const filiais = $derived(data.filiais);

  const TIPO_LABEL: Record<TipoLocalizacao, string> = {
    AIRPORT:       'Aeroporto',
    TRAIN_STATION: 'Estação de Trem',
    CITY_CENTER:   'Centro da Cidade',
    HOTEL:         'Hotel',
    PORT:          'Porto',
    MALL:          'Shopping',
    OTHER:         'Outro',
  };

  const TIPO_COR: Record<TipoLocalizacao, string> = {
    AIRPORT:       'bg-blue-400/10 text-blue-400',
    TRAIN_STATION: 'bg-purple-400/10 text-purple-400',
    CITY_CENTER:   'bg-emerald-400/10 text-emerald-400',
    HOTEL:         'bg-amber-400/10 text-amber-400',
    PORT:          'bg-cyan-400/10 text-cyan-400',
    MALL:          'bg-pink-400/10 text-pink-400',
    OTHER:         'bg-slate-400/10 text-slate-400',
  };

  const totalAtivas = $derived(filiais.filter(f => f.active).length);
</script>

<svelte:head>
  <title>Filiais — CarRental</title>
</svelte:head>

<!-- ── cabeçalho ── -->
<div class="page-header">
  <div class="page-header-info">
    <h1>Filiais</h1>
    <p>Gerencie as unidades da sua rede de locadoras</p>
  </div>
  <a href="/locadora/filiais/nova" class="btn-novo">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Nova Filial
  </a>
</div>

<!-- ── stats ── -->
<div class="stats-row">
  <div class="stat-card">
    <p class="stat-label">Total de Filiais</p>
    <p class="stat-valor">{filiais.length}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Filiais Ativas</p>
    <p class="stat-valor text-emerald">{totalAtivas}</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Inativas</p>
    <p class="stat-valor text-slate">{filiais.length - totalAtivas}</p>
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
    <h2>Todas as Filiais</h2>
  </div>

  {#if filiais.length === 0 && !data.erro}
    <!-- estado vazio -->
    <div class="vazio">
      <div class="vazio-icone">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M4 24V12L14 4l10 8v12" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <rect x="10" y="16" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
        </svg>
      </div>
      <p class="vazio-titulo">Nenhuma filial cadastrada</p>
      <p class="vazio-desc">Adicione a primeira filial da sua rede para começar a operar.</p>
      <a href="/locadora/filiais/nova" class="btn-novo" style="margin-top:16px;">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Cadastrar primeira filial
      </a>
    </div>
  {:else}
    <div class="overflow-x">
      <table>
        <thead>
          <tr>
            <th>Filial</th>
            <th>Tipo</th>
            <th>Endereço</th>
            <th>Contato</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each filiais as f}
            <tr>
              <!-- Nome + código -->
              <td>
                <p class="td-nome">{f.name}</p>
                <p class="td-sub">{f.code}</p>
              </td>

              <!-- Tipo -->
              <td>
                <span class="badge {TIPO_COR[f.location_type]}">
                  {TIPO_LABEL[f.location_type] ?? f.location_type}
                </span>
              </td>

              <!-- Endereço -->
              <td>
                <p class="td-principal">{f.address.city} — {f.address.state}</p>
                <p class="td-sub">{f.address.street}, {f.address.number}</p>
              </td>

              <!-- Contato -->
              <td>
                <p class="td-principal">{f.contact.email}</p>
                <p class="td-sub">{f.contact.phone}</p>
              </td>

              <!-- Status -->
              <td>
                {#if f.active}
                  <span class="badge bg-emerald-400/10 text-emerald-400">Ativa</span>
                {:else}
                  <span class="badge bg-slate-400/10 text-slate-500">Inativa</span>
                {/if}
              </td>

              <!-- Ações -->
              <td class="td-acoes">
                <a href="/locadora/filiais/{encodeURIComponent(f.id)}/funcionarios" class="btn-funcionarios">
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <circle cx="5" cy="4.5" r="2.5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M1 11.5c0-2.21 1.79-4 4-4s4 1.79 4 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    <path d="M9.5 6.5v3M11 8h-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                  </svg>
                  Equipe
                </a>
                <a href="/locadora/filiais/{encodeURIComponent(f.id)}/editar" class="btn-editar">
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
