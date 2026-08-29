# Design
## Deriva de: `requirements.md`

## 1. Arquitetura geral

```
frontend (React + Vite)  --HTTP JSON-->  backend (FastAPI)
                                             |
                                        allocation_engine.py
                                             |
                                        storage.py (em memória)
```

Separação escolhida para atender **RF04–RF11**: o backend concentra toda a
lógica de negócio e estado; o frontend é uma camada de apresentação sem
regras próprias, para que a governança e a explicabilidade fiquem
centralizadas em um único lugar auditável.

## 2. Modelo de dados (`models.py`) — atende RF01, RF02, RF03

`Sala`, `Setor`, `Equipe`, `Restricao` como `pydantic.BaseModel`, validados
na borda da API. `Restricao` tem um campo `tipo` (enum `TipoRestricao`) para
permitir novos tipos de restrição sem alterar o schema.

## 3. Motor de alocação (`allocation_engine.py`) — atende RF04, RF05, RF06, RNF01, RNF02, RNF04

**Decisão**: heurística gulosa determinística, não ML e não solver exato.
Justificativa: RNF01 exige resposta em segundos para dezenas de
equipes/salas; RNF02 exige explicabilidade total — um solver de caixa-preta
ou um modelo de ML dificultaria justificar cada decisão em linguagem
natural. A heurística troca otimalidade global por velocidade,
determinismo e rastreabilidade, o que é aceitável conforme o enunciado
("não é necessário implementar um modelo complexo de Machine Learning").

**Algoritmo**:
1. Ordena equipes por prioridade e tamanho (equipes maiores primeiro, dentro da mesma prioridade).
2. Filtra salas por restrições obrigatórias (RNF04 — nunca aloca acima da capacidade nem ignora obrigatórias).
3. Pontua as candidatas por ocupação, aderência a andar preferido e proximidade com equipes relacionadas.
4. Sem candidata → vira exceção com causa e encaminhamento (RF06), nunca uma alocação forçada.

## 4. API (`main.py`) — atende RF07, RF08, RF09, RF10, RF11

Endpoints REST simples, sem autenticação (fora de escopo do MVP, ver
`requirements.md` §6). `POST /alocacao/gerar` é a única rota que dispara o
motor; todas as outras são leitura ou intervenção humana
(`POST /alocacao/intervencao`, que atende RF07 e grava em
`storage.intervencoes`).

## 5. Frontend (`frontend/src`) — atende RF08, RF09

Uma aba por tela do fluxo descrito no enunciado (Painel, Alocação,
Comparação, Cadastro, Governança, Monitoramento), sem roteador — troca de
estado local (`aba`) é suficiente para o escopo do MVP e evita dependência
extra.

## 6. Alternativas consideradas e descartadas

- **Solver de programação linear (ex.: OR-Tools)**: descartado para o MVP
  por custo de setup dentro do prazo de uma semana; heurística é suficiente
  e mais fácil de explicar (RNF02). Pode ser adotado depois trocando apenas
  `allocation_engine.py`, sem alterar a API.
- **Banco de dados relacional**: descartado para o MVP (RNF de tempo);
  `storage.py` isola o acesso a dados para permitir a troca sem tocar em
  `main.py`.
