import { useMemo, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { hbar, PALETTE, tooltip } from "../components/charts.ts";
import { asNumber, fmtDate, fmtInt, fmtPct, type Row } from "../api.ts";
import { hateTypeLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type Data = { authors: Row[]; authorTypes: Array<{ author_hash: string; hate_type: string; total: number }> };

export function Authors() {
  const { filters } = useFilters();
  const [minRecords, setMinRecords] = useState(5);
  const { data, loading, error } = useApi<Data>("/api/authors", filters, { limit: 200, minRecords });

  const authors = data?.authors ?? [];

  const option = useMemo(
    () =>
      hbar(
        authors.slice(0, 20).map((r, i) => ({
          label: `perfil ${String(r.author_hash).slice(0, 6)}`,
          value: asNumber(r.total_hate),
          color: PALETTE[i % PALETTE.length],
        })),
      ),
    [authors],
  );

  const typeOptions = useMemo(() => {
    const top = authors.slice(0, 8).map((a) => String(a.author_hash));
    const types = Array.from(new Set((data?.authorTypes ?? []).map((t) => t.hate_type)));
    const series = types.map((type, i) => ({
      name: hateTypeLabel(type),
      color: PALETTE[i % PALETTE.length],
      data: top.map((hash) => (data?.authorTypes ?? []).find((t) => t.author_hash === hash && t.hate_type === type)?.total ?? 0),
    }));
    return {
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
      tooltip: tooltip(),
      legend: { top: 0, textStyle: { color: "#8b95a6", fontSize: 11 } },
      xAxis: { type: "category" as const, data: top.map((h) => h.slice(0, 6)), axisLabel: { color: "#8b95a6", fontSize: 10 } },
      yAxis: { type: "value" as const, axisLabel: { color: "#8b95a6", fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } } },
      series: series.map((s) => ({ name: s.name, type: "bar" as const, stack: "t", data: s.data, itemStyle: { color: s.color }, barMaxWidth: 26 })),
    };
  }, [authors, data]);

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !authors.length} />

      <div className="grid grid-kpi">
        <Kpi label="Perfis listados" value={fmtInt(authors.length)} hint={`mínimo de ${minRecords} registros`} />
        <Kpi label="Hate dos perfis" value={fmtInt(authors.reduce((acc, r) => acc + asNumber(r.total_hate), 0))} />
        <Kpi
          label="Perfil mais ativo"
          value={authors.length ? `perfil ${String(authors[0].author_hash).slice(0, 6)}` : "—"}
          hint={authors.length ? `${fmtInt(authors[0].total_hate)} conteúdos de ódio` : undefined}
        />
        <Kpi label="Filtro mínimo" value={`${minRecords} reg.`} />
      </div>

      <Card
        title="Perfis com mais discurso de ódio"
        subtitle="Autores anonimizados (hash). Perfis ficam identificados apenas por hash para preservar privacidade."
        actions={
          <select
            value={minRecords}
            onChange={(e) => setMinRecords(Number(e.target.value))}
            className="btn"
            style={{ padding: "6px 10px" }}
          >
            {[2, 3, 5, 10, 20].map((n) => (
              <option key={n} value={n}>
                ≥ {n} registros
              </option>
            ))}
          </select>
        }
      >
        <EChart option={option} height={420} />
      </Card>

      <Card title="Tipos por perfil (top 8)" subtitle="Composição das tipologias entre os perfis mais ativos.">
        <EChart option={typeOptions} height={340} />
      </Card>

      <Card title="Tabela de perfis" subtitle="Métricas completas por autor anonimizado.">
        <DataTable
          columns={[
            { key: "author_hash", label: "Perfil", render: (r: Row) => <code>{String(r.author_hash).slice(0, 12)}</code> },
            { key: "total_content", label: "Conteúdos", numeric: true, render: (r: Row) => fmtInt(r.total_content) },
            { key: "total_hate", label: "Ódio", numeric: true, render: (r: Row) => fmtInt(r.total_hate) },
            { key: "hate_percent", label: "Taxa", numeric: true, render: (r: Row) => fmtPct(r.hate_percent) },
            { key: "total_platforms", label: "Redes", numeric: true, render: (r: Row) => fmtInt(r.total_platforms) },
            { key: "total_posts", label: "Posts", numeric: true, render: (r: Row) => fmtInt(r.total_posts) },
            { key: "total_comments", label: "Coment.", numeric: true, render: (r: Row) => fmtInt(r.total_comments) },
            { key: "avg_hate_probability", label: "Prob. média", numeric: true, render: (r: Row) => asNumber(r.avg_hate_probability).toFixed(3) },
            { key: "first_seen", label: "1º registro", render: (r: Row) => fmtDate(r.first_seen) },
          ]}
          rows={authors}
          maxHeight={520}
        />
      </Card>
    </>
  );
}