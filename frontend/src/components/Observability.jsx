import { KpiRow, Kpi } from "./Kpi";

export default function Observability({ dados }) {
  if (!dados) return <p className="muted">Carregando…</p>;

  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Monitoramento do Motor de Alocação</span>
          <h1>O mecanismo continua funcionando corretamente?</h1>
        </div>
      </div>
      <KpiRow>
        <Kpi
          label="Tempo da última otimização"
          value={dados.tempo_ultima_otimizacao_s ?? "—"}
          suffix="s"
        />
        <Kpi label="Número de execuções" value={dados.numero_execucoes} />
        <Kpi
          label="Taxa de alocação média"
          value={dados.taxa_alocacao_media !== null ? Math.round(dados.taxa_alocacao_media * 100) : "—"}
          suffix="%"
        />
        <Kpi label="Ocupação média" value={dados.ocupacao_media ?? "—"} suffix="%" />
        <Kpi
          label="Conflitos acumulados"
          value={dados.conflitos_total}
          tone={dados.conflitos_total > 0 ? "alert" : "good"}
        />
        <Kpi label="Equipes não alocadas (última)" value={dados.nao_alocados_total} />
        <Kpi label="Intervenções manuais" value={dados.intervencoes_manuais} />
        <Kpi label="Erros" value={dados.erros} tone={dados.erros > 0 ? "alert" : "good"} />
      </KpiRow>
    </div>
  );
}
