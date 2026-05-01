<script lang="ts">
  import { enhance } from '$app/forms';
  import { page } from '$app/state';
  import type { ActionData, PageData } from './$types';
  import type { OneWayRule } from '$lib/services/tarifa.service';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const filial  = $derived((page.data as any)?.filial ?? null);
  const rules: OneWayRule[] = $derived(data.rules ?? []);
  const lojas   = $derived(data.lojas ?? []);

  let modal = $state(false);
  let editRule = $state<OneWayRule | null>(null);

  function abrirNova() { editRule = null; modal = true; }
  function abrirEdit(r: OneWayRule) { editRule = r; modal = true; }

  $effect(() => {
    if ((form as any)?.sucesso) modal = false;
  });

  function moeda(v: number) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  // ── Grafo SVG ──
  // Loja atual no centro, outras lojas ao redor em círculo
  const SVG_W = 560;
  const SVG_H = 360;
  const CX = SVG_W / 2;
  const CY = SVG_H / 2;
  const ORBIT_R = 140;
  const NODE_R  = 36;

  const TIPO_FEE_LABEL: Record<string, string> = {
    FREE: 'Grátis', FIXED: 'Taxa Fixa', PER_KM: 'Por Km',
  };

  // Lojas que NÃO são a atual (para posicionar no grafo)
  const lojasExternas = $derived(
    lojas.filter((l: any) => l.id !== filial?.id)
  );

  // Map ruleId → from_store_id para lookup rápido
  const rulesByStore = $derived(() => {
    const m = new Map<string, OneWayRule>();
    for (const r of rules) m.set(r.from_store_id, r);
    return m;
  });

  function nodePos(i: number, total: number): { x: number; y: number } {
    if (total === 0) return { x: CX, y: CY - ORBIT_R };
    const angle = (2 * Math.PI * i) / total - Math.PI / 2;
    return {
      x: CX + ORBIT_R * Math.cos(angle),
      y: CY + ORBIT_R * Math.sin(angle),
    };
  }

  let hoveredStore = $state<string | null>(null);
</script>

<div style="max-width:900px;">

  <!-- Header -->
  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:24px; flex-wrap:wrap;">
    <div>
      <h1 style="font-size:20px; font-weight:600; color:#f1f5f9; margin:0 0 4px;">Configuração One-Way</h1>
      <p style="font-size:13px; color:#475569; margin:0;">
        Defina quais lojas podem devolver veículos na <strong style="color:#94a3b8;">{filial?.name ?? 'sua loja'}</strong> e qual taxa será cobrada.
      </p>
    </div>
    <button onclick={abrirNova} style="
      display:flex; align-items:center; gap:6px;
      padding:8px 14px; border-radius:8px;
      background:rgba(52,211,153,0.12); border:1px solid rgba(52,211,153,0.25);
      color:#34d399; font-size:13px; font-weight:500; cursor:pointer; font-family:inherit;
    ">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1v11M1 6.5h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      Nova Regra
    </button>
  </div>

  {#if (form as any)?.erro}
    <div style="background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.2); border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:13px; color:#f87171;">{(form as any).erro}</div>
  {/if}

  <!-- ── Grafo ── -->
  <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.07); border-radius:16px; overflow:hidden; margin-bottom:24px;">
    <div style="padding:14px 20px; border-bottom:1px solid rgba(255,255,255,0.07);">
      <p style="font-size:13px; color:#475569; margin:0;">
        As linhas mostram as lojas que podem devolver veículos aqui.
        <span style="color:#34d399;">Verde</span> = regra ativa com taxa configurada.
        <span style="color:#334155;">Cinza</span> = sem regra definida.
      </p>
    </div>
    <div style="padding:20px; display:flex; justify-content:center;">
      <svg width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}" style="max-width:100%; overflow:visible;">

        <!-- Linhas de conexão -->
        {#each lojasExternas as loja, i}
          {@const pos = nodePos(i, lojasExternas.length)}
          {@const rule = rulesByStore().get(loja.id)}
          {@const hasRule = !!rule && rule.active}
          <line
            x1={CX} y1={CY}
            x2={pos.x} y2={pos.y}
            stroke={hasRule ? '#34d399' : '#1e293b'}
            stroke-width={hoveredStore === loja.id ? 2 : 1.5}
            stroke-dasharray={hasRule ? 'none' : '4 4'}
            opacity={hoveredStore && hoveredStore !== loja.id ? 0.3 : 1}
          />
          <!-- Label da taxa no meio da linha -->
          {#if hasRule}
            {@const mx = (CX + pos.x) / 2}
            {@const my = (CY + pos.y) / 2}
            <rect x={mx - 28} y={my - 10} width="56" height="18" rx="9"
              fill="rgba(52,211,153,0.12)" stroke="rgba(52,211,153,0.3)" stroke-width="1"/>
            <text x={mx} y={my + 4} text-anchor="middle"
              font-size="10" fill="#34d399" font-family="DM Sans, sans-serif">
              {rule.fee_type === 'FREE' ? 'Grátis' : rule.fee_type === 'PER_KM' ? '/km' : moeda(rule.amount)}
            </text>
          {:else}
            {@const mx = (CX + pos.x) / 2}
            {@const my = (CY + pos.y) / 2}
            <text x={mx} y={my + 4} text-anchor="middle"
              font-size="10" fill="#334155" font-family="DM Sans, sans-serif">sem regra</text>
          {/if}
        {/each}

        <!-- Nó da loja atual (centro) -->
        <circle cx={CX} cy={CY} r={NODE_R} fill="#0f172a" stroke="#34d399" stroke-width="2"/>
        <circle cx={CX} cy={CY} r={NODE_R - 6} fill="rgba(52,211,153,0.08)"/>
        <text x={CX} y={CY - 5} text-anchor="middle" font-size="11" font-weight="600" fill="#34d399" font-family="DM Sans, sans-serif">
          {filial?.code ?? '?'}
        </text>
        <text x={CX} y={CY + 8} text-anchor="middle" font-size="9" fill="#475569" font-family="DM Sans, sans-serif">
          Sua loja
        </text>

        <!-- Nós das lojas externas -->
        {#each lojasExternas as loja, i}
          {@const pos = nodePos(i, lojasExternas.length)}
          {@const rule = rulesByStore().get(loja.id)}
          {@const hasRule = !!rule && rule.active}
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <g
            style="cursor:pointer"
            onmouseenter={() => hoveredStore = loja.id}
            onmouseleave={() => hoveredStore = null}
            onclick={() => rule ? abrirEdit(rule) : abrirNova()}
            opacity={hoveredStore && hoveredStore !== loja.id ? 0.4 : 1}
          >
            <circle cx={pos.x} cy={pos.y} r={NODE_R}
              fill="#0f172a"
              stroke={hasRule ? 'rgba(52,211,153,0.5)' : 'rgba(255,255,255,0.1)'}
              stroke-width={hoveredStore === loja.id ? 2 : 1}/>
            <circle cx={pos.x} cy={pos.y} r={NODE_R - 6}
              fill={hasRule ? 'rgba(52,211,153,0.06)' : 'rgba(255,255,255,0.02)'}/>
            <text x={pos.x} y={pos.y - 5} text-anchor="middle" font-size="11" font-weight="600"
              fill={hasRule ? '#34d399' : '#64748b'} font-family="DM Sans, sans-serif">
              {loja.code}
            </text>
            <text x={pos.x} y={pos.y + 8} text-anchor="middle" font-size="9"
              fill="#475569" font-family="DM Sans, sans-serif">
              {loja.name.split(' ').slice(-1)[0]}
            </text>
          </g>
        {/each}

      </svg>
    </div>
  </div>

  <!-- ── Tabela de regras ── -->
  {#if rules.length === 0}
    <div style="text-align:center; padding:40px 0; color:#334155; font-size:14px;">
      Nenhuma regra one-way configurada. Clique em "Nova Regra" para começar.
    </div>
  {:else}
    <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.07); border-radius:12px; overflow:hidden;">
      <table style="width:100%; border-collapse:collapse;">
        <thead>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
            <th style="padding:12px 20px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Loja de origem</th>
            <th style="padding:12px 16px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Tipo de taxa</th>
            <th style="padding:12px 16px; text-align:right; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Valor</th>
            <th style="padding:12px 16px; text-align:center; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Status</th>
            <th style="padding:12px 16px; width:60px;"></th>
          </tr>
        </thead>
        <tbody>
          {#each rules as rule}
            <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
              <td style="padding:12px 20px; font-size:13px; font-weight:500; color:#cbd5e1;">{rule.from_store_name || rule.from_store_id}</td>
              <td style="padding:12px 16px; font-size:12px; color:#64748b;">{TIPO_FEE_LABEL[rule.fee_type] ?? rule.fee_type}</td>
              <td style="padding:12px 16px; text-align:right; font-size:13px; font-weight:600; color:#f1f5f9;">
                {rule.fee_type === 'FREE' ? '—' : rule.fee_type === 'PER_KM' ? `${moeda(rule.amount)}/km` : moeda(rule.amount)}
              </td>
              <td style="padding:12px 16px; text-align:center;">
                <span style="font-size:10px; font-weight:600; text-transform:uppercase; padding:2px 8px; border-radius:20px; background:{rule.active?'rgba(52,211,153,0.12)':'rgba(100,116,139,0.12)'}; color:{rule.active?'#34d399':'#64748b'};">{rule.active?'Ativa':'Inativa'}</span>
              </td>
              <td style="padding:12px 16px; text-align:right;">
                <button onclick={() => abrirEdit(rule)} style="background:transparent; border:none; color:#475569; cursor:pointer; padding:4px 8px; border-radius:6px; font-size:12px;" onmouseenter={(e)=>{(e.currentTarget as HTMLElement).style.color='#94a3b8'}} onmouseleave={(e)=>{(e.currentTarget as HTMLElement).style.color='#475569'}}>Editar</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- ── Modal ── -->
{#if modal}
  <div style="position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:50; display:flex; align-items:center; justify-content:center; padding:20px;" onclick={(e)=>{if(e.target===e.currentTarget)modal=false}}>
    <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.1); border-radius:16px; width:100%; max-width:420px;">
      <div style="padding:20px 24px; border-bottom:1px solid rgba(255,255,255,0.07); display:flex; align-items:center; justify-content:space-between;">
        <h2 style="font-size:16px; font-weight:600; color:#f1f5f9; margin:0;">{editRule ? 'Editar Regra' : 'Nova Regra One-Way'}</h2>
        <button onclick={()=>modal=false} style="background:transparent; border:none; color:#475569; cursor:pointer; font-size:20px;">×</button>
      </div>
      <form method="POST" action={editRule ? '?/atualizar' : '?/criar'} use:enhance style="padding:24px; display:flex; flex-direction:column; gap:16px;">
        {#if editRule}<input type="hidden" name="id" value={editRule.id}/>{/if}

        <div class="campo">
          <label class="label">Loja de origem (quem devolve aqui) *</label>
          <select class="input" name="from_store_id" required disabled={!!editRule}>
            <option value="">Selecione...</option>
            {#each lojas.filter((l: any) => l.id !== filial?.id) as loja}
              <option value={loja.id} selected={editRule?.from_store_id === loja.id}>{loja.name} ({loja.code})</option>
            {/each}
          </select>
          {#if editRule}<input type="hidden" name="from_store_id" value={editRule.from_store_id}/>{/if}
        </div>
        <div class="campo">
          <label class="label">Tipo de taxa</label>
          <select class="input" name="fee_type">
            <option value="FREE" selected={editRule?.fee_type === 'FREE' || !editRule}>Grátis (sem taxa)</option>
            <option value="FIXED" selected={editRule?.fee_type === 'FIXED'}>Taxa fixa (R$)</option>
            <option value="PER_KM" selected={editRule?.fee_type === 'PER_KM'}>Por quilômetro (R$/km)</option>
          </select>
        </div>
        <div class="campo">
          <label class="label">Valor (R$) — deixe 0 para Grátis</label>
          <input class="input" type="number" name="amount" step="0.01" min="0" value={editRule?.amount ?? 0} placeholder="0.00"/>
        </div>
        <div class="campo">
          <label class="label">Status</label>
          <select class="input" name="active">
            <option value="true" selected={editRule?.active !== false}>Ativa</option>
            <option value="false" selected={editRule?.active === false}>Inativa</option>
          </select>
        </div>
        <div style="display:flex; gap:8px; justify-content:flex-end; padding-top:8px;">
          <button type="button" onclick={()=>modal=false} style="padding:8px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); background:transparent; color:#64748b; font-size:13px; cursor:pointer; font-family:inherit;">Cancelar</button>
          <button type="submit" style="padding:8px 16px; border-radius:8px; border:none; background:#34d399; color:#0f172a; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit;">
            {editRule ? 'Salvar' : 'Criar Regra'}
          </button>
        </div>
        {#if editRule}
          <form method="POST" action="?/excluir" use:enhance style="border-top:1px solid rgba(255,255,255,0.07); padding-top:12px; margin-top:4px;">
            <input type="hidden" name="id" value={editRule.id}/>
            <button type="submit" style="width:100%; padding:8px; border-radius:8px; border:1px solid rgba(248,113,113,0.2); background:rgba(248,113,113,0.06); color:#f87171; font-size:13px; cursor:pointer; font-family:inherit;">
              Excluir Regra
            </button>
          </form>
        {/if}
      </form>
    </div>
  </div>
{/if}

<style>
  .campo { display: flex; flex-direction: column; gap: 5px; }
  .label { font-size: 12px; font-weight: 500; color: #94a3b8; }
  .input {
    width: 100%; padding: 8px 12px; border-radius: 8px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    color: #f1f5f9; font-size: 13px; font-family: inherit; box-sizing: border-box;
  }
  .input:focus { outline: none; border-color: #34d399; }
  select.input option { background: #1e293b; }
  select.input:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
