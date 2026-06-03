<script lang="ts">
  import type { ActionData } from './$types';
  import FilialForm from '$lib/components/FilialForm.svelte';

  let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
  <title>Nova Filial — CarRental</title>
</svelte:head>

<div class="page-header">
  <h1>Nova Filial</h1>
  <p>Preencha os dados para cadastrar uma nova filial na rede</p>
</div>

<FilialForm {form} action="?/criar" acaoLabel="Cadastrar Filial" />

<style>
  .page-header { margin-bottom: 28px; }
  .page-header h1 {
    font-family: 'Saira', sans-serif;
    font-size: 22px; font-weight: 600; color: #f1f5f9; margin: 0 0 4px;
  }
  .page-header p { font-size: 13px; color: #475569; margin: 0; }
</style>
