<script lang="ts">
  import type { ActionData } from './$types';
  import CategoriaForm from '$lib/components/CategoriaForm.svelte';

  let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
  <title>Nova Categoria — CarRental</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/categorias" class="breadcrumb">Categorias</a>
    <span class="breadcrumb-sep">›</span>
    <span class="breadcrumb-atual">Nova</span>
    <h1>Nova Categoria de Veículo</h1>
    <p>Defina um grupo de veículos com características similares para sua frota</p>
  </div>
</div>

<CategoriaForm {form} action="?/criar" acaoLabel="Cadastrar Categoria" />

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 { font-size: 22px; font-weight: 700; color: #f1f5f9; margin: 4px 0 0; }
  .page-header p  { font-size: 13px; color: #475569; margin: 4px 0 0; }
  .breadcrumb      { font-size: 12px; color: #475569; text-decoration: none; }
  .breadcrumb:hover { color: #64748b; }
  .breadcrumb-sep  { font-size: 12px; color: #334155; margin: 0 4px; }
  .breadcrumb-atual { font-size: 12px; color: #64748b; }
</style>
