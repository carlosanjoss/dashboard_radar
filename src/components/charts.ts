import type { EChartsOption } from "echarts";
import { CATEGORY_COLORS } from "../../shared/labels.ts";

/* Paleta da identidade: vermelho, azul-escuro, preto e cinzas frios. */
export const PALETTE = [
  "#d92b3f", "#16305e", "#0b0f16", "#2f4a7a", "#8c1c2b",
  "#5b6880", "#e0625a", "#4a6fa5", "#6b7280", "#b01628",
];

export function colorFor(code: string, index = 0): string {
  return CATEGORY_COLORS[code] ?? PALETTE[index % PALETTE.length];
}

// Cores de eixo/grid pensadas para funcionar nos dois temas (claro e escuro),
// sem depender de variáveis CSS dentro do canvas do ECharts.
export const AXIS_LABEL = "#8b95a6";
export const GRID_LINE = "rgba(139, 149, 166, 0.20)";
export const AXIS_LINE = "rgba(139, 149, 166, 0.42)";

const AXIS = {
  axisLine: { lineStyle: { color: AXIS_LINE } },
  axisLabel: { color: AXIS_LABEL, fontSize: 11 },
  splitLine: { lineStyle: { color: GRID_LINE } },
};

export function tooltip(
  extra: Record<string, unknown> = {},
  opts: { suffix?: string; digits?: number; suffixBySeries?: Record<string, string> } = {},
) {
  const digits = opts.digits ?? 2;
  return {
    trigger: "axis" as const,
    axisPointer: { type: "shadow" as const },
    backgroundColor: "rgba(255,255,255,0.98)",
    borderColor: "#e6e8ec",
    textStyle: { color: "#0b0f16", fontSize: 12 },
    // Formatter padrao: sem ele o ECharts imprimia o float cru
    // (ex.: "Taxa de odio 3.6374995661379335").
    formatter: (p: unknown) => {
      const arr = tipParams(p);
      if (!arr.length) return "";
      const body = arr
        .map((it) => {
          const name = String(it.seriesName ?? "");
          const sfx = opts.suffixBySeries?.[name] ?? opts.suffix ?? "";
          return `${name}: <b>${fmtValue(tipNumber(it), digits, sfx)}</b>`;
        })
        .join("<br>");
      return `<b>${tipLabel(arr[0])}</b><br>${body}`;
    },
    ...extra,
  };
}

/* ------------------------------------------------------------------ tooltip
   O ECharts entrega o parâmetro do formatter de formas diferentes conforme o
   trigger: com `trigger: 'axis'` é SEMPRE um array (um item por série); com
   `trigger: 'item'` é um objeto único. Assumir objeto único fazia o tooltip
   imprimir "undefined" e "NaN" nas barras horizontais. Normalize sempre. */

type TipParam = { name?: unknown; seriesName?: unknown; value?: unknown; data?: unknown };

function tipParams(p: unknown): TipParam[] {
  return (Array.isArray(p) ? p : [p]).filter(Boolean) as TipParam[];
}

function tipNumber(item: TipParam): number | null {
  const raw =
    item.value !== undefined && item.value !== null
      ? item.value
      : item.data && typeof item.data === "object"
        ? (item.data as { value?: unknown }).value
        : NaN;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

function fmtValue(n: number | null, digits: number, suffix: string): string {
  if (n === null) return "—";
  return `${n.toLocaleString("pt-BR", { maximumFractionDigits: digits })}${suffix}`;
}

function tipLabel(item: TipParam | undefined): string {
  return String(item?.name ?? item?.seriesName ?? "");
}

/** Barras horizontais (ranking). */
export function hbar(
  rows: Array<{ label: string; value: number; color?: string }>,
  opts: {
    suffix?: string;
    digits?: number;
    height?: number;
    /** Tamanho da fonte do valor ao lado da barra. */
    labelFontSize?: number;
    /** Tamanho da fonte dos rótulos de categoria. */
    nameFontSize?: number;
    /** Espessura máxima da barra. */
    barMaxWidth?: number;
  } = {},
): EChartsOption {
  const suffix = opts.suffix ?? "";
  const digits = opts.digits ?? 0;
  const labelFontSize = opts.labelFontSize ?? 11;
  const nameFontSize = opts.nameFontSize ?? 11;
  const barMaxWidth = opts.barMaxWidth ?? 22;
  const ordered = [...rows].reverse();
  return {
    grid: { left: 8, right: 64, top: 8, bottom: 8, containLabel: true },
    tooltip: tooltip({
      formatter: (p: unknown) =>
        tipParams(p)
          .map((item) => `<b>${tipLabel(item)}</b><br>${fmtValue(tipNumber(item), digits, suffix)}`)
          .join("<br>"),
    }),
    xAxis: { type: "value", ...AXIS, splitLine: { show: false } },
    yAxis: { type: "category", data: ordered.map((r) => r.label), ...AXIS, splitLine: { show: false }, axisLabel: { color: AXIS_LABEL, fontSize: nameFontSize } },
    series: [
      {
        type: "bar",
        data: ordered.map((r, i) => ({
          value: r.value,
          itemStyle: { color: r.color ?? PALETTE[i % PALETTE.length], borderRadius: [0, 5, 5, 0] },
        })),
        label: {
          show: true,
          position: "right",
          fontSize: labelFontSize,
          fontWeight: 600,
          color: "#8b95a6",
          formatter: (p: unknown) => {
            const item = p as { value: number };
            return `${Number(item.value).toLocaleString("pt-BR", { maximumFractionDigits: digits })}${suffix}`;
          },
        },
        barMaxWidth,
      },
    ],
  };
}

/** Barras agrupadas verticais. */
export function vbar(
  categories: string[],
  series: Array<{ name: string; data: number[]; color?: string }>,
  opts: { suffix?: string; stack?: boolean; digits?: number } = {},
): EChartsOption {
  const digits = opts.digits ?? 2;
  const suffix = opts.suffix ?? "";
  return {
    grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
    tooltip: tooltip({
      formatter: (p: unknown) => {
        const arr = tipParams(p);
        if (!arr.length) return "";
        const body = arr
          .map((it) => `${String(it.seriesName ?? "")}: <b>${fmtValue(tipNumber(it), digits, suffix)}</b>`)
          .join("<br>");
        return `<b>${tipLabel(arr[0])}</b><br>${body}`;
      },
    }),
    legend: { top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } },
    xAxis: { type: "category", data: categories, ...AXIS, splitLine: { show: false } },
    yAxis: { type: "value", ...AXIS },
    series: series.map((s, i) => ({
      name: s.name,
      type: "bar" as const,
      stack: opts.stack ? "total" : undefined,
      data: s.data,
      itemStyle: { color: s.color ?? PALETTE[i % PALETTE.length], borderRadius: opts.stack ? 0 : [4, 4, 0, 0] },
      barMaxWidth: 30,
    })),
  };
}

/** Linhas (séries temporais). */
export function lines(
  x: string[],
  series: Array<{ name: string; data: Array<number | null>; color?: string; dashed?: boolean; area?: boolean }>,
  opts: { suffix?: string; yMin?: number; yMax?: number; digits?: number } = {},
): EChartsOption {
  const digits = opts.digits ?? 2;
  const suffix = opts.suffix ?? "";
  return {
    grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
    tooltip: tooltip({
      formatter: (p: unknown) => {
        const arr = tipParams(p);
        if (!arr.length) return "";
        const body = arr
          .map((it) => `${String(it.seriesName ?? "")}: <b>${fmtValue(tipNumber(it), digits, suffix)}</b>`)
          .join("<br>");
        return `<b>${tipLabel(arr[0])}</b><br>${body}`;
      },
    }),
    legend: { top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } },
    xAxis: { type: "category", data: x, ...AXIS, splitLine: { show: false }, boundaryGap: false },
    yAxis: {
      type: "value",
      ...AXIS,
      min: opts.yMin,
      max: opts.yMax,
      axisLabel: { color: AXIS_LABEL, fontSize: 11, formatter: `{value}${opts.suffix ?? ""}` },
    },
    series: series.map((s, i) => ({
      name: s.name,
      type: "line" as const,
      data: s.data,
      smooth: true,
      symbol: "circle",
      symbolSize: 5,
      connectNulls: true,
      lineStyle: { width: 2.2, color: s.color ?? PALETTE[i % PALETTE.length], type: s.dashed ? "dashed" : "solid" },
      itemStyle: { color: s.color ?? PALETTE[i % PALETTE.length] },
      areaStyle: s.area ? { opacity: 0.12 } : undefined,
    })),
  };
}

/** Heatmap (ex.: plataforma × tipo, matriz de interseccionalidade). */
export function heatmap(
  xLabels: string[],
  yLabels: string[],
  data: Array<[number, number, number]>,
  opts: { max?: number; suffix?: string } = {},
): EChartsOption {
  const max = opts.max ?? Math.max(...data.map((d) => d[2]), 1);
  return {
    grid: { left: 8, right: 16, top: 8, bottom: 44, containLabel: true },
    tooltip: {
      position: "top",
      backgroundColor: "rgba(255,255,255,0.97)",
      borderColor: "#e2e8f0",
      textStyle: { color: "#1e293b", fontSize: 12 },
      formatter: (p: unknown) => {
        const d = (tipParams(p)[0] as { data?: [number, number, number] } | undefined)?.data;
        if (!d) return "";
        return `<b>${yLabels[d[1]]}</b> × <b>${xLabels[d[0]]}</b><br>${Number(d[2]).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}${opts.suffix ?? ""}`;
      },
    },
    xAxis: { type: "category", data: xLabels, ...AXIS, splitArea: { show: true }, axisLabel: { color: "#64748b", fontSize: 10, rotate: 30 } },
    yAxis: { type: "category", data: yLabels, ...AXIS, splitArea: { show: true }, axisLabel: { color: "#64748b", fontSize: 10 } },
    visualMap: {
      min: 0,
      max,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      textStyle: { color: "#64748b", fontSize: 11 },
      inRange: { color: ["#eef2ff", "#a5b4fc", "#4f46e5", "#312e81"] },
    },
    series: [
      {
        type: "heatmap",
        data,
        label: { show: false },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,0.25)" } },
      },
    ],
  };
}

/** Grafo de relações com layout circular estático. */
export function graph(
  nodes: Array<{ name: string; category: number; value: number; color?: string }>,
  links: Array<{ source: string; target: string; value: number }>,
  categories: string[],
): EChartsOption {
  return {
    tooltip: {
      backgroundColor: "rgba(255,255,255,0.97)",
      borderColor: "#e2e8f0",
      textStyle: { color: "#1e293b", fontSize: 12 },
      formatter: (p: unknown) => {
        const item = p as { dataType?: string; name?: string; value?: number; data?: { source?: string; target?: string; value?: number } };
        if (item.dataType === "edge") {
          return `<b>${item.data?.source ?? ""} → ${item.data?.target ?? ""}</b><br>${fmtValue(Number(item.data?.value), 0, " ocorrências")}`;
        }
        return `<b>${item.name ?? ""}</b><br>${fmtValue(Number(item.value), 0, " conexões ponderadas")}`;
      },
    },
    legend: [{ data: categories, top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } }],
    series: [
      {
        type: "graph",
        layout: "circular",
        circular: { rotateLabel: false },
        roam: true,
        draggable: false,
        label: { show: true, position: "right", fontSize: 11, color: AXIS_LABEL, formatter: "{b}" },
        lineStyle: { color: "source", opacity: 0.28, curveness: 0.08 },
        emphasis: { focus: "adjacency", label: { show: true, fontWeight: 700 }, lineStyle: { width: 4, opacity: 0.9 } },
        blur: { itemStyle: { opacity: 0.18 }, lineStyle: { opacity: 0.05 }, label: { show: false } },
        categories: categories.map((name, i) => ({ name, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
        data: nodes.map((n) => ({
          name: n.name,
          category: n.category,
          value: n.value,
          itemStyle: n.color ? { color: n.color } : undefined,
          symbolSize: Math.max(8, Math.min(46, 8 + Math.sqrt(n.value))),
        })),
        links: links.map((l) => ({
          source: l.source,
          target: l.target,
          value: l.value,
          lineStyle: { width: Math.max(1, Math.min(6, Math.log2(l.value + 1))) },
        })),
      },
    ],
  };
}

/** Treemap (nuvem de termos sem dependência extra). */
export function treemap(rows: Array<{ name: string; value: number }>): EChartsOption {
  return {
    tooltip: {
      backgroundColor: "rgba(255,255,255,0.97)",
      borderColor: "#e2e8f0",
      textStyle: { color: "#1e293b", fontSize: 12 },
      formatter: (p: unknown) => {
        const item = tipParams(p)[0];
        if (!item) return "";
        return `<b>${tipLabel(item)}</b><br>${fmtValue(tipNumber(item), 0, "")} ocorrências`;
      },
    },
    series: [
      {
        type: "treemap",
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        label: { show: true, formatter: "{b}", fontSize: 12, color: "#fff", overflow: "truncate" },
        upperLabel: { show: false },
        itemStyle: { borderColor: "#fff", borderWidth: 2, gapWidth: 2 },
        levels: [
          {
            itemStyle: { borderWidth: 0, gapWidth: 2 },
          },
        ],
        data: rows.map((r, i) => ({
          name: r.name,
          value: r.value,
          itemStyle: { color: PALETTE[i % PALETTE.length] },
        })),
      },
    ],
  };
}
