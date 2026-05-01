<script lang="ts">
  import type { PageData } from './$types';
  import type { RatePlanCompleto, TaxaLoja, AddonCompleto } from '$lib/services/tarifa.service';

  let { data }: { data: PageData } = $props();

  type Aba = 'rateplans' | 'fees' | 'addons';
  let abaAtiva = $state<Aba>('rateplans');

  const ratePlans: RatePlanCompleto[] = $derived(data.ratePlans ?? []);
  const fees: TaxaLoja[]              = $derived(data.fees ?? []);
  const addons: AddonCompleto[]       = $derived(data.addons ?? []);

  function moeda(v: number) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function fmtDate(s: string | null): string {
    if (!s) return '—';
    return new Date(s).toLocaleDateString('pt-BR');
  }

  // Group fees by store
  const feesPorLoja = $derived(() => {
    const map = new Map<string, { storeName: string; storeCode: string; fees: TaxaLoja[] }>();
    for (const f of fees) {
      const key = String(f.store);
      if (!map.has(key)) {
        map.set(key, { storeName: f.store_name ?? key, storeCode: f.store_code ?? '', fees: [] });
      }
      map.get(key)!.fees.push(f);
    }
    return [...map.values()];
  });

  const CALC_LABEL: Record<string, string> = {
    PERCENTAGE: '% do subtotal',
    FLAT_FEE:   'Valor fixo',
    PER_DAY:    'Por dia',
    PER_TRIP:   'Por viagem',
  };

  const MILEAGE_LABEL: Record<string, string> = {
    UNLIMITED: 'Km ilimitado',
    LIMITED:   'Km limitado',
  };
</script>

<div style="max-width:1100px;">

  <!-- Header -->
  <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:24px; gap:16px;">
    <div>
      <h1 style="font-size:20px; font-weight:600; color:#f1f5f9; margin:0 0 4px;">Tarifas</h1>
      <p style="font-size:13px; color:#475569; margin:0;">
        Visão gerencial de planos, taxas e adicionais. Edição via API/banco — veja nota abaixo.
      </p>
    </div>
  </div>

  <!-- Nota editorial -->
  <div style="
    background: rgba(251,191,36,0.06);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 24px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
  ">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="flex-shrink:0; margin-top:1px; color:#fbbf24">
      <path d="M8 1.5L14.5 13H1.5L8 1.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
      <path d="M8 6v3.5M8 11.5v.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    <div style="font-size:13px; color:#94a3b8; line-height:1.6;">
      <strong style="color:#fbbf24;">Somente leitura.</strong>
      Para habilitar edição inline, serão necessários endpoints de CRUD:
      <code style="background:rgba(255,255,255,0.06); border-radius:4px; padding:1px 5px; font-size:12px;">POST/PUT/DELETE /locadora/rate_plans/:id</code>,
      <code style="background:rgba(255,255,255,0.06); border-radius:4px; padding:1px 5px; font-size:12px;">/locadora/fees/:id</code> e
      <code style="background:rgba(255,255,255,0.06); border-radius:4px; padding:1px 5px; font-size:12px;">/locadora/addons/:id</code>.
      Os dados já estão sendo buscados e exibidos — basta conectar formulários quando o backend estiver pronto.
    </div>
  </div>

  <!-- Abas -->
  <div style="display:flex; gap:4px; margin-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.07); padding-bottom:0;">
    {#each ([['rateplans','Planos Tarifários', ratePlans.length], ['fees','Taxas por Loja', fees.length], ['addons','Adicionais', addons.length]] as [id, label, count]) as [id, label, count]}
      <button
        onclick={() => abaAtiva = id as Aba}
        style="
          padding: 8px 16px;
          border-radius: 8px 8px 0 0;
          border: none;
          border-bottom: 2px solid {abaAtiva === id ? '#60a5fa' : 'transparent'};
          background: {abaAtiva === id ? 'rgba(96,165,250,0.08)' : 'transparent'};
          color: {abaAtiva === id ? '#60a5fa' : '#64748b'};
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          font-family: inherit;
          transition: all 0.14s;
          display: flex;
          align-items: center;
          gap: 6px;
        "
      >
        {label}
        <span style="
          background: {abaAtiva === id ? 'rgba(96,165,250,0.15)' : 'rgba(255,255,255,0.06)'};
          color: {abaAtiva === id ? '#60a5fa' : '#475569'};
          font-size: 11px;
          font-weight: 600;
          padding: 1px 7px;
          border-radius: 20px;
        ">{count}</span>
      </button>
    {/each}
  </div>

  <!-- ── ABA: Rate Plans ── -->
  {#if abaAtiva === 'rateplans'}
    {#if ratePlans.length === 0}
      <div style="text-align:center; padding:60px 0; color:#334155; font-size:14px;">Nenhum plano tarifário cadastrado.</div>
    {:else}
      <div style="display:flex; flex-direction:column; gap:12px;">
        {#each ratePlans as plan}
          <div style="
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 18px 20px;
          ">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div>
                  <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:15px; font-weight:600; color:#e2e8f0;">{plan.name}</span>
                    <span style="
                      font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;
                      padding:2px 8px; border-radius:20px;
                      background:{plan.active ? 'rgba(52,211,153,0.12)' : 'rgba(100,116,139,0.12)'};
                      color:{plan.active ? '#34d399' : '#64748b'};
                    ">{plan.active ? 'Ativo' : 'Inativo'}</span>
                    {#if plan.conditions.promo_code}
                      <span style="
                        font-size:10px; font-weight:600; text-transform:uppercase;
                        padding:2px 8px; border-radius:20px;
                        background:rgba(251,191,36,0.1); color:#fbbf24;
                      ">Promo: {plan.conditions.promo_code}</span>
                    {/if}
                  </div>
                  <div style="font-size:12px; color:#475569; margin-top:3px;">
                    Prioridade {plan.priority} · {MILEAGE_LABEL[plan.price.mileage_policy] ?? plan.price.mileage_policy}
                    {#if plan.price.mileage_policy === 'LIMITED'}
                      · {plan.price.included_km_per_day} km/dia · +{moeda(plan.price.extra_km_price)}/km excedente
                    {/if}
                  </div>
                </div>
              </div>

              <div style="text-align:right;">
                <div style="font-size:18px; font-weight:700; color:#60a5fa;">{moeda(plan.price.daily_rate)}</div>
                <div style="font-size:11px; color:#475569;">por dia · {plan.price.currency}</div>
              </div>
            </div>

            <!-- Condições -->
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:14px;">
              <span class="badge-info">{plan.conditions.min_days}{plan.conditions.max_days ? `–${plan.conditions.max_days}` : '+'} dias</span>
              <span class="badge-info">Idade {plan.conditions.min_age}{plan.conditions.max_age ? `–${plan.conditions.max_age}` : '+'} anos</span>
              <span class="badge-info">Antec. {plan.conditions.advance_booking_days}d</span>
              {#if plan.conditions.allow_one_way}
                <span class="badge-info" style="color:#34d399; background:rgba(52,211,153,0.08);">One-way OK</span>
              {/if}
              {#if plan.conditions.valid_from || plan.conditions.valid_to}
                <span class="badge-info">Validade: {fmtDate(plan.conditions.valid_from)} → {fmtDate(plan.conditions.valid_to)}</span>
              {/if}
              {#if plan.conditions.stores.length > 0}
                <span class="badge-info">{plan.conditions.stores.length} loja(s) específica(s)</span>
              {:else}
                <span class="badge-info">Todas as lojas</span>
              {/if}
              {#if plan.conditions.categories.length > 0}
                <span class="badge-info">{plan.conditions.categories.length} categoria(s)</span>
              {/if}
            </div>

            {#if plan.included_protections.length > 0}
              <div style="margin-top:10px; font-size:12px; color:#475569;">
                Proteções incluídas:
                {#each plan.included_protections as pId}
                  <span style="
                    display:inline-block; margin-left:4px;
                    background:rgba(96,165,250,0.08); color:#60a5fa;
                    border-radius:4px; padding:1px 6px; font-size:11px;
                  ">{pId}</span>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}

  <!-- ── ABA: Fees ── -->
  {#if abaAtiva === 'fees'}
    {#if fees.length === 0}
      <div style="text-align:center; padding:60px 0; color:#334155; font-size:14px;">Nenhuma taxa cadastrada.</div>
    {:else}
      <div style="display:flex; flex-direction:column; gap:16px;">
        {#each feesPorLoja() as grupo}
          <div style="
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            overflow: hidden;
          ">
            <div style="
              padding: 12px 20px;
              background: rgba(255,255,255,0.02);
              border-bottom: 1px solid rgba(255,255,255,0.07);
              display: flex;
              align-items: center;
              gap: 8px;
            ">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="color:#60a5fa; flex-shrink:0">
                <path d="M6.5 1C3.46 1 1 3.46 1 6.5S3.46 12 6.5 12 12 9.54 12 6.5 9.54 1 6.5 1z" stroke="currentColor" stroke-width="1.2"/>
                <path d="M6.5 4v4M4.5 6.5h4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              <span style="font-size:13px; font-weight:600; color:#e2e8f0;">{grupo.storeName}</span>
              {#if grupo.storeCode}
                <span style="font-size:11px; color:#475569; font-family:monospace;">{grupo.storeCode}</span>
              {/if}
            </div>
            <table style="width:100%; border-collapse:collapse;">
              <thead>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                  <th style="padding:10px 20px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Nome</th>
                  <th style="padding:10px 16px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Tipo</th>
                  <th style="padding:10px 16px; text-align:right; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Valor</th>
                  <th style="padding:10px 16px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Horário</th>
                  <th style="padding:10px 16px; text-align:center; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Status</th>
                </tr>
              </thead>
              <tbody>
                {#each grupo.fees as fee}
                  <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:11px 20px; font-size:13px; font-weight:500; color:#cbd5e1;">{fee.name}</td>
                    <td style="padding:11px 16px; font-size:12px; color:#64748b;">{CALC_LABEL[fee.pricing.calculation_type] ?? fee.pricing.calculation_type}</td>
                    <td style="padding:11px 16px; text-align:right; font-size:13px; font-weight:600; color:#f1f5f9;">
                      {fee.pricing.calculation_type === 'PERCENTAGE'
                        ? `${fee.pricing.amount}%`
                        : moeda(fee.pricing.amount)}
                    </td>
                    <td style="padding:11px 16px; font-size:12px; color:#64748b;">
                      {#if fee.conditions.applies_after_time || fee.conditions.applies_before_time}
                        {fee.conditions.applies_after_time ?? '—'} → {fee.conditions.applies_before_time ?? '—'}
                      {:else}
                        Sempre
                      {/if}
                    </td>
                    <td style="padding:11px 16px; text-align:center;">
                      <span style="
                        font-size:10px; font-weight:600; text-transform:uppercase;
                        padding:2px 8px; border-radius:20px;
                        background:{fee.active ? 'rgba(52,211,153,0.12)' : 'rgba(100,116,139,0.12)'};
                        color:{fee.active ? '#34d399' : '#64748b'};
                      ">{fee.active ? 'Ativa' : 'Inativa'}</span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/each}
      </div>
    {/if}
  {/if}

  <!-- ── ABA: Addons ── -->
  {#if abaAtiva === 'addons'}
    {#if addons.length === 0}
      <div style="text-align:center; padding:60px 0; color:#334155; font-size:14px;">Nenhum adicional cadastrado.</div>
    {:else}
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:12px;">
        {#each addons as addon}
          <div style="
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 16px 18px;
          ">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:8px; margin-bottom:10px;">
              <div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:14px; font-weight:600; color:#e2e8f0;">{addon.name}</span>
                  <span style="
                    font-size:10px; font-weight:600; text-transform:uppercase;
                    padding:2px 8px; border-radius:20px;
                    background:{addon.active ? 'rgba(52,211,153,0.12)' : 'rgba(100,116,139,0.12)'};
                    color:{addon.active ? '#34d399' : '#64748b'};
                  ">{addon.active ? 'Ativo' : 'Inativo'}</span>
                </div>
                {#if addon.description}
                  <p style="font-size:12px; color:#475569; margin:4px 0 0;">{addon.description}</p>
                {/if}
              </div>
              <div style="text-align:right; flex-shrink:0;">
                <div style="font-size:15px; font-weight:700; color:#60a5fa;">
                  {addon.pricing.calculation_type === 'PERCENTAGE'
                    ? `${addon.pricing.amount}%`
                    : moeda(addon.pricing.amount)}
                </div>
                <div style="font-size:11px; color:#475569;">{CALC_LABEL[addon.pricing.calculation_type] ?? addon.pricing.calculation_type}</div>
              </div>
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              <span class="badge-info">{addon.type}</span>
              {#if addon.pricing.max_amount_per_trip !== null}
                <span class="badge-info">Teto {moeda(addon.pricing.max_amount_per_trip)}/viagem</span>
              {/if}
              {#if addon.stores.length > 0}
                <span class="badge-info">{addon.stores.length} loja(s)</span>
              {:else}
                <span class="badge-info">Todas as lojas</span>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}

</div>

<style>
  .badge-info {
    font-size: 11px;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.05);
    color: #64748b;
    white-space: nowrap;
  }
</style>
