<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { LayoutData } from './$types';
  import { page } from '$app/state';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();

  const usuario = $derived(data.usuario);
  const filial  = $derived((data as any).filial);

  const iniciais = $derived(
    usuario?.nome
      ? usuario.nome.split(' ').slice(0, 2).map((n: string) => n[0]).join('').toUpperCase()
      : '?'
  );

  const paginaTitulo: Record<string, string> = {
    '/filial/dashboard': 'Dashboard',
    '/filial/frota':     'Frota',
    '/filial/reservas':  'Reservas',
    '/filial/contratos': 'Contratos',
    '/filial/cotacao':   'Cotação',
    '/filial/one-way':   'One-Way',
  };

  const titulo = $derived(paginaTitulo[page.url.pathname] ?? 'Painel');

  function ativo(href: string): boolean {
    return page.url.pathname.startsWith(href);
  }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div style="display:flex; min-height:100vh; background:#080c14; font-family:'DM Sans',sans-serif; color:#f1f5f9;">

  <!-- ── SIDEBAR ── -->
  <aside style="
    position: fixed;
    top: 0; left: 0;
    width: 224px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0f172a;
    border-right: 1px solid rgba(255,255,255,0.07);
    z-index: 20;
  ">

    <!-- Logo -->
    <a
      href="/filial/dashboard"
      style="
        flex-shrink: 0;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        text-decoration: none;
        color: #f1f5f9;
        font-weight: 600;
        font-size: 15px;
      "
    >
      <span style="color:#34d399; font-size:18px;">◈</span>
      CarRental
    </a>

    <!-- Filial badge -->
    {#if filial}
      <div style="
        flex-shrink: 0;
        padding: 10px 14px 6px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
      ">
        <p style="font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #334155; margin: 0 0 3px;">Loja</p>
        <p style="font-size: 13px; font-weight: 600; color: #94a3b8; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filial.name}</p>
        <span style="font-size: 11px; color: #334155;">{filial.code}</span>
      </div>
    {/if}

    <!-- Nav -->
    <nav style="
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding: 12px 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    ">

      <p class="nav-label">Geral</p>

      <a href="/filial/dashboard" class="nav-item {ativo('/filial/dashboard') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <rect x="1" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="1" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        Dashboard
      </a>

      <p class="nav-label" style="margin-top:12px;">Operações</p>

      <a href="/filial/frota" class="nav-item {ativo('/filial/frota') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M1.5 7L3 3.5h9L13.5 7M1.5 7v4a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V10.5h8v.5a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V7M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="4" cy="9" r="0.8" fill="currentColor"/>
          <circle cx="11" cy="9" r="0.8" fill="currentColor"/>
        </svg>
        Frota
      </a>

      <a href="/filial/reservas" class="nav-item {ativo('/filial/reservas') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <rect x="2" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 1.5v2M10 1.5v2M2 6.5h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        Reservas
      </a>

      <a href="/filial/contratos" class="nav-item {ativo('/filial/contratos') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M4 1.5h5L12 4.5v9H3v-12z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <path d="M9 1.5V4.5H12M5.5 7.5h4M5.5 10h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        Contratos
      </a>

      <a href="/filial/one-way" class="nav-item {ativo('/filial/one-way') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M1.5 7.5h12M9.5 4.5l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="4" cy="7.5" r="1.5" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        One-Way
      </a>

      <a href="/filial/cotacao" class="nav-item {ativo('/filial/cotacao') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M1.5 7.5h12M1.5 4.5h12M1.5 10.5h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          <circle cx="5" cy="7.5" r="1" fill="currentColor"/>
          <circle cx="10" cy="4.5" r="1" fill="currentColor"/>
          <circle cx="7.5" cy="10.5" r="1" fill="currentColor"/>
        </svg>
        Cotação
      </a>

    </nav>

    <!-- Footer -->
    <div style="
      flex-shrink: 0;
      padding: 14px;
      border-top: 1px solid rgba(255,255,255,0.07);
    ">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="
          width:34px; height:34px;
          border-radius:50%;
          background:linear-gradient(135deg,#10b981,#059669);
          display:flex; align-items:center; justify-content:center;
          font-size:12px; font-weight:700; color:#fff;
          flex-shrink:0;
        ">{iniciais}</div>
        <div style="overflow:hidden;">
          <p style="font-size:13px; font-weight:500; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{usuario?.nome ?? ''}</p>
          <p style="font-size:11px; color:#475569; margin-top:1px;">Filial</p>
        </div>
      </div>
      <form method="POST" action="/login?/sair">
        <button type="submit" style="
          display:flex; align-items:center; gap:8px;
          width:100%; padding:8px 10px;
          border-radius:8px;
          border:1px solid rgba(255,255,255,0.08);
          background:transparent;
          color:#64748b;
          font-size:13px;
          cursor:pointer;
          transition:all 0.14s;
          font-family:inherit;
        "
          onmouseenter={(e) => { const t = e.currentTarget as HTMLButtonElement; t.style.borderColor='rgba(248,113,113,0.5)'; t.style.color='#f87171'; t.style.background='rgba(248,113,113,0.05)'; }}
          onmouseleave={(e) => { const t = e.currentTarget as HTMLButtonElement; t.style.borderColor='rgba(255,255,255,0.08)'; t.style.color='#64748b'; t.style.background='transparent'; }}
        >
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
            <path d="M5 1.5H2.5A1 1 0 001.5 2.5v8a1 1 0 001 1H5M9 9.5L11.5 6.5 9 3.5M11.5 6.5H5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Sair da conta
        </button>
      </form>
    </div>

  </aside>

  <!-- ── MAIN ── -->
  <div style="margin-left:224px; flex:1; display:flex; flex-direction:column; min-width:0;">

    <!-- Topbar -->
    <header style="
      position: sticky;
      top: 0;
      z-index: 10;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 28px;
      background: #0f172a;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      flex-shrink: 0;
    ">
      <div style="font-size:13px; color:#475569; display:flex; align-items:center; gap:6px;">
        <span>Filial</span>
        <span style="color:#1e293b;">/</span>
        <span style="color:#94a3b8; font-weight:500;">{titulo}</span>
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="
          background:rgba(52,211,153,0.12);
          color:#34d399;
          font-size:11px; font-weight:600;
          padding:3px 9px;
          border-radius:20px;
          text-transform:uppercase;
          letter-spacing:0.05em;
        ">{filial?.code ?? 'Filial'}</span>
        <span style="font-size:13px; color:#94a3b8;">{usuario?.nome?.split(' ')[0] ?? ''}</span>
      </div>
    </header>

    <!-- Page content -->
    <main style="flex:1; padding:28px; min-width:0;">
      {@render children()}
    </main>

  </div>

</div>

<style>
  .nav-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #334155;
    padding: 4px 10px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    transition: background 0.14s, color 0.14s;
  }
  .nav-item:hover {
    background: rgba(255, 255, 255, 0.04);
    color: #cbd5e1;
  }
  .nav-ativo {
    background: rgba(52, 211, 153, 0.10) !important;
    color: #34d399 !important;
  }
</style>
