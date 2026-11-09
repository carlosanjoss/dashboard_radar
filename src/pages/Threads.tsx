import { useMemo } from "react";
import { EChart } from "../components/EChart.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { vbar } from "../components/charts.ts";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { useFilters } from "../filters.tsx";

type Split = { content_kind: string; is_reply: boolean; n: number; hate: number };
type Size = { faixa: string; ordem: number; threads: number; comentarios: number; odiosos: number };
type Top = {
  root_post_id: number;
  root_post_key: string;
  comments: number;
  hate: number;
  autores: number;
  pct: number;
  root_title: string;
  root_text: string;
};
type Data = { split: Split[]; sizes: Size[]; top: Top[] };

function rate(hate: unknown, n: unknown): number {
  const total = asNumber(n);
  return total > 0 ? (100 * asNumber(hate)) / total : 0;
}

export function Threads() {
  const { filters } = useFilters();
  const { data, loading, error } = useApi<Data>("/api/threads", filters);

  const split = data?.split ?? [];
  const sizes = data?.sizes ?? [];
  const top = data?.top ?? [];

  const reply = split.find((r) => r.content_kind === "comment" && r.is_reply === true);
  const root = split.find((r) => r.content_kind === "comment" && r.is_reply === false);
  const posts = split.find((r) => r.content_kind === "post");

  const replyRate = rate(reply?.hate, reply?.n);
  const rootRate = rate(root?.hate, root?.n);
  const factor = rootRate > 0 ? replyRate / rootRate : 0;

  const threads = useMemo(() => sizes.reduce((acc, s) => acc + asNumber(s.threads), 0), [sizes]);

  const sizesOption = useMemo(
    () =>
      vbar(
        sizes.map((s) => String(s.faixa)),
        [
          {
            name: "Taxa de ódio",
            data: sizes.map((s) => Number(rate(s.odiosos, s.comentarios).toFixed(2))),
            color: "#d92b3f",
          },
        ],
        { suffix: "%" },
      ),
    [sizes],
  );

  const volumeOption = useMemo(
    () =>
      vbar(
        sizes.map((s) => String(s.faixa)),
        [
          { name: "Comentários", data: sizes.map((s) => asNumber(s.comentarios)), color: "#16305e" },
          { name: "Com ódio", data: sizes.map((s) => asNumber(s.odiosos)), color: "#d92b3f" },
        ],
        { stack: false },
      ),
    [sizes],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !split.length} />

      <div className="grid grid-kpi">
        <Kpi
          label="Ódio em respostas"
          value={fmtPct(replyRate)}
          hint={reply ? `${fmtInt(reply.hate)} de ${fmtInt(reply.n)} comentários` : undefined}
        />
        <Kpi
          label="Ódio em 1º nível"
          value={fmtPct(rootRate)}
          hint={root ? `${fmtInt(root.hate)} de ${fmtInt(root.n)} comentários` : undefined}
        />
        <Kpi
          label="Resposta vs 1º nível"
          value={factor ? `${factor.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}×` : "—"}
          hint="Quanto a resposta é mais tóxica"
        />
        <Kpi
          label="Threads analisadas"
          value={fmtInt(threads)}
          hint={posts ? `Posts isolados: ${fmtPct(rate(posts.hate, posts.n))} de ódio` : undefined}
        />
      </div>

      <Card
        title="Taxa de ódio por tamanho da thread"
        subtitle="Cada barra agrega os comentários de threads com aquele número de comentários. Responde se conversa grande é mais hostil que conversa curta."
      >
        <EChart option={sizesOption} height={300} />
      </Card>

      <Card
        title="Volume de comentários por tamanho da thread"
        subtitle="Quantos comentários existem em cada faixa e quantos deles foram classificados como ódio."
      >
        <EChart option={volumeOption} height={320} />
      </Card>

      <Card
        title="Posts que mais atraem ódio"
        subtitle="Posts raiz ordenados pelo número de comentários classificados como ódio. As colunas de contexto vêm do post original, quando ele está na base."
      >
        <DataTable
          columns={[
            {
              key: "root_title",
              label: "Post raiz",
              render: (r: Row) => (
                <span title={String(r.root_text ?? "")}>
                  {String(r.root_title ?? "").trim() || String(r.root_text ?? "").trim().slice(0, 110) || (
                    <em>sem texto na base (id {String(r.root_post_id)})</em>
                  )}
                </span>
              ),
            },
            { key: "comments", label: "Comentários", numeric: true, render: (r: Row) => fmtInt(r.comments) },
            { key: "hate", label: "Com ódio", numeric: true, render: (r: Row) => fmtInt(r.hate) },
            { key: "pct", label: "Taxa", numeric: true, render: (r: Row) => fmtPct(r.pct, 1) },
            { key: "autores", label: "Autores", numeric: true, render: (r: Row) => fmtInt(r.autores) },
          ]}
          rows={top as unknown as Row[]}
          maxHeight={520}
        />
      </Card>
    </>
  );
}
