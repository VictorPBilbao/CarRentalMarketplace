<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const etapa = $derived((form as any)?.etapa ?? 'buscar');
  const resultado = $derived((form as any)?.resultado ?? null);

  const campos = $state({
    pickupStoreId:  (form as any)?.campos?.pickupStoreId  ?? '',
    dropoffStoreId: (form as any)?.campos?.dropoffStoreId ?? '',
    categoryId:     (form as any)?.campos?.categoryId     ?? '',
    pickupTime:     (form as any)?.campos?.pickupTime     ?? '',
    dropoffTime:    (form as any)?.campos?.dropoffTime    ?? '',
    customerAge:    (form as any)?.campos?.customerAge    ?? '25',
    flightNumber:   '',
    notes:          '',
  });

  let carregando = $state(false);

  function erro(campo: string): string {
    return (form as any)?.erros?.[campo] ?? '';
  }

  function nomeLoja(id: string): string {
    return data.lojas.find((l: any) => l.id === id)?.name ?? id;
  }

  function nomeCategoria(id: string): string {
    const c = data.categorias.find((c: any) => c.id === id);
    return c ? `${c.group_name} (${c.code})` : id;
  }

  function formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  const melhorPlano = $derived(resultado?.rate_plans?.[0] ?? null);
</script>

<svelte:head>
  <title>Nova Reserva — Área do Cliente</title>
</svelte:head>

<div class="page-header">
  <a href="/cliente/reservas" class="breadcrumb">Minhas Reservas</a>
  <span class="breadcrumb-sep">›</span>
  <span class="breadcrumb-atual">Nova Reserva</span>
  <h1>{etapa === 'confirmar' ? 'Confirmar Reserva' : 'Buscar Disponibilidade'}</h1>
</div>

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<!-- ── Etapa 1: busca ──────────────────────────────────────────────────── -->
{#if etapa === 'buscar'}
<form method="POST" action="?/buscar" use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}>
  <div class="card">
    <div class="form-grid">

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

      <div class="field">
        <label for="customerAge">Sua Idade <span class="req">*</span></label>
        <input id="customerAge" name="customerAge" type="number" min="18" max="99"
          bind:value={campos.customerAge} />
      </div>

      <div class="field">
        <label for="pickupTime">Data/Hora de Retirada <span class="req">*</span></label>
        <input id="pickupTime" name="pickupTime" type="datetime-local"
          bind:value={campos.pickupTime} class:input-erro={!!erro('pickupTime')} />
        {#if erro('pickupTime')}<p class="msg-erro">{erro('pickupTime')}</p>{/if}
      </div>

      <div class="field">
        <label for="dropoffTime">Data/Hora de Devolução <span class="req">*</span></label>
        <input id="dropoffTime" name="dropoffTime" type="datetime-local"
          bind:value={campos.dropoffTime} class:input-erro={!!erro('dropoffTime')} />
        {#if erro('dropoffTime')}<p class="msg-erro">{erro('dropoffTime')}</p>{/if}
      </div>

    </div>

    <div class="form-acoes">
      <a href="/cliente/reservas" class="btn-cancelar">Cancelar</a>
      <button type="submit" class="btn-buscar" disabled={carregando}>
        {carregando ? 'Buscando...' : 'Verificar Disponibilidade'}
      </button>
    </div>
  </div>
</form>
{/if}

<!-- ── Etapa 2: confirmar ──────────────────────────────────────────────── -->
{#if etapa === 'confirmar' && resultado}
  <div class="resumo-card">
    <h3 class="card-title">Resumo da Busca</h3>
    <div class="resumo-grid">
      <div class="resumo-item"><span class="resumo-label">Retirada</span><span class="resumo-val">{formatDate(campos.pickupTime)}</span><span class="resumo-sub">{nomeLoja(campos.pickupStoreId)}</span></div>
      <div class="resumo-item"><span class="resumo-label">Devolução</span><span class="resumo-val">{formatDate(campos.dropoffTime)}</span><span class="resumo-sub">{nomeLoja(campos.dropoffStoreId)}</span></div>
      <div class="resumo-item"><span class="resumo-label">Categoria</span><span class="resumo-val">{nomeCategoria(campos.categoryId)}</span></div>
      <div class="resumo-item"><span class="resumo-label">Disponibilidade</span>
        {#if resultado.disponibilidade > 0}
          <span class="disponivel">{resultado.disponibilidade} unidade(s)</span>
        {:else}
          <span class="indisponivel">Sem disponibilidade</span>
        {/if}
      </div>
    </div>
  </div>

  {#if resultado.disponibilidade <= 0}
    <div class="banner-aviso">Sem disponibilidade para a categoria selecionada nas datas informadas.</div>
    <div class="form-acoes" style="margin-top:16px">
      <a href="/cliente/reservas/nova" class="btn-cancelar">Nova Busca</a>
    </div>
  {:else}
    {#if resultado.rate_plans.length > 0}
      <div class="planos-grid">
        {#each resultado.rate_plans as plano}
          <div class="plano-card {melhorPlano?.id === plano.id ? 'plano-destaque' : ''}">
            <p class="plano-nome">{plano.name}</p>
            <p class="plano-preco">
              <span class="preco-val">R$ {plano.daily_rate.toFixed(2)}</span>
              <span class="preco-unid">/dia</span>
            </p>
            <p class="plano-total">Total: <strong>R$ {plano.subtotal.toFixed(2)}</strong></p>
            <p class="plano-dias">{plano.total_days} dia(s)</p>
          </div>
        {/each}
      </div>
    {:else}
      <div class="banner-aviso">Nenhum plano de tarifa disponível. Entre em contato com a loja.</div>
    {/if}

    {#if melhorPlano}
      <form method="POST" action="?/confirmar" use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}>
        <input type="hidden" name="pickupStoreId"  value={campos.pickupStoreId} />
        <input type="hidden" name="dropoffStoreId" value={campos.dropoffStoreId} />
        <input type="hidden" name="categoryId"     value={campos.categoryId} />
        <input type="hidden" name="pickupTime"     value={new Date(campos.pickupTime).toISOString()} />
        <input type="hidden" name="dropoffTime"    value={new Date(campos.dropoffTime).toISOString()} />
        <input type="hidden" name="dailyRate"      value={melhorPlano.daily_rate} />
        <input type="hidden" name="totalDays"      value={melhorPlano.total_days} />
        <input type="hidden" name="fees"           value={resultado.store_fees.reduce((acc: number, f: any) => acc + f.amount, 0)} />
        <input type="hidden" name="ratePlanId"     value={melhorPlano.id} />

        <div class="card" style="margin-top:16px">
          <h3 class="card-title">Detalhes Opcionais</h3>
          <div class="form-grid">
            <div class="field">
              <label for="flightNumber">Número do Voo</label>
              <input id="flightNumber" name="flightNumber" type="text" placeholder="LA1234" bind:value={campos.flightNumber} />
            </div>
            <div class="field">
              <label for="notes">Observações</label>
              <input id="notes" name="notes" type="text" bind:value={campos.notes} />
            </div>
          </div>

          <div class="form-acoes">
            <a href="/cliente/reservas/nova" class="btn-cancelar">Voltar</a>
            <button type="submit" class="btn-confirmar" disabled={carregando}>
              {carregando ? 'Reservando...' : `Confirmar Reserva — R$ ${melhorPlano.subtotal.toFixed(2)}`}
            </button>
          </div>
        </div>
      </form>
    {/if}
  {/if}
{/if}

<style>
  .page-header { margin-bottom: 24px; }
  .breadcrumb { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
  h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 6px 0 0; }

  .banner-erro {
    margin-bottom: 16px; padding: 12px 16px; border-radius: 10px;
    border: 1px solid rgba(248,113,113,0.3); background: rgba(248,113,113,0.07);
    font-size: 13px; color: #f87171;
  }
  .banner-aviso {
    margin-bottom: 16px; padding: 12px 16px; border-radius: 10px;
    border: 1px solid rgba(251,191,36,0.3); background: rgba(251,191,36,0.07);
    font-size: 13px; color: #fbbf24;
  }

  .card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 24px;
    max-width: 780px;
    margin-bottom: 16px;
  }

  .card-title {
    font-size: 11px; font-weight: 600; color: #475569;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 18px;
  }

  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .field { display: flex; flex-direction: column; gap: 6px; }

  label {
    font-size: 12px; font-weight: 600;
    color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  }
  .req { color: #f87171; }

  input, select {
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
  input:focus, select:focus { outline: none; border-color: rgba(167,139,250,0.4); }
  .input-erro { border-color: rgba(248,113,113,0.5) !important; }
  .msg-erro { font-size: 11px; color: #f87171; margin: 0; }
  option { background: #0f172a; }

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
  .btn-cancelar:hover { color: #94a3b8; }

  .btn-buscar {
    padding: 9px 24px; border-radius: 8px; border: none;
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    color: #fff; font-size: 13px; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: opacity 0.14s;
  }
  .btn-buscar:hover:not(:disabled) { opacity: 0.88; }
  .btn-buscar:disabled { opacity: 0.5; cursor: not-allowed; }

  .btn-confirmar {
    padding: 9px 24px; border-radius: 8px; border: none;
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff; font-size: 13px; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: opacity 0.14s;
  }
  .btn-confirmar:hover:not(:disabled) { opacity: 0.88; }
  .btn-confirmar:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Resumo */
  .resumo-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; max-width: 780px; margin-bottom: 16px;
  }
  .resumo-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .resumo-item { display: flex; flex-direction: column; gap: 3px; }
  .resumo-label { font-size: 10px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.07em; }
  .resumo-val { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .resumo-sub { font-size: 11px; color: #475569; }
  .disponivel { font-size: 13px; font-weight: 600; color: #34d399; }
  .indisponivel { font-size: 13px; font-weight: 600; color: #f87171; }

  /* Planos */
  .planos-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px; max-width: 780px; margin-bottom: 16px;
  }
  .plano-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px;
    transition: border-color 0.14s;
  }
  .plano-destaque { border-color: rgba(167,139,250,0.4); }
  .plano-nome { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 8px; }
  .plano-preco { display: flex; align-items: baseline; gap: 3px; margin: 0 0 4px; }
  .preco-val { font-size: 22px; font-weight: 700; color: #a78bfa; }
  .preco-unid { font-size: 11px; color: #475569; }
  .plano-total { font-size: 12px; color: #94a3b8; margin: 0 0 3px; }
  .plano-dias { font-size: 11px; color: #475569; margin: 0; }
</style>
