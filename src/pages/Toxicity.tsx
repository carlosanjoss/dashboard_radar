import { useMemo, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { colorFor, lines, tooltip } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { hateTypeLabel, showHateTypeInCharts } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type ToxicityData = {
  grain: string;
  series: Row[];
  summary: Row[];
};

export function Toxicity() {
  const { filters, showPoliticalCharts } = useFilters();
  const [grain, setGrain] = useState("day");
  const { data, loading, error } = useApi<ToxicityData>("/api/toxicity", filters, { grain, limit: 10 });

  const summary = data?.summary ?? [];
  const series = data?.series ?? [];
  const visibleSummary = useMemo(
    () => summary.filter((row) => showHateTypeInCharts(String(row.hate_type), showPoliticalCharts)),
    [summary, showPoliticalCharts],
  );

  const periods = useMemo(() => Array.from(new Set(series.map((r) => String(r.period)))).sort(), [series]);

  const options = useMemo(() => {
    const share = visibleSummary.map((row) => {
      const code = String(row.hate_type);
      const byPeriod = periods.map((p) => {
        const hit = series.find((r) => String(r.period) === p && String(r.hate_type) === code);
        return hit ? asNumber(hit.percent_mentions) : null;
      });
      return { name: hateTypeLabel(code), data: byPeriod as Array<number | null>, color: colorFor(code) };
    });

    const volume = visibleSummary.map((row) => {
      const code = String(row.hate_type);
      const byPeriod = periods.map((p) => {
        const hit = series.find((r) => String(r.period) === p && String(r.hate_type) === code);
        return hit ? asNumber(hit.total_mentions) : 0;
      });
      return { name: hateTypeLabel(code), data: byPeriod, color: colorFor(code) };
    });

    return {
      share: lines(periods, share, {
        suffix: "%",
        yMin: 0,
        yMax: Math.min(100, Math.max(5, Math.ceil(Math.max(0, ...share.flatMap((s) => s.data.map((v) => v ?? 0))) / 5) * 5)),
      }),
      volume: {
        grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
        tooltip: tooltip(),
        legend: { top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } },
        xAxis: { type: "category" as const, data: periods, axisLabel: { color: "#8b95a6", fontSize: 10 } },
        yAxis: { type: "value" as const, axisLabel: { color: "#8b95a6", fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } } },
        series: volume.map((s) => ({
          name: s.name,
          type: "bar" as const,
          stack: "total",
          data: s.data,
          itemStyle: { color: s.color },
          barMaxWidth: 26,
        })),
      },
    };
  }, [visibleSummary, series, periods]);

  const topShare = useMemo(
    () => [...visibleSummary].sort((a, b) => asNumber(b.percent_mentions) - asNumber(a.percent_mentions))[0],
    [visibleSummary],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !visibleSummary.length} />

      <div className="grid grid-kpi">
        <Kpi label="Tipos analisados" value={fmtInt(visibleSummary.length)} />
        <Kpi label="Menções (tipos)" value={fmtInt(visibleSummary.reduce((acc, r) => acc + asNumber(r.total_mentions), 0))} />
        <Kpi
          label="Maior participação"
          value={topShare ? hateTypeLabel(String(topShare.hate_type)) : "—"}
          hint={topShare ? fmtPct(topShare.percent_mentions) : undefined}
        />
        <Kpi label="Granularidade" value={data?.grain ?? grain} />
      </div>

      <Card
        title="Participação por tipo"
        subtitle="Percentual de menções por período. A escala acompanha as categorias visíveis para destacar diferenças menores."
        actions={
          <select value={grain} onChange={(e) => setGrain(e.target.value)} className="btn" style={{ padding: "6px 10px" }}>
            <option value="day">Dia</option>
            <option value="week">Semana</option>
            <option value="month">Mês</option>
          </select>
        }
      >
        <EChart option={options.share} height={380} />
      </Card>

      <Card title="Volume por tipo" subtitle="Barras empilhadas: quantas menções sustentam cada ponto da série.">
        <EChart option={options.volume} height={320} />
      </Card>

      <Card title="Resumo do período" subtitle="Volume, cobertura de redes e distribuição por posts/comentários.">
        <DataTable
          columns={[
            { key: "hate_type", label: "Tipo", render: (r: Row) => <b>{hateTypeLabel(String(r.hate_type))}</b> },
            { key: "total_mentions", label: "Menções", numeric: true, render: (r: Row) => fmtInt(r.total_mentions) },
            { key: "percent_mentions", label: "% das menções", numeric: true, render: (r: Row) => fmtPct(r.percent_mentions) },
            { key: "total_platforms", label: "Redes", numeric: true, render: (r: Row) => fmtInt(r.total_platforms) },
            { key: "post_mentions", label: "Posts", numeric: true, render: (r: Row) => fmtInt(r.post_mentions) },
            { key: "comment_mentions", label: "Comentários", numeric: true, render: (r: Row) => fmtInt(r.comment_mentions) },
            { key: "avg_toxicity", label: "Prob. média", numeric: true, render: (r: Row) => asNumber(r.avg_toxicity).toFixed(3) },
          ]}
          rows={visibleSummary}
        />
      </Card>
    </>
  );
}
