import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import type { EChartsOption } from "echarts";
import { BarChart, GraphChart, HeatmapChart, LineChart, ScatterChart, TreemapChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

// Registro explícito (tree-shaking): só os gráficos/componentes usados entram no bundle.
echarts.use([
  BarChart,
  LineChart,
  ScatterChart,
  HeatmapChart,
  GraphChart,
  TreemapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
  CanvasRenderer,
]);

type Props = {
  /** Option do ECharts (tipagem aberta para aceitar builders e objetos literais). */
  option: unknown;
  height?: number;
  /** Reaplica o option completo (default true). */
  notMerge?: boolean;
};

/**
 * Wrapper responsivo do ECharts: redimensiona junto com o container
 * (ResizeObserver) — é o que garante a responsividade dos gráficos.
 */
export function EChart({ option, height = 320, notMerge = true }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);
  const chart = useRef<ReturnType<typeof echarts.init> | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const instance = echarts.init(ref.current, undefined, { renderer: "canvas" });
    chart.current = instance;
    const observer = new ResizeObserver(() => instance.resize());
    observer.observe(ref.current);
    return () => {
      observer.disconnect();
      instance.dispose();
      chart.current = null;
    };
  }, []);

  useEffect(() => {
    chart.current?.setOption(option as EChartsOption, notMerge);
  }, [option, notMerge]);

  return <div ref={ref} className="chart" style={{ height }} />;
}