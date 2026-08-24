from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time

from .models import Sala, Setor, Equipe, Restricao, TipoRestricao

ENGINE_VERSION = "allocation-engine-v1"

PESO_OCUPACAO = 0.5
PESO_ANDAR_PREFERIDO = 0.2
PESO_PROXIMIDADE = 0.2
PESO_PENALIDADE_SOFT = 0.1


@dataclass
class Alocacao:
    equipe_id: str
    equipe_nome: str
    setor_id: str
    sala_id: str
    sala_nome: str
    andar: int
    capacidade: int
    pessoas: int
    ocupacao_prevista: float
    alternativas_avaliadas: int
    recursos_atendidos: bool
    restricao_andar_atendida: bool
    restricao_acessibilidade_atendida: bool
    score: float
    justificativa: str


@dataclass
class Excecao:
    equipe_id: str
    equipe_nome: str
    restricao_nao_atendida: str
    causa: str
    encaminhamento_sugerido: str


@dataclass
class ResultadoAlocacao:
    execucao_id: int
    timestamp: float
    algoritmo: str
    equipes_analisadas: int
    salas_analisadas: int
    alocacoes: List[Alocacao] = field(default_factory=list)
    excecoes: List[Excecao] = field(default_factory=list)
    tempo_execucao_s: float = 0.0
    restricoes_violadas: int = 0


def _restricoes_da_equipe(equipe: Equipe, restricoes: List[Restricao]) -> List[Restricao]:
    return [
        r for r in restricoes
        if r.equipe_id == equipe.id or r.setor_id == equipe.setor_id
    ]


def _sala_atende_obrigatorias(
    sala: Sala, equipe: Equipe, restricoes_equipe: List[Restricao]
) -> tuple[bool, Optional[str], Optional[str]]:
    if not sala.disponivel:
        return False, "Sala indisponível no momento", "disponibilidade"

    if sala.setor_reservado and sala.setor_reservado != equipe.setor_id:
        return False, f"Sala reservada exclusivamente para outro setor", "sala_reservada"

    if sala.capacidade < equipe.quantidade_funcionarios:
        return False, (
            f"Capacidade da sala ({sala.capacidade}) menor que o tamanho da "
            f"equipe ({equipe.quantidade_funcionarios})"
        ), "capacidade_minima"

    if equipe.acessibilidade_obrigatoria and not sala.acessibilidade:
        return False, "Equipe exige acessibilidade e a sala não oferece", "acessibilidade_obrigatoria"

    for recurso in equipe.recursos_obrigatorios:
        if recurso not in sala.recursos:
            return False, f"Recurso obrigatório ausente: {recurso.value}", "equipamento_obrigatorio"

    for r in restricoes_equipe:
        if not r.obrigatoria:
            continue
        if r.tipo == TipoRestricao.ANDAR_PERMITIDO and r.valor:
            andares_permitidos = {int(a) for a in r.valor.split(",")}
            if sala.andar not in andares_permitidos:
                return False, f"Andar {sala.andar} fora dos andares permitidos ({r.valor})", "andar_permitido"
        if r.tipo == TipoRestricao.SEPARACAO_SETORES and r.valor:
            pass 
    return True, None, None


def _score_sala(
    sala: Sala,
    equipe: Equipe,
    alocacoes_ja_feitas: List[Alocacao],
    salas_por_id: Dict[str, Sala],
) -> float:
    ocupacao = equipe.quantidade_funcionarios / sala.capacidade
    score_ocupacao = ocupacao 

    score_andar = 1.0 if (
        equipe.andar_preferido is None or equipe.andar_preferido == sala.andar
    ) else 0.0

    score_proximidade = 0.0
    if equipe.proxima_de:
        relacionadas_alocadas = [
            a for a in alocacoes_ja_feitas if a.equipe_id in equipe.proxima_de
        ]
        if relacionadas_alocadas:
            mesmos_andar = sum(1 for a in relacionadas_alocadas if a.andar == sala.andar)
            score_proximidade = mesmos_andar / len(relacionadas_alocadas)
        else:
            score_proximidade = 0.5  

    penalidade_soft = 0.0 

    return (
        PESO_OCUPACAO * score_ocupacao
        + PESO_ANDAR_PREFERIDO * score_andar
        + PESO_PROXIMIDADE * score_proximidade
        - PESO_PENALIDADE_SOFT * penalidade_soft
    )


def gerar_alocacao(
    salas: List[Sala],
    setores: List[Setor],
    equipes: List[Equipe],
    restricoes: List[Restricao],
    execucao_id: int,
) -> ResultadoAlocacao:
    inicio = time.time()

    equipes_ordenadas = sorted(
        equipes, key=lambda e: (e.prioridade, -e.quantidade_funcionarios)
    )

    salas_disponiveis: Dict[str, Sala] = {s.id: s for s in salas if s.disponivel}
    salas_ocupadas_ids: set[str] = set()

    alocacoes: List[Alocacao] = []
    excecoes: List[Excecao] = []

    for equipe in equipes_ordenadas:
        restricoes_equipe = _restricoes_da_equipe(equipe, restricoes)
        candidatas = []
        causas_rejeicao = []

        for sala in salas.copy():
            if sala.id in salas_ocupadas_ids:
                continue
            ok, causa, tipo_restricao = _sala_atende_obrigatorias(sala, equipe, restricoes_equipe)
            if ok:
                candidatas.append(sala)
            elif causa:
                causas_rejeicao.append((causa, tipo_restricao))

        if not candidatas:
            if causas_rejeicao:
                causa_principal, tipo_r = causas_rejeicao[0]
            else:
                causa_principal, tipo_r = "Nenhuma sala disponível no prédio", "disponibilidade"

            maior_sala = max(salas, key=lambda s: s.capacidade, default=None)
            encaminhamento = (
                f"Considerar dividir a equipe em subgrupos, liberar uma sala maior, "
                f"ou revisar a restrição '{tipo_r}'. Maior sala do prédio: "
                f"{maior_sala.nome if maior_sala else 'N/A'} "
                f"({maior_sala.capacidade if maior_sala else 0} lugares)."
            )
            excecoes.append(Excecao(
                equipe_id=equipe.id,
                equipe_nome=equipe.nome,
                restricao_nao_atendida=tipo_r or "desconhecida",
                causa=causa_principal,
                encaminhamento_sugerido=encaminhamento,
            ))
            continue

        scored = [
            (sala, _score_sala(sala, equipe, alocacoes, salas_disponiveis))
            for sala in candidatas
        ]
        scored.sort(key=lambda t: t[1], reverse=True)
        melhor_sala, melhor_score = scored[0]

        ocupacao_prevista = round(equipe.quantidade_funcionarios / melhor_sala.capacidade * 100, 1)
        recursos_atendidos = all(r in melhor_sala.recursos for r in equipe.recursos_obrigatorios)
        restricao_andar_atendida = (
            equipe.andar_preferido is None or equipe.andar_preferido == melhor_sala.andar
        )
        restricao_acessibilidade_atendida = (
            not equipe.acessibilidade_obrigatoria or melhor_sala.acessibilidade
        )

        justificativa = (
            f"Sala {melhor_sala.nome} recomendada para {equipe.nome}. "
            f"Capacidade da sala: {melhor_sala.capacidade} pessoas. "
            f"Equipe: {equipe.quantidade_funcionarios} pessoas. "
            f"Ocupação prevista: {ocupacao_prevista}%. "
            f"Recursos necessários atendidos: {'sim' if recursos_atendidos else 'não'}. "
            f"Restrição de andar atendida: {'sim' if restricao_andar_atendida else 'não'}. "
            f"Alternativas avaliadas: {len(candidatas)}. "
            f"Esta sala apresentou o melhor equilíbrio entre capacidade, localização "
            f"e restrições dentre as alternativas disponíveis (score={round(melhor_score, 3)})."
        )

        alocacao = Alocacao(
            equipe_id=equipe.id,
            equipe_nome=equipe.nome,
            setor_id=equipe.setor_id,
            sala_id=melhor_sala.id,
            sala_nome=melhor_sala.nome,
            andar=melhor_sala.andar,
            capacidade=melhor_sala.capacidade,
            pessoas=equipe.quantidade_funcionarios,
            ocupacao_prevista=ocupacao_prevista,
            alternativas_avaliadas=len(candidatas),
            recursos_atendidos=recursos_atendidos,
            restricao_andar_atendida=restricao_andar_atendida,
            restricao_acessibilidade_atendida=restricao_acessibilidade_atendida,
            score=round(melhor_score, 4),
            justificativa=justificativa,
        )
        alocacoes.append(alocacao)
        salas_ocupadas_ids.add(melhor_sala.id)

    restricoes_violadas = validar_restricoes_globais(alocacoes, restricoes, equipes)

    fim = time.time()
    return ResultadoAlocacao(
        execucao_id=execucao_id,
        timestamp=inicio,
        algoritmo=ENGINE_VERSION,
        equipes_analisadas=len(equipes),
        salas_analisadas=len(salas),
        alocacoes=alocacoes,
        excecoes=excecoes,
        tempo_execucao_s=round(fim - inicio, 4),
        restricoes_violadas=restricoes_violadas,
    )


def validar_restricoes_globais(
    alocacoes: List[Alocacao], restricoes: List[Restricao], equipes: List[Equipe]
) -> int:
    """Valida restrições que dependem do resultado agregado (ex.: separação de setores)."""
    violacoes = 0
    por_sala: Dict[str, List[Alocacao]] = {}
    for a in alocacoes:
        por_sala.setdefault(a.sala_id, []).append(a)

    for r in restricoes:
        if r.tipo == TipoRestricao.SEPARACAO_SETORES and r.valor and r.obrigatoria:
            setores_proibidos = set(r.valor.split(","))
            for sala_id, lista in por_sala.items():
                setores_na_sala = {a.setor_id for a in lista}
                if len(setores_na_sala & setores_proibidos) > 1:
                    violacoes += 1

    for a in alocacoes:
        if a.pessoas > a.capacidade:
            violacoes += 1

    return violacoes
