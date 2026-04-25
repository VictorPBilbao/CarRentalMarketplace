<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { LayoutData } from './$types';
  import { page } from '$app/state';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();

  const usuario = $derived(data.usuario);

  const iniciais = $derived(
    usuario?.nome
      ? usuario.nome.split(' ').slice(0, 2).map((n: string) => n[0]).join('').toUpperCase()
      : '?'
  );

  const paginaTitulo: Record<string, string> = {
    '/locadora/dashboard':     'Dashboard',
    '/locadora/filiais':       'Filiais',
    '/locadora/frota':         'Frota',
    '/locadora/reservas':      'Reservas',
    '/locadora/contratos':     'Contratos',
    '/locadora/tarifas':       'Tarifas',
    '/locadora/adicionais':    'Adicionais',
    '/locadora/protecoes':     'Proteções',
    '/locadora/configuracoes': 'Configurações',
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

    <!-- Logo — altura fixa, não encolhe -->
    <a
      href="/locadora/dashboard"
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
      <span style="color:#60a5fa; font-size:18px;">◈</span>
      CarRental
    </a>

    <!-- Nav — flex-1 + min-height:0 permite overflow funcionar -->
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

      <a href="/locadora/dashboard" class="nav-item {ativo('/locadora/dashboard') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <rect x="1" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="1" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        Dashboard
      </a>

      <p class="nav-label" style="margin-top:12px;">Operações</p>

      <a href="/locadora/filiais" class="nav-item {ativo('/locadora/filiais') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M2 13V6.5L7.5 2 13 6.5V13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <rect x="5.5" y="9" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        Filiais
      </a>

      <a href="/locadora/frota" class="nav-item {ativo('/locadora/frota') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M1.5 7L3 3.5h9L13.5 7M1.5 7v4a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V10.5h8v.5a.5.5 0 00.5.5h1a.5.5 0 00.5-.5V7M1.5 7h13" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="4" cy="9" r="0.8" fill="currentColor"/>
          <circle cx="11" cy="9" r="0.8" fill="currentColor"/>
        </svg>
        Frota
      </a>

      <a href="/locadora/reservas" class="nav-item {ativo('/locadora/reservas') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <rect x="2" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 1.5v2M10 1.5v2M2 6.5h11" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        Reservas
      </a>

      <a href="/locadora/contratos" class="nav-item {ativo('/locadora/contratos') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M4 1.5h5L12 4.5v9H3v-12z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <path d="M9 1.5V4.5H12M5.5 7.5h4M5.5 10h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        Contratos
      </a>

      <p class="nav-label" style="margin-top:12px;">Configurações</p>

      <a href="/locadora/tarifas" class="nav-item {ativo('/locadora/tarifas') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M8 1.5L13.5 7l-5.5 5.5L2.5 7 2 1.5H8z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
          <circle cx="5" cy="5" r="1" fill="currentColor"/>
        </svg>
        Tarifas
      </a>

      <a href="/locadora/adicionais" class="nav-item {ativo('/locadora/adicionais') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M5.5 2.5v1a1 1 0 01-2 0v-1H1.5v4h1a1 1 0 010 2h-1v4h3.5v-1a1 1 0 012 0v1h4v-3h-1a1 1 0 010-2h1V2.5h-5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
        Adicionais
      </a>

      <a href="/locadora/protecoes" class="nav-item {ativo('/locadora/protecoes') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <path d="M7.5 1.5L2 4v4.5c0 3 2.5 5 5.5 5.5 3-.5 5.5-2.5 5.5-5.5V4L7.5 1.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
        Proteções
      </a>

      <a href="/locadora/configuracoes" class="nav-item {ativo('/locadora/configuracoes') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <circle cx="7.5" cy="7.5" r="2" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7.5 1.5v1M7.5 12.5v1M1.5 7.5h1M12.5 7.5h1M3.4 3.4l.7.7M10.9 10.9l.7.7M3.4 11.6l.7-.7M10.9 4.1l.7-.7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        Configurações
      </a>

    </nav>

    <!-- Footer — altura fixa, fixado no fundo -->
    <div style="
      flex-shrink: 0;
      padding: 14px;
      border-top: 1px solid rgba(255,255,255,0.07);
    ">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="
          width:34px; height:34px;
          border-radius:50%;
          background:linear-gradient(135deg,#3b82f6,#6366f1);
          display:flex; align-items:center; justify-content:center;
          font-size:12px; font-weight:700; color:#fff;
          flex-shrink:0;
        ">{iniciais}</div>
        <div style="overflow:hidden;">
          <p style="font-size:13px; font-weight:500; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{usuario?.nome ?? ''}</p>
          <p style="font-size:11px; color:#475569; margin-top:1px;">Locadora</p>
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
        <span>Locadora</span>
        <span style="color:#1e293b;">/</span>
        <span style="color:#94a3b8; font-weight:500;">{titulo}</span>
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="
          background:rgba(96,165,250,0.12);
          color:#60a5fa;
          font-size:11px; font-weight:600;
          padding:3px 9px;
          border-radius:20px;
          text-transform:uppercase;
          letter-spacing:0.05em;
        ">Matriz</span>
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
    background: rgba(96, 165, 250, 0.12) !important;
    color: #60a5fa !important;
  }
</style>
