<script lang="ts">
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  function v(key: string, fb = '') {
    return (form as any)?.campos?.[key] ?? fb;
  }
  function err(key: string): string {
    return (form as any)?.erros?.[key] ?? '';
  }

  let pickupTime  = $state(v('pickupTime'));
  let dropoffTime = $state(v('dropoffTime'));
  let dailyRate   = $state(parseFloat(v('dailyRate', '0')) || 0);
  let fees        = $state(parseFloat(v('fees', '0')) || 0);

  const totalDias = $derived(() => {
    if (!pickupTime || !dropoffTime) return 0;
    const p = new Date(pickupTime);
    const d = new Date(dropoffTime);
    if (d <= p) return 0;
    return Math.max(1, Math.ceil((d.getTime() - p.getTime()) / 86_400_000));
  });

  const totalValor = $derived(() => {
    const dias = totalDias();
    return dias > 0 ? dailyRate * dias + fees : 0;
  });
</script>

<svelte:head>
  <title>Nova Reserva — Locadora</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/reservas" class="breadcrumb">Reservas</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">Nova Reserva</span>
    <h1>Nova Reserva</h1>
    <p>Cadastre uma nova reserva para um cliente</p>
  </div>
</div>

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<form method="POST" action="?/criar" class="form-wrap">

  <!-- Cliente -->
  <div class="section-card">
    <h2 class="section-title">Cliente</h2>
    <div class="campo-group">
      <div class="campo">
        <label for="customerId">ID do Cliente</label>
        <input
          id="customerId" name="customerId" type="text"
          placeholder="user:abc123..."
          value={v('customerId')}
          class:erro={!!err('customerId')}
        />
        {#if err('customerId')}<span class="erro-msg">{err('customerId')}</span>{/if}
      </div>
    </div>
  </div>

  <!-- Veículo -->
  <div class="section-card">
    <h2 class="section-title">Veículo</h2>
    <div class="campo-group">
      <div class="campo">
        <label for="categoryId">Categoria</label>
        <select id="categoryId" name="categoryId" class:erro={!!err('categoryId')}>
          <option value="">Selecione uma categoria</option>
          {#each data.categorias as cat (cat.id)}
            <option value={cat.id} selected={v('categoryId') === cat.id}>
              {cat.group_name} — {cat.code}
            </option>
          {/each}
        </select>
        {#if err('categoryId')}<span class="erro-msg">{err('categoryId')}</span>{/if}
      </div>
    </div>
  </div>

  <!-- Lojas -->
  <div class="section-card">
    <h2 class="section-title">Lojas</h2>
    <div class="campo-group campo-2col">
      <div class="campo">
        <label for="pickupStoreId">Loja de Retirada</label>
        <select id="pickupStoreId" name="pickupStoreId" class:erro={!!err('pickupStoreId')}>
          <option value="">Selecione a loja</option>
          {#each data.lojas as loja (loja.id)}
            <option value={loja.id} selected={v('pickupStoreId') === loja.id}>
              {loja.name} ({loja.code})
            </option>
          {/each}
        </select>
        {#if err('pickupStoreId')}<span class="erro-msg">{err('pickupStoreId')}</span>{/if}
      </div>
      <div class="campo">
        <label for="dropoffStoreId">Loja de Devolução</label>
        <select id="dropoffStoreId" name="dropoffStoreId" class:erro={!!err('dropoffStoreId')}>
          <option value="">Selecione a loja</option>
          {#each data.lojas as loja (loja.id)}
            <option value={loja.id} selected={v('dropoffStoreId') === loja.id}>
              {loja.name} ({loja.code})
            </option>
          {/each}
        </select>
        {#if err('dropoffStoreId')}<span class="erro-msg">{err('dropoffStoreId')}</span>{/if}
      </div>
    </div>
  </div>

  <!-- Período -->
  <div class="section-card">
    <h2 class="section-title">Período</h2>
    <div class="campo-group campo-2col">
      <div class="campo">
        <label for="pickupTime">Data/Hora de Retirada</label>
        <input
          id="pickupTime" name="pickupTime" type="datetime-local"
          bind:value={pickupTime}
          class:erro={!!err('pickupTime')}
        />
        {#if err('pickupTime')}<span class="erro-msg">{err('pickupTime')}</span>{/if}
      </div>
      <div class="campo">
        <label for="dropoffTime">Data/Hora de Devolução</label>
        <input
          id="dropoffTime" name="dropoffTime" type="datetime-local"
          bind:value={dropoffTime}
          class:erro={!!err('dropoffTime')}
        />
        {#if err('dropoffTime')}<span class="erro-msg">{err('dropoffTime')}</span>{/if}
      </div>
    </div>
    {#if totalDias() > 0}
      <p class="dias-info">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
          <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M6.5 4.5v4M6.5 3.5v.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
        </svg>
        {totalDias()} dia{totalDias() !== 1 ? 's' : ''} de locação
      </p>
    {/if}
  </div>

  <!-- Extras -->
  <div class="section-card">
    <h2 class="section-title">Informações Extras</h2>
    <div class="campo-group campo-2col">
      <div class="campo">
        <label for="flightNumber">Número do Voo <span class="opcional">(opcional)</span></label>
        <input
          id="flightNumber" name="flightNumber" type="text"
          placeholder="Ex: LA1234"
          value={v('flightNumber')}
        />
      </div>
      <div class="campo campo-full">
        <label for="notes">Observações <span class="opcional">(opcional)</span></label>
        <textarea id="notes" name="notes" rows="2" placeholder="Informações adicionais...">{v('notes')}</textarea>
      </div>
    </div>
  </div>

  <!-- Precificação -->
  <div class="section-card">
    <h2 class="section-title">Precificação</h2>
    <div class="campo-group campo-3col">
      <div class="campo">
        <label for="dailyRate">Diária (R$)</label>
        <input
          id="dailyRate" name="dailyRate" type="number"
          min="0.01" step="0.01"
          bind:value={dailyRate}
          class:erro={!!err('dailyRate')}
        />
        {#if err('dailyRate')}<span class="erro-msg">{err('dailyRate')}</span>{/if}
      </div>
      <div class="campo">
        <label for="fees">Taxas Extras (R$)</label>
        <input
          id="fees" name="fees" type="number"
          min="0" step="0.01"
          bind:value={fees}
        />
      </div>
      <div class="campo">
        <label>Total Estimado</label>
        <div class="campo-total">
          {#if totalValor() > 0}
            {totalValor().toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          {:else}
            <span style="color:#334155">—</span>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <!-- Actions -->
  <div class="form-acoes">
    <a href="/locadora/reservas" class="btn-cancelar">Cancelar</a>
    <button type="submit" class="btn-salvar">Criar Reserva</button>
  </div>

</form>

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .page-header p  { font-size: 13px; color: #475569; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }

  .banner-erro {
    margin-bottom: 20px; padding: 12px 16px;
    border-radius: 10px; border: 1px solid rgba(248,113,113,0.3);
    background: rgba(248,113,113,0.07); font-size: 13px; color: #f87171;
  }

  .form-wrap { display: flex; flex-direction: column; gap: 16px; }

  .section-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px;
  }
  .section-title {
    font-size: 13px; font-weight: 600; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin: 0 0 16px;
  }

  .campo-group { display: flex; flex-direction: column; gap: 14px; }
  .campo-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .campo-3col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }

  .campo { display: flex; flex-direction: column; gap: 6px; }
  .campo-full { grid-column: 1 / -1; }

  label { font-size: 12px; font-weight: 500; color: #64748b; }
  .opcional { font-weight: 400; color: #334155; }

  input, select, textarea {
    background: #0a0f1a; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 12px;
    font-size: 13px; color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
    outline: none; width: 100%; box-sizing: border-box;
    transition: border-color 0.14s;
  }
  input:focus, select:focus, textarea:focus {
    border-color: rgba(96,165,250,0.4);
  }
  select option { background: #0f172a; }
  textarea { resize: vertical; }

  input.erro, select.erro { border-color: rgba(248,113,113,0.5); }
  .erro-msg { font-size: 11px; color: #f87171; }

  .campo-total {
    background: #0a0f1a; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 12px;
    font-size: 14px; font-weight: 700; color: #60a5fa;
    min-height: 40px; display: flex; align-items: center;
  }

  .dias-info {
    margin-top: 10px; display: flex; align-items: center; gap: 7px;
    font-size: 12px; color: #60a5fa;
  }

  .form-acoes {
    display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px;
  }
  .btn-cancelar {
    padding: 9px 20px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent; color: #64748b;
    font-size: 13px; font-family: 'DM Sans', sans-serif; text-decoration: none;
    display: inline-flex; align-items: center; cursor: pointer;
    transition: all 0.14s;
  }
  .btn-cancelar:hover { border-color: rgba(255,255,255,0.15); color: #94a3b8; }
  .btn-salvar {
    padding: 9px 24px; border-radius: 8px;
    background: #60a5fa; color: #fff; border: none;
    font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background 0.14s;
  }
  .btn-salvar:hover { background: #3b82f6; }
</style>
