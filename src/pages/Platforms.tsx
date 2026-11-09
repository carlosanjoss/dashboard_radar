import { useMemo } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { hbar } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, wilson, type Row } from "../api.ts";
import { platformColor, platformLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type PlatformData = {
  platforms: Row[];
  kinds: Row[];
};

export function Platforms() {
  const { filters } = useFilters();
  const { data, loading, error } = useApi<PlatformData>("/api/platforms", filters);

  const rows = data?.platforms ?? [];

  const withCi = useMemo<Row[]>(
    () =>
      rows.map((r) => {
        const total = asNumber(r.total_content);
        const hate = asNumber(r.total_hate);
        const ci = wilson(hate, total);
        return { ...r, ci_low: ci.low, ci_high: ci.high };
      }),
    [rows],
  );

  const options = useMemo(
    () => ({
      hate: hbar(
        withCi.map((r) => ({
          label: platformLabel(String(r.platform)),
          value: asNumber(r.hate_percent),
          color: platformColor(String(r.platform)),
        })),
        { suffix: "%", digits: 2 },
      ),
      volume: hbar(
        withCi.map((r) => ({
          label: platformLabel(String(r.platform)),
          value: asNumber(r.total_content),
          color: platformColor(String(r.platform)),
        })),
      ),
      scatter: {
        grid: { left: 8, right: 20, top: 24, bottom: 8, containLabel: true },
        tooltip: {
          backgroundColor: "rgba(255,255,255,0.97)",
          borderColor: "#e2e8f0",
          textStyle: { color: "#1e293b", fontSize: 12 },
          formatter: (p: unknown) => {
            const item = p as { data: [number, number, string, number, number, string] };
            return `<b>${item.data[2]}</b><br>conteúdos: ${item.data[0].toLocaleString("pt-BR")}<br>taxa: ${item.data[1].toFixed(2)}%<br>IC95%: ${item.data[3].toFixed(1)}%–${item.data[4].toFixed(1)}%`;
          },
        },
        xAxis: {
          type: "log" as const,
          name: "conteúdos (log)",
          nameTextStyle: { fontSize: 10 },
          axisLabel: { color: "#8b95a6", fontSize: 10 },
          splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } },
        },
        yAxis: {
          type: "value" as const,
          name: "% ódio",
          nameTextStyle: { fontSize: 10 },
          max: 100,
          axisLabel: { color: "#8b95a6", fontSize: 10, formatter: "{value}%" },
          splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } },
        },
        series: [
          {
            type: "scatter" as const,
            symbolSize: (d: number[]) => Math.max(14, Math.min(52, Math.sqrt(d[0]) / 3)),
            data: withCi.map((r) => [
              asNumber(r.total_content),
              asNumber(r.hate_percent),
              platformLabel(String(r.platform)),
              r.ci_low,
              r.ci_high,
              String(r.platform),
            ]),
            itemStyle: { color: (p: { data: Array<number | string> }) => platformColor(String(p.data[5])), opacity: 0.85 },
            label: {
              show: true,
              formatter: (p: { data: unknown[] }) => String(p.data[2]),
              position: "top",
              fontSize: 11,
              color: "#334155",
            },
          },
        ],
      },
    }),
    [withCi],
  );

  const columns = [
    { key: "platform", label: "Plataforma", render: (r: Row) => <b>{platformLabel(String(r.platform))}</b> },
    { key: "total_content", label: "Conteúdos", numeric: true, render: (r: Row) => fmtInt(r.total_content) },
    { key: "total_hate", label: "Ódio", numeric: true, render: (r: Row) => fmtInt(r.total_hate) },
    { key: "hate_percent", label: "Taxa", numeric: true, render: (r: Row) => fmtPct(r.hate_percent) },
    {
      key: "ci",
      label: "IC 95% (Wilson)",
      numeric: true,
      render: (r: Row) => `${fmtPct(r.ci_low, 1)} – ${fmtPct(r.ci_high, 1)}`,
    },
    { key: "avg_hate_probability", label: "Prob. média", numeric: true, render: (r: Row) => asNumber(r.avg_hate_probability).toFixed(3) },
    { key: "total_authors", label: "Autores", numeric: true, render: (r: Row) => fmtInt(r.total_authors) },
  ];

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !rows.length} />

      <div className="grid grid-kpi">
        <Kpi label="Plataformas" value={fmtInt(rows.length)} />
        <Kpi label="Conteúdos" value={fmtInt(rows.reduce((acc, r) => acc + asNumber(r.total_content), 0))} />
        <Kpi label="Discurso de ódio" value={fmtInt(rows.reduce((acc, r) => acc + asNumber(r.total_hate), 0))} />
        <Kpi
          label="Maior taxa"
          value={
            rows.length
              ? `${platformLabel(String([...rows].sort((a, b) => asNumber(b.hate_percent) - asNumber(a.hate_percent))[0].platform))} · ${fmtPct(
                  [...rows].sort((a, b) => asNumber(b.hate_percent) - asNumber(a.hate_percent))[0].hate_percent,
                )}`
              : "—"
          }
        />
      </div>

      <Card
        title="Comparação entre plataformas"
        subtitle="Taxa de discurso de ódio por plataforma, com intervalo de confiança de 95% (Wilson) para dar conta de amostras pequenas."
      >
        <EChart option={options.hate} height={300} />
      </Card>

      <div className="grid grid-2">
        <Card title="Volume vs. prevalência" subtitle="Tamanho = volume; eixo X em escala log. Plataformas com pouca amostra aparecem mais instáveis.">
          <EChart option={options.scatter} height={340} />
        </Card>
        <Card title="Volume por plataforma" subtitle="Total de conteúdos classificados no período.">
          <EChart option={options.volume} height={340} />
        </Card>
      </div>

      <Card title="Detalhe por plataforma" subtitle="Métricas e incerteza por rede.">
        <DataTable columns={columns} rows={withCi} />
      </Card>

      <Card title="Por tipo de conteúdo" subtitle="Posts vs. comentários.">
        <DataTable
          columns={[
            { key: "content_kind", label: "Tipo", render: (r: Row) => String(r.content_kind) },
            { key: "total_content", label: "Conteúdos", numeric: true, render: (r: Row) => fmtInt(r.total_content) },
            { key: "total_hate", label: "Ódio", numeric: true, render: (r: Row) => fmtInt(r.total_hate) },
            { key: "hate_percent", label: "Taxa", numeric: true, render: (r: Row) => fmtPct(r.hate_percent) },
          ]}
          rows={data?.kinds ?? []}
          maxHeight={260}
        />
      </Card>
    </>
  );
}
