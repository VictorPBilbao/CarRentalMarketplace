<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();

  const campos = $state({
    primeiroNome:    (form as any)?.campos?.primeiroNome    ?? '',
    sobrenome:       (form as any)?.campos?.sobrenome       ?? '',
    email:           (form as any)?.campos?.email           ?? '',
    telefone:        (form as any)?.campos?.telefone        ?? '',
    cpf:             (form as any)?.campos?.cpf             ?? '',
    dataNascimento:  (form as any)?.campos?.dataNascimento  ?? '',
    senha:           '',
    confirmarSenha:  '',
  });

  function mascararCPF(valor: string): string {
    return valor
      .replace(/\D/g, '')
      .slice(0, 11)
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3-$4');
  }

  function onCPFInput(e: Event) {
    const t = e.currentTarget as HTMLInputElement;
    t.value = mascararCPF(t.value);
    campos.cpf = t.value;
  }

  let carregando = $state(false);
  let tocado = $state<Record<string, boolean>>({});

  function blur(campo: string) { tocado[campo] = true; }

  function erroServidor(campo: string): string {
    return !tocado[campo] ? ((form as any)?.erros?.[campo] ?? '') : '';
  }
</script>

<svelte:head>
  <title>Criar Conta — CarRental</title>
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

      <div class="header">
        <p class="label">Área do Cliente</p>
        <h1>Criar sua conta</h1>
        <p class="sub">Preencha os dados abaixo para começar a alugar.</p>
      </div>

      <form
        method="POST"
        action="?/cadastrar"
        novalidate
        use:enhance={() => {
          carregando = true;
          return async ({ update }) => {
            await update();
            carregando = false;
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

        <div class="form-row">
          <div class="form-group" class:has-error={erroServidor('primeiroNome')}>
            <label for="primeiroNome">Primeiro nome</label>
            <input
              id="primeiroNome" name="primeiroNome" type="text" placeholder="João"
              bind:value={campos.primeiroNome} onblur={() => blur('primeiroNome')}
            />
            {#if erroServidor('primeiroNome')}
              <span class="campo-erro">{erroServidor('primeiroNome')}</span>
            {/if}
          </div>

          <div class="form-group" class:has-error={erroServidor('sobrenome')}>
            <label for="sobrenome">Sobrenome</label>
            <input
              id="sobrenome" name="sobrenome" type="text" placeholder="Silva"
              bind:value={campos.sobrenome} onblur={() => blur('sobrenome')}
            />
            {#if erroServidor('sobrenome')}
              <span class="campo-erro">{erroServidor('sobrenome')}</span>
            {/if}
          </div>
        </div>

        <div class="form-group" class:has-error={erroServidor('email')}>
          <label for="email">E-mail</label>
          <input
            id="email" name="email" type="email" placeholder="seu@email.com"
            bind:value={campos.email} onblur={() => blur('email')} autocomplete="email"
          />
          {#if erroServidor('email')}
            <span class="campo-erro">{erroServidor('email')}</span>
          {/if}
        </div>

        <div class="form-group">
          <label for="telefone">
            Telefone
            <span class="opcional">(opcional)</span>
          </label>
          <input
            id="telefone" name="telefone" type="tel" placeholder="+55 11 99999-9999"
            bind:value={campos.telefone}
          />
        </div>

        <div class="form-row">
          <div class="form-group" class:has-error={erroServidor('cpf')}>
            <label for="cpf">CPF</label>
            <input
              id="cpf" name="cpf" type="text" inputmode="numeric" placeholder="000.000.000-00"
              value={campos.cpf} oninput={onCPFInput} onblur={() => blur('cpf')}
              autocomplete="off"
            />
            {#if erroServidor('cpf')}
              <span class="campo-erro">{erroServidor('cpf')}</span>
            {/if}
          </div>

          <div class="form-group" style="width: 100%;" class:has-error={erroServidor('dataNascimento')}>
            <label for="dataNascimento">Data de nascimento</label>
            <input
              id="dataNascimento" name="dataNascimento" type="date"
              bind:value={campos.dataNascimento} onblur={() => blur('dataNascimento')}
              max={new Date(new Date().setFullYear(new Date().getFullYear() - 18)).toISOString().split('T')[0]}
            />
            {#if erroServidor('dataNascimento')}
              <span class="campo-erro">{erroServidor('dataNascimento')}</span>
            {/if}
          </div>
        </div>

        <div class="form-group" class:has-error={erroServidor('senha')}>
          <label for="senha">Senha</label>
          <input
            id="senha" name="senha" type="password" placeholder="Mínimo 6 caracteres"
            bind:value={campos.senha} onblur={() => blur('senha')} autocomplete="new-password"
          />
          {#if erroServidor('senha')}
            <span class="campo-erro">{erroServidor('senha')}</span>
          {/if}
        </div>

        <div class="form-group" class:has-error={erroServidor('confirmarSenha')}>
          <label for="confirmarSenha">Confirmar senha</label>
          <input
            id="confirmarSenha" name="confirmarSenha" type="password" placeholder="Repita a senha"
            bind:value={campos.confirmarSenha} onblur={() => blur('confirmarSenha')} autocomplete="new-password"
          />
          {#if erroServidor('confirmarSenha')}
            <span class="campo-erro">{erroServidor('confirmarSenha')}</span>
          {/if}
        </div>

        <button type="submit" class="btn-criar" disabled={carregando}>
          {#if carregando}
            <span class="spinner" aria-hidden="true"></span>
            Criando conta...
          {:else}
            Criar conta
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          {/if}
        </button>

      </form>

      <p class="link-login">
        Já tem conta?
        <a href="/cliente/login">Fazer login</a>
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
    font-family: 'Saira', sans-serif;
    font-size: 1.4rem; color: #e8eaf0; text-decoration: none;
    display: inline-flex; align-items: center; gap: 8px; letter-spacing: -0.02em;
  }
  .logo-icon { color: #a78bfa; }

  main {
    flex: 1; display: flex; align-items: center; justify-content: center;
    padding: 40px 24px 60px; position: relative; z-index: 1;
  }

  .box {
    width: 100%; max-width: 460px;
    animation: fadeUp 0.5s ease both;
  }

  .header { margin-bottom: 32px; text-align: center; }
  .label {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.13em;
    color: #a78bfa; margin-bottom: 12px; font-weight: 500;
  }
  .header h1 {
    font-family: 'Saira', sans-serif;
    font-size: 2.2rem; letter-spacing: -0.025em;
    color: #f0f2f8; margin-bottom: 10px; line-height: 1.1;
  }
  .sub { font-size: 0.9rem; color: rgba(232,234,240,0.48); font-weight: 300; line-height: 1.6; }

  form { display: flex; flex-direction: column; gap: 14px; margin-bottom: 20px; }

  .erro-geral {
    display: flex; align-items: center; gap: 8px;
    padding: 11px 14px;
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px; font-size: 0.85rem; color: #f87171;
  }

  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  .form-group { display: flex; flex-direction: column; gap: 7px; }
  .form-group label {
    font-size: 0.75rem; color: rgba(232,234,240,0.5);
    text-transform: uppercase; letter-spacing: 0.07em;
    display: flex; align-items: center; gap: 6px;
  }
  .opcional { font-size: 0.7rem; color: rgba(232,234,240,0.28); text-transform: none; letter-spacing: 0; font-weight: 400; }
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
  .form-group input[type="date"] { color-scheme: dark; }
  .form-group.has-error input {
    border-color: rgba(239,68,68,0.55);
    background: rgba(239,68,68,0.04);
  }
  .campo-erro { font-size: 0.78rem; color: #f87171; }

  .btn-criar {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    width: 100%; padding: 14px; margin-top: 4px;
    background: #7c3aed; color: #fff; border: none; border-radius: 10px;
    font-family: 'DM Sans', sans-serif; font-size: 0.95rem; font-weight: 500;
    cursor: pointer; transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  }
  .btn-criar:hover:not(:disabled) {
    background: #6d28d9; transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(124,58,237,0.32);
  }
  .btn-criar:disabled { opacity: 0.65; cursor: not-allowed; }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
    border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
  }

  .link-login {
    text-align: center; font-size: 0.875rem; color: rgba(232,234,240,0.45);
  }
  .link-login a { color: #a78bfa; text-decoration: none; font-weight: 500; }
  .link-login a:hover { color: #c4b5fd; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 520px) {
    .form-row { grid-template-columns: 1fr; }
    nav { padding: 20px 24px; }
    .header h1 { font-size: 1.9rem; }
  }
</style>
