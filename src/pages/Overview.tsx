import { useMemo } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, Kpi, Status, useApi } from "../components/ui.tsx";
import { colorFor, hbar, PALETTE, tooltip } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { hateTypeLabel, showHateTypeInCharts } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type OverviewData = {
  current: Row | null;
  previous?: Row;
  daily: Array<{ day: string; total: number; hate: number }>;
  types: Array<{ hate_type: string; total: number }>;
};

function delta(current: number, previous: number): number {
  if (!previous) return 0;
  return ((current - previous) / previous) * 100;
}

export function Overview() {
  const { filters, showPoliticalCharts } = useFilters();
  const { data, loading, error } = useApi<OverviewData>("/api/overview", filters);

  const current = data?.current ?? {};
  const previous = data?.previous ?? {};
  const hasPrevious = asNumber(previous.total_content) > 0;
  const deltaOrUndefined = (a: number, b: number) => (hasPrevious ? { value: delta(a, b) } : undefined);

  const dailyOption = useMemo(() => {
    const rows = data?.daily ?? [];
    return {
      grid: { left: 8, right: 12, top: 22, bottom: 8, containLabel: true },
      tooltip: tooltip(),
      xAxis: {
        type: "category" as const,
        data: rows.map((r) => r.day),
        axisLabel: { color: "#8b95a6", fontSize: 10 },
        axisLine: { lineStyle: { color: "#cbd5e1" } },
      },
      yAxis: {
        type: "value" as const,
        name: "ódio",
        nameTextStyle: { fontSize: 10 },
        axisLabel: { color: "#8b95a6", fontSize: 10 },
        splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } },
      },
      series: [
        {
          name: "Discurso de ódio",
          type: "bar" as const,
          data: rows.map((r) => r.hate),
          itemStyle: { color: PALETTE[1], borderRadius: [3, 3, 0, 0] },
          barMaxWidth: 18,
        },
        {
          name: "Linha diária",
          type: "line" as const,
          data: rows.map((r) => r.hate),
          smooth: true,
          symbol: "circle",
          symbolSize: 5,
          lineStyle: { color: PALETTE[0], width: 2.5 },
          itemStyle: { color: PALETTE[0] },
          z: 3,
        },
      ],
    };
  }, [data]);

  const typesOption = useMemo(
    () =>
      hbar(
        (data?.types ?? []).filter((t) => showHateTypeInCharts(t.hate_type, showPoliticalCharts)).map((t) => ({
          label: hateTypeLabel(t.hate_type),
          value: t.total,
          color: colorFor(t.hate_type),
        })),
        { labelFontSize: 14, nameFontSize: 14, barMaxWidth: 30 },
      ),
    [data, showPoliticalCharts],
  );

  return (
    <>
      <Status loading={loading} error={error} />

      <div className="grid grid-kpi">
        <Kpi
          label="Conteúdos"
          value={fmtInt(current.total_content)}
          delta={deltaOrUndefined(asNumber(current.total_content), asNumber(previous.total_content))}
          hint={hasPrevious ? undefined : "sem período anterior comparável"}
        />
        <Kpi
          label="Discurso de ódio"
          value={fmtInt(current.total_hate)}
          delta={deltaOrUndefined(asNumber(current.total_hate), asNumber(previous.total_hate))}
        />
        <Kpi
          label="Taxa de discurso de ódio"
          value={fmtPct(current.hate_percent)}
          delta={deltaOrUndefined(asNumber(current.hate_percent), asNumber(previous.hate_percent))}
        />
        <Kpi label="Autores distintos" value={fmtInt(current.total_authors)} hint="perfis com conteúdo no período" />
        <Kpi label="Plataformas" value={fmtInt(current.total_platforms)} hint={`${fmtInt(current.total_posts)} posts · ${fmtInt(current.total_comments)} comentários`} />
      </div>

      <Card
        title="Evolução diária"
        subtitle="Conteúdos com discurso de ódio identificados por dia."
      >
        <EChart option={dailyOption} height={340} />
      </Card>

      <Card
        title="Tipos de preconceito"
        subtitle="Menções por tipologia entre os conteúdos classificados como discurso de ódio."
      >
        <EChart option={typesOption} height={430} />
      </Card>
    </>
  );
}
