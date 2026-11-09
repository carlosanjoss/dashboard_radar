import { useMemo } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { lines, vbar } from "../components/charts.ts";
import { asNumber, fmtInt, type Row } from "../api.ts";
import { useFilters } from "../filters.tsx";

type Bucket = { bucket: number; n: number };
type Point = { threshold: number; n: number };
type Cut = { n_hate: number; n_not_hate: number; min_hate: number | null; max_not_hate: number | null };
type Data = { buckets: Bucket[]; curve: Point[]; cut: Cut | null };

function dec(value: unknown, digits = 2): string {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(digits).replace(".", ",");
}

function bucketLabel(bucket: number): string {
  return `${dec((bucket - 1) / 10, 1)}–${dec(bucket / 10, 1)}`;
}

export function Threshold() {
  const { filters } = useFilters();
  const { data, loading, error } = useApi<Data>("/api/threshold", filters);

  const buckets = data?.buckets ?? [];
  const curve = data?.curve ?? [];
  const cut = data?.cut ?? null;

  const nHate = asNumber(cut?.n_hate);
  const at = (t: number) => curve.find((p) => Math.abs(Number(p.threshold) - t) < 0.001)?.n ?? 0;
  const n50 = at(0.5);
  const n40 = at(0.4);

  const curveOption = useMemo(
    () =>
      lines(
        curve.map((p) => dec(p.threshold)),
        [
          {
            name: "Seria classificado como ódio",
            data: curve.map((p) => asNumber(p.n)),
            color: "#d92b3f",
            area: true,
          },
        ],
        { suffix: "" },
      ),
    [curve],
  );

  const histOption = useMemo(
    () =>
      vbar(
        buckets.map((b) => bucketLabel(asNumber(b.bucket))),
        [{ name: "Registros", data: buckets.map((b) => asNumber(b.n)), color: "#16305e" }],
      ),
    [buckets],
  );

  const tableRows = useMemo(
    () =>
      curve.map((p) => ({
        threshold: Number(p.threshold),
        n: asNumber(p.n),
        delta: asNumber(p.n) - nHate,
      })),
    [curve, nHate],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !curve.length} />

      <div className="grid grid-kpi">
        <Kpi
          label="Fronteira do modelo"
          value={dec(cut?.min_hate)}
          hint={`Nenhum ódio abaixo · nenhum não-ódio acima (${dec(cut?.max_not_hate)})`}
        />
        <Kpi
          label="Ódio hoje (rótulo do modelo)"
          value={fmtInt(nHate)}
          hint="Número que o resto do painel usa"
        />
        <Kpi
          label="Se o corte fosse 0,50"
          value={fmtInt(n50)}
          hint={`+${fmtInt(n50 - nHate)} registros entrariam`}
        />
        <Kpi
          label="Se o corte fosse 0,40"
          value={fmtInt(n40)}
          hint={`+${fmtInt(n40 - nHate)} registros entrariam`}
        />
      </div>

      <Card
        title="Sensibilidade ao limiar"
        subtitle="Quantos registros entrariam como ódio para cada corte aplicado sobre hate_probability. O rótulo atual do modelo não sai de um corte em 0,50 — a fronteira observada está em 0,64."
      >
        <EChart option={curveOption} height={320} />
      </Card>

      <Card
        title="Distribuição da probabilidade"
        subtitle="A grande maioria do corpus fica abaixo de 0,10. A decisão do modelo ocorre bem à direita da distribuição."
      >
        <EChart option={histOption} height={320} />
      </Card>

      <Card
        title="Efeito de cada corte"
        subtitle="Comparação de cada limiar com o rótulo atual do modelo. Diferença positiva = quantos registros passariam a ser contados como ódio."
      >
        <DataTable
          columns={[
            {
              key: "threshold",
              label: "Corte em hate_probability",
              numeric: true,
              render: (r: Row) => dec(r.threshold),
            },
            { key: "n", label: "Seria ódio", numeric: true, render: (r: Row) => fmtInt(r.n) },
            {
              key: "delta",
              label: "Diferença vs rótulo",
              numeric: true,
              render: (r: Row) => {
                const d = asNumber(r.delta);
                if (d === 0) return "—";
                return `${d > 0 ? "+" : "−"}${fmtInt(Math.abs(d))}`;
              },
            },
          ]}
          rows={tableRows as unknown as Row[]}
          maxHeight={460}
        />
      </Card>
    </>
  );
}
