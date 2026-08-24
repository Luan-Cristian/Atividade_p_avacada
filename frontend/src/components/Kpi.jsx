export function KpiRow({ children }) {
  return <div className="kpi-row">{children}</div>;
}

export function Kpi({ label, value, tone = "default", suffix = "" }) {
  return (
    <div className={`kpi kpi-${tone}`}>
      <span className="kpi-label">{label}</span>
      <span className="kpi-value mono">
        {value}
        {suffix && <span className="kpi-suffix">{suffix}</span>}
      </span>
    </div>
  );
}
