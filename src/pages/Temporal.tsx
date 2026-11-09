import { useMemo, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, Kpi, Status, useApi } from "../components/ui.tsx";
import { colorFor, lines, PALETTE, tooltip } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { hateTypeLabel, showHateTypeInCharts } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type TemporalData = {
  grain: string;
  series: Row[];
};

type TypeSeriesData = {
  grain: string;
  series: Row[];
  summary: Row[];
};

/** Média móvel simples de uma série numérica. */
function rolling(values: number[], window: number): Array<number | null> {
  return values.map((_, i) => {
    if (i < window - 1) return null;
    const slice = values.slice(i - window + 1, i + 1);
    return slice.reduce((a, b) => a + b, 0) / slice.length;
  });
}

/** Domínio percentual com folga para revelar variações sem cortar os dados. */
function percentDomain(values: number[]): { min: number; max: number } {
  if (!values.length) return { min: 0, max: 100 };
  const low = Math.min(...values);
  const high = Math.max(...values);
  const padding = Math.max(1, (high - low) * 0.2);
  return {
    min: Math.max(0, Math.floor((low - padding) / 5) * 5),
    max: Math.min(100, Math.max(5, Math.ceil((high + padding) / 5) * 5)),
  };
}

export function Temporal() {
  const { filters, showPoliticalCharts } = useFilters();
  const [grain, setGrain] = useState("day");
  const { data, loading, error } = useApi<TemporalData>("/api/temporal", filters, { grain });
  const typeData = useApi<TypeSeriesData>("/api/toxicity", filters, { grain, limit: 10 });

  const series = data?.series ?? [];
  const periods = series.map((r) => String(r.period));
  const typeSeries = typeData.data?.series ?? [];
  const typeSummary = typeData.data?.summary ?? [];
  const visibleTypeSummary = useMemo(
    () => typeSummary.filter((row) => showHateTypeInCharts(String(row.hate_type), showPoliticalCharts)),
    [typeSummary, showPoliticalCharts],
  );
  const typePeriods = useMemo(
    () => Array.from(new Set(typeSeries.map((row) => String(row.period)))).sort(),
    [typeSeries],
  );

  const option = useMemo(() => {
    const hate = series.map((r) => asNumber(r.total_hate));
    const rate = series.map((r) => asNumber(r.hate_percent));
    const rateDomain = percentDomain(rate);
    const seriesList: Array<{ name: string; data: Array<number | null>; color: string; dashed?: boolean }> = [
      { name: "Discurso de ódio", data: hate, color: PALETTE[1] },
    ];
    if (grain === "day" && series.length >= 7) {
      seriesList.push({ name: "Média móvel 7d (ódio)", data: rolling(hate, 7) as number[], color: PALETTE[0], dashed: true });
    }
    return {
      base: lines(periods, seriesList, { suffix: "" }),
      rate: lines(periods, [{ name: "Taxa de ódio (%)", data: rate, color: PALETTE[0], area: true }], {
        suffix: "%",
        yMin: rateDomain.min,
        yMax: rateDomain.max,
      }),
    };
  }, [series, periods, grain]);

  const typeOptions = useMemo(() => {
    const share = visibleTypeSummary.map((row) => {
      const code = String(row.hate_type);
      return {
        name: hateTypeLabel(code),
        data: typePeriods.map((period) => {
          const hit = typeSeries.find(
            (item) => String(item.period) === period && String(item.hate_type) === code,
          );
          return hit ? asNumber(hit.percent_mentions) : null;
        }) as Array<number | null>,
        color: colorFor(code),
      };
    });
    const volume = visibleTypeSummary.map((row) => {
      const code = String(row.hate_type);
      return {
        name: hateTypeLabel(code),
        data: typePeriods.map((period) => {
          const hit = typeSeries.find(
            (item) => String(item.period) === period && String(item.hate_type) === code,
          );
          return hit ? asNumber(hit.total_mentions) : 0;
        }),
        color: colorFor(code),
      };
    });
    const maxShare = Math.max(0, ...share.flatMap((item) => item.data.map((value) => value ?? 0)));

    return {
      share: lines(typePeriods, share, {
        suffix: "%",
        yMin: 0,
        yMax: Math.min(100, Math.max(5, Math.ceil(maxShare / 5) * 5)),
      }),
      volume: {
        grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
        tooltip: tooltip(),
        legend: { top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } },
        xAxis: { type: "category" as const, data: typePeriods, axisLabel: { color: "#8b95a6", fontSize: 10 } },
        yAxis: {
          type: "value" as const,
          axisLabel: { color: "#8b95a6", fontSize: 10 },
          splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } },
        },
        series: volume.map((item) => ({
          name: item.name,
          type: "bar" as const,
          stack: "total",
          data: item.data,
          itemStyle: { color: item.color },
          barMaxWidth: 26,
        })),
      },
    };
  }, [visibleTypeSummary, typeSeries, typePeriods]);

  const totals = series.reduce((acc, r) => acc + asNumber(r.total_content), 0);
  const totalHate = series.reduce((acc, r) => acc + asNumber(r.total_hate), 0);
  const peak = series.reduce<Row | null>(
    (best, r) => (best === null || asNumber(r.total_hate) > asNumber(best.total_hate) ? r : best),
    null,
  );

  return (
    <>
      <Status
        loading={loading || typeData.loading}
        error={error ?? typeData.error}
        empty={!loading && !typeData.loading && !series.length}
      />

      <div className="grid grid-kpi">
        <Kpi label="Períodos" value={fmtInt(series.length)} hint={`granularidade: ${data?.grain ?? grain}`} />
        <Kpi label="Conteúdos" value={fmtInt(totals)} />
        <Kpi label="Discurso de ódio" value={fmtInt(totalHate)} />
        <Kpi label="Taxa no período" value={fmtPct(totals ? (totalHate / totals) * 100 : 0)} />
        <Kpi
          label="Pico de ódio"
          value={peak ? String(peak.period) : "—"}
          hint={peak ? `${fmtInt(peak.total_hate)} registros` : undefined}
        />
      </div>

      <Card
        title="Evolução"
        subtitle="Conteúdos com discurso de ódio em cada período. Na granularidade diária, inclui média móvel de 7 dias para suavizar ruído."
        actions={
          <select value={grain} onChange={(e) => setGrain(e.target.value)} className="btn" style={{ padding: "6px 10px" }}>
            <option value="day">Dia</option>
            <option value="week">Semana</option>
            <option value="month">Mês</option>
            <option value="year">Ano</option>
          </select>
        }
      >
        <EChart option={option.base} height={340} />
      </Card>

      <Card title="Taxa de discurso de ódio" subtitle="Percentual por período, com escala adaptada ao recorte para evidenciar variações menores.">
        <EChart option={option.rate} height={280} />
      </Card>

      <Card
        title="Participação por tipo"
        subtitle="Percentual de menções de cada tipo de preconceito em cada período, usando a mesma granularidade temporal."
      >
        <EChart option={typeOptions.share} height={380} />
      </Card>

      <Card
        title="Volume por tipo"
        subtitle="Menções por tipo de preconceito em cada período, apresentadas em barras empilhadas."
      >
        <EChart option={typeOptions.volume} height={320} />
      </Card>
    </>
  );
}
