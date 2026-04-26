<script lang="ts">
  import type { ActionData, PageData } from './$types';
  import VeiculoForm from '$lib/components/VeiculoForm.svelte';

  let { data, form }: { data: PageData; form: ActionData } = $props();

  const filial = $derived((data as any).filial);
</script>

<svelte:head>
  <title>Novo Veículo — Filial</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/filial/frota" class="breadcrumb">Frota</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">Novo Veículo</span>
    <h1>Cadastrar Veículo</h1>
    <p>Adicione um novo veículo à frota desta loja</p>
  </div>
</div>

<VeiculoForm
  {form}
  action="?/criar"
  acaoLabel="Cadastrar Veículo"
  cancelarHref="/filial/frota"
  lojas={[]}
  categorias={data.categorias}
  lojaFixaId={filial?.id ?? ''}
  lojaFixaNome={filial?.name ?? 'Esta loja'}
/>

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .page-header p  { font-size: 13px; color: #475569; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
</style>
