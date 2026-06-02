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
    '/admin/dashboard': 'Dashboard',
    '/admin/ota-keys':  'Chaves OTA',
  };
  const titulo = $derived(paginaTitulo[page.url.pathname] ?? 'Admin');

  function ativo(href: string): boolean {
    return page.url.pathname.startsWith(href);
  }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div style="display:flex; min-height:100vh; background:#080c14; font-family:'DM Sans',sans-serif; color:#f1f5f9;">

  <!-- SIDEBAR -->
  <aside style="
    position:fixed; top:0; left:0;
    width:224px; height:100vh;
    display:flex; flex-direction:column;
    background:#0f172a;
    border-right:1px solid rgba(255,255,255,0.07);
    z-index:20;
  ">
    <a href="/admin/dashboard" style="
      flex-shrink:0; display:flex; align-items:center; gap:10px;
      padding:20px; border-bottom:1px solid rgba(255,255,255,0.07);
      text-decoration:none; color:#f1f5f9; font-weight:600; font-size:15px;
    ">
      <span style="color:#f59e0b; font-size:18px;">◈</span>
      CarRental
    </a>

    <nav style="flex:1; min-height:0; overflow-y:auto; padding:12px 10px; display:flex; flex-direction:column; gap:2px;">
      <p class="nav-label">Sistema</p>

      <a href="/admin/dashboard" class="nav-item {ativo('/admin/dashboard') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <rect x="1" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="1" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        Dashboard
      </a>

      <p class="nav-label" style="margin-top:12px;">Integrações</p>

      <a href="/admin/ota-keys" class="nav-item {ativo('/admin/ota-keys') ? 'nav-ativo' : ''}">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
          <circle cx="5" cy="10" r="3" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7.5 10h5.5M11 8.5v3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          <path d="M5 7V4.5L8.5 2 12 4.5V7" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
        </svg>
        Chaves OTA
      </a>
    </nav>

    <div style="flex-shrink:0; padding:14px; border-top:1px solid rgba(255,255,255,0.07);">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div style="
          width:34px; height:34px; border-radius:50%;
          background:linear-gradient(135deg,#f59e0b,#f97316);
          display:flex; align-items:center; justify-content:center;
          font-size:12px; font-weight:700; color:#fff; flex-shrink:0;
        ">{iniciais}</div>
        <div style="overflow:hidden;">
          <p style="font-size:13px; font-weight:500; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{usuario?.nome ?? ''}</p>
          <p style="font-size:11px; color:#475569; margin-top:1px;">Administrador</p>
        </div>
      </div>
      <form method="POST" action="/login?/sair">
        <button type="submit" style="
          display:flex; align-items:center; gap:8px; width:100%; padding:8px 10px;
          border-radius:8px; border:1px solid rgba(255,255,255,0.08);
          background:transparent; color:#64748b; font-size:13px; cursor:pointer; font-family:inherit;
          transition:all 0.14s;
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

  <!-- MAIN -->
  <div style="margin-left:224px; flex:1; display:flex; flex-direction:column; min-width:0;">
    <header style="
      position:sticky; top:0; z-index:10; height:52px;
      display:flex; align-items:center; justify-content:space-between;
      padding:0 28px; background:#0f172a;
      border-bottom:1px solid rgba(255,255,255,0.07); flex-shrink:0;
    ">
      <div style="font-size:13px; color:#475569; display:flex; align-items:center; gap:6px;">
        <span>Admin</span>
        <span style="color:#1e293b;">/</span>
        <span style="color:#94a3b8; font-weight:500;">{titulo}</span>
      </div>
      <span style="
        background:rgba(245,158,11,0.12); color:#f59e0b;
        font-size:11px; font-weight:600; padding:3px 9px;
        border-radius:20px; text-transform:uppercase; letter-spacing:0.05em;
      ">Admin</span>
    </header>

    <main style="flex:1; padding:28px; min-width:0;">
      {@render children()}
    </main>
  </div>

</div>

<style>
  .nav-label {
    font-size:10px; font-weight:600; text-transform:uppercase;
    letter-spacing:0.09em; color:#334155; padding:4px 10px;
  }
  .nav-item {
    display:flex; align-items:center; gap:10px; padding:8px 10px;
    border-radius:8px; color:#64748b; font-size:14px; font-weight:500;
    text-decoration:none; transition:background 0.14s, color 0.14s;
  }
  .nav-item:hover { background:rgba(255,255,255,0.04); color:#cbd5e1; }
  .nav-ativo { background:rgba(245,158,11,0.12) !important; color:#f59e0b !important; }
</style>
