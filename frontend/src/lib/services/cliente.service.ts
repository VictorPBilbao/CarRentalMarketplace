import { api } from './api';

export interface CadastrarClienteDTO {
  primeiroNome: string;
  sobrenome: string;
  email: string;
  telefone?: string | null;
  cpf: string;
  dataNascimento: string;
  senha: string;
}

export const clienteAuthService = {
  async cadastrar(dados: CadastrarClienteDTO): Promise<{ userId: string; mensagem: string }> {
    return api.post('/auth/cadastro/cliente', dados);
  },
};
