import { useState } from "react";
import { KpiRow, Kpi } from "./Kpi";
import FloorStack from "./FloorStack";

export default function Dashboard({ dashboard, onGerar, gerando, ultimaExecucao }) {
  const [andarSelecionado, setAndarSelecionado] = useState(null);

  if (!dashboard) return <p className="muted">Carregando painel…</p>;

  const detalheAndar = andarSelecionado ? dashboard.por_andar[andarSelecionado] : null;

  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Coordenador Geral</span>
          <h1>Situação do prédio</h1>
        </div>
        <button className="btn-primary" onClick={onGerar} disabled={gerando}>
          {gerando ? "Gerando alocação…" : "Gerar alocação otimizada"}
        </button>
      </div>

      {ultimaExecucao && (
        <p className="run-note mono">
          última execução #{ultimaExecucao.execucao_id} · {ultimaExecucao.tempo_execucao_s}s ·
          {" "}{ultimaExecucao.alocacoes.length} equipes alocadas ·{" "}
          {ultimaExecucao.excecoes.length} pendências ·{" "}
          {ultimaExecucao.restricoes_violadas} violações
        </p>
      )}

      <KpiRow>
        <Kpi label="Ocupação total" value={dashboard.ocupacao_total_percentual} suffix="%" />
        <Kpi label="Funcionários alocados" value={dashboard.funcionarios_alocados} />
        <Kpi label="Equipes alocadas" value={dashboard.equipes_alocadas} tone="good" />
        <Kpi
          label="Equipes não alocadas"
          value={dashboard.equipes_nao_alocadas}
          tone={dashboard.equipes_nao_alocadas > 0 ? "alert" : "good"}
        />
        <Kpi label="Salas disponíveis" value={dashboard.salas_disponiveis} />
        <Kpi label="Salas ocupadas" value={dashboard.salas_ocupadas} />
        <Kpi label="Utilização de salas" value={dashboard.percentual_utilizacao_salas} suffix="%" />
        <Kpi
          label="Restrições violadas"
          value={dashboard.restricoes_violadas}
          tone={dashboard.restricoes_violadas > 0 ? "alert" : "good"}
        />
      </KpiRow>

      <div className="grid-2">
        <FloorStack
          porAndar={dashboard.por_andar}
          selecionado={andarSelecionado}
          onSelect={setAndarSelecionado}
        />
        <div className="panel">
          <span className="eyebrow">
            {detalheAndar ? `Andar ${andarSelecionado}` : "Selecione um andar"}
          </span>
          {detalheAndar ? (
            <dl className="detail-list">
              <div><dt>Salas no andar</dt><dd className="mono">{detalheAndar.salas_total}</dd></div>
              <div><dt>Salas ocupadas</dt><dd className="mono">{detalheAndar.salas_ocupadas}</dd></div>
              <div><dt>Capacidade total</dt><dd className="mono">{detalheAndar.capacidade_total}</dd></div>
              <div><dt>Pessoas alocadas</dt><dd className="mono">{detalheAndar.pessoas_alocadas}</dd></div>
              <div><dt>Ocupação</dt><dd className="mono">{detalheAndar.percentual_ocupacao}%</dd></div>
            </dl>
          ) : (
            <p className="muted">Clique em um andar no corte do edifício para ver os detalhes.</p>
          )}
        </div>
      </div>
    </div>
  );
}
