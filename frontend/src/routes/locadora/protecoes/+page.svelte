<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData, PageData } from './$types';
  import type { ProtecaoItem } from '$lib/services/tarifa.service';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const protecoes: ProtecaoItem[] = $derived(data.protecoes ?? []);
  const categorias                = $derived(data.categorias ?? []);

  let modal    = $state(false);
  let editProt = $state<ProtecaoItem | null>(null);

  function moeda(v: number) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function abrirNova()                   { editProt = null; modal = true; }
  function abrirEditar(p: ProtecaoItem)  { editProt = p;    modal = true; }

  function rateForCat(prot: ProtecaoItem, catId: string): number {
    return prot.pricing_matrix.find((m) => m.category === catId)?.daily_rate ?? 0;
  }
  function deductibleForCat(prot: ProtecaoItem, catId: string): number {
    return prot.pricing_matrix.find((m) => m.category === catId)?.deductible_amount ?? 0;
  }

  $effect(() => {
    if ((form as any)?.sucesso) modal = false;
  });
</script>

<div style="max-width:1000px;">

  <!-- Header -->
  <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:24px; gap:16px; flex-wrap:wrap;">
    <div>
      <h1 style="font-size:20px; font-weight:600; color:#f1f5f9; margin:0 0 4px;">Proteções</h1>
      <p style="font-size:13px; color:#475569; margin:0;">Gerencie proteções incluídas nos planos tarifários.</p>
    </div>
    <button onclick={abrirNova} style="
      display:flex; align-items:center; gap:6px;
      padding:8px 14px; border-radius:8px;
      background:rgba(96,165,250,0.12); border:1px solid rgba(96,165,250,0.25);
      color:#60a5fa; font-size:13px; font-weight:500; cursor:pointer; font-family:inherit;
    ">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1v11M1 6.5h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      Nova Proteção
    </button>
  </div>

  {#if (form as any)?.erro}
    <div style="background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.2); border-radius:8px; padding:10px 14px; margin-bottom:16px; font-size:13px; color:#f87171;">{(form as any).erro}</div>
  {/if}

  {#if protecoes.length === 0}
    <div style="text-align:center; padding:60px 0; color:#334155;">Nenhuma proteção cadastrada. Clique em "Nova Proteção" para adicionar.</div>
  {:else}
    <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.07); border-radius:12px; overflow:hidden;">
      <table style="width:100%; border-collapse:collapse;">
        <thead>
          <tr style="border-bottom:1px solid rgba(255,255,255,0.07);">
            <th style="padding:12px 20px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Nome</th>
            <th style="padding:12px 16px; text-align:left; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Código</th>
            <th style="padding:12px 16px; text-align:center; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#334155;">Categorias</th>
            <th style="padding:12px 16px; width:100px;"></th>
          </tr>
        </thead>
        <tbody>
          {#each protecoes as prot}
            <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
              <td style="padding:13px 20px; font-size:13px; font-weight:500; color:#cbd5e1;">{prot.name}</td>
              <td style="padding:13px 16px; font-size:12px; font-family:monospace; color:#60a5fa;">{prot.code}</td>
              <td style="padding:13px 16px; text-align:center;">
                <span style="font-size:12px; font-weight:600; color:#94a3b8;">{prot.pricing_matrix.length}</span>
              </td>
              <td style="padding:13px 16px; text-align:right; display:flex; gap:4px; justify-content:flex-end;">
                <button onclick={() => abrirEditar(prot)} style="background:transparent; border:none; color:#475569; cursor:pointer; padding:4px 8px; border-radius:6px; font-size:12px;" onmouseenter={(e)=>{(e.currentTarget as HTMLElement).style.color='#94a3b8'}} onmouseleave={(e)=>{(e.currentTarget as HTMLElement).style.color='#475569'}}>Editar</button>
                <form method="POST" action="?/excluir" use:enhance>
                  <input type="hidden" name="id" value={prot.id}/>
                  <button type="submit" style="background:transparent; border:none; color:#475569; cursor:pointer; padding:4px 8px; border-radius:6px; font-size:12px;" onmouseenter={(e)=>{(e.currentTarget as HTMLElement).style.color='#f87171'}} onmouseleave={(e)=>{(e.currentTarget as HTMLElement).style.color='#475569'}}>Excluir</button>
                </form>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

</div>

<!-- ── Modal ─────────────────────────────────────────────────────────────────── -->
{#if modal}
  <div style="position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:50; display:flex; align-items:center; justify-content:center; padding:20px;" onclick={(e)=>{if(e.target===e.currentTarget)modal=false}}>
    <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.1); border-radius:16px; width:100%; max-width:520px; max-height:90vh; overflow-y:auto;">
      <div style="padding:20px 24px; border-bottom:1px solid rgba(255,255,255,0.07); display:flex; align-items:center; justify-content:space-between;">
        <h2 style="font-size:16px; font-weight:600; color:#f1f5f9; margin:0;">{editProt ? 'Editar Proteção' : 'Nova Proteção'}</h2>
        <button onclick={()=>modal=false} style="background:transparent; border:none; color:#475569; cursor:pointer; font-size:20px; line-height:1;">×</button>
      </div>
      <form method="POST" action={editProt ? '?/atualizar' : '?/criar'} use:enhance style="padding:24px; display:flex; flex-direction:column; gap:16px;">
        {#if editProt}<input type="hidden" name="id" value={editProt.id}/>{/if}

        <div style="display:grid; grid-template-columns:2fr 1fr; gap:12px;">
          <div class="campo">
            <label class="label">Nome *</label>
            <input class="input" name="name" required value={editProt?.name ?? ''} placeholder="Ex: Proteção Básica (LDW)"/>
          </div>
          <div class="campo">
            <label class="label">Código *</label>
            <input class="input" name="code" required value={editProt?.code ?? ''} placeholder="PROT_BASICA"/>
          </div>
        </div>

        <!-- Pricing por categoria -->
        {#if categorias.length > 0}
          <div style="border:1px solid rgba(255,255,255,0.07); border-radius:10px; overflow:hidden;">
            <div style="padding:12px 16px; background:rgba(255,255,255,0.02); border-bottom:1px solid rgba(255,255,255,0.07); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#475569;">
              Preços por Categoria
            </div>
            <div style="padding:12px 16px; display:flex; flex-direction:column; gap:12px;">
              {#each categorias as cat}
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; align-items:center;">
                  <div style="font-size:13px; color:#94a3b8;">
                    {cat.group_name} <span style="color:#475569; font-size:11px;">({cat.code})</span>
                  </div>
                  <div class="campo">
                    <label class="label">Diária (R$)</label>
                    <input type="hidden" name="cat_id" value={cat.id}/>
                    <input class="input" type="number" name="cat_rate" step="0.01" min="0"
                      value={editProt ? (editProt.pricing_matrix.find(m => m.category === cat.id)?.daily_rate ?? '') : ''}
                      placeholder="0.00"/>
                  </div>
                  <div class="campo">
                    <label class="label">Franquia (R$)</label>
                    <input class="input" type="number" name="cat_deductible" step="0.01" min="0"
                      value={editProt ? (editProt.pricing_matrix.find(m => m.category === cat.id)?.deductible_amount ?? '') : ''}
                      placeholder="0.00"/>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <div style="display:flex; gap:8px; justify-content:flex-end; padding-top:8px;">
          <button type="button" onclick={()=>modal=false} style="padding:8px 16px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); background:transparent; color:#64748b; font-size:13px; cursor:pointer; font-family:inherit;">Cancelar</button>
          <button type="submit" style="padding:8px 16px; border-radius:8px; border:none; background:#60a5fa; color:#0f172a; font-size:13px; font-weight:600; cursor:pointer; font-family:inherit;">
            {editProt ? 'Salvar Alterações' : 'Criar Proteção'}
          </button>
        </div>
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
    color: #f1f5f9; font-size: 13px; font-family: inherit;
    box-sizing: border-box;
  }
  .input:focus { outline: none; border-color: #60a5fa; }
  select.input option { background: #1e293b; }
</style>
