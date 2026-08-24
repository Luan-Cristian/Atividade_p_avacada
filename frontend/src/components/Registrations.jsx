import { useState } from "react";
import { api } from "../api";

export default function Registrations({ equipes, setores, restricoes, onChanged }) {
  const [filtroSetor, setFiltroSetor] = useState("todos");
  const [mensagem, setMensagem] = useState(null);

  const equipesFiltradas =
    filtroSetor === "todos" ? equipes : equipes.filter((e) => e.setor_id === filtroSetor);

  async function salvarQuantidade(equipeId, valor) {
    const n = parseInt(valor, 10);
    if (Number.isNaN(n) || n <= 0) return;
    await api.atualizarEquipe(equipeId, { quantidade_funcionarios: n });
    setMensagem(`Equipe ${equipeId} atualizada para ${n} funcionários.`);
    onChanged?.();
  }

  async function salvarPrioridade(equipeId, valor) {
    await api.atualizarEquipe(equipeId, { prioridade: parseInt(valor, 10) });
    onChanged?.();
  }

  return (
    <div className="stack-lg">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Coordenador de Setor</span>
          <h1>Equipes, funcionários e restrições</h1>
        </div>
        <select className="select-inline" value={filtroSetor} onChange={(e) => setFiltroSetor(e.target.value)}>
          <option value="todos">Todos os setores</option>
          {setores.map((s) => (
            <option key={s.id} value={s.id}>{s.nome}</option>
          ))}
        </select>
      </div>

      {mensagem && <p className="banner-ok">{mensagem}</p>}

      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Equipe</th>
              <th>Setor</th>
              <th>Funcionários</th>
              <th>Prioridade (1 = alta)</th>
              <th>Andar preferido</th>
            </tr>
          </thead>
          <tbody>
            {equipesFiltradas.map((eq) => (
              <tr key={eq.id}>
                <td>{eq.nome}</td>
                <td className="mono">{eq.setor_id}</td>
                <td>
                  <input
                    type="number"
                    className="input-inline mono"
                    defaultValue={eq.quantidade_funcionarios}
                    min={1}
                    onBlur={(e) => salvarQuantidade(eq.id, e.target.value)}
                  />
                </td>
                <td>
                  <select
                    className="select-inline"
                    defaultValue={eq.prioridade}
                    onChange={(e) => salvarPrioridade(eq.id, e.target.value)}
                  >
                    {[1, 2, 3, 4, 5].map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </td>
                <td className="mono">{eq.andar_preferido ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="panel">
        <span className="eyebrow">Restrições cadastradas</span>
        <table>
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Descrição</th>
              <th>Obrigatória</th>
            </tr>
          </thead>
          <tbody>
            {restricoes.map((r) => (
              <tr key={r.id}>
                <td className="mono">{r.tipo}</td>
                <td>{r.descricao}</td>
                <td className="mono">{r.obrigatoria ? "sim" : "não"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
