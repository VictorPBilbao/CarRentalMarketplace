# Car Rental Marketplace - TODO & Roadmap

## 1. Engine de Precificação e Reservas (Critico)

- [ ] **Tarifário (Rate Plans)**: Implementar lógica de busca no backend (`rate_plan`). Receber parâmetros (datas, loja, idade, promocode, etc) e retornar os planos validos priorizando o menor valor.
- [ ] **Tabela de Taxas e Opcionais Nível Loja**:
    - Garantir no backend que `fee` (aeroporto, adm) e `addon` associados às lojas sejam somados no `quote`.
    - Revisar se `protection` (atualmente a nível de `company`) precisa ser alterada para array de `stores` no SurrealDB caso as regras locais exijam divergência de proteção.
- [ ] **One Way Fee (Taxa de Retorno)**:
    - Ao fazer a cotação, se `pickup_store != dropoff_store`, consultar a edge `allows_return_to` para somar a taxa de devolução no extrato de preços.
- [ ] **Motor de Disponibilidade**:
    - Implementar lógica no backend/banco para consultar/modificar a `availability_ledger`.
    - Bloquear reserva se `total_fleet - total_booked - total_maintenance <= 0`.
    - Criar um **Event / Trigger no SurrealDB** (ou job Python) para atualizar o ledger automaticamente em toda transação de veículo ou nova reserva.
- [ ] **Estoque Compartilhado (Empréstimo de Veículos)**:
    - Se a cotação zerar na loja atual, realizar uma consulta de grafo `->can_supply_to->` para visualizar disponibilidade em filiais vizinhas, embutindo tempo de trânsito e `transfer_fee`.

## 2. API para OTAs (Online Travel Agencies)

- [ ] Criar rotas específicas `/api/v1/ota/*` focadas em B2B.
- [ ] Implementar autenticação severa (API Keys/Tokens longo prazo) vinculada a registros de "Company" parceira.
- [ ] Restringir acessos a apenas rotas de `quotes` e `reservation` creation (endpoints de frota e RH ocultos).

## 3. Gestão e Operações

- [ ] **Automação do Código ACRISS**:
    - Criar função utilitária e evento no banco para preencher automaticamente o campo `acriss_code` na criação de categorias (ex: `ECAR` = Econômico, 2-4 portas, Automático, A/C).
- [ ] **Validação de Documentos para Clientes**:
    - Garantir CNH válida (imagem/OCR) para "Reservantes" - Diferenciar cliente comum de funcionários na criação do `user`.
- [ ] **Funcionário Multi-Lojas**:
    - A estruturação no DB como grafo (`works_at`) já permite um `user` em várias `stores`.
    - Ajustar UI e Contexto Global do Svelte para permitir que o usuário de RH/Atendimento _"troque a loja ativa em sessão"_ na tela (Switch Store Context), muito comum em sistemas PDV de locadoras.
- [ ] **Contratos de Aluguel (Rental Agreement)**:
    - Criar fluxos inteiros para Check-In (Abertura de contrato, bloqueio caução/cartão, fotos de avarias, quilometragem, combustível).
    - Criar fluxos de Check-Out (Cálculo dias extras, cálculo combustível faltante, quebra de caução).

## 4. Frontend & Componentes (Svelte 5)

- [ ] Atualizar formulários criando componentes reutilizáveis para Taxas, Reservas e Contratos seguindo Runes do Svelte 5 (`$state`, `$derived`).
- [ ] Implementar as visões de _Disponibilidade Diária (Ledger Calendar)_ e _Radar de Frota_ no painel da Filial.
