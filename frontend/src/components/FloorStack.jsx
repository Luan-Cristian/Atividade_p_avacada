export default function FloorStack({ porAndar, selecionado, onSelect }) {
  const andares = Object.keys(porAndar || {}).sort((a, b) => b - a); // topo primeiro (9 -> 1)

  return (
    <div className="floorstack">
      <div className="floorstack-header">
        <span className="eyebrow">Corte do edifício</span>
        <span className="floorstack-caption">9 andares · clique para inspecionar</span>
      </div>
      <div className="floorstack-body">
        {andares.map((andar) => {
          const d = porAndar[andar];
          const pct = Math.min(d.percentual_ocupacao, 100);
          const ativo = String(selecionado) === String(andar);
          return (
            <button
              key={andar}
              className={`floor-row ${ativo ? "is-active" : ""}`}
              onClick={() => onSelect(ativo ? null : andar)}
              aria-pressed={ativo}
            >
              <span className="floor-label mono">{String(andar).padStart(2, "0")}</span>
              <span className="floor-bar-track">
                <span
                  className="floor-bar-fill"
                  style={{ width: `${pct}%` }}
                />
                <span className="floor-bar-meta mono">
                  {d.pessoas_alocadas}/{d.capacidade_total} · {d.percentual_ocupacao}%
                </span>
              </span>
              <span className="floor-rooms mono">{d.salas_ocupadas}/{d.salas_total} salas</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
