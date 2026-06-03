<script lang="ts">
  import type { PageData } from './$types';
  import {
    Chart, ArcElement, BarElement, CategoryScale, LinearScale,
    Tooltip, Legend, DoughnutController, BarController,
  } from 'chart.js';
  import { onMount } from 'svelte';

  Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend, DoughnutController, BarController);

  let { data }: { data: PageData } = $props();
  const s = $derived(data.stats);

  const statusLabel: Record<string, string> = {
    PENDING:        'Pendente',
    CONFIRMED:      'Confirmada',
    ACTIVE:         'Ativa',
    COMPLETED:      'Concluída',
    CANCELLED:      'Cancelada',
    NO_SHOW:        'Não compareceu',
    AVAILABLE:      'Disponível',
    RENTED:         'Alugado',
    MAINTENANCE:    'Manutenção',
    IN_TRANSIT:     'Em Trânsito',
    DECOMMISSIONED: 'Desativado',
  };

  const veiculo_color: Record<string, string> = {
    AVAILABLE: 'bg-emerald-400',
    RENTED: 'bg-blue-400',
    MAINTENANCE: 'bg-amber-400',
    IN_TRANSIT: 'bg-orange-400',
    DECOMMISSIONED: 'bg-slate-600',
  };

  const reservaColors = ['#f59e0b', '#60a5fa', '#34d399', '#94a3b8', '#f87171', '#fb923c'];
  const veiculoColors = ['#34d399', '#60a5fa', '#f59e0b', '#fb923c', '#94a3b8'];

  let canvasReservas: HTMLCanvasElement;
  let canvasVeiculos: HTMLCanvasElement;
  let canvasOta: HTMLCanvasElement;

  onMount(() => {
    if (!s) return;

    const reservasOrdenadas = [...s.reservas.por_status].sort((a, b) => b.qty - a.qty);
    if (canvasReservas && reservasOrdenadas.length > 0) {
      new Chart(canvasReservas, {
        type: 'doughnut',
        data: {
          labels: reservasOrdenadas.map(r => statusLabel[r.status] ?? r.status),
          datasets: [{
            data: reservasOrdenadas.map(r => r.qty),
            backgroundColor: reservaColors,
            borderWidth: 0,
            hoverOffset: 6,
          }],
        },
        options: {
          cutout: '68%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', boxWidth: 10, padding: 14, font: { size: 11 } },
            },
            tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } },
          },
        },
      });
    }

    const veiculosOrdenados = [...s.veiculos.por_status].sort((a, b) => b.qty - a.qty);
    if (canvasVeiculos && veiculosOrdenados.length > 0) {
      new Chart(canvasVeiculos, {
        type: 'doughnut',
        data: {
          labels: veiculosOrdenados.map(v => statusLabel[v.status] ?? v.status),
          datasets: [{
            data: veiculosOrdenados.map(v => v.qty),
            backgroundColor: veiculoColors,
            borderWidth: 0,
            hoverOffset: 6,
          }],
        },
        options: {
          cutout: '68%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', boxWidth: 10, padding: 14, font: { size: 11 } },
            },
            tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } },
          },
        },
      });
    }

    const otaEmpresas = s.ota_keys.por_empresa.slice(0, 8);
    if (canvasOta && otaEmpresas.length > 0) {
      new Chart(canvasOta, {
        type: 'bar',
        data: {
          labels: otaEmpresas.map(e => e.empresa),
          datasets: [{
            label: 'Chaves ativas',
            data: otaEmpresas.map(e => e.total),
            backgroundColor: 'rgba(245,158,11,0.20)',
            borderColor: '#f59e0b',
            borderWidth: 1.5,
            borderRadius: 6,
          }],
        },
        options: {
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.parsed.x} chave${ctx.parsed.x !== 1 ? 's' : ''}`,
              },
            },
          },
          scales: {
            x: {
              ticks: { color: '#475569', font: { size: 11 } },
              grid: { color: 'rgba(255,255,255,0.04)' },
            },
            y: {
              ticks: { color: '#94a3b8', font: { size: 12 } },
              grid: { display: false },
            },
          },
        },
      });
    }
  });

  const dataAtual = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });
</script>

<svelte:head>
  <title>Dashboard — Admin</title>
</svelte:head>

<!-- CABEÇALHO -->
<div class="mb-7">
  <p class="text-sm capitalize text-slate-500">{dataAtual}</p>
  <h1 class="mt-1 text-2xl font-semibold text-slate-100">
    Painel Administrativo
  </h1>
  <p class="mt-1 text-sm text-slate-500">Visão geral do sistema CarRental — dados em tempo real</p>
</div>

{#if !s}
  <div class="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/[0.07] px-4 py-3 text-sm text-red-400">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" class="shrink-0">
      <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Não foi possível carregar as estatísticas do sistema.
  </div>
{:else}

<!-- KPI CARDS -->
<div class="mb-5 grid grid-cols-2 gap-4 lg:grid-cols-5">

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Empresas</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/10">
        <svg class="text-violet-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M2 13V6.5L7.5 2 13 6.5V13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <rect x="5.5" y="9" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.3"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{s.empresas.total}</p>
    <p class="mt-1 text-xs text-slate-500">locadoras cadastradas</p>
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Filiais</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-500/10">
        <svg class="text-orange-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M1.5 6.5L7.5 2l6 4.5V13h-4v-3.5h-4V13h-4V6.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{s.lojas.ativas}</p>
    <p class="mt-1 text-xs text-slate-500">{s.lojas.total} no total</p>
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Veículos</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
        <svg class="text-blue-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <path d="M1.5 7L3 3.5h9L13.5 7M1.5 7v4a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V10.5h8v.5a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V7M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="4" cy="9" r="0.8" fill="currentColor"/>
          <circle cx="11" cy="9" r="0.8" fill="currentColor"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{s.veiculos.total}</p>
    <p class="mt-1 text-xs text-slate-500">na frota do sistema</p>
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Reservas</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
        <svg class="text-purple-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <rect x="2" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 1.5v2M10 1.5v2M2 6.5h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold text-slate-100">{s.reservas.total}</p>
    <p class="mt-1 text-xs text-slate-500">
      {s.reservas.por_status.find(r => r.status === 'ACTIVE')?.qty ?? 0} ativas agora
    </p>
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <div class="mb-3 flex items-start justify-between">
      <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Chaves OTA</p>
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
        <svg class="text-amber-400" width="15" height="15" viewBox="0 0 15 15" fill="none">
          <circle cx="5" cy="10" r="3" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7.5 10H13M11 8.5v3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          <path d="M5 7V4.5L8 2.5 11 4.5V7" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="text-3xl font-bold" style="color:#f59e0b">{s.ota_keys.ativas}</p>
    <p class="mt-1 text-xs text-slate-500">{s.ota_keys.total} cadastradas</p>
  </div>

</div>

<!-- GRÁFICOS: Reservas + Veículos -->
<div class="mb-5 grid grid-cols-1 gap-4 lg:grid-cols-2">

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <h2 class="mb-1 text-sm font-semibold text-slate-200">Reservas por Status</h2>
    <p class="mb-5 text-xs text-slate-500">{s.reservas.total} reservas no sistema</p>
    {#if s.reservas.por_status.length > 0}
      <div class="mx-auto" style="max-width:260px">
        <canvas bind:this={canvasReservas}></canvas>
      </div>
    {:else}
      <p class="py-10 text-center text-sm text-slate-600">Nenhuma reserva registrada</p>
    {/if}
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <h2 class="mb-1 text-sm font-semibold text-slate-200">Frota por Status</h2>
    <p class="mb-5 text-xs text-slate-500">{s.veiculos.total} veículos no sistema</p>
    {#if s.veiculos.por_status.length > 0}
      <div class="mx-auto" style="max-width:260px">
        <canvas bind:this={canvasVeiculos}></canvas>
      </div>
    {:else}
      <p class="py-10 text-center text-sm text-slate-600">Nenhum veículo registrado</p>
    {/if}
  </div>

</div>

<!-- GRÁFICO: OTA por Empresa + Ações -->
<div class="grid grid-cols-1 gap-4 lg:grid-cols-3">

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5 lg:col-span-2">
    <h2 class="mb-1 text-sm font-semibold text-slate-200">Chaves OTA por Empresa</h2>
    <p class="mb-5 text-xs text-slate-500">{s.ota_keys.ativas} chaves ativas distribuídas</p>
    {#if s.ota_keys.por_empresa.length > 0}
      <canvas bind:this={canvasOta} style="max-height:220px"></canvas>
    {:else}
      <p class="py-10 text-center text-sm text-slate-600">Nenhuma chave OTA ativa</p>
    {/if}
  </div>

  <div class="rounded-xl border border-white/[0.07] bg-slate-900 p-5">
    <h2 class="mb-4 text-sm font-semibold text-slate-200">Ações Rápidas</h2>
    <div class="space-y-2">
      <a
        href="/admin/ota-keys"
        class="flex items-center gap-3 rounded-lg border border-white/[0.07] p-3 text-sm text-slate-300 transition-colors hover:border-amber-500/30 hover:bg-amber-500/[0.06] hover:text-amber-400"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="shrink-0 text-amber-400">
          <circle cx="4.5" cy="9.5" r="3" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7 9.5H12.5M10.5 8v3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          <path d="M4.5 6.5V4L7.5 2 10.5 4v2.5" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
        Gerenciar Chaves OTA
      </a>
    </div>

    <div class="mt-6">
      <p class="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Status da Frota</p>
      <div class="space-y-2.5">
        {#each s.veiculos.por_status as v}
          {@const pct = s.veiculos.total > 0 ? Math.round((v.qty / s.veiculos.total) * 100) : 0}
          <div>
            <div class="mb-1 flex justify-between text-xs">
              <span class="text-slate-400">{statusLabel[v.status] ?? v.status}</span>
              <span class="text-slate-500">{v.qty} ({pct}%)</span>
            </div>
            <div class="h-1 overflow-hidden rounded-full bg-slate-800">
              <div
                class="h-full rounded-full {veiculo_color[v.status] ?? 'bg-slate-500'}"
                style="width:{pct}%"
              ></div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

</div>

{/if}
