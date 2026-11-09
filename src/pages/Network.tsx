import { useMemo, useState } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { colorFor, graph } from "../components/charts.ts";
import { fmtInt } from "../api.ts";
import { hateTypeLabel, platformColor, platformLabel } from "../../shared/labels.ts";
import { useFilters } from "../filters.tsx";

type Data = { edges: Array<{ source: string; target: string; relation: string; total: number }> };

const RELATION_LABELS: Record<string, string> = {
  rede_tipo: "Rede × tipo",
  conteudo_tipo: "Conteúdo × tipo",
  coocorrencia: "Coocorrência de tipos",
};

export function Network() {
  const { filters, showPoliticalCharts } = useFilters();
  const [minWeight, setMinWeight] = useState(5);
  const [relation, setRelation] = useState("rede_tipo");
  const { data, loading, error } = useApi<Data>("/api/network", filters, { limit: 300, minWeight });

  const edges = (data?.edges ?? []).filter(
    (edge) => showPoliticalCharts || (edge.source !== "tipo:political" && edge.target !== "tipo:political"),
  );
  const visibleEdges = useMemo(
    () => (relation === "all" ? edges : edges.filter((edge) => edge.relation === relation)),
    [edges, relation],
  );

  const option = useMemo(() => {
    const nodeMap = new Map<string, { name: string; category: number; value: number; color?: string }>();
    const links: Array<{ source: string; target: string; value: number }> = [];

    const pretty = (name: string): { label: string; category: number; color?: string } => {
      const [kind, raw] = name.split(":");
      if (kind === "rede") return { label: platformLabel(raw), category: 1, color: platformColor(raw) };
      if (kind === "tipo") return { label: hateTypeLabel(raw), category: 0, color: colorFor(raw) };
      if (kind === "conteudo") return { label: raw === "post" ? "Post" : "Comentário", category: 2, color: raw === "post" ? "#16305e" : "#d92b3f" };
      return { label: raw, category: 3 };
    };

    for (const edge of visibleEdges) {
      const source = pretty(edge.source);
      const target = pretty(edge.target);
      for (const node of [source, target]) {
        const current = nodeMap.get(node.label);
        nodeMap.set(node.label, {
          name: node.label,
          // A categoria vem do prefixo do nó (nunca da posição na aresta), senão o
          // mesmo nó troca de cor conforme a última aresta processada.
          category: node.category,
          color: node.color,
          value: (current?.value ?? 0) + edge.total,
        });
      }
      links.push({ source: source.label, target: target.label, value: edge.total });
    }

    return graph(Array.from(nodeMap.values()), links, [
      "Tipos de preconceito",
      "Plataformas",
      "Tipo de conteúdo",
    ]);
  }, [visibleEdges]);

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !visibleEdges.length} />

      <div className="grid grid-kpi">
        <Kpi label="Arestas" value={fmtInt(edges.length)} hint={`peso mínimo ${minWeight}`} />
        <Kpi label="Relações rede × tipo" value={fmtInt(edges.filter((e) => e.relation === "rede_tipo").length)} />
        <Kpi label="Relações conteúdo × tipo" value={fmtInt(edges.filter((e) => e.relation === "conteudo_tipo").length)} />
        <Kpi label="Coocorrências" value={fmtInt(edges.filter((e) => e.relation === "coocorrencia").length)} />
      </div>

      <Card
        title="Rede de relações"
        subtitle="Layout estático para facilitar a leitura. Passe o mouse para isolar vizinhos e use a roda para ampliar."
        actions={
          <div className="chart-controls">
            <select value={relation} onChange={(e) => setRelation(e.target.value)} className="btn" aria-label="Tipo de relação">
              <option value="rede_tipo">Rede × tipo</option>
              <option value="conteudo_tipo">Conteúdo × tipo</option>
              <option value="coocorrencia">Coocorrência de tipos</option>
              <option value="all">Todas as relações</option>
            </select>
            <select value={minWeight} onChange={(e) => setMinWeight(Number(e.target.value))} className="btn" aria-label="Peso mínimo">
              {[1, 3, 5, 10, 25, 50].map((n) => (
                <option key={n} value={n}>
                  peso ≥ {n}
                </option>
              ))}
            </select>
          </div>
        }
      >
        <EChart option={option} height={560} />
      </Card>

      <Card title="Arestas mais fortes" subtitle="Pares de nós com maior frequência conjunta.">
        <DataTable
          columns={[
            { key: "source", label: "Origem", render: (r) => String(r.source).replace(/^\w+:/, "") },
            { key: "target", label: "Destino", render: (r) => String(r.target).replace(/^\w+:/, "") },
            { key: "relation", label: "Relação", render: (r) => RELATION_LABELS[String(r.relation)] ?? String(r.relation) },
            { key: "total", label: "Peso", numeric: true, render: (r) => fmtInt(r.total) },
          ]}
          rows={visibleEdges.slice(0, 100) as unknown as Record<string, unknown>[]}
          maxHeight={420}
        />
      </Card>
    </>
  );
}
