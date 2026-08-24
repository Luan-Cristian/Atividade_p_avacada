"""
Modelos de dados do Sistema Inteligente de Gestão e Otimização de Espaços Corporativos.
"""
from __future__ import annotations
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class TipoSala(str, Enum):
    REUNIAO = "reuniao"
    TREINAMENTO = "treinamento"
    AUDITORIO = "auditorio"
    LABORATORIO = "laboratorio"
    PROJETO = "projeto"
    COLABORATIVO = "colaborativo"


class Recurso(str, Enum):
    PROJETOR = "projetor"
    VIDEOCONFERENCIA = "videoconferencia"
    QUADRO_BRANCO = "quadro_branco"
    COMPUTADORES = "computadores"
    AR_CONDICIONADO = "ar_condicionado"
    FIBRA_DEDICADA = "fibra_dedicada"


class Sala(BaseModel):
    id: str
    nome: str
    andar: int = Field(ge=1, le=9)
    capacidade: int = Field(gt=0)
    tipo: TipoSala
    recursos: List[Recurso] = []
    acessibilidade: bool = False
    disponivel: bool = True
    setor_reservado: Optional[str] = None  # id do setor, se a sala for exclusiva


class Setor(BaseModel):
    id: str
    nome: str
    coordenador: str
    total_funcionarios: int = Field(ge=0)


class Equipe(BaseModel):
    id: str
    setor_id: str
    nome: str
    quantidade_funcionarios: int = Field(gt=0)
    horario: str = "09:00-18:00"
    recursos_obrigatorios: List[Recurso] = []
    acessibilidade_obrigatoria: bool = False
    andar_preferido: Optional[int] = None
    prioridade: int = Field(default=3, ge=1, le=5)  # 1 = mais alta, 5 = mais baixa
    proxima_de: List[str] = []  # ids de outras equipes que devem ficar próximas


class TipoRestricao(str, Enum):
    CAPACIDADE_MINIMA = "capacidade_minima"
    ANDAR_PERMITIDO = "andar_permitido"
    ACESSIBILIDADE_OBRIGATORIA = "acessibilidade_obrigatoria"
    EQUIPAMENTO_OBRIGATORIO = "equipamento_obrigatorio"
    PROXIMIDADE = "proximidade"
    SEPARACAO_SETORES = "separacao_setores"
    SALA_RESERVADA = "sala_reservada"
    PRIORIDADE = "prioridade"


class Restricao(BaseModel):
    id: str
    tipo: TipoRestricao
    descricao: str
    equipe_id: Optional[str] = None
    setor_id: Optional[str] = None
    valor: Optional[str] = None  # payload livre (ex.: "4", "projetor", "setorA,setorB")
    obrigatoria: bool = True
