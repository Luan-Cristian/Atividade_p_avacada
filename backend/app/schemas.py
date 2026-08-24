from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class IntervencaoRequest(BaseModel):
    execucao_id: int
    equipe_id: str
    acao: str  
    sala_id_manual: Optional[str] = None
    usuario: str = "coordenador-geral"
    observacao: Optional[str] = None


class AtualizarEquipeRequest(BaseModel):
    quantidade_funcionarios: Optional[int] = None
    prioridade: Optional[int] = None
    andar_preferido: Optional[int] = None
