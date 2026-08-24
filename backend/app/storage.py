"""
Armazenamento em memória (adequado para o protótipo/MVP).
Troca-se facilmente por um banco real (Postgres/SQLite) mantendo a mesma interface.
"""
from __future__ import annotations
from typing import List, Dict
import random

from .models import Sala, Setor, Equipe, Restricao, TipoSala, Recurso, TipoRestricao


class Storage:
    def __init__(self) -> None:
        self.salas: Dict[str, Sala] = {}
        self.setores: Dict[str, Setor] = {}
        self.equipes: Dict[str, Equipe] = {}
        self.restricoes: Dict[str, Restricao] = {}
        self.execucoes: List[dict] = []  # log de governança
        self.intervencoes: List[dict] = []  # log de intervenções humanas
        self.metricas_observabilidade: List[dict] = []
        self._exec_counter = 0
        self._seed()

    def proximo_execucao_id(self) -> int:
        self._exec_counter += 1
        return self._exec_counter

    # ---------------------------------------------------------------- seed
    def _seed(self) -> None:
        random.seed(42)
        setores_info = [
            ("tecnologia", "Tecnologia", "Ana Souza"),
            ("rh", "Recursos Humanos", "Bruno Lima"),
            ("financeiro", "Financeiro", "Carla Dias"),
            ("juridico", "Jurídico", "Diego Alves"),
            ("marketing", "Marketing", "Elisa Rocha"),
            ("comercial", "Comercial", "Fábio Nunes"),
            ("operacoes", "Operações", "Gisele Melo"),
            ("pd", "Pesquisa e Desenvolvimento", "Hugo Castro"),
        ]
        for sid, nome, coord in setores_info:
            self.setores[sid] = Setor(id=sid, nome=nome, coordenador=coord, total_funcionarios=0)

        tipos = list(TipoSala)
        recursos_pool = list(Recurso)
        sala_count = 0
        for andar in range(1, 10):
            n_salas = random.randint(9, 14)
            for i in range(n_salas):
                sala_count += 1
                sid = f"sala-{andar}{i:02d}"
                capacidade = random.choice([8, 10, 15, 20, 25, 30, 40, 45, 50, 60, 80])
                recursos = random.sample(recursos_pool, k=random.randint(1, 3))
                self.salas[sid] = Sala(
                    id=sid,
                    nome=f"Sala {andar}{i:02d}",
                    andar=andar,
                    capacidade=capacidade,
                    tipo=random.choice(tipos),
                    recursos=recursos,
                    acessibilidade=random.random() > 0.4,
                    disponivel=random.random() > 0.05,
                )

        equipe_id = 0
        for sid, _, _ in setores_info:
            n_equipes = random.randint(3, 6)
            total = 0
            for i in range(n_equipes):
                equipe_id += 1
                qtd = random.choice([6, 10, 12, 15, 18, 22, 28, 35, 42, 54, 92])
                total += qtd
                eid = f"equipe-{equipe_id}"
                self.equipes[eid] = Equipe(
                    id=eid,
                    setor_id=sid,
                    nome=f"{self.setores[sid].nome} - Time {i+1}",
                    quantidade_funcionarios=qtd,
                    recursos_obrigatorios=random.sample(recursos_pool, k=random.randint(0, 1)),
                    acessibilidade_obrigatoria=random.random() > 0.8,
                    andar_preferido=random.choice([None, None, random.randint(1, 9)]),
                    prioridade=random.randint(1, 5),
                )
            self.setores[sid].total_funcionarios = total

        # Algumas restrições ilustrativas
        self.restricoes["r1"] = Restricao(
            id="r1", tipo=TipoRestricao.SEPARACAO_SETORES,
            descricao="Jurídico e Comercial não podem compartilhar a mesma sala",
            valor="juridico,comercial", obrigatoria=True,
        )
        self.restricoes["r2"] = Restricao(
            id="r2", tipo=TipoRestricao.SALA_RESERVADA,
            descricao="Sala 101 reservada para Jurídico",
            setor_id="juridico", obrigatoria=True,
        )
        if "sala-101" in self.salas:
            self.salas["sala-101"].setor_reservado = "juridico"

    # ------------------------------------------------------------- helpers
    def snapshot(self):
        return (
            list(self.salas.values()),
            list(self.setores.values()),
            list(self.equipes.values()),
            list(self.restricoes.values()),
        )


storage = Storage()
