<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const campos = $state({
    customerId:     (form as any)?.campos?.customerId     ?? '',
    categoryId:     (form as any)?.campos?.categoryId     ?? '',
    pickupStoreId:  (form as any)?.campos?.pickupStoreId  ?? '',
    dropoffStoreId: (form as any)?.campos?.dropoffStoreId ?? '',
    pickupTime:     (form as any)?.campos?.pickupTime     ?? '',
    dropoffTime:    (form as any)?.campos?.dropoffTime    ?? '',
    flightNumber:   (form as any)?.campos?.flightNumber   ?? '',
    notes:          (form as any)?.campos?.notes          ?? '',
    dailyRate:      (form as any)?.campos?.dailyRate      ?? '',
    fees:           (form as any)?.campos?.fees           ?? '0',
  });

  let carregando = $state(false);

  function erro(campo: string): string {
    return (form as any)?.erros?.[campo] ?? '';
  }
</script>

<svelte:head>
  <title>Nova Reserva — Filial</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/filial/reservas" class="breadcrumb">Reservas</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">Nova</span>
    <h1>Nova Reserva</h1>
  </div>
</div>

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<form method="POST" action="?/criar" use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}>

  <div class="form-grid">

    <!-- Cliente -->
    <div class="field full">
      <label for="customerId">ID do Cliente <span class="req">*</span></label>
      <input id="customerId" name="customerId" type="text" placeholder="user:abc123"
        bind:value={campos.customerId} class:input-erro={!!erro('customerId')} />
      {#if erro('customerId')}<p class="msg-erro">{erro('customerId')}</p>{/if}
    </div>

    <!-- Categoria -->
    <div class="field">
      <label for="categoryId">Categoria <span class="req">*</span></label>
      <select id="categoryId" name="categoryId" bind:value={campos.categoryId} class:input-erro={!!erro('categoryId')}>
        <option value="">Selecione...</option>
        {#each data.categorias as c}
          <option value={c.id}>{c.group_name} ({c.code})</option>
        {/each}
      </select>
      {#if erro('categoryId')}<p class="msg-erro">{erro('categoryId')}</p>{/if}
    </div>

    <!-- Diária -->
    <div class="field">
      <label for="dailyRate">Diária (R$) <span class="req">*</span></label>
      <input id="dailyRate" name="dailyRate" type="number" step="0.01" min="0"
        bind:value={campos.dailyRate} class:input-erro={!!erro('dailyRate')} />
      {#if erro('dailyRate')}<p class="msg-erro">{erro('dailyRate')}</p>{/if}
    </div>

    <!-- Loja retirada -->
    <div class="field">
      <label for="pickupStoreId">Loja de Retirada <span class="req">*</span></label>
      <select id="pickupStoreId" name="pickupStoreId" bind:value={campos.pickupStoreId} class:input-erro={!!erro('pickupStoreId')}>
        <option value="">Selecione...</option>
        {#each data.lojas as l}
          <option value={l.id}>{l.name} ({l.code})</option>
        {/each}
      </select>
      {#if erro('pickupStoreId')}<p class="msg-erro">{erro('pickupStoreId')}</p>{/if}
    </div>

    <!-- Loja devolução -->
    <div class="field">
      <label for="dropoffStoreId">Loja de Devolução <span class="req">*</span></label>
      <select id="dropoffStoreId" name="dropoffStoreId" bind:value={campos.dropoffStoreId} class:input-erro={!!erro('dropoffStoreId')}>
        <option value="">Selecione...</option>
        {#each data.lojas as l}
          <option value={l.id}>{l.name} ({l.code})</option>
        {/each}
      </select>
      {#if erro('dropoffStoreId')}<p class="msg-erro">{erro('dropoffStoreId')}</p>{/if}
    </div>

    <!-- Data retirada -->
    <div class="field">
      <label for="pickupTime">Data/Hora de Retirada <span class="req">*</span></label>
      <input id="pickupTime" name="pickupTime" type="datetime-local"
        bind:value={campos.pickupTime} class:input-erro={!!erro('pickupTime')} />
      {#if erro('pickupTime')}<p class="msg-erro">{erro('pickupTime')}</p>{/if}
    </div>

    <!-- Data devolução -->
    <div class="field">
      <label for="dropoffTime">Data/Hora de Devolução <span class="req">*</span></label>
      <input id="dropoffTime" name="dropoffTime" type="datetime-local"
        bind:value={campos.dropoffTime} class:input-erro={!!erro('dropoffTime')} />
      {#if erro('dropoffTime')}<p class="msg-erro">{erro('dropoffTime')}</p>{/if}
    </div>

    <!-- Taxas -->
    <div class="field">
      <label for="fees">Taxas (R$)</label>
      <input id="fees" name="fees" type="number" step="0.01" min="0"
        bind:value={campos.fees} />
    </div>

    <!-- Voo -->
    <div class="field">
      <label for="flightNumber">Número do Voo</label>
      <input id="flightNumber" name="flightNumber" type="text" placeholder="LA1234"
        bind:value={campos.flightNumber} />
    </div>

    <!-- Observações -->
    <div class="field full">
      <label for="notes">Observações</label>
      <textarea id="notes" name="notes" rows="3" bind:value={campos.notes}></textarea>
    </div>

  </div>

  <div class="form-acoes">
    <a href="/filial/reservas" class="btn-cancelar">Cancelar</a>
    <button type="submit" class="btn-criar" disabled={carregando}>
      {carregando ? 'Criando...' : 'Criar Reserva'}
    </button>
  </div>

</form>

<style>
  .page-header { margin-bottom: 28px; }
  .breadcrumb { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
  h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 6px 0 0; }

  .banner-erro {
    margin-bottom: 20px; padding: 12px 16px; border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.3); background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }

  form {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    max-width: 780px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }

  .field { display: flex; flex-direction: column; gap: 6px; }
  .field.full { grid-column: 1 / -1; }

  label {
    font-size: 12px; font-weight: 600;
    color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  }
  .req { color: #f87171; }

  input, select, textarea {
    background: #080c14;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px;
    color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
    transition: border-color 0.14s;
    width: 100%;
    box-sizing: border-box;
  }
  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: rgba(52,211,153,0.4);
  }
  .input-erro { border-color: rgba(248,113,113,0.5) !important; }
  .msg-erro { font-size: 11px; color: #f87171; margin: 0; }

  option { background: #0f172a; }
  textarea { resize: vertical; }

  .form-acoes {
    display: flex; gap: 10px; justify-content: flex-end;
    margin-top: 24px; padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.07);
  }

  .btn-cancelar {
    padding: 9px 20px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: transparent; color: #64748b;
    font-size: 13px; font-weight: 500; text-decoration: none;
    display: inline-flex; align-items: center;
    transition: all 0.14s;
  }
  .btn-cancelar:hover { border-color: rgba(255,255,255,0.2); color: #94a3b8; }

  .btn-criar {
    padding: 9px 24px; border-radius: 8px;
    border: none;
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff; font-size: 13px; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: opacity 0.14s;
  }
  .btn-criar:hover:not(:disabled) { opacity: 0.88; }
  .btn-criar:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
