# Tasks
## Deriva de: `design.md` — cada task referencia o(s) requisito(s) que atende

| # | Task | Requisitos | Arquivo(s) | Status |
|---|---|---|---|---|
| 1 | Modelar Sala, Setor, Equipe, Restrição | RF01, RF02, RF03 | `backend/app/models.py` | ✅ concluída |
| 2 | Implementar motor de alocação (heurística + score + exceções) | RF04, RF05, RF06, RNF01, RNF02, RNF04 | `backend/app/allocation_engine.py` | ✅ concluída |
| 3 | Gerar dados fictícios (seed) para demonstração | contexto §1 | `backend/app/storage.py` | ✅ concluída |
| 4 | Expor API REST (CRUD + gerar alocação + justificativa) | RF01–RF07 | `backend/app/main.py` | ✅ concluída |
| 5 | Endpoint de intervenção humana (aceitar/rejeitar/alterar) | RF07 | `backend/app/main.py` (`/alocacao/intervencao`) | ✅ concluída |
| 6 | Endpoint de dashboard (ocupação total/por andar) | RF08 | `backend/app/main.py` (`/dashboard`) | ✅ concluída |
| 7 | Endpoint de comparação antes/depois | RF09 | `backend/app/main.py` (`/dashboard/comparacao`) | ✅ concluída |
| 8 | Registro de governança por execução | RF10 | `backend/app/main.py` (`storage.execucoes`) | ✅ concluída |
| 9 | Métricas de observabilidade | RF11 | `backend/app/main.py` (`/observabilidade`) | ✅ concluída |
| 10 | Testes de capacidade e exceções | RNF04, critério de aceitação 1 e 4 | `backend/tests/test_allocation.py` | ✅ concluída |
| 11 | Testes metamórficos (expansão de sala, remoção de restrição, renomear equipe) | critério de aceitação 5 | `backend/tests/test_allocation.py` | ✅ concluída |
| 12 | Painel executivo com corte do edifício (9 andares) | RF08 | `frontend/src/components/Dashboard.jsx`, `FloorStack.jsx` | ✅ concluída |
| 13 | Tela de alocação com justificativa e intervenção | RF05, RF06, RF07 | `frontend/src/components/Allocation.jsx` | ✅ concluída |
| 14 | Tela de comparação antes/depois | RF09 | `frontend/src/components/Comparison.jsx` | ✅ concluída |
| 15 | Tela de cadastro (Coordenador de Setor) | RF02, RF03 | `frontend/src/components/Registrations.jsx` | ✅ concluída |
| 16 | Tela de governança | RF10 | `frontend/src/components/Governance.jsx` | ✅ concluída |
| 17 | Tela de monitoramento (observabilidade) | RF11 | `frontend/src/components/Observability.jsx` | ✅ concluída |
| 18 | Pipeline de CI (install, build, testes) | RNF03 | `.github/workflows/ci.yml` | ✅ concluída |
| 19 | Documentação (README com critérios de aceitação e roteiro de demo) | todos | `README.md` | ✅ concluída |
| 20 | Especificação SDD retroativa (este conjunto de documentos) | rastreabilidade do processo | `specs/` | ✅ concluída |

## Próximos passos sugeridos (não obrigatórios para o MVP)

| # | Task | Requisito relacionado |
|---|---|---|
| 21 | Trocar armazenamento em memória por Postgres/SQLite | fora de escopo, ver `requirements.md` §6 |
| 22 | Autenticação por perfil (Coordenador Geral vs. Setor) | fora de escopo, ver `requirements.md` §6 |
| 23 | Trocar heurística por solver exato (ex.: OR-Tools) opcional | ver alternativa descartada em `design.md` §6 |
