<script lang="ts">
  import type { PageData } from './$types';
  import type { StatusReserva } from '$lib/services/dashboard.service';

  let { data }: { data: PageData } = $props();

  const frota          = $derived(data.dashboard.frota);
  const reservas       = $derived(data.dashboard.reservas);
  const filiais        = $derived(data.dashboard.filiais);
  const reservasRecentes = $derived(data.dashboard.reservas_recentes);

  // ── Helpers ──
  const taxaUtilizacao = $derived(Math.round((frota.alugado / frota.total) * 100));

  function pct(v: number): string {
    return Math.round((v / frota.total) * 100) + '%';
  }

  function formatBRL(v: number): string {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function saudacao(): string {
    const h = new Date().getHours();
    if (h < 12) return 'Bom dia';
    if (h < 18) return 'Boa tarde';
    return 'Boa noite';
  }

  const dataAtual = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const statusConfig: Record<StatusReserva, { label: string; cls: string }> = {
    PENDING:   { label: 'Pendente',          cls: 'bg-amber-400/10 text-amber-400'   },
    CONFIRMED: { label: 'Confirmada',        cls: 'bg-blue-400/10 text-blue-400'     },
    ACTIVE:    { label: 'Ativa',             cls: 'bg-emerald-400/10 text-emerald-400' },
    COMPLETED: { label: 'Concluída',         cls: 'bg-slate-400/10 text-slate-400'   },
    CANCELLED: { label: 'Cancelada',         cls: 'bg-red-400/10 text-red-400'       },
    NO_SHOW:   { label: 'Não compareceu',    cls: 'bg-orange-400/10 text-orange-400' },
  };
</script>

<svelte:head>
  <title>Dashboard — CarRental</title>
</svelte:head>

{#if data.erro}
  <div class="mb-5 flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/[0.07] px-4 py-3 text-sm text-red-400">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" class="shrink-0">
      <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    {data.erro}
  </div>
{/if}

<!-- ── CABEÇALHO DA PÁGINA ── -->
<div class="mb-7">
  <p class="text-sm capitalize text-slate-500">{dataAtual}</p>
  <h1 class="mt-1 text-2xl font-semibold text-slate-100">
    {saudacao()}, bem-vindo ao painel
  </h1>
  <p class="mt-1 text-sm text-slate-500">Visão geral da operação — dados em tempo real</p>
</div>

<!-- ── KPI CARDS ── -->
<div class="mb-5 grid grid-cols-2 gap-4 lg:grid-cols-4">

  <!-- Frota Total -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Frota Total</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
        <svg class="text-blue-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M1.5 7L3 3.5h9L13.5 7M1.5 7v4a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V10.5h8v.5a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V7M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="4" cy="9" r="0.8" fill="currentColor"/>
          <circle cx="11" cy="9" r="0.8" fill="currentColor"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{frota.total}</p>
    <p class="mt-1 text-xs text-slate-500">{frota.disponivel} disponíveis agora</p>
  </div>

  <!-- Em Aluguel -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Em Aluguel</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
        <svg class="text-emerald-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M1.5 7.5l4 4 8-8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{frota.alugado}</p>
    <p class="mt-1 text-xs text-slate-500">{taxaUtilizacao}% de utilização da frota</p>
  </div>

  <!-- Reservas Ativas -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Reservas Ativas</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
        <svg class="text-purple-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <rect x="2" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 1.5v2M10 1.5v2M2 6.5h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{reservas.ativa}</p>
    <p class="mt-1 text-xs text-slate-500">{reservas.pendente} pendentes de confirmação</p>
  </div>

  <!-- Filiais -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Filiais</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-500/10">
        <svg class="text-orange-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M2 13V6.5L7.5 2 13 6.5V13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <rect x="5.5" y="9" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.3"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{filiais.ativas}</p>
    <p class="mt-1 text-xs text-slate-500">{filiais.total} lojas na rede</p>
  </div>

</div>

<!-- ── LINHA DO MEIO: Status da Frota + Hoje ── -->
<div class="mb-5 grid grid-cols-1 gap-4 lg:grid-cols-3">

  <!-- Status da Frota (2/3) -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5 lg:col-span-2">
    <h2 class="mb-5 text-sm font-semibold text-slate-200">Status da Frota</h2>
    <div class="space-y-4">

      <div>
        <div class="mb-1.5 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2 text-slate-400">
            <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
            Disponível
          </span>
          <span class="font-medium text-slate-300">
            {frota.disponivel}
            <span class="font-normal text-slate-600">({pct(frota.disponivel)})</span>
          </span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div class="h-full rounded-full bg-emerald-400" style="width: {pct(frota.disponivel)}"></div>
        </div>
      </div>

      <div>
        <div class="mb-1.5 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2 text-slate-400">
            <span class="h-2 w-2 rounded-full bg-blue-400"></span>
            Alugado
          </span>
          <span class="font-medium text-slate-300">
            {frota.alugado}
            <span class="font-normal text-slate-600">({pct(frota.alugado)})</span>
          </span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div class="h-full rounded-full bg-blue-400" style="width: {pct(frota.alugado)}"></div>
        </div>
      </div>

      <div>
        <div class="mb-1.5 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2 text-slate-400">
            <span class="h-2 w-2 rounded-full bg-amber-400"></span>
            Manutenção
          </span>
          <span class="font-medium text-slate-300">
            {frota.manutencao}
            <span class="font-normal text-slate-600">({pct(frota.manutencao)})</span>
          </span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div class="h-full rounded-full bg-amber-400" style="width: {pct(frota.manutencao)}"></div>
        </div>
      </div>

      <div>
        <div class="mb-1.5 flex items-center justify-between text-xs">
          <span class="flex items-center gap-2 text-slate-400">
            <span class="h-2 w-2 rounded-full bg-orange-400"></span>
            Em Trânsito
          </span>
          <span class="font-medium text-slate-300">
            {frota.em_transito}
            <span class="font-normal text-slate-600">({pct(frota.em_transito)})</span>
          </span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div class="h-full rounded-full bg-orange-400" style="width: {pct(frota.em_transito)}"></div>
        </div>
      </div>

    </div>
  </div>

  <!-- Hoje na Operação (1/3) -->
  <div class="min-w-0 rounded-xl border border-white/[0.07] bg-slate-900 p-5 lg:col-span-1">
    <h2 class="mb-4 text-sm font-semibold text-slate-200">Hoje na Operação</h2>
    <div class="space-y-1">

      <div class="flex items-center justify-between rounded-lg px-2 py-2.5 transition-colors hover:bg-white/[0.03]">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
            <svg class="text-emerald-400" width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="text-sm text-slate-300">Retiradas</span>
        </div>
        <span class="text-lg font-bold text-slate-100">{reservas.hoje_retirada}</span>
      </div>

      <div class="flex items-center justify-between rounded-lg px-2 py-2.5 transition-colors hover:bg-white/[0.03]">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
            <svg class="text-blue-400" width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M6.5 11V2M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="text-sm text-slate-300">Devoluções</span>
        </div>
        <span class="text-lg font-bold text-slate-100">{reservas.hoje_devolucao}</span>
      </div>

      <div class="flex items-center justify-between rounded-lg px-2 py-2.5 transition-colors hover:bg-white/[0.03]">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
            <svg class="text-amber-400" width="13" height="13" viewBox="0 0 13 13" fill="none">
              <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M6.5 4v3.5M6.5 9h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="text-sm text-slate-300">Pendentes</span>
        </div>
        <span class="text-lg font-bold text-slate-100">{reservas.pendente}</span>
      </div>

      <div class="flex items-center justify-between rounded-lg px-2 py-2.5 transition-colors hover:bg-white/[0.03]">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
            <svg class="text-purple-400" width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M2 6.5l3.5 3.5 5.5-7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="text-sm text-slate-300">Confirmadas</span>
        </div>
        <span class="text-lg font-bold text-slate-100">{reservas.confirmada}</span>
      </div>

    </div>
  </div>

</div>

<!-- ── RESERVAS RECENTES ── -->
<div class="rounded-xl border border-white/[0.07] bg-slate-900">

  <div class="flex items-center justify-between border-b border-white/[0.07] px-5 py-4">
    <h2 class="text-sm font-semibold text-slate-200">Reservas Recentes</h2>
    <a
      href="/locadora/reservas"
      class="text-xs text-blue-400 transition-colors hover:text-blue-300"
    >
      Ver todas →
    </a>
  </div>

  <div class="overflow-x-auto">
    <table class="w-full">
      <thead>
        <tr class="border-b border-white/[0.05]">
          <th class="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500">Cliente</th>
          <th class="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500">Categoria</th>
          <th class="hidden px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500 md:table-cell">Filial</th>
          <th class="hidden px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500 lg:table-cell">Período</th>
          <th class="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500">Status</th>
          <th class="px-5 py-3 text-right text-[11px] font-semibold uppercase tracking-wider text-slate-500">Valor</th>
        </tr>
      </thead>
      <tbody>
        {#each reservasRecentes as r}
          <tr class="border-b border-white/[0.04] transition-colors last:border-0 hover:bg-white/[0.02]">
            <td class="px-5 py-3.5">
              <p class="text-sm font-medium text-slate-200">{r.cliente}</p>
              <p class="text-xs text-slate-500">#{r.id}</p>
            </td>
            <td class="px-5 py-3.5 text-sm text-slate-400">{r.categoria}</td>
            <td class="hidden px-5 py-3.5 text-sm text-slate-400 md:table-cell">{r.filial}</td>
            <td class="hidden px-5 py-3.5 lg:table-cell">
              <p class="text-xs text-slate-400">{r.retirada}</p>
              <p class="text-xs text-slate-600">{r.devolucao}</p>
            </td>
            <td class="px-5 py-3.5">
              <span class="inline-flex items-center rounded px-2 py-0.5 text-[11px] font-medium {statusConfig[r.status].cls}">
                {statusConfig[r.status].label}
              </span>
            </td>
            <td class="px-5 py-3.5 text-right text-sm font-medium text-slate-200">{formatBRL(r.valor)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

</div>
