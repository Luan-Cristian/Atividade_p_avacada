export default function Governance({ execucoes, intervencoes }) {
  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Governança</span>
          <h1>Histórico de execuções e intervenções</h1>
        </div>
      </div>

      <div className="panel">
        <span className="eyebrow">Execuções do motor</span>
        {execucoes.length === 0 ? (
          <p className="muted">Nenhuma execução registrada ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Data/hora</th>
                <th>Usuário</th>
                <th>Algoritmo</th>
                <th>Equipes</th>
                <th>Alocadas</th>
                <th>Não alocadas</th>
                <th>Violações</th>
                <th>Ocupação prevista</th>
              </tr>
            </thead>
            <tbody>
              {[...execucoes].reverse().map((e) => (
                <tr key={e.execucao_id}>
                  <td className="mono">{e.execucao_id}</td>
                  <td className="mono">{new Date(e.data_hora * 1000).toLocaleString("pt-BR")}</td>
                  <td>{e.usuario}</td>
                  <td className="mono">{e.algoritmo}</td>
                  <td className="mono">{e.equipes_analisadas}</td>
                  <td className="mono">{e.equipes_alocadas}</td>
                  <td className="mono">{e.equipes_nao_alocadas}</td>
                  <td className="mono">{e.restricoes_violadas}</td>
                  <td className="mono">{e.ocupacao_prevista}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="panel">
        <span className="eyebrow">Intervenções humanas</span>
        {intervencoes.length === 0 ? (
          <p className="muted">Nenhuma intervenção registrada ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Execução</th>
                <th>Equipe</th>
                <th>Ação</th>
                <th>Usuário</th>
                <th>Quando</th>
              </tr>
            </thead>
            <tbody>
              {[...intervencoes].reverse().map((i, idx) => (
                <tr key={idx}>
                  <td className="mono">{i.execucao_id}</td>
                  <td>{i.equipe_id}</td>
                  <td className="mono">{i.acao}</td>
                  <td>{i.usuario}</td>
                  <td className="mono">{new Date(i.timestamp * 1000).toLocaleString("pt-BR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
