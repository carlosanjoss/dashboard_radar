import { useEffect, useState } from "react";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { CategoryProbabilities } from "../components/CategoryProbabilities.tsx";
import { asNumber, fmtDate, fmtInt, fmtPct, fmtProb, type Row } from "../api.ts";
import { hateTypeLabel, platformLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type Data = { rows: Row[]; total: number; page: number; pageSize: number };

export function Comments() {
  const { filters } = useFilters();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [selectedId, setSelectedId] = useState<string | number | null>(null);

  const { data, loading, error } = useApi<Data>("/api/records", filters, { page, pageSize });

  const rows = data?.rows ?? [];
  const total = asNumber(data?.total);
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const selected = rows.find((r) => String(r.analysis_id) === String(selectedId)) ?? null;

  // Ao mudar qualquer filtro volta para a primeira página e fecha o detalhe:
  // manter a página antiga levava a uma tabela vazia e a um registro fora do recorte.
  const filterKey = JSON.stringify(filters);
  useEffect(() => {
    setPage(1);
    setSelectedId(null);
  }, [filterKey]);

  // Se o recorte atual tem menos páginas, não deixa a paginação fora de faixa.
  useEffect(() => {
    if (!loading && page > pages) setPage(pages);
  }, [loading, page, pages]);

  return (
    <>
      <Status loading={loading} error={error} />

      <div className="grid grid-kpi">
        <Kpi label="Registros no recorte" value={fmtInt(total)} />
        <Kpi label="Página" value={`${page} / ${pages}`} hint={`${pageSize} por página`} />
        <Kpi
          label="Modelo"
          value="BERT"
          hint="binário → multilabel quando há ódio"
        />
        <Kpi label="Filtros ativos" value={fmtInt(
          filters.platforms.length + filters.contentKinds.length + filters.predLabels.length + filters.hateTypes.length,
        )} />
      </div>

      <Card
        title="Registros classificados"
        subtitle="Use os filtros globais (topo) para restringir por plataforma, tipo, período ou termo. Clique em uma linha para ver as probabilidades por categoria."
        actions={
          <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }} className="btn" style={{ padding: "6px 10px" }}>
            {[10, 25, 50, 100].map((n) => (
              <option key={n} value={n}>
                {n} / página
              </option>
            ))}
          </select>
        }
      >
        <DataTable
          columns={[
            { key: "analysis_id", label: "ID", numeric: true, render: (r: Row) => fmtInt(r.analysis_id) },
            { key: "platform", label: "Rede", render: (r: Row) => platformLabel(String(r.platform)) },
            { key: "content_kind", label: "Tipo", render: (r: Row) => (r.content_kind === "post" ? "Post" : "Comentário") },
            { key: "pred_label", label: "Classificação", render: (r: Row) => (r.pred_label === "hate" ? "Discurso de ódio" : "Sem ódio") },
            { key: "hate_probability", label: "Prob. ódio", numeric: true, render: (r: Row) => fmtProb(r.hate_probability) },
            {
              key: "hate_types",
              label: "Tipos",
              render: (r: Row) =>
                Array.isArray(r.hate_types) && (r.hate_types as string[]).length
                  ? (r.hate_types as string[]).map(hateTypeLabel).join(", ")
                  : "—",
            },
            { key: "published_at", label: "Publicado", render: (r: Row) => fmtDate(r.published_at) },
            { key: "text_excerpt", label: "Trecho", render: (r: Row) => String(r.text_excerpt ?? "").slice(0, 220) },
            {
              key: "open",
              label: "",
              render: (r: Row) => (
                <button type="button" className="btn" style={{ padding: "3px 10px", fontSize: 12 }} onClick={() => setSelectedId(r.analysis_id as number)}>
                  ver
                </button>
              ),
            },
          ]}
          rows={rows}
          maxHeight={520}
        />

        <div className="pager">
          <button type="button" className="btn" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
            ‹ anterior
          </button>
          <button type="button" className="btn" disabled={page >= pages} onClick={() => setPage((p) => Math.min(pages, p + 1))}>
            próxima ›
          </button>
          <span>
            {fmtInt(total)} registros · página {page} de {pages}
          </span>
        </div>
      </Card>

      {selected && (
        <Card
          title={`Probabilidades por categoria — ID ${String(selected.analysis_id)}`}
          subtitle="Montadas na ordem da hierarquia de tipos, a partir dos scores do modelo multilabel."
          actions={
            <button type="button" className="btn" onClick={() => setSelectedId(null)}>
              fechar
            </button>
          }
        >
          <div className="grid grid-kpi" style={{ marginBottom: 14 }}>
            <Kpi label="Classificação" value={selected.pred_label === "hate" ? "Discurso de ódio" : "Sem ódio"} />
            <Kpi label="Probabilidade de ódio" value={fmtPct(asNumber(selected.hate_probability) * 100)} />
            <Kpi label="Categoria principal" value={hateTypeLabel(String(selected.pred_category ?? "")) || "—"} />
            <Kpi label="Rede / data" value={`${platformLabel(String(selected.platform))} · ${fmtDate(selected.published_at)}`} />
          </div>

          <div className="card" style={{ marginBottom: 14 }}>
            <div className="card-body">
              <div className="kpi-label" style={{ marginBottom: 6 }}>Conteúdo analisado</div>
              <div style={{ fontSize: 14, color: "var(--text)" }}>{String(selected.text_excerpt ?? "(sem texto)")}</div>
            </div>
          </div>

          <CategoryProbabilities scores={selected.category_scores} />
        </Card>
      )}
    </>
  );
}