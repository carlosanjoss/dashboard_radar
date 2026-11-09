import { useMemo, useState } from "react";
import { WordCloud } from "../components/WordCloud.tsx";
import { Card, DataTable, Kpi, Status, useApi } from "../components/ui.tsx";
import { asNumber, fmtInt } from "../api.ts";
import { useFilters } from "../filters.tsx";

type Data = {
  terms: Array<{ term: string; frequency: number }>;
  termsHate: Array<{ term: string; frequency: number }>;
};

const HIDDEN_TERMS = new Set(["esquerda", "flavio", "url"]);

function visibleTerm(term: string): boolean {
  const normalized = term
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
  return !HIDDEN_TERMS.has(normalized);
}

export function Terms() {
  const { filters } = useFilters();
  const [limit, setLimit] = useState(60);
  const { data, loading, error } = useApi<Data>("/api/terms", filters, { limit });

  // Defesa no cliente: a nuvem não reexibe stopwords caso uma instância antiga
  // da API ainda esteja em execução ou entregue dados armazenados em cache.
  const termsHate = (data?.termsHate ?? []).filter((item) => visibleTerm(item.term));

  const hateCloud = useMemo(
    () => termsHate.slice(0, 70).map((t) => ({ text: t.term, value: t.frequency })),
    [termsHate],
  );

  return (
    <>
      <Status loading={loading} error={error} empty={!loading && !termsHate.length} />

      <div className="grid grid-kpi">
        <Kpi label="Termos de ódio distintos" value={fmtInt(termsHate.length)} hint={`top ${limit}`} />
        <Kpi label="Ocorrências em conteúdo de ódio" value={fmtInt(termsHate.reduce((acc, t) => acc + asNumber(t.frequency), 0))} />
        <Kpi label="Termo líder (ódio)" value={termsHate[0]?.term ?? "—"} hint={termsHate[0] ? `${fmtInt(termsHate[0].frequency)} ocorrências` : undefined} />
      </div>

      <Card
        title="Nuvem de termos"
        subtitle="Termos presentes nos conteúdos classificados como discurso de ódio. Tamanho proporcional à frequência."
        actions={
          <select value={limit} onChange={(e) => setLimit(Number(e.target.value))} className="btn" aria-label="Quantidade de termos">
            {[30, 60, 100, 150].map((n) => (
              <option key={n} value={n}>
                top {n}
              </option>
            ))}
          </select>
        }
      >
        <WordCloud words={hateCloud} height={430} />
      </Card>

      <Card title="Termos em conteúdo de ódio" subtitle="Frequência apenas nos registros classificados como discurso de ódio.">
        <DataTable
          columns={[
            { key: "term", label: "Termo" },
            { key: "frequency", label: "Ocorrências", numeric: true, render: (r) => fmtInt(r.frequency) },
          ]}
          rows={termsHate as unknown as Record<string, unknown>[]}
          maxHeight={420}
        />
      </Card>
    </>
  );
}
