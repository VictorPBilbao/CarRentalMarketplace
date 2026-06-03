<script lang="ts">
  import type { ActionData, PageData } from './$types';
  import FilialForm from '$lib/components/FilialForm.svelte';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<svelte:head>
  <title>Editar Filial — CarRental</title>
</svelte:head>

<div class="page-header">
  <div>
    <a href="/locadora/filiais" class="breadcrumb">← Filiais</a>
    <h1>{data.filial.name}</h1>
    <p>Edite os dados da filial</p>
  </div>
  <span class="codigo-badge">{data.filial.code}</span>
</div>

<FilialForm
  {form}
  filial={data.filial}
  action="?/atualizar"
  acaoLabel="Salvar Alterações"
/>

<style>
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 28px;
  }
  .breadcrumb {
    font-size: 12px; color: #475569; text-decoration: none;
    display: inline-block; margin-bottom: 6px;
    transition: color 0.14s;
  }
  .breadcrumb:hover { color: #94a3b8; }
  .page-header h1 {
    font-family: 'Saira', sans-serif;
    font-size: 22px; font-weight: 600; color: #f1f5f9; margin: 0 0 4px;
  }
  .page-header p { font-size: 13px; color: #475569; margin: 0; }
  .codigo-badge {
    background: rgba(96,165,250,0.1); color: #60a5fa;
    font-size: 12px; font-weight: 600;
    padding: 4px 12px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin-top: 4px;
  }
</style>
