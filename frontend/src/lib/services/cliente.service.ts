import { api } from './api';

export interface CadastrarClienteDTO {
  primeiroNome: string;
  sobrenome: string;
  email: string;
  telefone?: string | null;
  senha: string;
}

export const clienteAuthService = {
  async cadastrar(dados: CadastrarClienteDTO): Promise<{ userId: string; mensagem: string }> {
    return api.post('/auth/cadastro/cliente', dados);
  },
};
