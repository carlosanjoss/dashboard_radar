import { useMemo } from "react";
import { EChart } from "./EChart.tsx";
import { DataTable } from "./ui.tsx";
import { colorFor, hbar } from "./charts.ts";
import { fmtPct } from "../api.ts";
import { CATEGORY_HIERARCHY, hateTypeLabel, showHateTypeInCharts } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

/**
 * Monta as probabilidades por categoria de um registro "pegando as hierarquias":
 * percorre CATEGORY_HIERARCHY (sort_order canônico) e lê category_scores.
 */
export function CategoryProbabilities({ scores }: { scores: unknown }) {
  const { showPoliticalCharts } = useFilters();
  const rows = useMemo(() => {
    if (!scores || typeof scores !== "object") return [];
    const obj = scores as Record<string, number>;
    return CATEGORY_HIERARCHY.filter((code) => obj[code] !== undefined && obj[code] !== null).map((code) => ({
      category: code,
      label: hateTypeLabel(code),
      value: Number(obj[code]) * 100,
    }));
  }, [scores]);

  if (!rows.length) {
    return (
      <div className="empty">
        Este registro não tem probabilidades por categoria — o modelo multilabel só roda quando o binário aponta ódio.
      </div>
    );
  }

  const chartRows = rows.filter((row) => showHateTypeInCharts(row.category, showPoliticalCharts));
  const top = [...chartRows].sort((a, b) => b.value - a.value)[0];

  return (
    <>
      <EChart
        option={hbar(
          chartRows.map((r) => ({ label: r.label, value: r.value, color: colorFor(r.category) })),
          { suffix: "%", digits: 2 },
        )}
        height={320}
      />
      <p className="card-sub" style={{ marginTop: 8 }}>
        Categoria visível mais provável: <b>{top?.label ?? "—"}</b>{top ? ` (${fmtPct(top.value)})` : ""}. Categorias na ordem da hierarquia.
      </p>
      <DataTable
        columns={[
          { key: "label", label: "Categoria" },
          { key: "value", label: "Probabilidade", numeric: true, render: (r) => fmtPct(r.value) },
        ]}
        rows={rows as unknown as Record<string, unknown>[]}
        maxHeight={300}
      />
    </>
  );
}
