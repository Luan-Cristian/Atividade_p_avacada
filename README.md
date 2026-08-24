# Sistema Inteligente de Gestão e Otimização de Espaços Corporativos

Protótipo funcional full stack (MVP) para alocação otimizada de salas de um
prédio corporativo de 9 andares entre setores e equipes, com motor de
recomendação explicável, dashboard executivo, governança, observabilidade e
intervenção humana.

## Stack

- **Backend**: Python 3.12 + FastAPI (API REST) — armazenamento em memória (fácil de trocar por Postgres/SQLite mantendo a mesma interface em `storage.py`)
- **Frontend**: React + Vite
- **Testes**: pytest (incluindo testes metamórficos do motor de alocação)
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`)

## Como executar localmente

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
A API sobe em `http://127.0.0.1:8000` (documentação interativa em `/docs`).

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Acesse `http://127.0.0.1:5173`. Por padrão aponta para a API em `127.0.0.1:8000`
(configurável via `VITE_API_URL`, ver `.env.example`).

### Testes
```bash
cd backend
python -m pytest tests/ -v
```

## Arquitetura e decisões principais

- **Dados fictícios (seed)**: ao subir, o backend gera ~7.000 funcionários
  distribuídos em ~40 equipes e ~100 salas nos 9 andares, para permitir uma
  demonstração realista sem depender de cadastro manual prévio.
- **Motor de alocação (`allocation_engine.py`)**: heurística gulosa
  determinística (não é ML, conforme permitido no enunciado):
  1. Ordena equipes por prioridade e tamanho.
  2. Filtra salas que atendem restrições **obrigatórias** (capacidade,
     acessibilidade, recursos, andar, reserva de sala).
  3. Entre as candidatas, escolhe a de maior *score* — combinação ponderada de
     eficiência de ocupação, atendimento de andar preferido e proximidade com
     equipes relacionadas.
  4. Equipes sem sala compatível viram uma **exceção documentada** (nunca uma
     alocação inválida "forçada").
- **Explicabilidade**: toda alocação carrega uma `justificativa` textual (capacidade,
  ocupação prevista, recursos/andar atendidos, nº de alternativas avaliadas).
- **Governança**: cada execução do motor grava um registro (`/governanca/execucoes`)
  com quem executou, quando, quantas equipes/salas, algoritmo e versão.
  Intervenções humanas (aceitar/rejeitar/alterar) também são registradas
  (`/governanca/intervencoes`).
- **Observabilidade**: `/observabilidade` expõe tempo de execução, taxa de
  alocação, ocupação média, conflitos e intervenções manuais acumuladas.
- **Intervenção humana**: o Coordenador Geral pode aceitar, rejeitar ou
  alterar manualmente qualquer recomendação na tela de Alocação — a decisão
  final nunca é automática.

## Critérios de aceitação

1. Nenhuma sala pode receber mais pessoas do que sua capacidade (verificado
   em `test_capacidade_nunca_e_excedida` e reforçado no cálculo de
   `restricoes_violadas`).
2. Nenhuma restrição obrigatória (`obrigatoria=True`) pode ser ignorada por
   uma alocação válida.
3. 100% das alocações retornadas pela API possuem o campo `justificativa`
   preenchido.
4. Toda equipe não alocada aparece na lista de exceções com `causa` e
   `encaminhamento_sugerido` preenchidos — nunca é omitida silenciosamente.
5. A alocação otimizada não pode apresentar mais assentos ociosos, mais
   equipes sem sala ou mais violações do que a alocação inicial (baseline),
   verificável na tela de Comparação.
6. Toda execução do motor deve ser concluída em menos de 5 segundos
   (`test_execucao_e_rapida`) e fica registrada no log de governança.

## Testes automatizados (incluindo testes metamórficos)

Como não é viável conhecer de antemão a alocação ótima para dezenas de
equipes/salas/restrições, além dos testes de propriedade diretos (ex.:
capacidade nunca excedida) usamos **testes metamórficos** — validam relações
esperadas entre uma entrada e uma entrada modificada:

| Teste | Relação verificada |
|---|---|
| `test_metamorfico_adicionar_sala_nao_piora_alocacao` | Adicionar uma sala não pode diminuir o nº de equipes alocáveis |
| `test_metamorfico_remover_restricao_nao_piora_alocacao` | Remover uma restrição não pode diminuir o espaço de soluções |
| `test_metamorfico_renomear_equipe_mantem_qualidade` | Renomear uma equipe não pode alterar drasticamente a qualidade da solução |
| `test_capacidade_nunca_e_excedida` | Nenhuma sala recebe mais pessoas que sua capacidade |
| `test_equipe_maior_que_todas_as_salas_gera_excecao_com_causa` | Exceções nunca viram alocações inválidas |

Rodar: `python -m pytest backend/tests/ -v` (9 testes, todos passando).

## CI/CD

A cada `push`/`pull_request`, o GitHub Actions (`.github/workflows/ci.yml`) executa:
1. Instalação das dependências (backend e frontend);
2. Build/validação da aplicação (`import` da API FastAPI + `npm run build` do React);
3. Execução dos testes automatizados do backend.

## Roteiro de demonstração (mapeado ao desafio)

1. Coordenador Geral abre o **Painel** → vê a ocupação dos 9 andares no corte do edifício.
2. Um Coordenador de Setor altera a quantidade de funcionários de uma equipe em **Cadastro**.
3. Restrições são visualizadas em **Cadastro** (ex.: separação Jurídico/Comercial, sala reservada).
4. Usuário clica **"Gerar alocação otimizada"**.
5. Sistema mostra a distribuição em **Alocação**, com exceções destacadas.
6. Usuário abre a **justificativa** de uma recomendação e pode aceitar, rejeitar ou alterar manualmente.
7. **Comparação** mostra antes/depois (ocupação, ociosidade, equipes sem sala, violações).
8. **Governança** mostra o histórico de execuções e intervenções.
9. **Monitoramento** mostra tempo de execução, taxa de alocação e conflitos acumulados.

## Respostas às perguntas da demonstração final

**1. Como o sistema distribuiu os funcionários pelos espaços?**
Por uma heurística determinística: ordena equipes por prioridade/tamanho e,
para cada uma, escolhe entre as salas compatíveis (restrições obrigatórias)
a que maximiza um score de ocupação, aderência ao andar preferido e
proximidade com equipes relacionadas.

**2. Por que determinada sala foi recomendada para determinada equipe?**
Cada alocação carrega uma justificativa com capacidade, ocupação prevista,
recursos e restrições atendidos, e quantas alternativas foram avaliadas —
visível na tela de Alocação.

**3. O que acontece quando não existe solução possível?**
A equipe aparece na lista de **exceções**, com a causa e um encaminhamento
sugerido. O sistema nunca aloca acima da capacidade só para "fechar a conta".

**4. Como vocês sabem que uma nova versão do sistema não piorou a solução?**
Pelos testes metamórficos (adicionar sala não piora, remover restrição não
piora) rodando no CI a cada mudança, mais o comparativo antes/depois exposto
na própria interface.

**5. Por que o Coordenador Geral deveria confiar na recomendação?**
Não "porque é IA": porque existem critérios de aceitação objetivos, testes
automatizados no CI, explicabilidade em cada decisão, registro de governança
de cada execução, métricas de observabilidade em produção, e a possibilidade
de o coordenador aceitar, rejeitar ou substituir qualquer recomendação — a
decisão final é sempre humana.

## Limitações conhecidas (transparência)

- Armazenamento em memória (reinicia ao reiniciar o backend) — adequado para
  o protótipo de curto prazo; troca para banco persistente é isolada em `storage.py`.
- A heurística é gulosa, não um solver de otimização exato — pode não achar
  o ótimo global, mas é rápida, determinística e 100% explicável.
- Autenticação/perfis de usuário não foram implementados (fora do escopo do MVP).
