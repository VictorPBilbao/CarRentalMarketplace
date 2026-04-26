<script lang="ts">
  import type { ActionData, PageData } from './$types';
  import VeiculoForm from '$lib/components/VeiculoForm.svelte';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<svelte:head>
  <title>Editar Veículo — CarRental</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/frota" class="breadcrumb">Frota</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">{data.veiculo.make} {data.veiculo.model}</span>
    <h1>Editar Veículo</h1>
    <p>{data.veiculo.plate} · {data.veiculo.year}</p>
  </div>
</div>

<VeiculoForm
  {form}
  veiculo={data.veiculo}
  action="?/atualizar"
  acaoLabel="Salvar Alterações"
  lojas={data.lojas}
  categorias={data.categorias}
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
