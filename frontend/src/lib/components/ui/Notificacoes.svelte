<script lang="ts">
  import { notificacoes } from '$lib/stores/notificacoes.store';
  import type { Notificacao } from '$lib/stores/notificacoes.store';

  const icones = {
    sucesso: `<path d="M2 7l3.5 3.5L12 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>`,
    erro:    `<circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="M7.5 4.5V8M7.5 10.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`,
    aviso:   `<path d="M7.5 1L14 13H1L7.5 1Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M7.5 5.5V9M7.5 11h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`,
    info:    `<circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="M7.5 7v4M7.5 4.5h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`,
  };

  function progresso(n: Notificacao) {
    return n.duracao && n.duracao > 0
      ? `animation: progresso ${n.duracao}ms linear forwards`
      : '';
  }
</script>

<div class="notif-container" aria-live="polite" aria-atomic="false">
  {#each $notificacoes as n (n.id)}
    <div class="notif notif-{n.tipo}" role="alert">

      <div class="notif-icon">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
          {@html icones[n.tipo]}
        </svg>
      </div>

      <div class="notif-body">
        {#if n.titulo}
          <p class="notif-titulo">{n.titulo}</p>
        {/if}
        <p class="notif-mensagem">{n.mensagem}</p>
      </div>

      <button
        class="notif-fechar"
        onclick={() => notificacoes.remover(n.id)}
        aria-label="Fechar notificação"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
          <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>

      {#if n.duracao && n.duracao > 0}
        <div class="notif-barra" style={progresso(n)}></div>
      {/if}

    </div>
  {/each}
</div>

<style>
  .notif-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 380px;
    width: calc(100vw - 48px);
    pointer-events: none;
  }

  .notif {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid;
    position: relative;
    overflow: hidden;
    pointer-events: all;
    animation: entrar 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  /* tipos */
  .notif-sucesso {
    background: rgba(16, 185, 129, 0.08);
    border-color: rgba(16, 185, 129, 0.25);
  }
  .notif-erro {
    background: rgba(239, 68, 68, 0.08);
    border-color: rgba(239, 68, 68, 0.25);
  }
  .notif-aviso {
    background: rgba(245, 158, 11, 0.08);
    border-color: rgba(245, 158, 11, 0.25);
  }
  .notif-info {
    background: rgba(79, 142, 247, 0.08);
    border-color: rgba(79, 142, 247, 0.25);
  }

  /* ícone */
  .notif-icon {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .notif-sucesso .notif-icon { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  .notif-erro    .notif-icon { background: rgba(239, 68, 68, 0.15);  color: #f87171; }
  .notif-aviso   .notif-icon { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
  .notif-info    .notif-icon { background: rgba(79, 142, 247, 0.15); color: #93b8fb; }

  /* texto */
  .notif-body { flex: 1; min-width: 0; }
  .notif-titulo {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 2px;
  }
  .notif-sucesso .notif-titulo { color: #34d399; }
  .notif-erro    .notif-titulo { color: #f87171; }
  .notif-aviso   .notif-titulo { color: #fbbf24; }
  .notif-info    .notif-titulo { color: #93b8fb; }

  .notif-mensagem {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.835rem;
    line-height: 1.5;
    color: rgba(232, 234, 240, 0.75);
  }

  /* fechar */
  .notif-fechar {
    flex-shrink: 0;
    background: none;
    border: none;
    cursor: pointer;
    color: rgba(232, 234, 240, 0.3);
    padding: 2px;
    transition: color 0.2s;
    line-height: 0;
  }
  .notif-fechar:hover { color: rgba(232, 234, 240, 0.7); }

  /* barra de progresso */
  .notif-barra {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    width: 100%;
    transform-origin: left;
  }
  .notif-sucesso .notif-barra { background: #34d399; }
  .notif-erro    .notif-barra { background: #f87171; }
  .notif-aviso   .notif-barra { background: #fbbf24; }
  .notif-info    .notif-barra { background: #4f8ef7; }

  @keyframes entrar {
    from { opacity: 0; transform: translateX(20px) scale(0.95); }
    to   { opacity: 1; transform: translateX(0)    scale(1); }
  }
  @keyframes progresso {
    from { transform: scaleX(1); }
    to   { transform: scaleX(0); }
  }

  @media (max-width: 480px) {
    .notif-container { bottom: 16px; right: 16px; left: 16px; width: auto; }
  }
</style>