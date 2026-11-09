import { useEffect, useMemo, useRef, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { CategoryProbabilities } from "../components/CategoryProbabilities.tsx";
import { hbar, tooltip } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { hateTypeLabel, platformColor, platformLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type Data = { posts: Row[] };

export function Posts() {
  const { filters } = useFilters();
  const [minRecords, setMinRecords] = useState(3);
  const [selected, setSelected] = useState<string | null>(null);
  const detailRef = useRef<HTMLDivElement | null>(null);
  const { data, loading, error } = useApi<Data>("/api/posts", filters, { limit: 200, minRecords });
  const detail = useApi<Row[]>("/api/records/post/" + encodeURIComponent(selected ?? "_"), filters, { pageSize: 50 }, Boolean(selected));

  // Fecha o detalhe quando o recorte muda — a thread aberta pode sair do filtro.
  const filterKey = JSON.stringify([filters, minRecords]);
  useEffect(() => {
    setSelected(null);
  }, [filterKey]);

  // O detalhe fica depois da tabela; trazê-lo para a viewport torna explícito
  // que o botão abriu o post e evita a impressão de que nada aconteceu.
  useEffect(() => {
    if (!selected) return;
    const frame = window.requestAnimationFrame(() =>
      detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );
    return () => window.cancelAnimationFrame(frame);
  }, [selected]);

  const posts = data?.posts ?? [];

  const option = useMemo(
    () =>
      hbar(
        posts.slice(0, 20).map((r) => ({
          label: `${platformLabel(String(r.platform))} · ${String(r.post_title ?? "").slice(0, 42)}`,
          value: asNumber(r.total_hate),
        })),
      ),
    [posts],
  );

  const scatter = useMemo(
    () => {
      const platforms = Array.from(new Set(posts.map((r) => String(r.platform))));
      return {
      grid: { left: 8, right: 20, top: 52, bottom: 12, containLabel: true },
      tooltip: tooltip({
        formatter: (p: unknown) => {
          const item = p as { data: [number, number, string, number] };
          return `<b>${item.data[2]}</b><br>registros: ${item.data[0].toLocaleString("pt-BR")}<br>com ódio: ${item.data[3].toLocaleString("pt-BR")}<br>prevalência: ${item.data[1].toFixed(2)}%`;
        },
      }),
      legend: { top: 0, type: "scroll" as const, textStyle: { color: "#8b95a6", fontSize: 11 } },
      xAxis: { type: "log" as const, name: "total de registros (escala log)", nameTextStyle: { fontSize: 10 }, axisLabel: { color: "#8b95a6", fontSize: 10 }, splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } } },
      yAxis: { type: "value" as const, name: "prevalência de ódio", nameTextStyle: { fontSize: 10 }, min: 0, max: 100, axisLabel: { color: "#8b95a6", fontSize: 10, formatter: "{value}%" }, splitLine: { lineStyle: { color: "rgba(139, 149, 166, 0.20)" } } },
      series: platforms.map((platform) => ({
          name: platformLabel(platform),
          type: "scatter" as const,
          symbolSize: (d: number[]) => Math.max(10, Math.min(42, 8 + Math.sqrt(d[3]) * 2)),
          data: posts
            .filter((r) => String(r.platform) === platform)
            .map((r) => [asNumber(r.total_records), asNumber(r.hate_percent), String(r.post_title ?? "").slice(0, 90), asNumber(r.total_hate)]),
          itemStyle: { color: platformColor(platform), opacity: 0.78 },
          emphasis: { focus: "series" as const, scale: 1.35 },
        })),
      };
    },
    [posts],
  );

  const selectedPost = posts.find((p) => String(p.post_id) === selected);

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !posts.length} />

      <div className="grid grid-kpi">
        <Kpi label="Posts" value={fmtInt(posts.length)} hint={`≥ ${minRecords} registros`} />
        <Kpi label="Registros" value={fmtInt(posts.reduce((acc, r) => acc + asNumber(r.total_records), 0))} />
        <Kpi label="Discurso de ódio" value={fmtInt(posts.reduce((acc, r) => acc + asNumber(r.total_hate), 0))} />
        <Kpi label="Comentários" value={fmtInt(posts.reduce((acc, r) => acc + asNumber(r.total_comments), 0))} />
      </div>

      <div className="grid grid-2">
        <Card
          title="Posts com mais ódio"
          subtitle="Ranking por volume absoluto de registros com discurso de ódio."
          actions={
            <select value={minRecords} onChange={(e) => setMinRecords(Number(e.target.value))} className="btn" style={{ padding: "6px 10px" }}>
              {[1, 2, 3, 5, 10].map((n) => (
                <option key={n} value={n}>
                  ≥ {n} registros
                </option>
              ))}
            </select>
          }
        >
          <EChart option={option} height={460} />
        </Card>
        <Card title="Volume × prevalência por post" subtitle="Cada bolha é um post: posição horizontal = volume total, altura = prevalência, tamanho = registros com ódio e cor = plataforma.">
          <EChart option={scatter} height={460} />
        </Card>
      </div>

      <Card title="Posts" subtitle="Clique em abrir para ver os registros e as probabilidades por categoria.">
        <DataTable
          columns={[
            { key: "platform", label: "Rede", render: (r: Row) => platformLabel(String(r.platform)) },
            { key: "post_title", label: "Post", render: (r: Row) => String(r.post_title ?? "").slice(0, 120) },
            { key: "total_records", label: "Registros", numeric: true, render: (r: Row) => fmtInt(r.total_records) },
            { key: "total_hate", label: "Ódio", numeric: true, render: (r: Row) => fmtInt(r.total_hate) },
            { key: "hate_percent", label: "Taxa", numeric: true, render: (r: Row) => fmtPct(r.hate_percent) },
            { key: "total_comments", label: "Coment.", numeric: true, render: (r: Row) => fmtInt(r.total_comments) },
            { key: "avg_hate_probability", label: "Prob. média", numeric: true, render: (r: Row) => asNumber(r.avg_hate_probability).toFixed(3) },
            {
              key: "open",
              label: "",
              render: (r: Row) => (
                <button type="button" className="btn" style={{ padding: "3px 10px", fontSize: 12 }} onClick={() => setSelected(String(r.post_id))}>
                  abrir
                </button>
              ),
            },
          ]}
          rows={posts}
          maxHeight={520}
        />
      </Card>

      {selected && (
        <div ref={detailRef}>
          <Card
            title={`Registros do post — ${String(selectedPost?.post_title ?? selected).slice(0, 80)}`}
            subtitle="Conteúdos classificados associados ao post selecionado."
            actions={
              <button type="button" className="btn" onClick={() => setSelected(null)}>
                fechar
              </button>
            }
          >
            <Status loading={detail.loading} error={detail.error} empty={!detail.loading && !(detail.data ?? []).length} />
            {(detail.data ?? []).length > 0 && (
              <>
                <DataTable
                  columns={[
                    { key: "platform", label: "Rede", render: (r: Row) => platformLabel(String(r.platform)) },
                    { key: "content_kind", label: "Tipo", render: (r: Row) => String(r.content_kind) },
                    { key: "pred_label", label: "Classificação", render: (r: Row) => (r.pred_label === "hate" ? "Discurso de ódio" : "Sem ódio") },
                    { key: "hate_probability", label: "Prob.", numeric: true, render: (r: Row) => asNumber(r.hate_probability).toFixed(3) },
                    {
                      key: "hate_types",
                      label: "Tipos",
                      render: (r: Row) => (Array.isArray(r.hate_types) ? (r.hate_types as string[]).map(hateTypeLabel).join(", ") : "—"),
                    },
                    { key: "text_excerpt", label: "Trecho", render: (r: Row) => String(r.text_excerpt ?? "").slice(0, 300) },
                  ]}
                  rows={detail.data ?? []}
                  maxHeight={340}
                />
                <div style={{ marginTop: 18 }}>
                  <h3 className="card-title" style={{ fontSize: 14, marginBottom: 8 }}>
                    Probabilidades por categoria (primeiro registro do recorte)
                  </h3>
                  <CategoryProbabilities scores={(detail.data ?? [])[0]?.category_scores} />
                </div>
              </>
            )}
          </Card>
        </div>
      )}
    </>
  );
}
