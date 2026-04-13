import { writable } from 'svelte/store';

export type TipoNotificacao = 'sucesso' | 'erro' | 'aviso' | 'info';

export interface Notificacao {
  id:        string;
  tipo:      TipoNotificacao;
  titulo?:   string;
  mensagem:  string;
  duracao?:  number; // ms — 0 = não fecha sozinho
}

function criarStore() {
  const { subscribe, update } = writable<Notificacao[]>([]);

  function adicionar(notificacao: Omit<Notificacao, 'id'>) {
    const id = crypto.randomUUID();
    const duracao = notificacao.duracao ?? 4000;

    update(lista => [...lista, { ...notificacao, id, duracao }]);

    if (duracao > 0) {
      setTimeout(() => remover(id), duracao);
    }
  }

  function remover(id: string) {
    update(lista => lista.filter(n => n.id !== id));
  }

  return {
    subscribe,
    remover,
    sucesso: (mensagem: string, titulo?: string) =>
      adicionar({ tipo: 'sucesso', mensagem, titulo }),
    erro: (mensagem: string, titulo?: string) =>
      adicionar({ tipo: 'erro', mensagem, titulo, duracao: 6000 }),
    aviso: (mensagem: string, titulo?: string) =>
      adicionar({ tipo: 'aviso', mensagem, titulo }),
    info: (mensagem: string, titulo?: string) =>
      adicionar({ tipo: 'info', mensagem, titulo }),
  };
}

export const notificacoes = criarStore();