import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { api, type Filters } from "../api.ts";

/** Hook de leitura da API com estados de carregando/erro. */
export function useApi<T>(
  path: string,
  filters: Filters,
  extra: Record<string, unknown> = {},
  enabled = true,
): { data: T | null; loading: boolean; error: string | null; reload: () => void } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const seq = useRef(0);
  // O caminho também faz parte da identidade da requisição. Sem ele, trocar o
  // post selecionado mantinha o detalhe anterior e o botão "abrir" parecia não
  // funcionar.
  const key = JSON.stringify({ path, filters, extra, nonce });

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    let alive = true;
    // Guarda de corrida: filtros rápidos geram várias requisições e a resposta de
    // uma antiga não pode sobrescrever a da mais recente.
    const mySeq = ++seq.current;
    setLoading(true);
    setError(null);
    api<T>(path, filters, extra)
      .then((result) => {
        if (alive && mySeq === seq.current) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (alive && mySeq === seq.current) {
          setError(err instanceof Error ? err.message : String(err));
          setLoading(false);
        }
      });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, enabled]);

  return { data, loading, error, reload: () => setNonce((n) => n + 1) };
}

export function Card({
  title,
  subtitle,
  children,
  actions,
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <section className="card">
      {(title || actions) && (
        <header className="card-header" style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <div>
            {title && <h2 className="card-title">{title}</h2>}
            {subtitle && <p className="card-sub">{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      <div className="card-body">{children}</div>
    </section>
  );
}

export function Kpi({
  label,
  value,
  hint,
  delta,
}: {
  label: string;
  value: string;
  hint?: string;
  delta?: { value: number; suffix?: string; invert?: boolean };
}) {
  let cls = "kpi-delta flat";
  if (delta && Number.isFinite(delta.value) && Math.abs(delta.value) >= 0.05) {
    const rising = delta.value > 0;
    const bad = delta.invert ? !rising : rising;
    cls = `kpi-delta ${bad ? "up" : "down"}`;
  }
  return (
    <div className="card kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {delta && (
        <div className={cls}>
          {delta.value > 0 ? "▲" : delta.value < 0 ? "▼" : "■"}{" "}
          {Math.abs(delta.value).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}
          {delta.suffix ?? "%"} vs. período anterior
        </div>
      )}
      {hint && <div className="kpi-hint">{hint}</div>}
    </div>
  );
}

export function Skeleton({ rows = 3, bar = false }: { rows?: number; bar?: boolean }) {
  return (
    <div className="skeleton" aria-hidden="true">
      {bar && <div className="skeleton-row bar" />}
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="skeleton-row" style={{ width: `${100 - index * 9}%` }} />
      ))}
    </div>
  );
}

export function Status({
  loading,
  error,
  empty,
  rows = 3,
}: {
  loading: boolean;
  error: string | null;
  empty?: boolean;
  rows?: number;
}) {
  if (error) {
    return (
      <div className="chart-error">
        <b>Não foi possível carregar os dados.</b>
        <div style={{ marginTop: 4, opacity: 0.85 }}>{error}</div>
      </div>
    );
  }
  if (loading) return <Skeleton rows={rows} />;
  if (empty) return <div className="empty">Sem dados para os filtros selecionados.</div>;
  return null;
}

export type Column = {
  key: string;
  label: string;
  numeric?: boolean;
  render?: (row: Record<string, unknown>) => ReactNode;
  width?: string;
};

export function DataTable({ columns, rows, maxHeight }: { columns: Column[]; rows: Record<string, unknown>[]; maxHeight?: number }) {
  if (!rows.length) return <div className="empty">Sem registros.</div>;
  return (
    <div className="table-wrap" style={maxHeight ? { maxHeight } : undefined}>
      <table className="data">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className={col.numeric ? "num" : ""} style={col.width ? { width: col.width } : undefined}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={String(row.id ?? index)}>
              {columns.map((col) => (
                <td key={col.key} className={col.numeric ? "num" : "cell-text"}>
                  {col.render ? col.render(row) : String(row[col.key] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Pill({ children, tone }: { children: ReactNode; tone?: "hate" | "ok" | "muted" }) {
  return <span className={`badge${tone ? ` ${tone}` : ""}`}>{children}</span>;
}
