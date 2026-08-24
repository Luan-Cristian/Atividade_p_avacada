import { useEffect, useState, useCallback } from "react";
import { api } from "./api";
import Dashboard from "./components/Dashboard";
import Allocation from "./components/Allocation";
import Comparison from "./components/Comparison";
import Governance from "./components/Governance";
import Observability from "./components/Observability";
import Registrations from "./components/Registrations";
import "./App.css";

const ABAS = [
  { id: "dashboard", label: "Painel" },
  { id: "alocacao", label: "Alocação" },
  { id: "comparacao", label: "Comparação" },
  { id: "cadastro", label: "Cadastro" },
  { id: "governanca", label: "Governança" },
  { id: "observabilidade", label: "Monitoramento" },
];

export default function App() {
  const [aba, setAba] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [comparacao, setComparacao] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [execucoes, setExecucoes] = useState([]);
  const [intervencoes, setIntervencoes] = useState([]);
  const [observ, setObserv] = useState(null);
  const [salas, setSalas] = useState([]);
  const [setores, setSetores] = useState([]);
  const [equipes, setEquipes] = useState([]);
  const [restricoes, setRestricoes] = useState([]);
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState(null);

  const carregarBase = useCallback(async () => {
    try {
      const [d, s, st, eq, r] = await Promise.all([
        api.dashboard(),
        api.salas(),
        api.setores(),
        api.equipes(),
        api.restricoes(),
      ]);
      setDashboard(d);
      setSalas(s);
      setSetores(st);
      setEquipes(eq);
      setRestricoes(r);
    } catch (e) {
      setErro(e.message);
    }
  }, []);

  const carregarGovernanca = useCallback(async () => {
    try {
      const [ex, iv, ob] = await Promise.all([
        api.execucoes(),
        api.intervencoes(),
        api.observabilidade(),
      ]);
      setExecucoes(ex);
      setIntervencoes(iv);
      setObserv(ob);
    } catch (e) {
      setErro(e.message);
    }
  }, []);

  useEffect(() => {
    carregarBase();
    carregarGovernanca();
  }, [carregarBase, carregarGovernanca]);

  async function gerarAlocacao() {
    setGerando(true);
    setErro(null);
    try {
      const res = await api.gerarAlocacao();
      setResultado(res);
      const [d, comp] = await Promise.all([api.dashboard(), api.comparacao()]);
      setDashboard(d);
      setComparacao(comp);
      await carregarGovernanca();
      setAba("alocacao");
    } catch (e) {
      setErro(e.message);
    } finally {
      setGerando(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">SGE</span>
          <span className="brand-name">Sistema de Gestão e Otimização de Espaços Corporativos</span>
        </div>
        <nav className="tabs">
          {ABAS.map((a) => (
            <button
              key={a.id}
              className={`tab ${aba === a.id ? "is-active" : ""}`}
              onClick={() => setAba(a.id)}
            >
              {a.label}
            </button>
          ))}
        </nav>
      </header>

      {erro && <div className="banner-error">Erro: {erro}</div>}

      <main className="content">
        {aba === "dashboard" && (
          <Dashboard
            dashboard={dashboard}
            onGerar={gerarAlocacao}
            gerando={gerando}
            ultimaExecucao={resultado}
          />
        )}
        {aba === "alocacao" && (
          <Allocation
            resultado={resultado}
            salas={salas}
            onIntervencaoRegistrada={carregarGovernanca}
          />
        )}
        {aba === "comparacao" && <Comparison comparacao={comparacao} />}
        {aba === "cadastro" && (
          <Registrations
            equipes={equipes}
            setores={setores}
            restricoes={restricoes}
            onChanged={carregarBase}
          />
        )}
        {aba === "governanca" && (
          <Governance execucoes={execucoes} intervencoes={intervencoes} />
        )}
        {aba === "observabilidade" && <Observability dados={observ} />}
      </main>

      <footer className="footer mono">
        allocation-engine-v1 · protótipo MVP · decisões revisáveis por intervenção humana
      </footer>
    </div>
  );
}
