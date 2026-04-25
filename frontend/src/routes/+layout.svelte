<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import Notificacoes from '$lib/components/ui/Notificacoes.svelte';
  import { notificacoes } from '$lib/stores/notificacoes.store';

  type FlashMessage = {
    id: string;
    tipo: 'sucesso' | 'erro' | 'aviso' | 'info';
    mensagem: string;
    titulo?: string;
  };

  let { data, children }: { data: { flash: FlashMessage | null }; children: Snippet } = $props();
  let ultimoFlashId = $state<string | null>(null);

  $effect(() => {
    const flash = data.flash;

    if (!flash || flash.id === ultimoFlashId) {
      return;
    }

    ultimoFlashId = flash.id;

    if (flash.tipo === 'erro') notificacoes.erro(flash.mensagem, flash.titulo);
    if (flash.tipo === 'sucesso') notificacoes.sucesso(flash.mensagem, flash.titulo);
    if (flash.tipo === 'aviso') notificacoes.aviso(flash.mensagem, flash.titulo);
    if (flash.tipo === 'info') notificacoes.info(flash.mensagem, flash.titulo);
  });
</script>

<style>
  :global(html, body) { margin: 0; padding: 0; }
</style>

{@render children()}

<Notificacoes />
