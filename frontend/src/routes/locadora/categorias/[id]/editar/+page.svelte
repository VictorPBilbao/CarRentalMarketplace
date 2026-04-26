<script lang="ts">
  import type { ActionData, PageData } from './$types';
  import CategoriaForm from '$lib/components/CategoriaForm.svelte';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<svelte:head>
  <title>Editar Categoria — CarRental</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/categorias" class="breadcrumb">Categorias</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">{data.categoria?.group_name ?? '...'}</span>
    <h1>Editar Categoria</h1>
    <p>Atualize as informações desta categoria de veículo</p>
  </div>
</div>

<CategoriaForm {form} categoria={data.categoria} action="?/atualizar" acaoLabel="Salvar Alterações" />

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .page-header p  { font-size: 13px; color: #475569; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
</style>
