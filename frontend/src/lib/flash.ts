import type { Cookies } from '@sveltejs/kit';

export type FlashType = 'sucesso' | 'erro' | 'aviso' | 'info';

export interface FlashMessage {
  id: string;
  tipo: FlashType;
  mensagem: string;
  titulo?: string;
}

const FLASH_COOKIE = 'cr_flash';

export function setFlash(
  cookies: Cookies,
  flash: Omit<FlashMessage, 'id'>,
): void {
  const payload: FlashMessage = {
    id: crypto.randomUUID(),
    ...flash,
  };

  cookies.set(FLASH_COOKIE, JSON.stringify(payload), {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60,
  });
}

export function popFlash(cookies: Cookies): FlashMessage | null {
  const raw = cookies.get(FLASH_COOKIE);

  if (!raw) {
    return null;
  }

  cookies.delete(FLASH_COOKIE, { path: '/' });

  try {
    const parsed = JSON.parse(raw) as Partial<FlashMessage>;

    if (!parsed.id || !parsed.tipo || !parsed.mensagem) {
      return null;
    }

    return {
      id: parsed.id,
      tipo: parsed.tipo,
      mensagem: parsed.mensagem,
      titulo: parsed.titulo,
    };
  } catch {
    return null;
  }
}
