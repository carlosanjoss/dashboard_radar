import { useMemo, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { hbar, heatmap } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { CATEGORY_HIERARCHY, hateTypeLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type Data = { rows: Row[] };

export function Intersectionality() {
  const { filters } = useFilters();
  const [minCooccurrences, setMinCooccurrences] = useState(10);
  const { data, loading, error } = useApi<Data>("/api/intersectionality", filters);

  const rows = data?.rows ?? [];

  const pairs = useMemo(
    () =>
      rows
        .filter(
          (r) =>
            String(r.hate_type_a) < String(r.hate_type_b) &&
            asNumber(r.total_cooccurrences) >= minCooccurrences,
        )
        .sort((a, b) => asNumber(b.total_cooccurrences) - asNumber(a.total_cooccurrences)),
    [rows, minCooccurrences],
  );

  const present = useMemo(() => {
    const set = new Set<string>();
    for (const r of pairs) {
      set.add(String(r.hate_type_a));
      set.add(String(r.hate_type_b));
    }
    return CATEGORY_HIERARCHY.filter((c) => set.has(c));
  }, [pairs]);

  const matrix = useMemo(() => {
    const index = new Map<string, Row>();
    for (const r of rows) index.set(`${r.hate_type_a}|${r.hate_type_b}`, r);
    const cells: Array<[number, number, number]> = [];
    present.forEach((a, y) => {
      present.forEach((b, x) => {
        const row = index.get(`${a}|${b}`) ?? index.get(`${b}|${a}`);
        const allowed = a === b || (row && asNumber(row.total_cooccurrences) >= minCooccurrences);
        cells.push([x, y, allowed && row ? asNumber(row.overlap_percentage) : 0]);
      });
    });
    return heatmap(present.map(hateTypeLabel), present.map(hateTypeLabel), cells, { max: 100, suffix: "%" });
  }, [rows, present, minCooccurrences]);

  const pairsOption = useMemo(
    () =>
      hbar(
        pairs.slice(0, 12).map((r) => ({
          label: `${hateTypeLabel(String(r.hate_type_a))} + ${hateTypeLabel(String(r.hate_type_b))}`,
          value: asNumber(r.total_cooccurrences),
        })),
      ),
    [pairs],
  );

  const strongest = useMemo(
    () => [...pairs].sort((a, b) => asNumber(b.overlap_percentage) - asNumber(a.overlap_percentage))[0],
    [pairs],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !pairs.length} />

      <div className="grid grid-kpi">
        <Kpi label="Tipos com coocorrência" value={fmtInt(present.length)} />
        <Kpi label="Pares com coocorrência" value={fmtInt(pairs.length)} />
        <Kpi label="Coocorrências" value={fmtInt(pairs.reduce((acc, r) => acc + asNumber(r.total_cooccurrences), 0))} />
        <Kpi
          label="Sobreposição mais forte"
          value={
            strongest
              ? `${hateTypeLabel(String(strongest.hate_type_a))} + ${hateTypeLabel(String(strongest.hate_type_b))}`
              : "—"
          }
          hint={strongest ? fmtPct(strongest.overlap_percentage) : undefined}
        />
      </div>

      <Card
        title="Matriz de sobreposição"
        subtitle={`Percentual de sobreposição entre pares com pelo menos ${minCooccurrences} coocorrências. Diagonal = 100%.`}
        actions={
          <label className="number-control">
            mínimo
            <input
              type="number"
              min={0}
              step={1}
              value={minCooccurrences}
              onChange={(e) => setMinCooccurrences(Math.max(0, Math.trunc(Number(e.target.value) || 0)))}
              aria-label="Mínimo de coocorrências"
            />
          </label>
        }
      >
        <EChart option={matrix} height={420} />
      </Card>

      <Card title="Pares que mais coocorrem" subtitle="Volume absoluto de conteúdos com ambos os tipos.">
        <EChart option={pairsOption} height={340} />
      </Card>

      <Card title="Detalhe dos pares" subtitle="Coocorrências, contagens individuais e sobreposição relativa.">
        <DataTable
          columns={[
            { key: "a", label: "Tipo A", render: (r: Row) => hateTypeLabel(String(r.hate_type_a)) },
            { key: "b", label: "Tipo B", render: (r: Row) => hateTypeLabel(String(r.hate_type_b)) },
            { key: "total_cooccurrences", label: "Juntos", numeric: true, render: (r: Row) => fmtInt(r.total_cooccurrences) },
            { key: "count_a", label: "Só A", numeric: true, render: (r: Row) => fmtInt(r.count_a) },
            { key: "count_b", label: "Só B", numeric: true, render: (r: Row) => fmtInt(r.count_b) },
            {
              key: "overlap_percentage",
              label: "Sobreposição",
              numeric: true,
              render: (r: Row) => fmtPct(r.overlap_percentage),
            },
          ]}
          rows={pairs}
          maxHeight={420}
        />
      </Card>
    </>
  );
}
