export default function Comparison({ comparacao }) {
  if (!comparacao) {
    return (
      <div className="panel">
        <p className="muted">Gere uma alocação no Painel para ver a comparação.</p>
      </div>
    );
  }

  const linhas = [
    { label: "Ocupação média", chave: "ocupacao_media", suf: "%", melhorMaior: true },
    { label: "Assentos ociosos", chave: "assentos_ociosos", suf: "", melhorMaior: false },
    { label: "Equipes sem sala", chave: "equipes_sem_sala", suf: "", melhorMaior: false },
    { label: "Violações", chave: "violacoes", suf: "", melhorMaior: false },
  ];

  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Antes vs. depois</span>
          <h1>A recomendação é realmente vantajosa?</h1>
        </div>
      </div>
      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Indicador</th>
              <th>Antes (baseline manual)</th>
              <th>Depois (otimizado)</th>
              <th>Variação</th>
            </tr>
          </thead>
          <tbody>
            {linhas.map((l) => {
              const antes = comparacao.antes[l.chave];
              const depois = comparacao.depois[l.chave];
              const melhora = l.melhorMaior ? depois >= antes : depois <= antes;
              return (
                <tr key={l.chave}>
                  <td>{l.label}</td>
                  <td className="mono">{antes}{l.suf}</td>
                  <td className="mono">{depois}{l.suf}</td>
                  <td className={`mono ${melhora ? "text-good" : "text-alert"}`}>
                    {depois - antes > 0 ? "+" : ""}
                    {(depois - antes).toFixed ? (depois - antes).toFixed(1) : depois - antes}
                    {l.suf}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
