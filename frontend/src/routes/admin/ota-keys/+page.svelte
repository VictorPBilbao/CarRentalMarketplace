<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  $effect(() => { const m = (form as any)?.erro; if (m) notificacoes.erro(m); });
  $effect(() => { if ((form as any)?.revogadoSucesso) notificacoes.sucesso('Chave revogada com sucesso.'); });

  // Quando uma chave é gerada, exibe o modal uma única vez
  let chaveModal = $state<{ key: string; nome: string } | null>(null);
  let copiado    = $state(false);

  $effect(() => {
    const f = form as any;
    if (f?.chaveGerada && f?.chaveName) {
      chaveModal = { key: f.chaveGerada, nome: f.chaveName };
    }
  });

  async function copiarChave() {
    if (!chaveModal) return;
    await navigator.clipboard.writeText(chaveModal.key);
    copiado = true;
    setTimeout(() => { copiado = false; }, 2000);
  }
</script>

<svelte:head>
  <title>Chaves OTA — Admin</title>
</svelte:head>

<!-- Header -->
<div class="page-header">
  <div>
    <h1>Chaves OTA</h1>
    <p>Gerencie o acesso de parceiros (OTAs) à API pública</p>
  </div>
</div>

<!-- Formulário de criação -->
<div class="card" style="margin-bottom:20px;">
  <h3 class="card-title">Nova Chave</h3>
  <form method="POST" action="?/criar" use:enhance>
    <div class="form-row">
      <div class="field">
        <label for="name">Nome do Parceiro <span class="req">*</span></label>
        <input id="name" name="name" type="text" placeholder="Decolar.com, Booking.com..." />
      </div>
      <div class="field">
        <label for="company_id">Locadora (opcional)</label>
        <select id="company_id" name="company_id">
          <option value="">Todas as locadoras</option>
          {#each data.empresas as emp}
            <option value={emp.id}>{emp.nome}</option>
          {/each}
        </select>
      </div>
      <div class="field field-btn">
        <label>&nbsp;</label>
        <button type="submit" class="btn-criar">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 1v10M1 6h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          Gerar Chave
        </button>
      </div>
    </div>
  </form>
</div>

<!-- Tabela de chaves -->
<div class="card">
  <h3 class="card-title">Chaves Cadastradas</h3>
  {#if data.chaves.length === 0}
    <p style="font-size:13px; color:#475569; margin:0;">Nenhuma chave cadastrada ainda.</p>
  {:else}
    <div class="tabela-wrap">
      <table>
        <thead>
          <tr>
            <th>Parceiro</th>
            <th>Locadora</th>
            <th>Prévia da chave</th>
            <th>Status</th>
            <th>Criada em</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each data.chaves as chave}
            <tr class:linha-inativa={!chave.active}>
              <td class="td-nome">{chave.name}</td>
              <td class="td-empresa">
                {#if chave.company_name}
                  {chave.company_name}
                {:else}
                  <span style="color:#334155">Global</span>
                {/if}
              </td>
              <td>
                <code class="chave-preview">{chave.key_preview}</code>
              </td>
              <td>
                {#if chave.active}
                  <span class="badge badge-ativo">Ativa</span>
                {:else}
                  <span class="badge badge-inativo">Revogada</span>
                {/if}
              </td>
              <td class="td-data">
                {new Date(chave.created_at).toLocaleDateString('pt-BR')}
              </td>
              <td class="td-acao">
                {#if chave.active}
                  <form method="POST" action="?/revogar" use:enhance>
                    <input type="hidden" name="id" value={chave.id} />
                    <button type="submit" class="btn-revogar"
                      onclick={(e) => { if (!confirm(`Revogar chave de "${chave.name}"?`)) e.preventDefault(); }}
                    >
                      Revogar
                    </button>
                  </form>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- Modal: chave gerada -->
{#if chaveModal}
  <div class="overlay" role="dialog" aria-modal="true">
    <div class="modal">
      <div class="modal-icone">🔑</div>
      <h2 class="modal-titulo">Guarde sua chave!</h2>
      <p class="modal-desc">
        A chave completa de <strong>{chaveModal.nome}</strong> é exibida <strong>apenas agora</strong>.
        Após fechar este modal não será possível recuperá-la.
      </p>
      <div class="chave-box">
        <code>{chaveModal.key}</code>
        <button class="btn-copiar" onclick={copiarChave}>
          {copiado ? '✓ Copiado' : 'Copiar'}
        </button>
      </div>
      <button class="btn-fechar" onclick={() => { chaveModal = null; }}>
        Entendi, fechar
      </button>
    </div>
  </div>
{/if}

<style>
  .page-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:24px; }
  .page-header h1 { font-size:22px; font-weight:700; color:#f1f5f9; margin:0 0 4px; }
  .page-header p  { font-size:13px; color:#475569; margin:0; }

  .card {
    background:#0f172a; border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:20px 22px;
  }
  .card-title { font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.07em; color:#475569; margin:0 0 14px; }

  .form-row { display:flex; gap:12px; align-items:flex-end; flex-wrap:wrap; }
  .field { display:flex; flex-direction:column; gap:5px; flex:1; min-width:160px; }
  .field-btn { flex:0; min-width:auto; }
  label { font-size:13px; font-weight:500; color:#94a3b8; }
  .req  { color:#f87171; }
  input, select {
    padding:9px 12px; border-radius:9px;
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
    color:#f1f5f9; font-size:13px; font-family:inherit; width:100%; box-sizing:border-box;
  }
  input:focus, select:focus { outline:none; border-color:#f59e0b; }
  select option { background:#1e293b; }
  .btn-criar {
    display:inline-flex; align-items:center; gap:7px;
    padding:9px 18px; border-radius:9px; border:none;
    background:#f59e0b; color:#0a0a0a; font-size:13px; font-weight:700;
    cursor:pointer; font-family:inherit; white-space:nowrap;
    transition:background .14s;
  }
  .btn-criar:hover { background:#fbbf24; }

  .tabela-wrap { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; }
  thead tr { border-bottom:1px solid rgba(255,255,255,0.07); }
  th {
    text-align:left; padding:11px 12px;
    font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.07em; color:#334155;
  }
  td { padding:13px 12px; font-size:13px; border-bottom:1px solid rgba(255,255,255,0.04); }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr:hover td { background:rgba(255,255,255,0.015); }
  .linha-inativa td { opacity:.45; }

  .td-nome    { font-weight:500; color:#e2e8f0; }
  .td-empresa { color:#94a3b8; }
  .td-data    { color:#475569; font-size:12px; }
  .td-acao    { text-align:right; }

  .chave-preview {
    font-family:monospace; font-size:12px;
    background:rgba(255,255,255,0.05); padding:3px 8px; border-radius:5px; color:#94a3b8;
  }

  .badge {
    display:inline-block; padding:3px 9px; border-radius:20px;
    font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.05em;
  }
  .badge-ativo  { background:rgba(74,222,128,0.1);  color:#4ade80; }
  .badge-inativo{ background:rgba(100,116,139,0.1); color:#64748b; }

  .btn-revogar {
    padding:5px 11px; border-radius:7px; border:1px solid rgba(248,113,113,0.3);
    background:transparent; color:#f87171; font-size:12px; cursor:pointer; font-family:inherit;
    transition:all .14s;
  }
  .btn-revogar:hover { background:rgba(248,113,113,0.08); border-color:rgba(248,113,113,0.6); }

  /* ── Modal ── */
  .overlay {
    position:fixed; inset:0; background:rgba(0,0,0,0.7);
    display:flex; align-items:center; justify-content:center; z-index:100;
  }
  .modal {
    background:#0f172a; border:1px solid rgba(245,158,11,0.3);
    border-radius:16px; padding:32px 28px; max-width:480px; width:90%;
    display:flex; flex-direction:column; align-items:center; text-align:center;
  }
  .modal-icone { font-size:36px; margin-bottom:12px; }
  .modal-titulo { font-size:18px; font-weight:700; color:#f1f5f9; margin:0 0 10px; }
  .modal-desc {
    font-size:13px; color:#94a3b8; line-height:1.6; margin:0 0 20px;
  }
  .modal-desc strong { color:#e2e8f0; }
  .chave-box {
    display:flex; align-items:center; gap:10px;
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
    border-radius:10px; padding:12px 14px; width:100%; box-sizing:border-box;
    margin-bottom:20px;
  }
  .chave-box code {
    font-family:monospace; font-size:13px; color:#f59e0b;
    flex:1; word-break:break-all; text-align:left;
  }
  .btn-copiar {
    padding:6px 14px; border-radius:7px; border:1px solid rgba(245,158,11,0.4);
    background:transparent; color:#f59e0b; font-size:12px; font-weight:600;
    cursor:pointer; font-family:inherit; white-space:nowrap; transition:all .14s; flex-shrink:0;
  }
  .btn-copiar:hover { background:rgba(245,158,11,0.1); }
  .btn-fechar {
    padding:10px 28px; border-radius:10px; border:none;
    background:#f59e0b; color:#0a0a0a; font-size:14px; font-weight:700;
    cursor:pointer; font-family:inherit; transition:background .14s;
  }
  .btn-fechar:hover { background:#fbbf24; }
</style>
