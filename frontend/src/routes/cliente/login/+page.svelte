<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';
  import { page } from '$app/state';

  let { form }: { form: ActionData } = $props();

  const flash = $derived((page.data as any)?.flash ?? null);

  let email = $state((form as any)?.email ?? '');
  let senha = $state('');
  let carregando = $state(false);

  let erros = $state<Record<string, string>>({});
  let tocado = $state<Record<string, boolean>>({});

  function validarEmail(v: string) {
    if (!v) return 'E-mail obrigatório';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'E-mail inválido';
    return '';
  }

  function blur(campo: string, valor: string) {
    tocado[campo] = true;
    erros[campo] = campo === 'email' ? validarEmail(valor) : (valor ? '' : 'Senha obrigatória');
  }

  function input(campo: string, valor: string) {
    if (tocado[campo]) {
      erros[campo] = campo === 'email' ? validarEmail(valor) : (valor ? '' : 'Senha obrigatória');
    }
  }
</script>

<svelte:head>
  <title>Login do Cliente — CarRental</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet" />
</svelte:head>

<div class="page">

  <div class="bg" aria-hidden="true">
    <div class="grid-lines"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
  </div>

  <nav>
    <a href="/" class="logo">
      <span class="logo-icon">◈</span>
      CarRental
    </a>
  </nav>

  <main>
    <div class="box">

      {#if flash?.tipo === 'sucesso'}
        <div class="flash-sucesso">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style="flex-shrink:0">
            <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.3"/>
            <path d="M4.5 7.5l2 2 4-4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {flash.mensagem}
        </div>
      {/if}

      <div class="header">
        <p class="label">Área do Cliente</p>
        <h1>Entrar na sua conta</h1>
        <p class="sub">Acesse sua conta para gerenciar suas reservas.</p>
      </div>

      <form
        method="POST"
        action="?/entrar"
        novalidate
        use:enhance={() => {
          carregando = true;
          return async ({ update }) => {
            await update();
            carregando = false;
            senha = '';
          };
        }}
      >

        {#if (form as any)?.erro}
          <div class="erro-geral">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
              <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.4"/>
              <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            {(form as any).erro}
          </div>
        {/if}

        <div
          class="form-group"
          class:has-error={(tocado.email && erros.email) || ((form as any)?.erros?.email && !tocado.email)}
        >
          <label for="email">E-mail</label>
          <input
            id="email" name="email" type="email" placeholder="seu@email.com"
            bind:value={email} autocomplete="email"
            onblur={() => blur('email', email)}
            oninput={() => input('email', email)}
          />
          {#if tocado.email && erros.email}
            <span class="campo-erro">{erros.email}</span>
          {:else if (form as any)?.erros?.email && !tocado.email}
            <span class="campo-erro">{(form as any).erros.email}</span>
          {/if}
        </div>

        <div
          class="form-group"
          class:has-error={(tocado.senha && erros.senha) || ((form as any)?.erros?.senha && !tocado.senha)}
        >
          <label for="senha">Senha</label>
          <input
            id="senha" name="senha" type="password" placeholder="••••••••"
            bind:value={senha} autocomplete="current-password"
            onblur={() => blur('senha', senha)}
            oninput={() => input('senha', senha)}
          />
          {#if tocado.senha && erros.senha}
            <span class="campo-erro">{erros.senha}</span>
          {:else if (form as any)?.erros?.senha && !tocado.senha}
            <span class="campo-erro">{(form as any).erros.senha}</span>
          {/if}
        </div>

        <button type="submit" class="btn-entrar" disabled={carregando}>
          {#if carregando}
            <span class="spinner" aria-hidden="true"></span>
            Entrando...
          {:else}
            Entrar
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          {/if}
        </button>

      </form>

      <p class="link-cadastro">
        Ainda não tem conta?
        <a href="/cliente/cadastro">Criar conta gratuita</a>
      </p>

    </div>
  </main>

</div>

<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  .page {
    font-family: 'DM Sans', sans-serif;
    background: #080c14;
    color: #e8eaf0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
  .grid-lines {
    position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(167,139,250,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(167,139,250,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
  }
  .orb { position: absolute; border-radius: 50%; filter: blur(120px); }
  .orb-1 { width: 500px; height: 500px; background: rgba(124,58,237,0.18); top: -180px; left: -120px; }
  .orb-2 { width: 420px; height: 420px; background: rgba(167,139,250,0.12); bottom: -100px; right: -100px; }

  nav { position: relative; z-index: 10; padding: 24px 40px; }
  .logo {
    font-family: 'Instrument Serif', serif;
    font-size: 1.4rem; color: #e8eaf0; text-decoration: none;
    display: inline-flex; align-items: center; gap: 8px; letter-spacing: -0.02em;
  }
  .logo-icon { color: #a78bfa; }

  main {
    flex: 1; display: flex; align-items: center; justify-content: center;
    padding: 40px 24px 60px; position: relative; z-index: 1;
  }

  .box {
    width: 100%; max-width: 420px;
    animation: fadeUp 0.5s ease both;
  }

  .flash-sucesso {
    display: flex; align-items: center; gap: 8px;
    padding: 11px 14px; margin-bottom: 20px;
    background: rgba(167,139,250,0.08);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 8px; font-size: 0.85rem; color: #a78bfa;
  }

  .header { margin-bottom: 32px; text-align: center; }
  .label {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.13em;
    color: #a78bfa; margin-bottom: 12px; font-weight: 500;
  }
  .header h1 {
    font-family: 'Instrument Serif', serif;
    font-size: 2.2rem; letter-spacing: -0.025em;
    color: #f0f2f8; margin-bottom: 10px; line-height: 1.1;
  }
  .sub { font-size: 0.9rem; color: rgba(232,234,240,0.48); font-weight: 300; line-height: 1.6; }

  form { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }

  .erro-geral {
    display: flex; align-items: center; gap: 8px;
    padding: 11px 14px;
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px; font-size: 0.85rem; color: #f87171;
  }

  .form-group { display: flex; flex-direction: column; gap: 7px; }
  .form-group label {
    font-size: 0.75rem; color: rgba(232,234,240,0.5);
    text-transform: uppercase; letter-spacing: 0.07em;
  }
  .form-group input {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 13px 16px;
    color: #e8eaf0; font-family: 'DM Sans', sans-serif; font-size: 0.92rem;
    transition: border-color 0.2s, background 0.2s; outline: none; width: 100%;
  }
  .form-group input:focus {
    border-color: rgba(167,139,250,0.55);
    background: rgba(167,139,250,0.04);
  }
  .form-group input::placeholder { color: rgba(232,234,240,0.2); }
  .form-group.has-error input {
    border-color: rgba(239,68,68,0.55);
    background: rgba(239,68,68,0.04);
  }
  .campo-erro { font-size: 0.78rem; color: #f87171; }

  .btn-entrar {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    width: 100%; padding: 14px;
    background: #7c3aed; color: #fff; border: none; border-radius: 10px;
    font-family: 'DM Sans', sans-serif; font-size: 0.95rem; font-weight: 500;
    cursor: pointer; transition: background 0.2s, transform 0.15s, box-shadow 0.2s; margin-top: 4px;
  }
  .btn-entrar:hover:not(:disabled) {
    background: #6d28d9; transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(124,58,237,0.32);
  }
  .btn-entrar:disabled { opacity: 0.65; cursor: not-allowed; }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
    border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
  }

  .link-cadastro {
    text-align: center; font-size: 0.875rem; color: rgba(232,234,240,0.45);
  }
  .link-cadastro a { color: #a78bfa; text-decoration: none; font-weight: 500; }
  .link-cadastro a:hover { color: #c4b5fd; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 480px) {
    nav { padding: 20px 24px; }
    .header h1 { font-size: 1.9rem; }
  }
</style>
