<script lang="ts">
  import './cadastro.css';
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();

  // controle de etapa atual (1 = dados da empresa, 2 = dados de acesso)
  let etapa = $state(1);

  // campos etapa 1
  let nomeEmpresa  = $state('');
  let cnpj         = $state('');
  let telefone     = $state('');
  let cidade       = $state('');
  let estado       = $state('');

  // campos etapa 2
  let nomeResponsavel = $state('');
  let email           = $state('');
  let senha           = $state('');
  let confirmarSenha  = $state('');

  // erros por campo
  let erros = $state<Record<string, string>>({});
  let tocado = $state<Record<string, boolean>>({});

  // ── máscaras ──
  function mascaraCNPJ(v: string) {
    return v.replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '$1.$2')
      .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/\.(\d{3})(\d)/, '.$1/$2')
      .replace(/(\d{4})(\d)/, '$1-$2')
      .slice(0, 18);
  }

  function mascaraTelefone(v: string) {
    return v.replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{5})(\d)/, '$1-$2')
      .slice(0, 15);
  }

  // ── validações ──
  const regras: Record<string, (v: string) => string> = {
    nomeEmpresa:     v => v.trim().length < 3    ? 'Nome da empresa obrigatório'      : '',
    cnpj:            v => v.replace(/\D/g,'').length !== 14 ? 'CNPJ inválido'         : '',
    telefone:        v => v.replace(/\D/g,'').length < 10   ? 'Telefone inválido'     : '',
    cidade:          v => !v.trim()              ? 'Cidade obrigatória'               : '',
    estado:          v => !v                     ? 'Selecione um estado'              : '',
    nomeResponsavel: v => v.trim().length < 3    ? 'Nome do responsável obrigatório'  : '',
    email:           v => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? 'E-mail inválido'  : '',
    senha:           v => v.length < 8           ? 'Mínimo 8 caracteres'             : '',
    confirmarSenha:  v => v !== senha            ? 'As senhas não coincidem'          : '',
  };

  function validar(campo: string, valor: string) {
    erros[campo] = regras[campo]?.(valor) ?? '';
  }

  function blur(campo: string, valor: string) {
    tocado[campo] = true;
    validar(campo, valor);
  }

  function input(campo: string, valor: string) {
    if (tocado[campo]) validar(campo, valor);
  }

  const camposEtapa1 = ['nomeEmpresa', 'cnpj', 'telefone', 'cidade', 'estado'];
  const camposEtapa2 = ['nomeResponsavel', 'email', 'senha', 'confirmarSenha'];

  function avancarEtapa() {
    const valores: Record<string, string> = { nomeEmpresa, cnpj, telefone, cidade, estado };
    camposEtapa1.forEach(c => { tocado[c] = true; validar(c, valores[c]); });
    const temErro = camposEtapa1.some(c => erros[c]);
    if (!temErro) etapa = 2;
  }

  let carregando = $state(false);
</script>

<svelte:head>
  <title>Cadastro — CarRental Marketplace</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet" />
</svelte:head>

<div class="page cadastro-page">

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
    <a href="/locadora/login" class="nav-login">Já tenho conta</a>
  </nav>

  <main>
    <div class="cadastro-box">

      <!-- HEADER -->
      <div class="cadastro-header">
        <p class="cadastro-label">Cadastro gratuito</p>
        <h1>Cadastre sua locadora</h1>
        <p class="cadastro-sub">Comece a receber reservas das maiores redes em até 48h.</p>
      </div>

      <!-- STEPS INDICATOR -->
      <div class="steps-indicator">
        <div class="step-item" class:active={etapa >= 1} class:done={etapa > 1}>
          <div class="step-bubble">
            {#if etapa > 1}
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                <path d="M2 7l3.5 3.5L12 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            {:else}
              1
            {/if}
          </div>
          <span>Dados da empresa</span>
        </div>
        <div class="step-connector" class:done={etapa > 1}></div>
        <div class="step-item" class:active={etapa >= 2}>
          <div class="step-bubble">2</div>
          <span>Dados de acesso</span>
        </div>
      </div>

      <!-- ERRO DO SERVER -->
      {#if form?.erro}
        <div class="erro-geral">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          {form.erro}
        </div>
      {/if}

      <!-- FORM -->
      <form
        method="POST"
        action="?/cadastrar"
        use:enhance={() => {
          carregando = true;
          return async ({ update }) => {
            await update();
            carregando = false;
          };
        }}
      >

        <!-- ── ETAPA 1 ── -->
        {#if etapa === 1}
          <div class="etapa" >

            <div class="form-group" class:has-error={tocado.nomeEmpresa && erros.nomeEmpresa}>
              <label for="nomeEmpresa">Nome da empresa</label>
              <input
                id="nomeEmpresa" name="nomeEmpresa" type="text"
                placeholder="Ex: Locadora Central Ltda"
                bind:value={nomeEmpresa}
                onblur={() => blur('nomeEmpresa', nomeEmpresa)}
                oninput={() => input('nomeEmpresa', nomeEmpresa)}
              />
              {#if tocado.nomeEmpresa && erros.nomeEmpresa}
                <span class="campo-erro">{@render ErrIcon()}{erros.nomeEmpresa}</span>
              {/if}
            </div>

            <div class="form-group" class:has-error={tocado.cnpj && erros.cnpj}>
              <label for="cnpj">CNPJ</label>
              <input
                id="cnpj" name="cnpj" type="text"
                placeholder="00.000.000/0000-00"
                value={cnpj}
                onblur={() => blur('cnpj', cnpj)}
                oninput={(e) => {
                  cnpj = mascaraCNPJ((e.target as HTMLInputElement).value);
                  input('cnpj', cnpj);
                }}
              />
              {#if tocado.cnpj && erros.cnpj}
                <span class="campo-erro">{@render ErrIcon()}{erros.cnpj}</span>
              {/if}
            </div>

            <div class="form-group" class:has-error={tocado.telefone && erros.telefone}>
              <label for="telefone">Telefone</label>
              <input
                id="telefone" name="telefone" type="tel"
                placeholder="(00) 00000-0000"
                value={telefone}
                onblur={() => blur('telefone', telefone)}
                oninput={(e) => {
                  telefone = mascaraTelefone((e.target as HTMLInputElement).value);
                  input('telefone', telefone);
                }}
              />
              {#if tocado.telefone && erros.telefone}
                <span class="campo-erro">{@render ErrIcon()}{erros.telefone}</span>
              {/if}
            </div>

            <div class="form-row">
              <div class="form-group" class:has-error={tocado.cidade && erros.cidade}>
                <label for="cidade">Cidade</label>
                <input
                  id="cidade" name="cidade" type="text"
                  placeholder="Sua cidade"
                  bind:value={cidade}
                  onblur={() => blur('cidade', cidade)}
                  oninput={() => input('cidade', cidade)}
                />
                {#if tocado.cidade && erros.cidade}
                  <span class="campo-erro">{@render ErrIcon()}{erros.cidade}</span>
                {/if}
              </div>

              <div class="form-group" class:has-error={tocado.estado && erros.estado}>
                <label for="estado">Estado</label>
                <select
                  id="estado" name="estado"
                  bind:value={estado}
                  onblur={() => blur('estado', estado)}
                  onchange={() => input('estado', estado)}
                >
                  <option value="">UF</option>
                  {#each ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'] as uf}
                    <option value={uf}>{uf}</option>
                  {/each}
                </select>
                {#if tocado.estado && erros.estado}
                  <span class="campo-erro">{@render ErrIcon()}{erros.estado}</span>
                {/if}
              </div>
            </div>

            <button type="button" class="btn-avancar" onclick={avancarEtapa}>
              Próximo
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

          </div>
        {/if}

        <!-- ── ETAPA 2 ── -->
        {#if etapa === 2}
          <div class="etapa">

            <!-- campos ocultos da etapa 1 para o server receber tudo -->
            <input type="hidden" name="nomeEmpresa" value={nomeEmpresa} />
            <input type="hidden" name="cnpj" value={cnpj} />
            <input type="hidden" name="telefone" value={telefone} />
            <input type="hidden" name="cidade" value={cidade} />
            <input type="hidden" name="estado" value={estado} />

            <div class="form-group" class:has-error={tocado.nomeResponsavel && erros.nomeResponsavel}>
              <label for="nomeResponsavel">Seu nome</label>
              <input
                id="nomeResponsavel" name="nomeResponsavel" type="text"
                placeholder="Nome completo"
                bind:value={nomeResponsavel}
                onblur={() => blur('nomeResponsavel', nomeResponsavel)}
                oninput={() => input('nomeResponsavel', nomeResponsavel)}
              />
              {#if tocado.nomeResponsavel && erros.nomeResponsavel}
                <span class="campo-erro">{@render ErrIcon()}{erros.nomeResponsavel}</span>
              {/if}
            </div>

            <div class="form-group" class:has-error={tocado.email && erros.email}>
              <label for="email">E-mail</label>
              <input
                id="email" name="email" type="email"
                placeholder="seu@email.com"
                bind:value={email}
                onblur={() => blur('email', email)}
                oninput={() => input('email', email)}
              />
              {#if tocado.email && erros.email}
                <span class="campo-erro">{@render ErrIcon()}{erros.email}</span>
              {/if}
            </div>

            <div class="form-group" class:has-error={tocado.senha && erros.senha}>
              <label for="senha">Senha</label>
              <input
                id="senha" name="senha" type="password"
                placeholder="Mínimo 8 caracteres"
                bind:value={senha}
                onblur={() => blur('senha', senha)}
                oninput={() => { input('senha', senha); if (tocado.confirmarSenha) validar('confirmarSenha', confirmarSenha); }}
              />
              {#if tocado.senha && erros.senha}
                <span class="campo-erro">{@render ErrIcon()}{erros.senha}</span>
              {/if}
            </div>

            <div class="form-group" class:has-error={tocado.confirmarSenha && erros.confirmarSenha}>
              <label for="confirmarSenha">Confirmar senha</label>
              <input
                id="confirmarSenha" name="confirmarSenha" type="password"
                placeholder="Repita a senha"
                bind:value={confirmarSenha}
                onblur={() => blur('confirmarSenha', confirmarSenha)}
                oninput={() => input('confirmarSenha', confirmarSenha)}
              />
              {#if tocado.confirmarSenha && erros.confirmarSenha}
                <span class="campo-erro">{@render ErrIcon()}{erros.confirmarSenha}</span>
              {/if}
            </div>

            <div class="btn-group">
              <button type="button" class="btn-voltar" onclick={() => etapa = 1}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M13 8H3M7 4l-4 4 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Voltar
              </button>
              <button type="submit" class="btn-cadastrar" disabled={carregando}>
                {#if carregando}
                  <span class="spinner" aria-hidden="true"></span>
                  Cadastrando...
                {:else}
                  Criar conta
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                {/if}
              </button>
            </div>

            <p class="termos">
              Ao cadastrar, você concorda com nossos
              <a href="/termos">Termos de uso</a> e
              <a href="/privacidade">Política de privacidade</a>.
            </p>

          </div>
        {/if}

      </form>

      <p class="login-link">
        Já tem uma conta?
        <a href="/locadora/login">Entrar</a>
      </p>

    </div>
  </main>
</div>

<!-- snippet reutilizável do ícone de erro -->
{#snippet ErrIcon()}
  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
    <path d="M6.5 1L12 11.5H1L6.5 1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
    <path d="M6.5 5v3M6.5 9.5h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
  </svg>
{/snippet}