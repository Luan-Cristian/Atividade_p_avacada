const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function req(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  dashboard: () => req("/dashboard"),
  comparacao: () => req("/dashboard/comparacao"),
  gerarAlocacao: () => req("/alocacao/gerar", { method: "POST" }),
  justificativa: (equipeId) => req(`/alocacao/justificativa/${equipeId}`),
  intervencao: (payload) =>
    req("/alocacao/intervencao", { method: "POST", body: JSON.stringify(payload) }),
  execucoes: () => req("/governanca/execucoes"),
  intervencoes: () => req("/governanca/intervencoes"),
  observabilidade: () => req("/observabilidade"),
  salas: () => req("/salas"),
  setores: () => req("/setores"),
  equipes: () => req("/equipes"),
  atualizarEquipe: (id, payload) =>
    req(`/equipes/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  restricoes: () => req("/restricoes"),
  criarRestricao: (payload) => req("/restricoes", { method: "POST", body: JSON.stringify(payload) }),
  removerRestricao: (id) => req(`/restricoes/${id}`, { method: "DELETE" }),
};
