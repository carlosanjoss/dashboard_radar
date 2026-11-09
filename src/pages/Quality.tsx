import { Card, Kpi, Status, useApi } from "../components/ui.tsx";
import { asNumber, fmtInt, fmtPct, type Row } from "../api.ts";
import { useFilters } from "../filters.tsx";

type Data = { row: Row | null };

export function Quality() {
  const { filters } = useFilters();
  const { data, loading, error } = useApi<Data>("/api/quality", filters);
  const row = data?.row ?? {};

  const total = asNumber(row.total);
  const emptyText = asNumber(row.empty_text);
  const missingDate = asNumber(row.missing_date);
  const futureDate = asNumber(row.future_date);
  const nullLabel = asNumber(row.null_label);
  const dupGroups = asNumber(row.duplicate_groups);
  const dupRows = asNumber(row.duplicate_rows);

  const pct = (n: number) => (total ? (n / total) * 100 : 0);

  return (
    <>
      <Status loading={loading} error={error} />

      <div className="grid grid-kpi">
        <Kpi label="Registros no recorte" value={fmtInt(total)} />
        <Kpi label="Grupos duplicados" value={fmtInt(dupGroups)} hint={`${fmtInt(dupRows)} registros (${fmtPct(pct(dupRows), 2)})`} />
        <Kpi label="Texto vazio" value={fmtInt(emptyText)} hint={fmtPct(pct(emptyText), 2)} />
        <Kpi label="Sem data" value={fmtInt(missingDate)} hint={fmtPct(pct(missingDate), 2)} />
      </div>

      <div className="grid grid-2">
        <Card title="Checagens de qualidade" subtitle="Indicadores que afetam a leitura dos volumes e taxas.">
          <table className="data">
            <tbody>
              <tr>
                <td>Registros com rótulo nulo</td>
                <td className="num">{fmtInt(nullLabel)} ({fmtPct(pct(nullLabel), 3)})</td>
              </tr>
              <tr>
                <td>Registros com data futura</td>
                <td className="num">{fmtInt(futureDate)}</td>
              </tr>
              <tr>
                <td>Registros em grupos de texto duplicado</td>
                <td className="num">{fmtInt(dupRows)} ({fmtPct(pct(dupRows), 2)})</td>
              </tr>
              <tr>
                <td>Grupos de duplicatas</td>
                <td className="num">{fmtInt(dupGroups)}</td>
              </tr>
              <tr>
                <td>Registros sem texto utilizável</td>
                <td className="num">{fmtInt(emptyText)} ({fmtPct(pct(emptyText), 3)})</td>
              </tr>
              <tr>
                <td>Registros sem data</td>
                <td className="num">{fmtInt(missingDate)}</td>
              </tr>
            </tbody>
          </table>
        </Card>

        <Card title="Como ler" subtitle="Notas metodológicas do painel.">
          <ul style={{ margin: 0, paddingLeft: 18, color: "var(--text-soft)", fontSize: 13.5, lineHeight: 1.9 }}>
            <li>
              A classificação é automatizada (ensembles BERT <code>radarodio-v01</code>): há falsos positivos e negativos.
            </li>
            <li>
              O fluxo é hierárquico — o modelo multilabel só roda quando o binário aponta ódio, então categorias só existem
              para registros de ódio.
            </li>
            <li>
              Textos duplicados podem inflar volumes e frequências; compares com o total do recorte antes de conclusões.
            </li>
            <li>
              Taxas de plataformas com amostra pequena aparecem com intervalo de confiança largo na página de Plataformas.
            </li>
            <li>
              A janela do painel é o período eleições 1º turno; registros fora dela (e sem data) não entram nas análises.
            </li>
          </ul>
        </Card>
      </div>
    </>
  );
}