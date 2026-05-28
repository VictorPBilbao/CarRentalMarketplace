<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8080/api/v1';

  interface LojaProxima {
    id: string;
    name: string;
    code: string;
    address: { city: string; state: string; neighborhood: string; street: string };
    location: { latitude: number; longitude: number };
    distancia_km: number | null;
  }

  // ── Estado do formulário ───────────────────────────────────────────────
  const campos = $state({
    pickupStoreId:   (form as any)?.campos?.pickupStoreId   ?? '',
    dropoffStoreId:  (form as any)?.campos?.dropoffStoreId  ?? '',
    categoryId:      (form as any)?.campos?.categoryId      ?? '',
    pickupTime:      (form as any)?.campos?.pickupTime      ?? '',
    dropoffTime:     (form as any)?.campos?.dropoffTime     ?? '',
    customerAge:     (form as any)?.campos?.customerAge     ?? '25',
    pickupCep:       (form as any)?.campos?.pickupCep       ?? '',
    dropoffCep:      (form as any)?.campos?.dropoffCep      ?? '',
    pickupStoreName:  (form as any)?.campos?.pickupStoreName  ?? '',
    dropoffStoreName: (form as any)?.campos?.dropoffStoreName ?? '',
    nationality:     (form as any)?.campos?.nationality     ?? '',
    flightNumber:    '',
    notes:           '',
  });

  // ── Estado da busca de lojas por CEP ──────────────────────────────────
  let lojasRetirada:  LojaProxima[] = $state([]);
  let lojasDevolucao: LojaProxima[] = $state([]);
  let lojasVisiveis   = $state(false);
  let buscandoLojas   = $state(false);
  let erroCep         = $state('');
  let carregando      = $state(false);

  // ── Etapa vinda do servidor ────────────────────────────────────────────
  const etapa     = $derived((form as any)?.etapa ?? 'buscar');
  const resultado = $derived((form as any)?.resultado ?? null);
  const melhorPlano = $derived(resultado?.rate_plans?.[0] ?? null);

  function erro(campo: string): string {
    return (form as any)?.erros?.[campo] ?? '';
  }

  // ── Helpers ────────────────────────────────────────────────────────────
  function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function formatarCep(v: string): string {
    const digits = v.replace(/\D/g, '').slice(0, 8);
    return digits.length > 5 ? digits.slice(0, 5) + '-' + digits.slice(5) : digits;
  }

  function onCepInput(e: Event, campo: 'pickupCep' | 'dropoffCep') {
    campos[campo] = formatarCep((e.target as HTMLInputElement).value);
    resetarLojas();
  }

  function onCategoriaChange() {
    resetarLojas();
  }

  function resetarLojas() {
    lojasVisiveis = false;
    lojasRetirada = [];
    lojasDevolucao = [];
    campos.pickupStoreId = '';
    campos.dropoffStoreId = '';
    campos.pickupStoreName = '';
    campos.dropoffStoreName = '';
    erroCep = '';
  }

  function selecionarLoja(tipo: 'pickup' | 'dropoff', loja: LojaProxima) {
    if (tipo === 'pickup') {
      campos.pickupStoreId = loja.id;
      campos.pickupStoreName = loja.name;
    } else {
      campos.dropoffStoreId = loja.id;
      campos.dropoffStoreName = loja.name;
    }
  }

  function formatKm(km: number | null): string {
    if (km === null) return '— km';
    return km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(1)} km`;
  }

  function formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function nomeCategoria(id: string): string {
    const c = data.categorias.find((c: any) => c.id === id);
    return c ? `${c.group_name} (${c.code})` : id;
  }

  // ── Busca lojas por CEP (client-side) ─────────────────────────────────
  async function buscarLojas(e: Event) {
    e.preventDefault();
    erroCep = '';

    if (!campos.categoryId) {
      erroCep = 'Selecione uma categoria antes de buscar lojas.';
      return;
    }
    const cepR = campos.pickupCep.replace(/\D/g, '');
    const cepD = campos.dropoffCep.replace(/\D/g, '');
    if (cepR.length !== 8) { erroCep = 'CEP de retirada inválido.'; return; }
    if (cepD.length !== 8) { erroCep = 'CEP de devolução inválido.'; return; }

    buscandoLojas = true;
    try {
      const [dadosR, dadosD, lojas] = await Promise.all([
        fetch(`https://brasilapi.com.br/api/cep/v2/${cepR}`).then(r => { if (!r.ok) throw new Error(`CEP ${campos.pickupCep} não encontrado.`); return r.json(); }),
        fetch(`https://brasilapi.com.br/api/cep/v2/${cepD}`).then(r => { if (!r.ok) throw new Error(`CEP ${campos.dropoffCep} não encontrado.`); return r.json(); }),
        fetch(`${API_URL}/publico/lojas-com-categoria?category_id=${encodeURIComponent(campos.categoryId)}`).then(r => r.json()),
      ]);

      const coordR = dadosR.location?.coordinates;
      const coordD = dadosD.location?.coordinates;

      const latR = coordR?.latitude  ? parseFloat(String(coordR.latitude))  : null;
      const lonR = coordR?.longitude ? parseFloat(String(coordR.longitude)) : null;
      const latD = coordD?.latitude  ? parseFloat(String(coordD.latitude))  : null;
      const lonD = coordD?.longitude ? parseFloat(String(coordD.longitude)) : null;

      function computar(lista: any[], lat: number | null, lon: number | null): LojaProxima[] {
        if (lat === null || lon === null) {
          return lista.slice(0, 5).map((l: any) => ({ ...l, distancia_km: null }));
        }
        return lista
          .filter((l: any) => l.location?.latitude && l.location?.longitude)
          .map((l: any) => ({
            ...l,
            distancia_km: haversine(lat, lon, parseFloat(l.location.latitude), parseFloat(l.location.longitude)),
          }))
          .sort((a: LojaProxima, b: LojaProxima) => a.distancia_km - b.distancia_km)
          .slice(0, 5);
      }

      lojasRetirada  = computar(lojas, latR, lonR);
      lojasDevolucao = computar(lojas, latD, lonD);
      lojasVisiveis  = true;

      if (lojasRetirada.length === 1)  selecionarLoja('pickup',  lojasRetirada[0]);
      if (lojasDevolucao.length === 1) selecionarLoja('dropoff', lojasDevolucao[0]);

    } catch (e: any) {
      erroCep = e?.message ?? 'Erro ao buscar lojas. Verifique os CEPs e tente novamente.';
      lojasVisiveis = false;
    } finally {
      buscandoLojas = false;
    }
  }

  const podeVerificar = $derived(
    lojasVisiveis &&
    !!campos.pickupStoreId &&
    !!campos.dropoffStoreId &&
    !!campos.pickupTime &&
    !!campos.dropoffTime
  );
</script>

<svelte:head>
  <title>Nova Reserva — Área do Cliente</title>
</svelte:head>

<div class="page-header">
  <a href="/cliente/reservas" class="breadcrumb">Minhas Reservas</a>
  <span class="breadcrumb-sep">›</span>
  <span class="breadcrumb-atual">Nova Reserva</span>
  <h1>{etapa === 'confirmar' ? 'Confirmar Reserva' : 'Nova Reserva'}</h1>
</div>

{#if (form as any)?.erro}
  <div class="banner-erro">{(form as any).erro}</div>
{/if}

<!-- ── Etapa 1: busca por CEP ─────────────────────────────────────────── -->
{#if etapa === 'buscar'}

  <form onsubmit={buscarLojas}>
    <div class="card">
      <h3 class="card-title">Localização</h3>
      <div class="form-grid">

        <div class="field">
          <label for="pickupCep">CEP de Retirada <span class="req">*</span></label>
          <input
            id="pickupCep" type="text" inputmode="numeric" placeholder="00000-000"
            value={campos.pickupCep}
            oninput={(e) => onCepInput(e, 'pickupCep')}
            maxlength={9}
          />
        </div>

        <div class="field">
          <label for="dropoffCep">CEP de Devolução <span class="req">*</span></label>
          <input
            id="dropoffCep" type="text" inputmode="numeric" placeholder="00000-000"
            value={campos.dropoffCep}
            oninput={(e) => onCepInput(e, 'dropoffCep')}
            maxlength={9}
          />
        </div>

      </div>

      <h3 class="card-title" style="margin-top:22px">Categoria e Período</h3>
      <div class="form-grid">

        <div class="field">
          <label for="categoryId">Categoria <span class="req">*</span></label>
          <select
            id="categoryId"
            bind:value={campos.categoryId}
            onchange={onCategoriaChange}
            class:input-erro={!!erro('categoryId')}
          >
            <option value="">Selecione...</option>
            {#each data.categorias as c}
              <option value={c.id}>{c.group_name} ({c.code})</option>
            {/each}
          </select>
          {#if erro('categoryId')}<p class="msg-erro">{erro('categoryId')}</p>{/if}
        </div>

        <div class="field">
          <label for="customerAge">Sua Idade <span class="req">*</span></label>
          <input id="customerAge" type="number" min="18" max="99" bind:value={campos.customerAge} />
        </div>

        <div class="field">
          <label for="nationality">Nacionalidade</label>
          <input id="nationality" type="text" placeholder="BR, US, EU..." bind:value={campos.nationality} />
        </div>

        <div class="field">
          <label for="pickupTime">Data/Hora de Retirada <span class="req">*</span></label>
          <input
            id="pickupTime" type="datetime-local"
            bind:value={campos.pickupTime}
            class:input-erro={!!erro('pickupTime')}
            onchange={resetarLojas}
          />
          {#if erro('pickupTime')}<p class="msg-erro">{erro('pickupTime')}</p>{/if}
        </div>

        <div class="field">
          <label for="dropoffTime">Data/Hora de Devolução <span class="req">*</span></label>
          <input
            id="dropoffTime" type="datetime-local"
            bind:value={campos.dropoffTime}
            class:input-erro={!!erro('dropoffTime')}
            onchange={resetarLojas}
          />
          {#if erro('dropoffTime')}<p class="msg-erro">{erro('dropoffTime')}</p>{/if}
        </div>

      </div>

      {#if erroCep}
        <div class="banner-aviso" style="margin-top:16px">{erroCep}</div>
      {/if}

      <div class="form-acoes">
        <a href="/cliente/reservas" class="btn-cancelar">Cancelar</a>
        <button type="submit" class="btn-buscar" disabled={buscandoLojas}>
          {#if buscandoLojas}
            <span class="spinner"></span> Buscando...
          {:else}
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
              <circle cx="5.5" cy="5.5" r="4" stroke="currentColor" stroke-width="1.4"/>
              <path d="M9 9l2.5 2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            Buscar Lojas Próximas
          {/if}
        </button>
      </div>
    </div>
  </form>

  <!-- ── Seleção de lojas ──────────────────────────────────────────────── -->
  {#if lojasVisiveis}
    <form
      method="POST"
      action="?/buscar"
      use:enhance={() => { carregando = true; return async ({ update }) => { carregando = false; await update(); }; }}
    >
      <input type="hidden" name="categoryId"      value={campos.categoryId} />
      <input type="hidden" name="pickupTime"      value={campos.pickupTime} />
      <input type="hidden" name="dropoffTime"     value={campos.dropoffTime} />
      <input type="hidden" name="customerAge"     value={campos.customerAge} />
      <input type="hidden" name="pickupCep"       value={campos.pickupCep} />
      <input type="hidden" name="dropoffCep"      value={campos.dropoffCep} />
      <input type="hidden" name="pickupStoreId"   value={campos.pickupStoreId} />
      <input type="hidden" name="dropoffStoreId"  value={campos.dropoffStoreId} />
      <input type="hidden" name="pickupStoreName"  value={campos.pickupStoreName} />
      <input type="hidden" name="dropoffStoreName" value={campos.dropoffStoreName} />
      <input type="hidden" name="nationality"      value={campos.nationality} />

      <div class="card">
        <h3 class="card-title">Lojas Disponíveis — {nomeCategoria(campos.categoryId)}</h3>

        <div class="lojas-secoes">
          <!-- Retirada -->
          <div class="lojas-secao">
            <p class="secao-label">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none" style="flex-shrink:0">
                <circle cx="5.5" cy="4" r="3" stroke="currentColor" stroke-width="1.2"/>
                <path d="M5.5 7v3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              Retirada — CEP {campos.pickupCep}
            </p>

            {#if lojasRetirada.length === 0}
              <p class="sem-lojas">Nenhuma loja com esta categoria próxima ao CEP informado.</p>
            {:else}
              <div class="lojas-lista">
                {#each lojasRetirada as loja}
                  <button
                    type="button"
                    class="loja-card"
                    class:loja-selecionada={campos.pickupStoreId === loja.id}
                    onclick={() => selecionarLoja('pickup', loja)}
                  >
                    <div class="loja-radio">
                      <div class="radio-dot" class:radio-ativo={campos.pickupStoreId === loja.id}></div>
                    </div>
                    <div class="loja-info">
                      <p class="loja-nome">{loja.name}</p>
                      <p class="loja-end">{loja.address.neighborhood}, {loja.address.city} — {loja.address.state}</p>
                    </div>
                    <span class="loja-dist">{formatKm(loja.distancia_km)}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>

          <!-- Devolução -->
          <div class="lojas-secao">
            <p class="secao-label">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none" style="flex-shrink:0">
                <circle cx="5.5" cy="4" r="3" stroke="currentColor" stroke-width="1.2"/>
                <path d="M5.5 7v3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              Devolução — CEP {campos.dropoffCep}
            </p>

            {#if lojasDevolucao.length === 0}
              <p class="sem-lojas">Nenhuma loja com esta categoria próxima ao CEP informado.</p>
            {:else}
              <div class="lojas-lista">
                {#each lojasDevolucao as loja}
                  <button
                    type="button"
                    class="loja-card"
                    class:loja-selecionada={campos.dropoffStoreId === loja.id}
                    onclick={() => selecionarLoja('dropoff', loja)}
                  >
                    <div class="loja-radio">
                      <div class="radio-dot" class:radio-ativo={campos.dropoffStoreId === loja.id}></div>
                    </div>
                    <div class="loja-info">
                      <p class="loja-nome">{loja.name}</p>
                      <p class="loja-end">{loja.address.neighborhood}, {loja.address.city} — {loja.address.state}</p>
                    </div>
                    <span class="loja-dist">{formatKm(loja.distancia_km)}</span>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        </div>

        {#if erro('pickupStoreId') || erro('dropoffStoreId')}
          <div class="banner-aviso" style="margin-top:12px">
            {erro('pickupStoreId') || erro('dropoffStoreId')}
          </div>
        {/if}

        <div class="form-acoes">
          <button
            type="submit"
            class="btn-buscar"
            disabled={!podeVerificar || carregando}
          >
            {carregando ? 'Verificando...' : 'Verificar Disponibilidade'}
          </button>
        </div>
      </div>
    </form>
  {/if}

{/if}

<!-- ── Etapa 2: confirmar ──────────────────────────────────────────────── -->
{#if etapa === 'confirmar' && resultado}
  <div class="resumo-card">
    <h3 class="card-title">Resumo</h3>
    <div class="resumo-grid">
      <div class="resumo-item">
        <span class="resumo-label">Retirada</span>
        <span class="resumo-val">{formatDate(campos.pickupTime)}</span>
        <span class="resumo-sub">{campos.pickupStoreName || campos.pickupStoreId}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Devolução</span>
        <span class="resumo-val">{formatDate(campos.dropoffTime)}</span>
        <span class="resumo-sub">{campos.dropoffStoreName || campos.dropoffStoreId}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Categoria</span>
        <span class="resumo-val">{nomeCategoria(campos.categoryId)}</span>
      </div>
      <div class="resumo-item">
        <span class="resumo-label">Disponibilidade</span>
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
      <div class="form-acoes" style="margin-top:16px">
        <a href="/cliente/reservas/nova" class="btn-cancelar">Nova Busca</a>
      </div>
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
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
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
    border-radius: 12px; padding: 24px;
    max-width: 780px; margin-bottom: 16px;
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
    border-radius: 8px; padding: 9px 12px;
    font-size: 13px; color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
    transition: border-color 0.14s;
    width: 100%; box-sizing: border-box;
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
    display: inline-flex; align-items: center; gap: 7px;
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

  /* Spinner */
  .spinner {
    width: 12px; height: 12px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Lojas ── */
  .lojas-secoes {
    display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  }
  .lojas-secao { display: flex; flex-direction: column; gap: 8px; }

  .secao-label {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 600; color: #475569;
    text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 4px;
  }

  .sem-lojas {
    font-size: 12px; color: #334155; padding: 16px;
    background: rgba(255,255,255,0.02); border-radius: 8px;
    border: 1px dashed rgba(255,255,255,0.06); text-align: center;
  }

  .lojas-lista { display: flex; flex-direction: column; gap: 6px; }

  .loja-card {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 9px; cursor: pointer;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    text-align: left; width: 100%;
    transition: border-color 0.14s, background 0.14s;
    font-family: 'DM Sans', sans-serif;
  }
  .loja-card:hover { border-color: rgba(167,139,250,0.25); background: rgba(167,139,250,0.04); }
  .loja-selecionada {
    border-color: rgba(167,139,250,0.5) !important;
    background: rgba(167,139,250,0.08) !important;
  }

  .loja-radio { flex-shrink: 0; }
  .radio-dot {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.15);
    background: transparent; transition: all 0.14s;
  }
  .radio-ativo {
    border-color: #a78bfa;
    background: #a78bfa;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.2);
  }

  .loja-info { flex: 1; min-width: 0; }
  .loja-nome { font-size: 13px; font-weight: 600; color: #e2e8f0; margin: 0 0 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .loja-end  { font-size: 11px; color: #475569; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .loja-dist {
    font-size: 11px; font-weight: 600; color: #64748b;
    background: rgba(255,255,255,0.04); border-radius: 5px;
    padding: 3px 8px; flex-shrink: 0; white-space: nowrap;
  }
  .loja-selecionada .loja-dist { color: #a78bfa; background: rgba(167,139,250,0.1); }

  /* Resumo */
  .resumo-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; max-width: 780px; margin-bottom: 16px;
  }
  .resumo-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .resumo-item { display: flex; flex-direction: column; gap: 3px; }
  .resumo-label { font-size: 10px; font-weight: 600; color: #334155; text-transform: uppercase; letter-spacing: 0.07em; }
  .resumo-val   { font-size: 13px; font-weight: 600; color: #e2e8f0; }
  .resumo-sub   { font-size: 11px; color: #475569; }
  .disponivel   { font-size: 13px; font-weight: 600; color: #34d399; }
  .indisponivel { font-size: 13px; font-weight: 600; color: #f87171; }

  /* Planos */
  .planos-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px; max-width: 780px; margin-bottom: 16px;
  }
  .plano-card {
    background: #0f172a; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px; transition: border-color 0.14s;
  }
  .plano-destaque { border-color: rgba(167,139,250,0.4); }
  .plano-nome  { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 8px; }
  .plano-preco { display: flex; align-items: baseline; gap: 3px; margin: 0 0 4px; }
  .preco-val   { font-size: 22px; font-weight: 700; color: #a78bfa; }
  .preco-unid  { font-size: 11px; color: #475569; }
  .plano-total { font-size: 12px; color: #94a3b8; margin: 0 0 3px; }
  .plano-dias  { font-size: 11px; color: #475569; margin: 0; }
</style>
