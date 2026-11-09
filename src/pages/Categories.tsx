import { useMemo } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { colorFor, hbar, heatmap } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { CATEGORY_HIERARCHY, hateTypeLabel, platformLabel, showHateTypeInCharts } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type CategoryData = {
  frequency: Row[];
  byPlatform: Array<{ platform: string; hate_type: string; total: number }>;
  cooccurrence: Array<{ hate_type_a: string; hate_type_b: string; total: number }>;
  totalHateRecords: number;
};

type ProbData = {
  rows: Row[];
  totalHate: number;
};

export function Categories() {
  const { filters, showPoliticalCharts } = useFilters();
  const { data, loading, error } = useApi<CategoryData>("/api/categories", filters);
  const probs = useApi<ProbData>("/api/category-probabilities", filters);

  const frequency = data?.frequency ?? [];
  const dominantVisibleType = frequency.find((r) => showHateTypeInCharts(String(r.hate_type), showPoliticalCharts));

  const freqOption = useMemo(
    () =>
      hbar(
        frequency.filter((r) => showHateTypeInCharts(String(r.hate_type), showPoliticalCharts)).map((r) => ({
          label: hateTypeLabel(String(r.hate_type)),
          value: asNumber(r.total_mentions),
          color: colorFor(String(r.hate_type)),
        })),
      ),
    [frequency, showPoliticalCharts],
  );

  const platformHeatmap = useMemo(() => {
    const rows = data?.byPlatform ?? [];
    const platforms = Array.from(new Set(rows.map((r) => r.platform))).sort();
    const types = CATEGORY_HIERARCHY.filter((t) => showHateTypeInCharts(t, showPoliticalCharts) && rows.some((r) => r.hate_type === t));
    const index = new Map<string, number>();
    for (const r of rows) index.set(`${r.platform}|${r.hate_type}`, r.total);
    const cells: Array<[number, number, number]> = [];
    types.forEach((type, y) => {
      platforms.forEach((platform, x) => {
        cells.push([x, y, index.get(`${platform}|${type}`) ?? 0]);
      });
    });
    return heatmap(platforms.map(platformLabel), types.map(hateTypeLabel), cells);
  }, [data, showPoliticalCharts]);

  const coocOption = useMemo(
    () =>
      hbar(
        (data?.cooccurrence ?? [])
          .filter((r) => showHateTypeInCharts(r.hate_type_a, showPoliticalCharts) && showHateTypeInCharts(r.hate_type_b, showPoliticalCharts))
          .slice(0, 12)
          .map((r) => ({
          label: `${hateTypeLabel(r.hate_type_a)} + ${hateTypeLabel(r.hate_type_b)}`,
          value: r.total,
        })),
      ),
    [data, showPoliticalCharts],
  );

  // Probabilidades por categoria, montadas "pegando as hierarquias".
  const probRows = useMemo<Row[]>(() => {
    const byCat = new Map<string, Row>();
    for (const r of probs.data?.rows ?? []) byCat.set(String(r.category), r);
    return CATEGORY_HIERARCHY.filter((c) => byCat.has(c)).map((c) => ({ ...byCat.get(c)!, category: c }));
  }, [probs.data]);

  const probOption = useMemo(
    () =>
      hbar(
        probRows.filter((r) => showHateTypeInCharts(String(r.category), showPoliticalCharts)).map((r) => ({
          label: hateTypeLabel(String(r.category)),
          value: asNumber(r.avg_probability) * 100,
          color: colorFor(String(r.category)),
        })),
        { suffix: "%", digits: 2 },
      ),
    [probRows, showPoliticalCharts],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !frequency.length} />

      <div className="grid grid-kpi">
        <Kpi label="Tipos de preconceito" value={fmtInt(frequency.length)} />
        <Kpi label="Menções (tipos)" value={fmtInt(frequency.reduce((acc, r) => acc + asNumber(r.total_mentions), 0))} />
        <Kpi label="Registros de ódio" value={fmtInt(data?.totalHateRecords)} />
        <Kpi
          label="Tipo dominante"
          value={dominantVisibleType ? hateTypeLabel(String(dominantVisibleType.hate_type)) : "—"}
          hint={dominantVisibleType ? `${fmtInt(dominantVisibleType.total_mentions)} menções` : undefined}
        />
      </div>

      <Card
        title="Frequência por tipo"
        subtitle="Menções por tipologia. Um registro pode ter mais de um tipo (multilabel)."
      >
        <EChart option={freqOption} height={340} />
      </Card>

      <Card title="Plataforma × tipo" subtitle="Distribuição das tipologias por rede.">
        <EChart option={platformHeatmap} height={360} />
      </Card>

      <div className="grid grid-2">
        <Card title="Coocorrência de tipos" subtitle="Pares que aparecem juntos no mesmo conteúdo.">
          <EChart option={coocOption} height={360} />
        </Card>
        <Card
          title="Probabilidade média por categoria"
          subtitle="Média do score do modelo para cada categoria, na ordem da hierarquia (só registros com ódio)."
        >
          <EChart option={probOption} height={360} />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Detalhe por tipo" subtitle="Volume, presença por rede e probabilidade média.">
          <DataTable
            columns={[
              { key: "hate_type", label: "Tipo", render: (r: Row) => <b>{hateTypeLabel(String(r.hate_type))}</b> },
              { key: "total_mentions", label: "Menções", numeric: true, render: (r: Row) => fmtInt(r.total_mentions) },
              {
                key: "share",
                label: "% do ódio",
                numeric: true,
                render: (r: Row) =>
                  fmtPct((asNumber(r.total_mentions) / Math.max(1, data?.totalHateRecords ?? 1)) * 100),
              },
              { key: "post_mentions", label: "Posts", numeric: true, render: (r: Row) => fmtInt(r.post_mentions) },
              { key: "comment_mentions", label: "Coment.", numeric: true, render: (r: Row) => fmtInt(r.comment_mentions) },
              { key: "total_platforms", label: "Redes", numeric: true, render: (r: Row) => fmtInt(r.total_platforms) },
              { key: "avg_hate_probability", label: "Prob. média", numeric: true, render: (r: Row) => asNumber(r.avg_hate_probability).toFixed(3) },
            ]}
            rows={frequency}
          />
        </Card>

        <Card
          title="Probabilidades por categoria (hierarquia)"
          subtitle="Média, mediana, máximo e quantos registros passam de 0,50 em cada categoria."
        >
          <Status loading={probs.loading} error={probs.error} empty={!probs.loading && !probRows.length} />
          {probRows.length > 0 && (
            <DataTable
              columns={[
                { key: "category", label: "Categoria", render: (r: Row) => <b>{hateTypeLabel(String(r.category))}</b> },
                { key: "avg_probability", label: "Média", numeric: true, render: (r: Row) => asNumber(r.avg_probability).toFixed(3) },
                { key: "median_probability", label: "Mediana", numeric: true, render: (r: Row) => asNumber(r.median_probability).toFixed(3) },
                { key: "max_probability", label: "Máx.", numeric: true, render: (r: Row) => asNumber(r.max_probability).toFixed(3) },
                { key: "above_half", label: "≥ 0,50", numeric: true, render: (r: Row) => fmtInt(r.above_half) },
                {
                  key: "above_half_pct",
                  label: "% ≥ 0,50",
                  numeric: true,
                  render: (r: Row) => fmtPct((asNumber(r.above_half) / Math.max(1, asNumber(r.total))) * 100),
                },
              ]}
              rows={probRows}
              maxHeight={380}
            />
          )}
        </Card>
      </div>
    </>
  );
}
