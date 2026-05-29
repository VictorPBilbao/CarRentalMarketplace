<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';
  import type { RatePlanCompleto, ProtecaoItem } from '$lib/services/tarifa.service';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const ratePlans: RatePlanCompleto[] = $derived(data.ratePlans ?? []);
  const protecoes: ProtecaoItem[]     = $derived(data.protecoes ?? []);
  const categorias                    = $derived(data.categorias ?? []);

  let modalRatePlan = $state(false);
  let editRatePlan  = $state<RatePlanCompleto | null>(null);

  function moeda(v: number) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  function fmtDate(s: string | null | undefined): string {
    if (!s) return '—';
    return new Date(s).toLocaleDateString('pt-BR');
  }
  function fmtDateInput(s: string | null | undefined): string {
    if (!s) return '';
    return new Date(s).toISOString().substring(0, 10);
  }

  const MILEAGE_LABEL: Record<string, string> = {
    UNLIMITED: 'Km ilimitado', LIMITED: 'Km limitado',
  };

  function abrirNovo() { editRatePlan = null; modalRatePlan = true; }
  function abrirEditar(p: RatePlanCompleto) { editRatePlan = p; modalRatePlan = true; }

  $effect(() => {
    if ((form as any)?.ratePlanSucesso) { modalRatePlan = false; }
  });
</script>

<div style="max-width:1100px;">

  <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:24px; gap:16px; flex-wrap:wrap;">
    <div>
      <h1 style="font-size:20px; font-weight:600; color:#f1f5f9; margin:0 0 4px;">Planos Tarifários</h1>
      <p style="font-size:13px; color:#475569; margin:0;">Gerencie os planos tarifários da sua loja.</p>
    </div>
    <button onclick={abrirNovo} style="
      display:flex; align-items:center; gap:6px;
      padding:8px 14px; border-radius:8px;
      background:rgba(96,165,250,0.12); border:1px solid rgba(96,165,250,0.25);
      color:#60a5fa; font-size:13px; font-weight:500; cursor:pointer; font-family:inherit;
    ">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1v11M1 6.5h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      Novo Plano
    </button>
  </div>

  {#if (form as any)?.ratePlanErro}
    <div style="background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.2); border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:13px; color:#f87171;">{(form as any).ratePlanErro}</div>
  {/if}

  {#if ratePlans.length === 0}
    <div style="text-align:center; padding:60px 0; color:#334155;">Nenhum plano tarifário cadastrado para esta loja.</div>
  {:else}
    <div style="display:flex; flex-direction:column; gap:12px;">
      {#each ratePlans as plan}
        <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:18px 20px;">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:15px; font-weight:600; color:#e2e8f0;">{plan.name}</span>
                <span style="font-size:10px; font-weight:600; text-transform:uppercase; padding:2px 8px; border-radius:20px; background:{plan.active?'rgba(52,211,153,0.12)':'rgba(100,116,139,0.12)'}; color:{plan.active?'#34d399':'#64748b'};">{plan.active?'Ativo':'Inativo'}</span>
                {#if plan.conditions.promo_code}
                  <span style="font-size:10px; font-weight:600; padding:2px 8px; border-radius:20px; background:rgba(251,191,36,0.1); color:#fbbf24;">Promo: {plan.conditions.promo_code}</span>
                {/if}
              </div>
              <div style="font-size:12px; color:#475569; margin-top:3px;">Prioridade {plan.priority} · {MILEAGE_LABEL[plan.price.mileage_policy]??plan.price.mileage_policy}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:18px; font-weight:700; color:#60a5fa;">{moeda(plan.price.daily_rate)}</div>
              <div style="font-size:11px; color:#475569;">por dia · {plan.price.currency}</div>
            </div>
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; align-items:center;">
            <span class="badge-info">{plan.conditions.min_days}{plan.conditions.max_days?`–${plan.conditions.max_days}`:'+' } dias</span>
            <span class="badge-info">Idade {plan.conditions.min_age}{plan.conditions.max_age?`–${plan.conditions.max_age}`:'+' } anos</span>
            <span class="badge-info">Antec. {plan.conditions.advance_booking_days}d</span>
            {#if plan.conditions.allow_one_way}<span class="badge-info" style="color:#34d399; background:rgba(52,211,153,0.08);">One-way OK</span>{/if}
            {#if plan.conditions.valid_from || plan.conditions.valid_to}<span class="badge-info">Validade: {fmtDate(plan.conditions.valid_from)} → {fmtDate(plan.conditions.valid_to)}</span>{/if}
            <button onclick={() => abrirEditar(plan)} style="margin-left:auto; background:transparent; border:none; color:#475569; cursor:pointer; padding:4px 8px; border-radius:6px; font-size:12px;" onmouseenter={(e)=>{(e.currentTarget as HTMLElement).style.color='#94a3b8'}} onmouseleave={(e)=>{(e.currentTarget as HTMLElement).style.color='#475569'}}>Editar</button>
            <form method="POST" action="?/desativarRatePlan" use:enhance>
              <input type="hidden" name="id" value={plan.id}/>
              <button type="submit" style="background:transparent; border:none; color:#475569; cursor:pointer; padding:4px 8px; border-radius:6px; font-size:12px;" onmouseenter={(e)=>{(e.currentTarget as HTMLElement).style.color='#f87171'}} onmouseleave={(e)=>{(e.currentTarget as HTMLElement).style.color='#475569'}}>Desativar</button>
            </form>
          </div>
        </div>
      {/each}
    </div>
  {/if}

</div>

<!-- ── Modal: Rate Plan ──────────────────────────────────────────────────────── -->
{#if modalRatePlan}
  <div style="position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:50; display:flex; align-items:center; justify-content:center; padding:20px;" onclick={(e)=>{if(e.target===e.currentTarget)modalRatePlan=false}}>
    <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.1); border-radius:16px; width:100%; max-width:600px; max-height:90vh; overflow-y:auto;">
      <div style="padding:20px 24px; border-bottom:1px solid rgba(255,255,255,0.07); display:flex; align-items:center; justify-content:space-between;">
        <h2 style="font-size:16px; font-weight:600; color:#f1f5f9; margin:0;">{editRatePlan ? 'Editar Plano Tarifário' : 'Novo Plano Tarifário'}</h2>
        <button onclick={()=>modalRatePlan=false} style="background:transparent; border:none; color:#475569; cursor:pointer; font-size:20px; line-height:1;">×</button>
      </div>
      <form method="POST" action={editRatePlan ? '?/atualizarRatePlan' : '?/criarRatePlan'} use:enhance style="padding:24px; display:flex; flex-direction:column; gap:18px;">
        {#if editRatePlan}<input type="hidden" name="id" value={editRatePlan.id}/>{/if}

        <!-- Nome + Prioridade + Status -->
        <div style="display:grid; grid-template-columns:2fr 1fr 1fr; gap:12px;">
          <div class="campo">
            <label class="label">Nome *</label>
            <input class="input" name="name" required value={editRatePlan?.name ?? ''} placeholder="Ex: Tarifa Flexível"/>
          </div>
          <div class="campo">
            <label class="label">Prioridade</label>
            <input class="input" type="number" name="priority" min="0" value={editRatePlan?.priority ?? 0}/>
          </div>
          <div class="campo">
            <label class="label">Status</label>
            <select class="input" name="active">
              <option value="true" selected={editRatePlan?.active !== false}>Ativo</option>
              <option value="false" selected={editRatePlan?.active === false}>Inativo</option>
            </select>
          </div>
        </div>

        <!-- Preço -->
        <div style="border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px 16px;">
          <div style="font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#475569; margin-bottom:12px;">Preço</div>
          <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;">
            <div class="campo">
              <label class="label">Diária (R$) *</label>
              <input class="input" type="number" name="daily_rate" step="0.01" min="0" required value={editRatePlan?.price?.daily_rate ?? ''} placeholder="0.00"/>
            </div>
            <div class="campo">
              <label class="label">Moeda</label>
              <select class="input" name="currency">
                {#each ['BRL','USD','EUR'] as cur}
                  <option value={cur} selected={editRatePlan?.price?.currency === cur || (!editRatePlan && cur === 'BRL')}>{cur}</option>
                {/each}
              </select>
            </div>
            <div class="campo">
              <label class="label">Política Km</label>
              <select class="input" name="mileage_policy">
                <option value="UNLIMITED" selected={editRatePlan?.price?.mileage_policy !== 'LIMITED'}>Km ilimitado</option>
                <option value="LIMITED" selected={editRatePlan?.price?.mileage_policy === 'LIMITED'}>Km limitado</option>
              </select>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;">
            <div class="campo">
              <label class="label">Km incluído/dia</label>
              <input class="input" type="number" name="included_km_per_day" min="0" value={editRatePlan?.price?.included_km_per_day ?? 0}/>
            </div>
            <div class="campo">
              <label class="label">Preço extra Km (R$)</label>
              <input class="input" type="number" name="extra_km_price" step="0.01" min="0" value={editRatePlan?.price?.extra_km_price ?? 0}/>
            </div>
          </div>
        </div>

        <!-- Condições -->
        <div style="border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px 16px;">
          <div style="font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#475569; margin-bottom:12px;">Condições</div>
          <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;">
            <div class="campo">
              <label class="label">Min dias</label>
              <input class="input" type="number" name="min_days" min="1" value={editRatePlan?.conditions?.min_days ?? 1}/>
            </div>
            <div class="campo">
              <label class="label">Max dias</label>
              <input class="input" type="number" name="max_days" min="1" value={editRatePlan?.conditions?.max_days ?? ''} placeholder="Sem limite"/>
            </div>
            <div class="campo">
              <label class="label">Antec. (dias)</label>
              <input class="input" type="number" name="advance_booking_days" min="0" value={editRatePlan?.conditions?.advance_booking_days ?? 0}/>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-top:12px;">
            <div class="campo">
              <label class="label">Min idade</label>
              <input class="input" type="number" name="min_age" min="18" value={editRatePlan?.conditions?.min_age ?? 18}/>
            </div>
            <div class="campo">
              <label class="label">Max idade</label>
              <input class="input" type="number" name="max_age" min="18" value={editRatePlan?.conditions?.max_age ?? ''} placeholder="Sem limite"/>
            </div>
            <div class="campo" style="justify-content:flex-end; padding-bottom:4px;">
              <label class="label"> </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#94a3b8; cursor:pointer; margin-top:8px;">
                <input type="hidden" name="allow_one_way" value="false"/>
                <input type="checkbox" name="allow_one_way" value="true" checked={editRatePlan?.conditions?.allow_one_way !== false} style="accent-color:#60a5fa;"/>
                Permite one-way
              </label>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;">
            <div class="campo">
              <label class="label">Válido de</label>
              <input class="input" type="date" name="valid_from" value={fmtDateInput(editRatePlan?.conditions?.valid_from)}/>
            </div>
            <div class="campo">
              <label class="label">Válido até</label>
              <input class="input" type="date" name="valid_to" value={fmtDateInput(editRatePlan?.conditions?.valid_to)}/>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;">
            <div class="campo">
              <label class="label">Código promo</label>
              <input class="input" name="promo_code" value={editRatePlan?.conditions?.promo_code ?? ''} placeholder="Opcional"/>
            </div>
            <div class="campo">
              <label class="label">Nacionalidades permitidas (vírgula)</label>
              <input class="input" name="allowed_nationalities" value={(editRatePlan?.conditions?.allowed_nationalities ?? []).join(', ')} placeholder="BR, US, EU..."/>
            </div>
          </div>
        </div>

        <!-- Categorias -->
        <div class="campo">
          <label class="label">Categorias *</label>
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:4px;">
            {#each categorias as cat}
              <label style="display:flex; align-items:center; gap:6px; font-size:13px; color:#94a3b8; cursor:pointer; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:5px 10px;">
                <input type="checkbox" name="categories" value={cat.id} checked={editRatePlan?.conditions?.categories?.includes(cat.id) ?? false} style="accent-color:#60a5fa;"/>
                {cat.group_name} <span style="color:#475569; font-size:11px;">({cat.code})</span>
              </label>
            {/each}
          </div>
        </div>

        <!-- Proteções -->
        {#if protecoes.length > 0}
          <div class="campo">
            <label class="label">Proteções incluídas</label>
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:4px;">
              {#each protecoes as prot}
                <label style="display:flex; align-items:center; gap:6px; font-size:13px; color:#94a3b8; cursor:pointer; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:5px 10px;">
                  <input type="checkbox" name="included_protections" value={prot.id} checked={editRatePlan?.included_protections?.includes(prot.id) ?? false} style="accent-color:#60a5fa;"/>
                  {prot.name} <span style="color:#475569; font-size:11px;">({prot.code})</span>
                </label>
              {/each}
            </div>
          </div>
        {/if}

        <div style="display:flex; gap:8px; justify-content:flex-end; padding-top:8px;">
          <button type="button" onclick={()=>modalRatePlan=false} style="padding:8px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); background:transparent; color:#64748b; font-size:13px; cursor:pointer; font-family:inherit;">Cancelar</button>
          <button type="submit" style="padding:8px 16px; border-radius:8px; border:none; background:#60a5fa; color:#0f172a; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit;">
            {editRatePlan ? 'Salvar Alterações' : 'Criar Plano'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .badge-info {
    font-size: 11px; font-weight: 500;
    padding: 3px 9px; border-radius: 20px;
    background: rgba(255,255,255,0.05); color: #64748b;
    white-space: nowrap;
  }
  .campo { display: flex; flex-direction: column; gap: 5px; }
  .label { font-size: 12px; font-weight: 500; color: #94a3b8; }
  .input {
    width: 100%; padding: 8px 12px; border-radius: 8px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    color: #f1f5f9; font-size: 13px; font-family: inherit;
    box-sizing: border-box;
  }
  .input:focus { outline: none; border-color: #60a5fa; }
  select.input option { background: #1e293b; }
</style>
