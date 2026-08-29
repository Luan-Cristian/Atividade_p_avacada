# Especificação de Requisitos
## Sistema Inteligente de Gestão e Otimização de Espaços Corporativos

> Este documento é a fonte da verdade do projeto. Toda decisão de design
> (`design.md`) e toda tarefa de implementação (`tasks.md`) deve remeter a um
> requisito listado aqui. Mudanças de comportamento passam primeiro por este
> arquivo, depois pelo design, só então pelo código.

## 1. Contexto

Empresa multinacional com ~7.000 funcionários em um prédio de 9 andares.
A distribuição de salas hoje é manual, gerando ociosidade, conflitos e falta
de rastreabilidade nas decisões. Precisamos de um sistema que sugira
automaticamente a melhor distribuição possível, mantendo a decisão final sob
controle humano.

## 2. Perfis de usuário

| Perfil | Pode fazer |
|---|---|
| Coordenador Geral | cadastrar/visualizar salas, disponibilizar espaços por setor, executar otimização global, aprovar/revisar sugestões |
| Coordenador de Setor | informar equipes, quantidade de funcionários, restrições, prioridades do seu setor |

## 3. Requisitos funcionais

- **RF01** — Cadastrar e listar salas (id, andar, capacidade, tipo, recursos, acessibilidade, disponibilidade).
- **RF02** — Cadastrar setores e equipes (funcionários, horário, requisitos, prioridade).
- **RF03** — Cadastrar restrições (capacidade mínima, andar permitido, acessibilidade obrigatória, equipamento obrigatório, proximidade, separação de setores, sala reservada, prioridade).
- **RF04** — Gerar uma proposta de alocação automaticamente a partir dos dados acima ("Gerar alocação otimizada").
- **RF05** — Cada alocação sugerida deve vir acompanhada de uma justificativa legível por humanos (explicabilidade).
- **RF06** — Equipes sem solução compatível devem aparecer como exceção documentada (causa + encaminhamento), nunca como alocação inválida.
- **RF07** — O Coordenador Geral pode aceitar, rejeitar ou alterar manualmente qualquer alocação sugerida; toda intervenção é registrada.
- **RF08** — Dashboard executivo com ocupação total, por andar, salas disponíveis/ocupadas, funcionários (não) alocados, violações de restrição.
- **RF09** — Tela de comparação entre a situação inicial (baseline manual) e a otimizada.
- **RF10** — Toda execução do motor gera um registro de governança (quem, quando, algoritmo, resultado agregado).
- **RF11** — Painel de observabilidade com tempo de execução, taxa de alocação, ocupação média, conflitos e intervenções manuais acumuladas.

## 4. Requisitos não funcionais

- **RNF01** — Uma execução do motor de alocação deve terminar em menos de 5 segundos para o volume de dados do protótipo (~40 equipes, ~100 salas).
- **RNF02** — O motor não pode ser uma caixa-preta: toda decisão precisa ser explicável em linguagem natural.
- **RNF03** — O código deve ter testes automatizados executados em CI a cada push.
- **RNF04** — O sistema não pode gerar alocações que violem capacidade de sala ou restrições obrigatórias, mesmo sob pressão de "fechar a conta".

## 5. Critérios de aceitação

1. Nenhuma sala recebe mais pessoas do que sua capacidade.
2. Nenhuma restrição obrigatória é ignorada por uma alocação válida.
3. 100% das alocações retornadas possuem justificativa preenchida.
4. Toda equipe não alocada tem causa e encaminhamento registrados.
5. A alocação otimizada nunca é pior que a baseline manual (ociosidade, equipes sem sala, violações).
6. Toda execução é registrada no log de governança e concluída em < 5s.

## 6. Fora de escopo (para o MVP de uma semana)

- Autenticação/perfis de usuário reais.
- Persistência em banco de dados (o protótipo usa armazenamento em memória).
- Otimização exata (solver de programação linear); usamos heurística gulosa.
