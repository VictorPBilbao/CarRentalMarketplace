<script lang="ts">
  import './login.css';
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
  let emailInicial = $derived(form?.email ?? '');

  // campos
  let email = $state('');
  let senha = $state('');
  let carregando = $state(false);

  $effect(() => {
    email = emailInicial;
  });

  // erros client-side (validação ao sair do campo)
  let erros = $state<Record<string, string>>({});
  let tocado = $state<Record<string, boolean>>({});

  // ── validações ──
  function validarEmail(v: string) {
    if (!v) return 'E-mail obrigatório';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'E-mail inválido';
    return '';
  }

  function validarSenha(v: string) {
    if (!v) return 'Senha obrigatória';
    if (v.length < 6) return 'Mínimo 6 caracteres';
    return '';
  }

  function blur(campo: string, valor: string) {
    tocado[campo] = true;
    erros[campo] = campo === 'email' ? validarEmail(valor) : validarSenha(valor);
  }

  function input(campo: string, valor: string) {
    if (tocado[campo]) {
      erros[campo] = campo === 'email' ? validarEmail(valor) : validarSenha(valor);
    }
  }
</script>

<svelte:head>
  <title>Login — CarRental Marketplace</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Saira:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
</svelte:head>

<div class="page login-page">

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
    <div class="login-box">

      <div class="login-header">
        <p class="login-label">Painel da locadora</p>
        {#if (form as any)?.stores}
          <h1>Selecione a filial</h1>
          <p class="login-sub">Você trabalha em mais de uma filial. Escolha com qual deseja entrar.</p>
        {:else}
          <h1>Entrar na sua conta</h1>
          <p class="login-sub">Acesse o painel para gerenciar sua frota e reservas.</p>
        {/if}
      </div>

      {#if (form as any)?.stores}
        <!-- ── seleção de filial para funcionários multi-loja ── -->
        <div class="store-selector">
          {#each (form as any).stores as store}
            <form method="POST" action="?/entrar" use:enhance={() => { carregando = true; return async ({ update }) => { await update(); carregando = false; }; }}>
              <input type="hidden" name="email"   value={(form as any).email} />
              <input type="hidden" name="senha"   value={(form as any).senha} />
              <input type="hidden" name="storeId" value={store.id} />
              <button type="submit" class="store-btn" disabled={carregando}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <rect x="1" y="5" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.3"/>
                  <path d="M4 5V4a4 4 0 018 0v1" stroke="currentColor" stroke-width="1.3"/>
                </svg>
                {store.name}
              </button>
            </form>
          {/each}
          <a href="/login" class="btn-voltar">← Voltar ao login</a>
        </div>
      {:else}

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

        <!-- erro geral vindo do server (ex: credenciais inválidas) -->
        {#if form?.erro}
          <div class="erro-geral">
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
              <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.4"/>
              <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            {form.erro}
          </div>
        {/if}

        <!-- E-MAIL -->
        <div
          class="form-group"
          class:has-error={(tocado.email && erros.email) || (form?.erros?.email && !tocado.email)}
        >
          <label for="email">E-mail</label>
          <input
            id="email"
            name="email"
            type="email"
            placeholder="seu@email.com"
            bind:value={email}
            autocomplete="email"
            onblur={() => blur('email', email)}
            oninput={() => input('email', email)}
          />
          {#if tocado.email && erros.email}
            <span class="campo-erro">{@render IconErro()}{erros.email}</span>
          {:else if form?.erros?.email && !tocado.email}
            <span class="campo-erro">{@render IconErro()}{form.erros.email}</span>
          {/if}
        </div>

        <!-- SENHA -->
        <div
          class="form-group"
          class:has-error={(tocado.senha && erros.senha) || (form?.erros?.senha && !tocado.senha)}
        >
          <div class="label-row">
            <label for="senha">Senha</label>
            <a href="/locadora/recuperar-senha" class="link-esqueci">Esqueci minha senha</a>
          </div>
          <input
            id="senha"
            name="senha"
            type="password"
            placeholder="••••••••"
            bind:value={senha}
            autocomplete="current-password"
            onblur={() => blur('senha', senha)}
            oninput={() => input('senha', senha)}
          />
          {#if tocado.senha && erros.senha}
            <span class="campo-erro">{@render IconErro()}{erros.senha}</span>
          {:else if form?.erros?.senha && !tocado.senha}
            <span class="campo-erro">{@render IconErro()}{form.erros.senha}</span>
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

      {/if}

      <p class="cadastro-link">
        Ainda não tem conta?
        <a href="/cadastro">Cadastre sua locadora</a>
      </p>

    </div>
  </main>

</div>

{#snippet IconErro()}
  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
    <path d="M6.5 1L12 11.5H1L6.5 1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
    <path d="M6.5 5v3M6.5 9.5h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
  </svg>
{/snippet}