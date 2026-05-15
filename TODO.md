# Plano de Desenvolvimento: B2B2C Car Rental Marketplace

Este documento detalha todos os recursos pendentes para transformar o projeto em um marketplace completo (B2B2C), incluindo o sistema de gestão das locadoras, a visão do cliente final e as APIs leves em JSON para as OTAs. Tudo será implementado seguindo o modelo "Pagamento no Destino" (Pay at Desk).

## Fase 1: Correções Core e Lógicas Base

### 1. Correções de Bugs

- **O que**: Corrigir erro de cancelamento de reservas e Erro 500 na criação de tarifa One Way (Taxa de Retorno).
- **Por que**: Bloqueiam o fluxo básico e de cadastro do sistema.
- **Como**: Investigar a rota de cancelamento no backend e a payload de inserção de `One Way Fees` associadas à relação store -> store.
- **Exemplo**: Ao tentar definir R$ 150 entre GRU e CGH num `POST`, resolver o HTTP 500 corrigindo as entidades no SurrealDB.

### 2. Contexto Multi-Filial para Funcionários

- **O que**: Permitir que um funcionário trabalhe em mais de uma filial e possa alternar a visão do terminal.
- **Por que**: Funcionários muitas vezes cobrem turnos em lojas diferentes da mesma locadora (ex: folgas).
- **Como**: Usar a relação `works_at` entre tabela `usuario` e `filial`. Criar um "context switcher" (um dropdown) no frontend e repassar o ID da Loja ativa para filtrar as requisições na API.
- **Exemplo**: João loga e vê o painel da Filial "Guarulhos". No topo da tela, ele seleciona "Congonhas", a tela recarrega trazendo apenas as informações, reservas e frota da filial Congonhas.

### 3. Mecânica Prática de One-Way (Devolução Externa)

- **O que**: Lógica refinada da taxa de retorno (Drop-off fee).
- **Por que**: O carro devolvido em outra cidade precisa retornar de cegonha ou via logística paga, gerando custo adicional à locadora.
- **Como**: Avaliar a tabela `allows_return_to`. A filial de **RECEBIMENTO** (destino) configura a taxa contra quem enviou. O motor de cotação busca essa taxa extra caso a filial base de devolução seja diferente da retirada, cruzando localizações e cálculos de quilometragem entre os endereços das filiais se configurado assim.
- **Exemplo**: Retirada na Loja A e devolução na B. O motor consulta qual valor a B exige para carros da A. A loja B configurou "Taxa BRL 500". Esse valor extra surge como One-Way Fee no pacote de locação.

---

## Fase 2: Motor de Preços (Pricing Engine) e Tarifas

### 4. Inteligência de Pesquisa de Tarifas (`rate_plan`)

- **O que**: Encontrar a tabela de preço certa baseada na data, local e grupo.
- **Por que**: Diárias variam absurdamente por sazonalidade (ex: Carnaval é dobro de preço).
- **Como**: Ao receber as datas, conectar aos nós do tipo `rate_plan`. Quando as datas passam por mais de uma regra válida, aplicar lógica: Maior prioridade sempre vence (ex: tarifa feriado vence a padrão). Em caso de prioridade igual, o sistema fornece o menor valor.
- **Exemplo**: Resgate de 12 a 15 de janeiro. O sistema detecta a tarifa "Janeiro Férias" (Prioridade 1 = R$120) e "Promo Semanal" (Prioridade 2 = R$95). Sistema aplica a regra que o de maior P ganha na data especificada.

### 5. Calculadora Geral da Cotação (Quote Generator)

- **O que**: Api final de agregação do preço do aluguel (`/quote`).
- **Por que**: O cliente quer ver o envelope final detalhado (taxas, seguros, adicionais).
- **Como**: Rota estruturada `POST /quote` no python que aplica base rate x dias, depois adiciona proteções e pacotes (`protection`), taxas fixas do hub (`fee` como taxa de aeroporto) e assessórios opcionais (`addon` como bebê conforto). Também computando as regras de tolerância de hora para cobrança extra de nova diária.
- **Exemplo**: Cliente cota via sistema as infos, o backend devolve: `{"diaria_base": 300, "protecao_casco": 50, "taxa_aeroporto": 35, "one_way": 0, "total": 385}`.

---

## Fase 3: Controle Dinâmico: Ledger de Disponibilidade

### 6. Subtração e Adição do Availability Ledger

- **O que**: Controle contábil real-time de veículos livres na filial x dia x categoria.
- **Por que**: Prevenir overbooking (vender carros que não tem).
- **Como**: Rota backend que, ao rodar criação (ação do cliente), bloqueia -1 unidade no inventário de calendário daquele grupo, se confirmada a criação de `reservation`. Se houver cancelamento (ou término antecipado), sistema atualiza o ledger com +1. Mesma coisa ocorre assim que um veículo entrar em modo de DECOMMISSIONED/MANUTENÇÃO.
- **Exemplo**: Categoria SUV tem 3 veículos na frota de SP. 2 alugados do dia 01 ao dia 05. Cliente pesquisando dia 02 vai visualizar que só 1 SUV está livre.

### 7. Empréstimos Multilojas (Cross-Branch Borrowing)

- **O que**: Gestão de pátio entre filiais da mesma Locadora.
- **Por que**: Maximizar lucros. Se uma loja zerar o estoque de utilitários, puxar da filial em bairro vizinho pode salvar reservas.
- **Como**: Relacionar garagens via `can_supply_to`. Criar lógica que a pesquisa possa usar essa margem.
- **Exemplo**: Reserva em "Campinas" esgotou a categoria Sedan, mas a loja "Jundiaí" vizinha permite suprir e passa o status de ledger virtual.

---

## Fase 4: O Caminho do Consumidor C2C (Frontend `/cliente/`)

### 8. Wizard de Agendamento da Viagem (`/busca` Frontend B2C)

- **O que**: As telas de "Book a Car". Step 1 ao Step Final.
- **Por que**: Para efetivar o site como Marketplace, o cliente comum deve ter uma forma polida e confiável para cotar entre as locadoras listadas na plataforma.
- **Como**: Módulos Svelte:
    - 1º Local, Retirada e Devolução e Horários.
    - 2º Vitrine de Categorias gerada pelo `/quote`. Onde o cliente filtra.
    - 3º Página Detalhe do Carro e Proteções/Acessórios extras (cadeirinha infantil etc).
    - 4º Login (ou sign-up) -> Tela Resumo -> Tela Confirmação sem passar cartão ("Pague lá na Loja").

---

## Fase 5: Operação - Contrato de Posse e Checkout

### 9. Abertura do Aluguel Oficial - Check-out/Balcão

- **O que**: Pegar a Reserva que estava "em nuvem" ou de sistema de fora e virar chave em que o cliente leva um modelo de carne-e-osso pra casa.
- **Por que**: O contrato real detém responsabilidades legais sob aquele número de chassi, não sob "Qualquer SUV Econômico" e registra a base material da saída (hodômetro e combustível).
- **Como**: Via frontend painel Filial (PDV), o atendente puxa a `reservation`, vincula o carro físico, preenche `mileage` e visual do `fuel_level` da tela e clica e emite o Contrsto em PDF e salva o recorde `rental_agreement` do banco.
- **Exemplo**: Sistema abre reserva #99. Atendente clica "Designar", coloca placa AAA-0A0A (Renegade), KM Inicial marca 14.500KM e Tanque Cheio (8/8). O status muda de Reserved pra Active Rental.

### 10. Check-in e Encerramento Operacional

- **O que**: Procedimento de retorno do carro pela filial e apuração do faturado vs prometido.
- **Por que**: O cliente pode devolver antes, ou entregar com o tanque vazio e para-choque avariado. Tudo tem ônus para a locadora.
- **Como**: Cadastrar inspeção `checkin`. Comparar data de devolução atual real (se for tardio, o sistema emite diárias extras), quilometragem (passou do limite? então rodar faturação de kms extras pela taxa informada), combustível. Fechar saldo de "payable na devolução".

---

## Fase 6: API B2B e as OTAs (Integração Leve API - Customizada)

### 11. Endpoints Base via JSON Prático

- **O que**: Um modo dos gigantes e agências (Rentcars, Expedia, Turismos) consultarem e comprarem locações no site como robôs sem tela do Svelte.
- **Por que**: O grosso do dinheiro na locação advém do mundo corporativo/turismo massivo puxado por canais que agregam preço de todas locadoras online.
- **Como**: Descartar protocolos arcaicos (XML enormes do meio aéreo) criando APis JSON (REST) fáceis e leves.
    - `POST /api/v1/ota/auth` (Troca de credenciais).
    - `POST /api/v1/ota/availability` (Fura a DB baseado em destinos universais ou iatas e emite as cotações livres em arrays fáceis).
    - `POST /api/v1/ota/reservation` (Dá dump nos dados de reserva direta usando AuthKey robusto).
- **Exemplo**: Um servidor NodeJS de fora da Expedia manda as datas GRU a VCP. Nosso sistema dispara Quotes filtrando somente "Locadora autorizou Expedia a ser broker" respondendo um body JSON em 200 ms.

### 12. Mecanismo de Webhook Ativo

- **O que**: Eventos via HTTP (POST pra fora) quando mudanças doem o processo da OTA.
- **Por que**: Para evitar que OTAs fiquem mandando query "Já confirmou? Cancelou?" sobrecargando nosso Backend.
- **Como**: Toda OTA registrada tem um webhook_url atrelado ao perfil. Módulos do core (`cancellation`, `active_rental_start`) trigam disparo assíncrono pro lado deles.
- **Exemplo**: A OTA vendeu, mas no balcão a pessoa xingou o atendente e tomou no-show/cancel. Nós avisamos a url da OTA que a reserva #A1 morreu na origem e foi listada com reason `CANCELED_AT_DESK`.

---

## Fase 7: Centralizador (Admin Marketplace Dashboard)

### 13. Visão do Dono do B2B2C (Métricas e Onboardings)

- **O que**: Se o software é Marketplace, eu dono do software vejo dados totais pra cobrar os royalties das minhas Locadoras associadas (seja o volume vendido direto do meu b2c).
- **Por que**: Precisamos rastrear Locadoras cadastradas x Vendas Globais na aba `admin/`.
- **Como**: Utilizar Svelte route `admin/` rodando views polars ou query agregacionais SurrealDB de contagem de bookings do mês por `locadora`, além de botões "Banir Locadora X", "Aprovar Cadastro Y", "Forçar Atualizar Cache Categorias Universais".
