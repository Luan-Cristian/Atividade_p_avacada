import { useState, Fragment } from "react";
import { api } from "../api";

export default function Allocation({ resultado, salas, onIntervencaoRegistrada }) {
  const [selecionada, setSelecionada] = useState(null);
  const [salaManual, setSalaManual] = useState("");
  const [mensagem, setMensagem] = useState(null);

  if (!resultado) {
    return (
      <div className="panel">
        <p className="muted">
          Nenhuma alocação gerada ainda. Volte ao Painel e clique em
          "Gerar alocação otimizada".
        </p>
      </div>
    );
  }

  async function agir(equipeId, acao) {
    try {
      await api.intervencao({
        execucao_id: resultado.execucao_id,
        equipe_id: equipeId,
        acao,
        sala_id_manual: acao === "alterar_manual" ? salaManual : undefined,
      });
      setMensagem(`Intervenção "${acao}" registrada para ${equipeId}.`);
      setSalaManual("");
      onIntervencaoRegistrada?.();
    } catch (e) {
      setMensagem("Erro ao registrar intervenção: " + e.message);
    }
  }

  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Motor de alocação</span>
          <h1>Distribuição proposta</h1>
        </div>
      </div>

      {mensagem && <p className="banner-ok">{mensagem}</p>}

      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Equipe</th>
              <th>Pessoas</th>
              <th>Sala sugerida</th>
              <th>Capacidade</th>
              <th>Andar</th>
              <th>Ocupação</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {resultado.alocacoes.map((a) => (
              <Fragment key={a.equipe_id}>
                <tr
                  className={selecionada === a.equipe_id ? "is-selected" : ""}
                >
                  <td>{a.equipe_nome}</td>
                  <td className="mono">{a.pessoas}</td>
                  <td className="mono">{a.sala_nome}</td>
                  <td className="mono">{a.capacidade}</td>
                  <td className="mono">{a.andar}º</td>
                  <td className="mono">{a.ocupacao_prevista}%</td>
                  <td>
                    <button
                      className="btn-link"
                      onClick={() =>
                        setSelecionada(selecionada === a.equipe_id ? null : a.equipe_id)
                      }
                    >
                      {selecionada === a.equipe_id ? "Fechar" : "Justificativa"}
                    </button>
                  </td>
                </tr>
                {selecionada === a.equipe_id && (
                  <tr className="justification-row">
                    <td colSpan={7}>
                      <div className="justification-box">
                        <p>{a.justificativa}</p>
                        <div className="intervention-actions">
                          <button className="btn-ghost" onClick={() => agir(a.equipe_id, "aceitar")}>
                            Aceitar recomendação
                          </button>
                          <button className="btn-ghost" onClick={() => agir(a.equipe_id, "rejeitar")}>
                            Rejeitar
                          </button>
                          <select
                            className="select-inline"
                            value={salaManual}
                            onChange={(e) => setSalaManual(e.target.value)}
                          >
                            <option value="">Alterar manualmente para…</option>
                            {salas
                              .filter((s) => s.id !== a.sala_id)
                              .map((s) => (
                                <option key={s.id} value={s.id}>
                                  {s.nome} (andar {s.andar}, cap. {s.capacidade})
                                </option>
                              ))}
                          </select>
                          <button
                            className="btn-primary-sm"
                            disabled={!salaManual}
                            onClick={() => agir(a.equipe_id, "alterar_manual")}
                          >
                            Confirmar alteração
                          </button>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {resultado.excecoes.length > 0 && (
        <div className="panel panel-alert">
          <span className="eyebrow eyebrow-alert">Exceções — sem solução compatível</span>
          <table>
            <thead>
              <tr>
                <th>Equipe</th>
                <th>Restrição não atendida</th>
                <th>Causa</th>
                <th>Encaminhamento sugerido</th>
              </tr>
            </thead>
            <tbody>
              {resultado.excecoes.map((e) => (
                <tr key={e.equipe_id}>
                  <td>{e.equipe_nome}</td>
                  <td className="mono">{e.restricao_nao_atendida}</td>
                  <td>{e.causa}</td>
                  <td>{e.encaminhamento_sugerido}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
