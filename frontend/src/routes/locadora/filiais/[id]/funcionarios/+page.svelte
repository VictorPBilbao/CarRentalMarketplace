<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageData, ActionData } from './$types';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  $effect(() => { const m = (data as any)?.erro; if (m) notificacoes.erro(m); });
  $effect(() => { const m = (form as any)?.erro; if (m) notificacoes.erro(m); });
  $effect(() => { if ((form as any)?.sucesso) notificacoes.sucesso('Funcionário cadastrado com sucesso.'); });

  const filial        = $derived(data.filial);
  const funcionarios  = $derived(data.funcionarios ?? []);
  const outrasFiliais = $derived((data as any).outrasFiliais ?? []);
  const erros         = $derived((form as any)?.erros  ?? {});
  const erroGlobal    = $derived((form as any)?.erro   ?? null);
  const campos        = $derived((form as any)?.campos ?? {});

  const ROLES = [
    { value: 'CLERK',    label: 'Atendente'  },
    { value: 'MANAGER',  label: 'Gerente'    },
    { value: 'MECHANIC', label: 'Mecânico'   },
  ];

  const ROLE_COR: Record<string, string> = {
    MANAGER:  'bg-blue-400/10 text-blue-400',
    CLERK:    'bg-emerald-400/10 text-emerald-400',
    MECHANIC: 'bg-amber-400/10 text-amber-400',
  };

  let enviando    = $state(false);
  let removendo   = $state<string | null>(null);
  let mostrarForm = $state(false);

  let extraStoreIds = $state<string[]>((form as any)?.campos?.extraStoreIds ?? []);
  const extraStoreIdsJSON = $derived(JSON.stringify(extraStoreIds));

  function toggleStore(id: string) {
    extraStoreIds = extraStoreIds.includes(id)
      ? extraStoreIds.filter((x) => x !== id)
      : [...extraStoreIds, id];
  }
</script>

<svelte:head>
  <title>Funcionários{filial ? ` — ${filial.name}` : ''} — CarRental</title>
</svelte:head>

<!-- ── cabeçalho ── -->
<div class="page-header">
  <div class="page-header-info">
    <a href="/locadora/filiais" class="breadcrumb">Filiais</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">{filial?.name ?? '...'}</span>
    <h1>Funcionários</h1>
    <p>Gerencie os funcionários desta filial</p>
  </div>
  <a href="/locadora/filiais/{encodeURIComponent(data.filial?.id ?? '')}/editar" class="btn-sec">
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M9 2l2 2-7 7H2V9l7-7z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
    </svg>
    Editar Filial
  </a>
</div>

<!-- ── formulário de novo funcionário ── -->
<div class="secao">
  <div class="secao-header">
    <p class="secao-titulo">Adicionar Funcionário</p>
    <button type="button" class="btn-toggle" onclick={() => mostrarForm = !mostrarForm}>
      {#if mostrarForm}
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Ocultar
      {:else}
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 2v9M2 6.5h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Novo Funcionário
      {/if}
    </button>
  </div>

  {#if mostrarForm}
    <form method="POST" action="?/criar"
      use:enhance={() => {
        enviando = true;
        return async ({ update }) => {
          await update();
          enviando = false;
          mostrarForm = Object.keys(erros).length > 0 || !!erroGlobal;
          if (!mostrarForm) extraStoreIds = [];
        };
      }}
    >
      <input type="hidden" name="extraStoreIds" value={extraStoreIdsJSON} />
      <div class="form-grid">

        <div class="campo">
          <label for="firstName">Nome <span class="obrigatorio">*</span></label>
          <input id="firstName" name="firstName" type="text" placeholder="João"
            value={campos.firstName ?? ''} class={erros.firstName ? 'erro' : ''} />
          {#if erros.firstName}<span class="erro-msg">{erros.firstName}</span>{/if}
        </div>

        <div class="campo">
          <label for="lastName">Sobrenome <span class="obrigatorio">*</span></label>
          <input id="lastName" name="lastName" type="text" placeholder="Silva"
            value={campos.lastName ?? ''} class={erros.lastName ? 'erro' : ''} />
          {#if erros.lastName}<span class="erro-msg">{erros.lastName}</span>{/if}
        </div>

        <div class="campo">
          <label for="email">E-mail <span class="obrigatorio">*</span></label>
          <input id="email" name="email" type="email" placeholder="funcionario@empresa.com"
            value={campos.email ?? ''} class={erros.email ? 'erro' : ''} />
          {#if erros.email}<span class="erro-msg">{erros.email}</span>{/if}
        </div>

        <div class="campo">
          <label for="senha">Senha <span class="obrigatorio">*</span></label>
          <input id="senha" name="senha" type="password" placeholder="Mínimo 6 caracteres"
            class={erros.senha ? 'erro' : ''} />
          {#if erros.senha}<span class="erro-msg">{erros.senha}</span>{/if}
        </div>

        <div class="campo">
          <label for="role">Cargo <span class="obrigatorio">*</span></label>
          <select id="role" name="role">
            {#each ROLES as r}
              <option value={r.value} selected={(campos.role ?? 'CLERK') === r.value}>{r.label}</option>
            {/each}
          </select>
        </div>

        {#if outrasFiliais.length > 0}
          <div class="campo campo-full">
            <label>Também trabalha em</label>
            <div class="filiais-checks">
              {#each outrasFiliais as f}
                <label class="check-item {extraStoreIds.includes(f.id) ? 'check-ativo' : ''}">
                  <input type="checkbox" checked={extraStoreIds.includes(f.id)}
                    onchange={() => toggleStore(f.id)} />
                  {f.name} <span class="check-code">({f.code})</span>
                </label>
              {/each}
            </div>
          </div>
        {/if}

        <div class="campo campo-acao">
          <button type="submit" class="btn-salvar" disabled={enviando}>
            {#if enviando}
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="animation:spin 0.8s linear infinite">
                <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" stroke-width="1.5" stroke-dasharray="20 12"/>
              </svg>
              Salvando...
            {:else}
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M2 7l3.5 3.5 5.5-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Cadastrar
            {/if}
          </button>
        </div>

      </div>
    </form>
  {/if}
</div>

<!-- ── tabela de funcionários ── -->
<div class="tabela-container">

  <div class="tabela-header">
    <h2>Equipe da Filial</h2>
    <span class="contador">{funcionarios.length} funcionário{funcionarios.length !== 1 ? 's' : ''}</span>
  </div>

  {#if funcionarios.length === 0}
    <div class="vazio">
      <div class="vazio-icone">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <circle cx="14" cy="10" r="5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M4 24c0-5.523 4.477-10 10-10s10 4.477 10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="vazio-titulo">Nenhum funcionário cadastrado</p>
      <p class="vazio-desc">Adicione funcionários para que possam acessar o sistema desta filial.</p>
    </div>
  {:else}
    <div class="overflow-x">
      <table>
        <thead>
          <tr>
            <th>Funcionário</th>
            <th>E-mail</th>
            <th>Cargo</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each funcionarios as f}
            <tr>
              <td>
                <p class="td-nome">{f.first_name} {f.last_name}</p>
              </td>
              <td>
                <p class="td-principal">{f.email}</p>
              </td>
              <td>
                <span class="badge {ROLE_COR[f.role] ?? 'bg-slate-400/10 text-slate-400'}">
                  {ROLES.find(r => r.value === f.role)?.label ?? f.role}
                </span>
              </td>
              <td>
                {#if f.active}
                  <span class="badge bg-emerald-400/10 text-emerald-400">Ativo</span>
                {:else}
                  <span class="badge bg-slate-400/10 text-slate-500">Inativo</span>
                {/if}
              </td>
              <td class="td-acoes">
                <form method="POST" action="?/remover"
                  use:enhance={() => {
                    removendo = f.id;
                    return async ({ update }) => { await update(); removendo = null; };
                  }}
                >
                  <input type="hidden" name="userId" value={f.id} />
                  <button type="submit" class="btn-remover" disabled={removendo === f.id}>
                    {#if removendo === f.id}
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="animation:spin 0.8s linear infinite">
                        <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.3" stroke-dasharray="16 8"/>
                      </svg>
                    {:else}
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <path d="M2 3h9M5 3V2h3v1M4 3l.5 8M9 3l-.5 8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    {/if}
                    Remover
                  </button>
                </form>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

</div>

<style>
  /* ── breadcrumb ── */
  .breadcrumb { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }

  /* ── header ── */
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 28px; gap: 16px;
  }
  .page-header-info { display: flex; flex-direction: column; gap: 2px; }
  .page-header-info h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .page-header-info p  { font-size: 13px; color: #475569; margin: 0; }

  /* ── botões de cabeçalho ── */
  .btn-sec {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 9px 16px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: transparent; color: #94a3b8;
    font-size: 13px; font-family: 'DM Sans', sans-serif;
    text-decoration: none; cursor: pointer;
    transition: border-color 0.14s, color 0.14s;
    white-space: nowrap;
  }
  .btn-sec:hover { border-color: rgba(255,255,255,0.2); color: #cbd5e1; }

  /* ── seção do formulário ── */
  .secao {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .secao-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0;
  }
  .secao-titulo {
    font-size: 12px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #475569; margin: 0;
  }
  .btn-toggle {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 6px 12px; border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.09);
    background: transparent; color: #60a5fa;
    font-size: 12px; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: border-color 0.14s;
  }
  .btn-toggle:hover { border-color: rgba(96,165,250,0.3); }

  /* ── formulário ── */
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr auto;
    gap: 14px;
    align-items: end;
    margin-top: 20px;
  }
  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo label { font-size: 12px; font-weight: 500; color: #94a3b8; }
  .campo label .obrigatorio { color: #f87171; margin-left: 2px; }
  .campo input, .campo select {
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    padding: 9px 12px;
    transition: border-color 0.14s, box-shadow 0.14s;
    outline: none;
    width: 100%;
    box-sizing: border-box;
  }
  .campo input::placeholder { color: #334155; }
  .campo input:focus, .campo select:focus {
    border-color: rgba(96,165,250,0.5);
    box-shadow: 0 0 0 3px rgba(96,165,250,0.08);
  }
  .campo select option { background: #0f172a; }
  .campo input.erro { border-color: rgba(248,113,113,0.5); }
  .campo .erro-msg { font-size: 11px; color: #f87171; }
  .campo-acao  { justify-content: flex-end; }
  .campo-full  { grid-column: 1 / -1; }

  /* ── multi-loja checkboxes ── */
  .filiais-checks {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .check-item {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    border-radius: 7px;
    border: 1px solid rgba(255,255,255,0.09);
    background: #080c14;
    font-size: 12px;
    color: #64748b;
    cursor: pointer;
    transition: border-color 0.14s, color 0.14s, background 0.14s;
  }
  .check-item input[type="checkbox"] { display: none; }
  .check-item:hover { border-color: rgba(96,165,250,0.3); color: #94a3b8; }
  .check-ativo {
    border-color: rgba(96,165,250,0.5);
    background: rgba(96,165,250,0.07);
    color: #93c5fd;
  }
  .check-code { color: #334155; font-size: 11px; }

  /* ── botões de ação no form ── */
  .btn-salvar {
    padding: 9px 20px; border-radius: 8px; border: none;
    background: #3b82f6; color: #fff;
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
    transition: background 0.14s, opacity 0.14s; white-space: nowrap;
  }
  .btn-salvar:hover { background: #2563eb; }
  .btn-salvar:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── tabela ── */
  .tabela-container {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 40px;
  }
  .tabela-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .tabela-header h2 { font-size: 14px; font-weight: 600; color: #e2e8f0; margin: 0; }
  .contador { font-size: 12px; color: #475569; }

  .overflow-x { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
  th {
    padding: 11px 16px; text-align: left;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em; color: #475569;
  }
  td { padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.03); }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.015); }

  .td-nome { font-size: 13px; font-weight: 500; color: #e2e8f0; margin: 0; }
  .td-principal { font-size: 13px; color: #94a3b8; margin: 0; }
  .td-acoes { text-align: right; }

  .badge {
    display: inline-flex; align-items: center;
    padding: 3px 8px; border-radius: 5px;
    font-size: 11px; font-weight: 600;
  }

  /* ── botão remover ── */
  .btn-remover {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 6px 10px; border-radius: 7px;
    border: 1px solid rgba(248,113,113,0.2);
    background: transparent; color: #f87171;
    font-size: 12px; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: border-color 0.14s, background 0.14s;
  }
  .btn-remover:hover { border-color: rgba(248,113,113,0.4); background: rgba(248,113,113,0.05); }
  .btn-remover:disabled { opacity: 0.4; cursor: not-allowed; }

  /* ── estado vazio ── */
  .vazio {
    display: flex; flex-direction: column; align-items: center;
    padding: 48px 24px; gap: 10px;
  }
  .vazio-icone {
    width: 56px; height: 56px; border-radius: 14px;
    background: rgba(255,255,255,0.04);
    display: flex; align-items: center; justify-content: center;
    color: #334155; margin-bottom: 4px;
  }
  .vazio-titulo { font-size: 14px; font-weight: 600; color: #475569; margin: 0; }
  .vazio-desc { font-size: 13px; color: #334155; margin: 0; text-align: center; }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
