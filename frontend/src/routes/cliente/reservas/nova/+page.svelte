<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';
  import type { AddonDisponivel, CidadeResponse, CidadeStore, ResultadoCategoriaDisponivel } from '$lib/services/publico.service';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  $effect(() => { const m = (form as any)?.erro; if (m) notificacoes.erro(m); });
  $effect(() => {
    const r = (form as any)?.resultado;
    if (r && r.categorias?.length === 0) notificacoes.aviso('Nenhum veículo disponível para a loja selecionada.');
  });

  // ── Dados do servidor ─────────────────────────────────────────────────
  const cidades: CidadeResponse[] = $derived(data.cidades ?? []);

  // ── Estado da etapa ───────────────────────────────────────────────────
  const etapa     = $derived((form as any)?.etapa ?? 'buscar');
  const resultado = $derived((form as any)?.resultado ?? null);

  // ── Campos do formulário ──────────────────────────────────────────────
  const campos = $state({
    pickupStoreId:    (form as any)?.campos?.pickupStoreId    ?? '',
    dropoffStoreId:   (form as any)?.campos?.dropoffStoreId   ?? '',
    pickupTime:       (form as any)?.campos?.pickupTime       ?? '',
    dropoffTime:      (form as any)?.campos?.dropoffTime      ?? '',
    customerAge:      (form as any)?.campos?.customerAge      ?? '25',
    pickupCity:       (form as any)?.campos?.pickupCity       ?? '',
    dropoffCity:      (form as any)?.campos?.dropoffCity      ?? '',
    pickupStoreName:  (form as any)?.campos?.pickupStoreName  ?? '',
    dropoffStoreName: (form as any)?.campos?.dropoffStoreName ?? '',
    nationality:      (form as any)?.campos?.nationality      ?? '',
    flightNumber:     '',
    notes:            '',
  });

  // ── Categoria escolhida pelo cliente (etapa 'categorias') ─────────────
  let categoriaEscolhida = $state<ResultadoCategoriaDisponivel | null>(null);
  let carregando = $state(false);

  // Reseta categoria escolhida sempre que um novo resultado de busca chega
  $effect(() => { resultado; categoriaEscolhida = null; addonsSelecionados = new Map(); });

  // ── Adicionais ────────────────────────────────────────────────────────────
  let addonsSelecionados = $state<Map<string, number>>(new Map());

  function toggleAddon(addon: AddonDisponivel) {
    const m = new Map(addonsSelecionados);
    if (m.has(addon.id)) m.delete(addon.id);
    else m.set(addon.id, 1);
    addonsSelecionados = m;
  }

  function calcAddonTotal(addon: AddonDisponivel, subtotal: number, totalDays: number, qty: number): number {
    let raw = 0;
    if (addon.pricing_type === 'PER_DAY') {
      raw = addon.pricing_amount * totalDays * qty;
      if (addon.max_amount_per_trip !== null) raw = Math.min(raw, addon.max_amount_per_trip * qty);
    } else if (addon.pricing_type === 'PERCENTAGE') {
      raw = subtotal * addon.pricing_amount / 100 * qty;
      if (addon.max_amount_per_trip !== null) raw = Math.min(raw, addon.max_amount_per_trip * qty);
    } else {
      raw = addon.pricing_amount * qty;
    }
    return round2(raw);
  }

  // ── Lojas da cidade selecionada ───────────────────────────────────────
  const lojasRetirada  = $derived<CidadeStore[]>(
    cidades.find(c => c.city === campos.pickupCity)?.stores ?? []
  );

  // IDs efetivos: auto-selecionado se cidade tem 1 loja, senão depende do radio
  const pickupStoreId   = $derived(lojasRetirada.length === 1  ? lojasRetirada[0].id       : campos.pickupStoreId);
  const pickupStoreName = $derived(lojasRetirada.length === 1  ? lojasRetirada[0].name     : campos.pickupStoreName);
  const pickupCompanyId = $derived(lojasRetirada.find(l => l.id === pickupStoreId)?.company_id ?? lojasRetirada[0]?.company_id ?? '');

  // Devolução: somente lojas da mesma locadora que a retirada
  const lojasDevolucaoTodas = $derived<CidadeStore[]>(
    cidades.find(c => c.city === campos.dropoffCity)?.stores ?? []
  );
  const lojasDevolucao = $derived<CidadeStore[]>(
    pickupCompanyId
      ? lojasDevolucaoTodas.filter(l => l.company_id === pickupCompanyId)
      : lojasDevolucaoTodas
  );

  const dropoffStoreId  = $derived(lojasDevolucao.length === 1 ? lojasDevolucao[0].id   : campos.dropoffStoreId);
  const dropoffStoreName= $derived(lojasDevolucao.length === 1 ? lojasDevolucao[0].name : campos.dropoffStoreName);

  // Limpa seleção manual quando a cidade muda
  $effect(() => { campos.pickupCity;  campos.pickupStoreId  = ''; campos.pickupStoreName  = ''; });
  $effect(() => { campos.dropoffCity; campos.dropoffStoreId = ''; campos.dropoffStoreName = ''; });

  // ── Helpers ───────────────────────────────────────────────────────────
  function formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function moeda(v: number): string {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  const LOCATION_TYPE_LABEL: Record<string, string> = {
    AIRPORT:       'Aeroporto',
    TRAIN_STATION: 'Estação de Trem',
    CITY_CENTER:   'Centro',
    HOTEL:         'Hotel',
    PORT:          'Porto',
    MALL:          'Shopping',
    OTHER:         'Outro',
  };

  function erro(campo: string): string {
    return (form as any)?.erros?.[campo] ?? '';
  }

  function selecionarLoja(tipo: 'pickup' | 'dropoff', loja: CidadeStore) {
    if (tipo === 'pickup') {
      campos.pickupStoreId  = loja.id;
      campos.pickupStoreName = loja.name;
    } else {
      campos.dropoffStoreId  = loja.id;
      campos.dropoffStoreName = loja.name;
    }
  }

  function selecionarCategoria(cat: ResultadoCategoriaDisponivel) {
    if (cat.disponibilidade === 0 || cat.rate_plans.length === 0) return;
    categoriaEscolhida = cat;
  }

  function totalComFees(cat: ResultadoCategoriaDisponivel): number {
    const melhor = cat.rate_plans[0];
    if (!melhor) return 0;
    const feesTotal = cat.store_fees.reduce((s, f) => s + f.amount, 0);
    return round2(melhor.subtotal + feesTotal);
  }

  function round2(v: number) { return Math.round(v * 100) / 100; }

  const podeVerificar = $derived(
    !!pickupStoreId && !!dropoffStoreId &&
    !!campos.pickupTime && !!campos.dropoffTime
  );
</script>

<svelte:head>
  <title>Nova Reserva — Área do Cliente</title>
</svelte:head>

<div class="page-header">
  <a href="/cliente/reservas" class="breadcrumb">Minhas Reservas</a>
  <span class="breadcrumb-sep">›</span>
  <span class="breadcrumb-atual">Nova Reserva</span>
  <h1>{etapa === 'categorias' && categoriaEscolhida ? 'Confirmar Reserva' : 'Nova Reserva'}</h1>
</div>

<!-- ══ ETAPA 1: BUSCA ══════════════════════════════════════════════════════ -->
{#if etapa === 'buscar'}

  <form
    method="POST"
    action="?/buscar"
    use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}
  >
    <div class="card">
      <h3 class="card-title">Localização</h3>
      <div class="form-grid">

        <!-- Cidade de Retirada -->
        <div class="field">
          <label for="pickupCity">Cidade de Retirada <span class="req">*</span></label>
          <select id="pickupCity" bind:value={campos.pickupCity} class:input-erro={!!erro('pickupStoreId')}>
            <option value="">Selecione...</option>
            {#each cidades as cidade}
              <option value={cidade.city}>{cidade.city} — {cidade.state}</option>
            {/each}
          </select>
        </div>

        <!-- Cidade de Devolução -->
        <div class="field">
          <label for="dropoffCity">Cidade de Devolução <span class="req">*</span></label>
          <select id="dropoffCity" bind:value={campos.dropoffCity} class:input-erro={!!erro('dropoffStoreId')}>
            <option value="">Selecione...</option>
            {#each cidades as cidade}
              <option value={cidade.city}>{cidade.city} — {cidade.state}</option>
            {/each}
          </select>
        </div>

      </div>

      <!-- Seleção de loja (quando há mais de uma na cidade) -->
      {#if campos.pickupCity && lojasRetirada.length > 1}
        <div class="field" style="margin-top:14px;">
          <label>Loja de Retirada <span class="req">*</span></label>
          <div class="lojas-lista">
            {#each lojasRetirada as loja}
              <button
                type="button"
                class="loja-card"
                class:loja-selecionada={pickupStoreId === loja.id}
                onclick={() => selecionarLoja('pickup', loja)}
              >
                <div class="loja-radio">
                  <div class="radio-dot" class:radio-ativo={pickupStoreId === loja.id}></div>
                </div>
                <div class="loja-info">
                  <p class="loja-nome">{loja.name}</p>
                  <p class="loja-end">{LOCATION_TYPE_LABEL[loja.location_type] ?? loja.location_type} · {loja.code}</p>
                </div>
              </button>
            {/each}
          </div>
        </div>
      {/if}
      {#if erro('pickupStoreId')}
        <p class="msg-erro">{erro('pickupStoreId')}</p>
      {/if}

      {#if campos.dropoffCity && lojasDevolucao.length === 0 && lojasDevolucaoTodas.length > 0 && pickupCompanyId}
        <p class="msg-aviso" style="margin-top:14px;">
          A locadora da cidade de retirada não possui filial em {campos.dropoffCity}. Escolha outra cidade de devolução.
        </p>
      {:else if campos.dropoffCity && lojasDevolucao.length > 1}
        <div class="field" style="margin-top:14px;">
          <label>Loja de Devolução <span class="req">*</span></label>
          <div class="lojas-lista">
            {#each lojasDevolucao as loja}
              <button
                type="button"
                class="loja-card"
                class:loja-selecionada={dropoffStoreId === loja.id}
                onclick={() => selecionarLoja('dropoff', loja)}
              >
                <div class="loja-radio">
                  <div class="radio-dot" class:radio-ativo={dropoffStoreId === loja.id}></div>
                </div>
                <div class="loja-info">
                  <p class="loja-nome">{loja.name}</p>
                  <p class="loja-end">{LOCATION_TYPE_LABEL[loja.location_type] ?? loja.location_type} · {loja.code}</p>
                </div>
              </button>
            {/each}
          </div>
        </div>
      {/if}
      {#if erro('dropoffStoreId')}
        <p class="msg-erro">{erro('dropoffStoreId')}</p>
      {/if}

      <!-- Campos ocultos das lojas selecionadas -->
      <input type="hidden" name="pickupStoreId"    value={pickupStoreId} />
      <input type="hidden" name="dropoffStoreId"   value={dropoffStoreId} />
      <input type="hidden" name="pickupCity"        value={campos.pickupCity} />
      <input type="hidden" name="dropoffCity"       value={campos.dropoffCity} />
      <input type="hidden" name="pickupStoreName"   value={pickupStoreName} />
      <input type="hidden" name="dropoffStoreName"  value={dropoffStoreName} />

      <h3 class="card-title" style="margin-top:22px">Período</h3>
      <div class="form-grid">

        <div class="field">
          <label for="pickupTime">Data/Hora de Retirada <span class="req">*</span></label>
          <input
            id="pickupTime" name="pickupTime" type="datetime-local"
            bind:value={campos.pickupTime}
            class:input-erro={!!erro('pickupTime')}
          />
          {#if erro('pickupTime')}<p class="msg-erro">{erro('pickupTime')}</p>{/if}
        </div>

        <div class="field">
          <label for="dropoffTime">Data/Hora de Devolução <span class="req">*</span></label>
          <input
            id="dropoffTime" name="dropoffTime" type="datetime-local"
            bind:value={campos.dropoffTime}
            class:input-erro={!!erro('dropoffTime')}
          />
          {#if erro('dropoffTime')}<p class="msg-erro">{erro('dropoffTime')}</p>{/if}
        </div>

        <div class="field">
          <label for="customerAge">Sua Idade <span class="req">*</span></label>
          <input id="customerAge" name="customerAge" type="number" min="18" max="99" bind:value={campos.customerAge} />
        </div>

        <div class="field">
          <label for="nationality">Nacionalidade</label>
          <input id="nationality" name="nationality" type="text" placeholder="BR, US, EU..." bind:value={campos.nationality} />
        </div>

      </div>

      <div class="form-acoes">
        <a href="/cliente/reservas" class="btn-cancelar">Cancelar</a>
        <button type="submit" class="btn-buscar" disabled={!podeVerificar || carregando}>
          {#if carregando}
            <span class="spinner"></span> Buscando...
          {:else}
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
              <circle cx="5.5" cy="5.5" r="4" stroke="currentColor" stroke-width="1.4"/>
              <path d="M9 9l2.5 2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            Buscar Veículos
          {/if}
        </button>
      </div>
    </div>
  </form>

{/if}

<!-- ══ ETAPA 2: RESULTADOS POR CATEGORIA ══════════════════════════════════ -->
{#if etapa === 'categorias' && resultado}

  <!-- Resumo da busca — lê do form retornado pelo servidor (campos $state ainda não sincronizado) -->
  {@const fc = (form as any)?.campos ?? {}}
  <div class="resumo-card" style="margin-bottom:20px;">
    <div class="resumo-grid">
      <div class="resumo-item">
        <span class="resumo-label">Retirada</span>
        <span class="resumo-val">{formatDate(fc.pickupTime ?? '')}</span>
        <span class="resumo-sub">{fc.pickupStoreName || fc.pickupCity || fc.pickupStoreId || '—'}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Devolução</span>
        <span class="resumo-val">{formatDate(fc.dropoffTime ?? '')}</span>
        <span class="resumo-sub">{fc.dropoffStoreName || fc.dropoffCity || fc.dropoffStoreId || '—'}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Período</span>
        <span class="resumo-val">{resultado.total_days} dia(s)</span>
        {#if resultado.is_one_way}<span class="resumo-sub">One-way</span>{/if}
      </div>
    </div>
    <div style="margin-top:10px;">
      <a href="/cliente/reservas/nova" class="btn-cancelar" style="font-size:12px;">← Nova busca</a>
    </div>
  </div>

  {#if resultado.categorias.length === 0}
    <!-- aviso disparado via $effect no script -->
  {:else}
    <h3 style="font-size:15px; font-weight:600; color:#e2e8f0; margin:0 0 14px;">
      Selecione uma categoria
    </h3>

    <div class="categorias-grid">
      {#each resultado.categorias as cat}
        {@const semUnidades = cat.disponibilidade === 0}
        {@const semTarifa   = cat.disponibilidade > 0 && cat.rate_plans.length === 0}
        {@const disponivel  = !semUnidades && !semTarifa}
        {@const melhorPlano = cat.rate_plans[0]}
        <button
          type="button"
          class="categoria-card"
          class:categoria-selecionada={categoriaEscolhida?.category_id === cat.category_id}
          class:categoria-indisponivel={!disponivel}
          onclick={() => selecionarCategoria(cat)}
          disabled={!disponivel}
        >
          {#if cat.image_url}
            <img src={cat.image_url} alt={cat.category_name} class="cat-imagem"/>
          {:else}
            <div class="cat-placeholder">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M4 20L7 12h18l3 8M4 20v4h4v-2h16v2h4v-4M4 20h24" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                <circle cx="10" cy="22" r="2" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="22" cy="22" r="2" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
          {/if}

          <div class="cat-info">
            <p class="cat-nome">{cat.category_name}</p>
            <p class="cat-code">{cat.category_code}</p>
          </div>

          {#if disponivel && melhorPlano}
            <div class="cat-preco">
              <span class="preco-val">{moeda(melhorPlano.daily_rate)}</span>
              <span class="preco-unid">/dia</span>
            </div>
            <div class="cat-total">Total: <strong>{moeda(totalComFees(cat))}</strong></div>
            {#if cat.store_fees.length > 0}
              <div class="cat-taxas">+taxas da loja</div>
            {/if}
            <div class="cat-disp">{cat.disponibilidade} unidade(s)</div>
          {:else if semTarifa}
            <div class="cat-indisponivel-label">Sem tarifas para este percurso</div>
          {:else}
            <div class="cat-indisponivel-label">Indisponível</div>
          {/if}
        </button>
      {/each}
    </div>
  {/if}

  <!-- ── Confirmação (aparece quando o cliente escolheu uma categoria) ── -->
  {#if categoriaEscolhida}
    {@const melhorPlano  = categoriaEscolhida.rate_plans[0]}
    {@const feesTotal    = categoriaEscolhida.store_fees.reduce((s, f) => s + f.amount, 0)}
    {@const subtotalBase = melhorPlano ? melhorPlano.subtotal : 0}
    {@const addonsTotal  = categoriaEscolhida.available_addons.reduce((s, a) => {
      const qty = addonsSelecionados.get(a.id) ?? 0;
      return qty > 0 ? s + calcAddonTotal(a, subtotalBase, melhorPlano?.total_days ?? 0, qty) : s;
    }, 0)}
    {@const total = round2(subtotalBase + feesTotal + addonsTotal)}

    <div class="card" style="margin-top:24px; border-color:rgba(96,165,250,0.3);">
      <h3 class="card-title" style="color:#60a5fa;">Confirmar Reserva</h3>

      <div class="resumo-grid" style="margin-bottom:16px;">
        <div class="resumo-item">
          <span class="resumo-label">Categoria</span>
          <span class="resumo-val">{categoriaEscolhida.category_name}</span>
          <span class="resumo-sub">{categoriaEscolhida.category_code}</span>
        </div>
        {#if melhorPlano}
          <div class="resumo-item">
            <span class="resumo-label">Plano</span>
            <span class="resumo-val">{melhorPlano.name}</span>
            <span class="resumo-sub">{moeda(melhorPlano.daily_rate)}/dia × {melhorPlano.total_days} dia(s)</span>
          </div>
          {#if categoriaEscolhida.store_fees.length > 0}
            <div class="resumo-item">
              <span class="resumo-label">Taxas da loja</span>
              {#each categoriaEscolhida.store_fees as taxa}
                <span class="resumo-sub">{taxa.name}: {moeda(taxa.amount)}</span>
              {/each}
            </div>
          {/if}
          <div class="resumo-item">
            <span class="resumo-label">Total estimado</span>
            <span class="resumo-val" style="color:#34d399;">{moeda(total)}</span>
          </div>
        {/if}
      </div>

      <!-- ── Adicionais ── -->
      {#if categoriaEscolhida.available_addons.length > 0}
        <div style="border-top:1px solid rgba(255,255,255,0.07); padding-top:16px; margin-bottom:16px;">
          <p style="font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.06em; color:#475569; margin:0 0 12px;">Adicionais</p>
          <div style="display:flex; flex-direction:column; gap:8px;">
            {#each categoriaEscolhida.available_addons as addon}
              {@const selecionado = addonsSelecionados.has(addon.id)}
              {@const previewAmt  = calcAddonTotal(addon, subtotalBase, melhorPlano?.total_days ?? 0, 1)}
              <button
                type="button"
                onclick={() => toggleAddon(addon)}
                style="
                  display:flex; align-items:center; gap:12px;
                  padding:10px 12px; border-radius:10px; text-align:left;
                  border:1px solid {selecionado ? 'rgba(96,165,250,0.4)' : 'rgba(255,255,255,0.07)'};
                  background:{selecionado ? 'rgba(96,165,250,0.06)' : 'transparent'};
                  cursor:pointer; width:100%; transition:all .14s;
                "
              >
                <div style="
                  width:20px; height:20px; border-radius:4px; flex-shrink:0;
                  border:1.5px solid {selecionado ? '#60a5fa' : '#334155'};
                  background:{selecionado ? '#60a5fa' : 'transparent'};
                  display:flex; align-items:center; justify-content:center;
                ">
                  {#if selecionado}
                    <svg width="11" height="9" viewBox="0 0 11 9" fill="none">
                      <path d="M1 4l3 3 6-6" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  {/if}
                </div>
                <div style="flex:1; min-width:0;">
                  <p style="font-size:13px; font-weight:500; color:#e2e8f0; margin:0;">{addon.name}</p>
                  {#if addon.description}
                    <p style="font-size:11px; color:#475569; margin:2px 0 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{addon.description}</p>
                  {/if}
                </div>
                <span style="font-size:13px; font-weight:600; color:{selecionado ? '#60a5fa' : '#64748b'}; white-space:nowrap;">
                  {moeda(previewAmt)}
                  <span style="font-size:10px; font-weight:400; color:#475569;">
                    /{addon.pricing_type === 'PER_DAY' ? 'dia' : addon.pricing_type === 'PERCENTAGE' ? '%' : 'viagem'}
                  </span>
                </span>
              </button>
            {/each}
          </div>
        </div>
      {/if}

      <form
        method="POST"
        action="?/confirmar"
        use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}
      >
        <input type="hidden" name="pickupStoreId"  value={fc.pickupStoreId  || pickupStoreId} />
        <input type="hidden" name="dropoffStoreId" value={fc.dropoffStoreId || dropoffStoreId} />
        <input type="hidden" name="categoryId"     value={categoriaEscolhida.category_id} />
        <input type="hidden" name="pickupTime"     value={new Date(fc.pickupTime  || campos.pickupTime).toISOString()} />
        <input type="hidden" name="dropoffTime"    value={new Date(fc.dropoffTime || campos.dropoffTime).toISOString()} />
        <input type="hidden" name="dailyRate"      value={melhorPlano?.daily_rate ?? 0} />
        <input type="hidden" name="totalDays"      value={melhorPlano?.total_days ?? resultado.total_days} />
        <input type="hidden" name="fees"           value={feesTotal} />
        <input type="hidden" name="feesJson"       value={JSON.stringify(categoriaEscolhida.store_fees.map(f => ({ name: f.name, amount: f.amount, is_tax: f.is_tax })))} />
        <input type="hidden" name="ratePlanId"     value={melhorPlano?.id ?? ''} />
        {#each addonsSelecionados as [addonId, qty]}
          <input type="hidden" name="addon_{addonId}" value={qty} />
        {/each}

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

        <div class="form-acoes" style="margin-top:16px;">
          <button type="button" class="btn-cancelar" onclick={() => categoriaEscolhida = null}>
            Voltar
          </button>
          <button type="submit" class="btn-confirmar" disabled={carregando}>
            {carregando ? 'Confirmando...' : 'Confirmar Reserva'}
          </button>
        </div>
      </form>
    </div>
  {/if}

{/if}

<style>
  /* ── Layout ──────────────────────────────────────────────────────────── */
  .page-header { margin-bottom: 24px; }
  .breadcrumb { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #94a3b8; }
  .breadcrumb-sep { font-size: 12px; color: #334155; margin: 0 6px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
  h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 6px 0 0; }

  /* ── Cards ───────────────────────────────────────────────────────────── */
  .card {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 16px;
  }
  .card-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #475569; margin: 0 0 14px; }

  /* ── Formulário ──────────────────────────────────────────────────────── */
  .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  label { font-size: 13px; font-weight: 500; color: #94a3b8; }
  .req { color: #f87171; }
  input, select {
    padding: 9px 12px; border-radius: 9px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    color: #f1f5f9; font-size: 13px; font-family: inherit; width: 100%; box-sizing: border-box;
  }
  input:focus, select:focus { outline: none; border-color: #60a5fa; }
  select option { background: #1e293b; }
  .input-erro { border-color: rgba(248,113,113,0.4); }
  .msg-erro   { font-size: 12px; color: #f87171; margin: 2px 0 0; }
  .msg-aviso  { font-size: 12px; color: #fbbf24; margin: 2px 0 0; }

  /* ── Botões ──────────────────────────────────────────────────────────── */
  .form-acoes { display: flex; gap: 10px; justify-content: flex-end; margin-top: 18px; flex-wrap: wrap; }
  .btn-cancelar {
    padding: 9px 18px; border-radius: 9px;
    border: 1px solid rgba(255,255,255,0.1); background: transparent;
    color: #64748b; font-size: 13px; cursor: pointer; font-family: inherit; text-decoration: none;
    display: inline-flex; align-items: center;
  }
  .btn-cancelar:hover { color: #94a3b8; }
  .btn-buscar {
    padding: 9px 20px; border-radius: 9px; border: none;
    background: #3b82f6; color: #fff; font-size: 13px; font-weight: 600;
    cursor: pointer; font-family: inherit; display: flex; align-items: center; gap: 7px;
  }
  .btn-buscar:disabled { opacity: .5; cursor: not-allowed; }
  .btn-confirmar {
    padding: 9px 20px; border-radius: 9px; border: none;
    background: #10b981; color: #fff; font-size: 13px; font-weight: 600;
    cursor: pointer; font-family: inherit;
  }
  .btn-confirmar:disabled { opacity: .5; cursor: not-allowed; }

  /* ── Spinner ─────────────────────────────────────────────────────────── */
  .spinner {
    display: inline-block; width: 12px; height: 12px;
    border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
    border-radius: 50%; animation: spin 0.6s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Seleção de loja ─────────────────────────────────────────────────── */
  .lojas-lista { display: flex; flex-direction: column; gap: 8px; margin-top: 6px; }
  .loja-card {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px; border-radius: 10px;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; text-align: left; width: 100%; font-family: inherit;
    transition: border-color .14s, background .14s;
  }
  .loja-card:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.12); }
  .loja-selecionada { border-color: rgba(96,165,250,0.4); background: rgba(96,165,250,0.06); }
  .loja-radio { flex-shrink: 0; }
  .radio-dot {
    width: 16px; height: 16px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    transition: border-color .14s;
  }
  .radio-ativo { border-color: #60a5fa; background: rgba(96,165,250,0.15); }
  .radio-ativo::after { content:''; width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; }
  .loja-info { flex: 1; }
  .loja-nome { font-size: 13px; font-weight: 500; color: #e2e8f0; margin: 0; }
  .loja-end  { font-size: 12px; color: #475569; margin: 2px 0 0; }

  /* ── Categorias grid ─────────────────────────────────────────────────── */
  .categorias-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 16px;
  }
  .categoria-card {
    display: flex; flex-direction: column; align-items: center; gap: 8px;
    padding: 18px 14px; border-radius: 14px;
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; font-family: inherit; text-align: center;
    transition: border-color .14s, background .14s;
  }
  .categoria-card:hover:not(:disabled) { border-color: rgba(96,165,250,0.3); background: rgba(96,165,250,0.04); }
  .categoria-selecionada { border-color: rgba(96,165,250,0.5); background: rgba(96,165,250,0.08); }
  .categoria-indisponivel { opacity: .4; cursor: not-allowed; }
  .cat-imagem { width: 100%; max-width: 160px; height: 90px; object-fit: cover; border-radius: 8px; }
  .cat-placeholder {
    width: 100%; max-width: 160px; height: 90px;
    background: rgba(255,255,255,0.03); border-radius: 8px;
    display: flex; align-items: center; justify-content: center; color: #334155;
  }
  .cat-info { width: 100%; }
  .cat-nome { font-size: 13px; font-weight: 600; color: #e2e8f0; margin: 0; }
  .cat-code { font-size: 11px; color: #475569; margin: 2px 0 0; }
  .cat-preco { margin-top: 6px; }
  .preco-val { font-size: 20px; font-weight: 700; color: #60a5fa; }
  .preco-unid { font-size: 12px; color: #475569; }
  .cat-total { font-size: 12px; color: #94a3b8; }
  .cat-taxas { font-size: 10px; color: #64748b; margin-top: 1px; }
  .cat-disp { font-size: 11px; color: #334155; margin-top: 2px; }
  .cat-indisponivel-label { font-size: 12px; color: #475569; margin-top: 6px; }

  /* ── Resumo ──────────────────────────────────────────────────────────── */
  .resumo-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 16px 20px;
  }
  .resumo-grid { display: flex; gap: 24px; flex-wrap: wrap; }
  .resumo-item { display: flex; flex-direction: column; gap: 2px; }
  .resumo-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #334155; }
  .resumo-val { font-size: 14px; font-weight: 600; color: #e2e8f0; }
  .resumo-sub { font-size: 12px; color: #475569; }
</style>
