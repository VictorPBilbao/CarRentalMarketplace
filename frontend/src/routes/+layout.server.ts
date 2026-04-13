import type { LayoutServerLoad } from './$types';
import { popFlash } from '$lib/flash';

export const load: LayoutServerLoad = async ({ cookies }) => {
  type PublicFlash = {
    id: string;
    tipo: 'sucesso' | 'erro' | 'aviso' | 'info';
    mensagem: string;
    titulo?: string;
  } | null;

  const flash = popFlash(cookies);
  const publicFlash: PublicFlash = flash
    ? {
        id: flash.id,
        tipo: flash.tipo,
        mensagem: flash.mensagem,
        titulo: flash.titulo,
      }
    : null;

  return {
    flash: publicFlash,
  };
};
