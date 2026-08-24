from __future__ import annotations
from typing import List, Optional
import time
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .storage import storage
from .models import Sala, Setor, Equipe, Restricao
from .schemas import IntervencaoRequest, AtualizarEquipeRequest
from .allocation_engine import gerar_alocacao, ResultadoAlocacao, Alocacao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("allocation-engine")

app = FastAPI(
    title="Sistema Inteligente de Gestão e Otimização de Espaços Corporativos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_ultima_otimizada: Optional[ResultadoAlocacao] = None
_alocacao_inicial: Optional[ResultadoAlocacao] = None


# --------------------------------------------------------------------- CRUD
@app.get("/salas", response_model=List[Sala])
def listar_salas():
    return list(storage.salas.values())


@app.post("/salas", response_model=Sala)
def criar_sala(sala: Sala):
    storage.salas[sala.id] = sala
    return sala


@app.get("/setores", response_model=List[Setor])
def listar_setores():
    return list(storage.setores.values())


@app.get("/equipes", response_model=List[Equipe])
def listar_equipes():
    return list(storage.equipes.values())


@app.post("/equipes", response_model=Equipe)
def criar_equipe(equipe: Equipe):
    storage.equipes[equipe.id] = equipe
    return equipe


@app.patch("/equipes/{equipe_id}", response_model=Equipe)
def atualizar_equipe(equipe_id: str, dados: AtualizarEquipeRequest):
    if equipe_id not in storage.equipes:
        raise HTTPException(404, "Equipe não encontrada")
    equipe = storage.equipes[equipe_id]
    if dados.quantidade_funcionarios is not None:
        equipe.quantidade_funcionarios = dados.quantidade_funcionarios
    if dados.prioridade is not None:
        equipe.prioridade = dados.prioridade
    if dados.andar_preferido is not None:
        equipe.andar_preferido = dados.andar_preferido
    return equipe


@app.get("/restricoes", response_model=List[Restricao])
def listar_restricoes():
    return list(storage.restricoes.values())


@app.post("/restricoes", response_model=Restricao)
def criar_restricao(restricao: Restricao):
    storage.restricoes[restricao.id] = restricao
    return restricao


@app.delete("/restricoes/{restricao_id}")
def remover_restricao(restricao_id: str):
    storage.restricoes.pop(restricao_id, None)
    return {"ok": True}


def _alocacao_inicial_simples() -> ResultadoAlocacao:
    salas, setores, equipes, restricoes = storage.snapshot()
    salas_ocupadas = set()
    alocacoes: List[Alocacao] = []
    excecoes = []
    for equipe in equipes:
        candidata = next(
            (s for s in salas if s.id not in salas_ocupadas and s.disponivel
             and s.capacidade >= equipe.quantidade_funcionarios),
            None,
        )
        if candidata:
            alocacoes.append(Alocacao(
                equipe_id=equipe.id, equipe_nome=equipe.nome, setor_id=equipe.setor_id,
                sala_id=candidata.id, sala_nome=candidata.nome, andar=candidata.andar,
                capacidade=candidata.capacidade, pessoas=equipe.quantidade_funcionarios,
                ocupacao_prevista=round(equipe.quantidade_funcionarios / candidata.capacidade * 100, 1),
                alternativas_avaliadas=1, recursos_atendidos=True,
                restricao_andar_atendida=True, restricao_acessibilidade_atendida=True,
                score=0.0, justificativa="Alocação inicial (primeira sala compatível encontrada).",
            ))
            salas_ocupadas.add(candidata.id)
        else:
            from .allocation_engine import Excecao
            excecoes.append(Excecao(
                equipe_id=equipe.id, equipe_nome=equipe.nome,
                restricao_nao_atendida="capacidade_minima",
                causa="Nenhuma sala livre compatível na ordem de cadastro",
                encaminhamento_sugerido="Revisar manualmente.",
            ))
    return ResultadoAlocacao(
        execucao_id=0, timestamp=time.time(), algoritmo="baseline-manual",
        equipes_analisadas=len(equipes), salas_analisadas=len(salas),
        alocacoes=alocacoes, excecoes=excecoes, tempo_execucao_s=0.0,
        restricoes_violadas=0,
    )


@app.post("/alocacao/gerar")
def gerar_alocacao_endpoint(usuario: str = "coordenador-geral"):
    global _ultima_otimizada, _alocacao_inicial
    if _alocacao_inicial is None:
        _alocacao_inicial = _alocacao_inicial_simples()

    salas, setores, equipes, restricoes = storage.snapshot()
    exec_id = storage.proximo_execucao_id()
    resultado = gerar_alocacao(salas, setores, equipes, restricoes, exec_id)
    _ultima_otimizada = resultado

    registro = {
        "execucao_id": resultado.execucao_id,
        "data_hora": resultado.timestamp,
        "usuario": usuario,
        "algoritmo": resultado.algoritmo,
        "equipes_analisadas": resultado.equipes_analisadas,
        "salas_analisadas": resultado.salas_analisadas,
        "equipes_alocadas": len(resultado.alocacoes),
        "equipes_nao_alocadas": len(resultado.excecoes),
        "restricoes_violadas": resultado.restricoes_violadas,
        "ocupacao_prevista": _ocupacao_media(resultado),
        "tempo_execucao_s": resultado.tempo_execucao_s,
    }
    storage.execucoes.append(registro)

    storage.metricas_observabilidade.append({
        "execucao_id": resultado.execucao_id,
        "tempo_s": resultado.tempo_execucao_s,
        "taxa_alocacao": len(resultado.alocacoes) / max(resultado.equipes_analisadas, 1),
        "ocupacao_media": _ocupacao_media(resultado),
        "conflitos": resultado.restricoes_violadas,
        "nao_alocados": len(resultado.excecoes),
    })

    logger.info("Execução #%s concluída em %.3fs", resultado.execucao_id, resultado.tempo_execucao_s)

    return {
        "execucao_id": resultado.execucao_id,
        "algoritmo": resultado.algoritmo,
        "tempo_execucao_s": resultado.tempo_execucao_s,
        "alocacoes": [a.__dict__ for a in resultado.alocacoes],
        "excecoes": [e.__dict__ for e in resultado.excecoes],
        "restricoes_violadas": resultado.restricoes_violadas,
    }


def _ocupacao_media(resultado: ResultadoAlocacao) -> float:
    if not resultado.alocacoes:
        return 0.0
    return round(sum(a.ocupacao_prevista for a in resultado.alocacoes) / len(resultado.alocacoes), 1)


@app.get("/alocacao/justificativa/{equipe_id}")
def justificativa(equipe_id: str):
    if _ultima_otimizada is None:
        raise HTTPException(400, "Nenhuma alocação gerada ainda. Execute /alocacao/gerar primeiro.")
    for a in _ultima_otimizada.alocacoes:
        if a.equipe_id == equipe_id:
            return a.__dict__
    for e in _ultima_otimizada.excecoes:
        if e.equipe_id == equipe_id:
            return {"excecao": e.__dict__}
    raise HTTPException(404, "Equipe não encontrada na última execução")


@app.post("/alocacao/intervencao")
def registrar_intervencao(req: IntervencaoRequest):
    if _ultima_otimizada is None:
        raise HTTPException(400, "Nenhuma alocação gerada ainda.")

    registro = {
        "execucao_id": req.execucao_id,
        "equipe_id": req.equipe_id,
        "acao": req.acao,
        "sala_id_manual": req.sala_id_manual,
        "usuario": req.usuario,
        "observacao": req.observacao,
        "timestamp": time.time(),
    }
    storage.intervencoes.append(registro)

    if req.acao == "alterar_manual" and req.sala_id_manual:
        for a in _ultima_otimizada.alocacoes:
            if a.equipe_id == req.equipe_id:
                a.sala_id = req.sala_id_manual
                sala = storage.salas.get(req.sala_id_manual)
                if sala:
                    a.sala_nome = sala.nome
                    a.andar = sala.andar
                    a.capacidade = sala.capacidade
                a.justificativa = f"Alocação alterada manualmente por {req.usuario}."

    return {"ok": True, "registro": registro}


@app.get("/dashboard")
def dashboard():
    salas = list(storage.salas.values())
    total_capacidade = sum(s.capacidade for s in salas if s.disponivel)
    salas_disponiveis = [s for s in salas if s.disponivel]

    if _ultima_otimizada:
        alocados = sum(a.pessoas for a in _ultima_otimizada.alocacoes)
        equipes_alocadas = len(_ultima_otimizada.alocacoes)
        equipes_nao_alocadas = len(_ultima_otimizada.excecoes)
        salas_ocupadas_ids = {a.sala_id for a in _ultima_otimizada.alocacoes}
        restricoes_violadas = _ultima_otimizada.restricoes_violadas
    else:
        alocados = 0
        equipes_alocadas = 0
        equipes_nao_alocadas = 0
        salas_ocupadas_ids = set()
        restricoes_violadas = 0

    por_andar = {}
    for andar in range(1, 10):
        salas_andar = [s for s in salas_disponiveis if s.andar == andar]
        cap_andar = sum(s.capacidade for s in salas_andar)
        ocupadas_andar = [s for s in salas_andar if s.id in salas_ocupadas_ids]
        pessoas_andar = sum(
            a.pessoas for a in (_ultima_otimizada.alocacoes if _ultima_otimizada else [])
            if a.andar == andar
        )
        por_andar[andar] = {
            "salas_total": len(salas_andar),
            "salas_ocupadas": len(ocupadas_andar),
            "capacidade_total": cap_andar,
            "pessoas_alocadas": pessoas_andar,
            "percentual_ocupacao": round(pessoas_andar / cap_andar * 100, 1) if cap_andar else 0,
        }

    return {
        "ocupacao_total_percentual": round(alocados / total_capacidade * 100, 1) if total_capacidade else 0,
        "capacidade_disponivel": total_capacidade,
        "funcionarios_alocados": alocados,
        "equipes_alocadas": equipes_alocadas,
        "equipes_nao_alocadas": equipes_nao_alocadas,
        "salas_disponiveis": len(salas_disponiveis) - len(salas_ocupadas_ids),
        "salas_ocupadas": len(salas_ocupadas_ids),
        "percentual_utilizacao_salas": round(
            len(salas_ocupadas_ids) / len(salas_disponiveis) * 100, 1
        ) if salas_disponiveis else 0,
        "restricoes_violadas": restricoes_violadas,
        "por_andar": por_andar,
    }


@app.get("/dashboard/comparacao")
def comparacao():
    global _alocacao_inicial
    if _alocacao_inicial is None:
        _alocacao_inicial = _alocacao_inicial_simples()
    if _ultima_otimizada is None:
        raise HTTPException(400, "Execute /alocacao/gerar primeiro.")

    def resumo(resultado: ResultadoAlocacao):
        salas = list(storage.salas.values())
        ocupacoes = [a.ocupacao_prevista for a in resultado.alocacoes]
        ociosos = sum(a.capacidade - a.pessoas for a in resultado.alocacoes)
        return {
            "ocupacao_media": round(sum(ocupacoes) / len(ocupacoes), 1) if ocupacoes else 0,
            "assentos_ociosos": ociosos,
            "equipes_sem_sala": len(resultado.excecoes),
            "violacoes": resultado.restricoes_violadas,
        }

    return {"antes": resumo(_alocacao_inicial), "depois": resumo(_ultima_otimizada)}


@app.get("/governanca/execucoes")
def listar_execucoes():
    return storage.execucoes


@app.get("/governanca/intervencoes")
def listar_intervencoes():
    return storage.intervencoes


@app.get("/observabilidade")
def observabilidade():
    metricas = storage.metricas_observabilidade
    if not metricas:
        return {
            "tempo_ultima_otimizacao_s": None,
            "numero_execucoes": 0,
            "taxa_alocacao_media": None,
            "ocupacao_media": None,
            "conflitos_total": 0,
            "nao_alocados_total": 0,
            "intervencoes_manuais": len(storage.intervencoes),
            "erros": 0,
        }
    ultima = metricas[-1]
    return {
        "tempo_ultima_otimizacao_s": ultima["tempo_s"],
        "numero_execucoes": len(metricas),
        "taxa_alocacao_media": round(sum(m["taxa_alocacao"] for m in metricas) / len(metricas), 3),
        "ocupacao_media": round(sum(m["ocupacao_media"] for m in metricas) / len(metricas), 1),
        "conflitos_total": sum(m["conflitos"] for m in metricas),
        "nao_alocados_total": ultima["nao_alocados"],
        "intervencoes_manuais": len(storage.intervencoes),
        "erros": 0,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
