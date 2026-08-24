"""
Testes do motor de alocação.

Inclui testes de propriedade/metamórficos (seção 15 do desafio), já que
não conhecemos de antemão qual é a alocação ótima para dezenas de
equipes/salas/restrições -- então testamos RELAÇÕES esperadas entre
entradas e saídas, em vez de comparar contra um "gabarito" fixo.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import copy
import pytest

from app.models import Sala, Setor, Equipe, Restricao, TipoSala, TipoRestricao, Recurso
from app.allocation_engine import gerar_alocacao


def _sala(id, andar, capacidade, **kw):
    return Sala(id=id, nome=id, andar=andar, capacidade=capacidade, tipo=TipoSala.REUNIAO, **kw)


def _equipe(id, setor_id, qtd, **kw):
    return Equipe(id=id, setor_id=setor_id, nome=id, quantidade_funcionarios=qtd, **kw)


def _cenario_base():
    salas = [
        _sala("s1", 1, 15),
        _sala("s2", 1, 30),
        _sala("s3", 2, 45),
        _sala("s4", 2, 80),
    ]
    setores = [Setor(id="tec", nome="Tecnologia", coordenador="Ana", total_funcionarios=100)]
    equipes = [
        _equipe("e1", "tec", 12),
        _equipe("e2", "tec", 28),
        _equipe("e3", "tec", 40),
    ]
    restricoes = []
    return salas, setores, equipes, restricoes


# --------------------------------------------------------------------------
# Teste 1 — Capacidade: nenhuma sala pode receber mais pessoas que sua capacidade
# --------------------------------------------------------------------------
def test_capacidade_nunca_e_excedida():
    salas, setores, equipes, restricoes = _cenario_base()
    resultado = gerar_alocacao(salas, setores, equipes, restricoes, execucao_id=1)

    assert len(resultado.alocacoes) > 0
    for alocacao in resultado.alocacoes:
        assert alocacao.pessoas <= alocacao.capacidade, (
            f"Sala {alocacao.sala_nome} recebeu {alocacao.pessoas} pessoas "
            f"mas tem capacidade para apenas {alocacao.capacidade}"
        )
    assert resultado.restricoes_violadas == 0


def test_equipe_12_pessoas_nao_vai_para_sala_de_80_se_existe_sala_de_15():
    """Caso ilustrativo do próprio enunciado (seção 4)."""
    salas, setores, _, restricoes = _cenario_base()
    equipes = [_equipe("e1", "tec", 12)]
    resultado = gerar_alocacao(salas, setores, equipes, restricoes, execucao_id=1)
    assert resultado.alocacoes[0].sala_id == "s1"  # a sala de 15, não a de 80


def test_equipe_60_pessoas_nao_e_colocada_em_sala_de_40():
    salas = [_sala("s1", 1, 40), _sala("s2", 1, 45)]
    setores = [Setor(id="tec", nome="Tecnologia", coordenador="Ana", total_funcionarios=60)]
    equipes = [_equipe("e1", "tec", 60)]
    resultado = gerar_alocacao(salas, setores, equipes, [], execucao_id=1)
    # nenhuma sala comporta 60 pessoas -> deve virar exceção, nunca uma alocação inválida
    assert len(resultado.alocacoes) == 0
    assert len(resultado.excecoes) == 1
    assert resultado.excecoes[0].equipe_id == "e1"


# --------------------------------------------------------------------------
# Teste 2 — Expansão da capacidade: adicionar uma sala não deve diminuir
# a quantidade de equipes alocáveis
# --------------------------------------------------------------------------
def test_metamorfico_adicionar_sala_nao_piora_alocacao():
    salas, setores, equipes, restricoes = _cenario_base()
    resultado_original = gerar_alocacao(salas, setores, equipes, restricoes, execucao_id=1)

    salas_expandidas = salas + [_sala("s_nova", 3, 100)]
    resultado_expandido = gerar_alocacao(salas_expandidas, setores, equipes, restricoes, execucao_id=2)

    assert len(resultado_expandido.alocacoes) >= len(resultado_original.alocacoes)
    assert len(resultado_expandido.excecoes) <= len(resultado_original.excecoes)


# --------------------------------------------------------------------------
# Teste 3 — Remoção de restrição: o espaço de soluções não deve encolher
# --------------------------------------------------------------------------
def test_metamorfico_remover_restricao_nao_piora_alocacao():
    salas, setores, equipes, _ = _cenario_base()
    restricao_andar = Restricao(
        id="r1", tipo=TipoRestricao.ANDAR_PERMITIDO,
        descricao="Equipe e3 só pode ficar no andar 1", equipe_id="e3",
        valor="1", obrigatoria=True,
    )
    resultado_com_restricao = gerar_alocacao(salas, setores, equipes, [restricao_andar], execucao_id=1)
    resultado_sem_restricao = gerar_alocacao(salas, setores, equipes, [], execucao_id=2)

    assert len(resultado_sem_restricao.alocacoes) >= len(resultado_com_restricao.alocacoes)
    assert len(resultado_sem_restricao.excecoes) <= len(resultado_com_restricao.excecoes)


# --------------------------------------------------------------------------
# Teste 4 — Equipes equivalentes: renomear uma equipe não deve alterar
# drasticamente a qualidade global da solução
# --------------------------------------------------------------------------
def test_metamorfico_renomear_equipe_mantem_qualidade():
    salas, setores, equipes, restricoes = _cenario_base()
    resultado_original = gerar_alocacao(salas, setores, equipes, restricoes, execucao_id=1)

    equipes_renomeadas = copy.deepcopy(equipes)
    equipes_renomeadas[0].nome = "Equipe Renomeada XYZ"
    resultado_renomeado = gerar_alocacao(salas, setores, equipes_renomeadas, restricoes, execucao_id=2)

    assert len(resultado_original.alocacoes) == len(resultado_renomeado.alocacoes)
    ocupacao_media_original = sum(a.ocupacao_prevista for a in resultado_original.alocacoes)
    ocupacao_media_renomeado = sum(a.ocupacao_prevista for a in resultado_renomeado.alocacoes)
    assert ocupacao_media_original == pytest.approx(ocupacao_media_renomeado, rel=0.01)


# --------------------------------------------------------------------------
# Teste 5 — Exceções nunca viram alocações inválidas (não "escondem o problema")
# --------------------------------------------------------------------------
def test_equipe_maior_que_todas_as_salas_gera_excecao_com_causa():
    salas = [_sala("s1", 1, 10)]
    setores = [Setor(id="tec", nome="Tecnologia", coordenador="Ana", total_funcionarios=92)]
    equipes = [_equipe("delta", "tec", 92)]  # exemplo do próprio enunciado (seção 11)
    resultado = gerar_alocacao(salas, setores, equipes, [], execucao_id=1)

    assert len(resultado.alocacoes) == 0
    assert len(resultado.excecoes) == 1
    excecao = resultado.excecoes[0]
    assert excecao.equipe_id == "delta"
    assert excecao.causa
    assert excecao.encaminhamento_sugerido


# --------------------------------------------------------------------------
# Teste 6 — Restrição de acessibilidade obrigatória é sempre respeitada
# --------------------------------------------------------------------------
def test_restricao_acessibilidade_obrigatoria_e_respeitada():
    salas = [
        _sala("s1", 1, 20, acessibilidade=False),
        _sala("s2", 1, 20, acessibilidade=True),
    ]
    setores = [Setor(id="rh", nome="RH", coordenador="Bruno", total_funcionarios=15)]
    equipes = [_equipe("e1", "rh", 15, acessibilidade_obrigatoria=True)]
    resultado = gerar_alocacao(salas, setores, equipes, [], execucao_id=1)

    assert len(resultado.alocacoes) == 1
    assert resultado.alocacoes[0].sala_id == "s2"


def test_execucao_e_rapida():
    """Critério de aceitação: recomendação dentro de um limite de tempo (ex.: 5s)."""
    salas, setores, equipes, restricoes = _cenario_base()
    resultado = gerar_alocacao(salas, setores, equipes, restricoes, execucao_id=1)
    assert resultado.tempo_execucao_s < 5.0
