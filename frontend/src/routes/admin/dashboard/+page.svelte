<script lang="ts">
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>Dashboard — Admin</title>
</svelte:head>

<div class="page-header">
  <h1>Dashboard</h1>
  <p>Visão geral do sistema CarRental</p>
</div>

<div class="stats-row">
  <div class="stat-card">
    <p class="stat-label">Chaves OTA</p>
    <p class="stat-valor">{data.totalChaves}</p>
    <p class="stat-sub">total cadastradas</p>
  </div>
  <div class="stat-card">
    <p class="stat-label">Chaves Ativas</p>
    <p class="stat-valor" style="color:#f59e0b">{data.chavesAtivas}</p>
    <p class="stat-sub">em uso por parceiros</p>
  </div>
</div>

<div class="acoes-card">
  <p class="acoes-titulo">Ações rápidas</p>
  <a href="/admin/ota-keys" class="btn-acao">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <circle cx="4.5" cy="9" r="2.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M6.5 9H11M9.5 7.5v3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      <path d="M4.5 6.5V4L7.5 2 10.5 4v2.5" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
    </svg>
    Gerenciar Chaves OTA
  </a>
</div>

<style>
  .page-header { margin-bottom:24px; }
  .page-header h1 { font-size:22px; font-weight:700; color:#f1f5f9; margin:0 0 4px; }
  .page-header p  { font-size:13px; color:#475569; margin:0; }

  .stats-row {
    display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));
    gap:12px; margin-bottom:20px;
  }
  .stat-card {
    background:#0f172a; border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:18px 20px;
  }
  .stat-label { font-size:11px; color:#475569; font-weight:600; text-transform:uppercase; letter-spacing:.07em; margin:0 0 8px; }
  .stat-valor { font-size:28px; font-weight:700; color:#f1f5f9; margin:0 0 2px; }
  .stat-sub   { font-size:11px; color:#334155; margin:0; }

  .acoes-card {
    background:#0f172a; border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:18px 20px;
  }
  .acoes-titulo { font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.07em; color:#475569; margin:0 0 12px; }
  .btn-acao {
    display:inline-flex; align-items:center; gap:7px;
    padding:9px 16px; border-radius:9px;
    background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25);
    color:#f59e0b; font-size:13px; font-weight:500; text-decoration:none;
    transition:all .14s;
  }
  .btn-acao:hover { background:rgba(245,158,11,0.18); border-color:rgba(245,158,11,0.4); }
</style>
