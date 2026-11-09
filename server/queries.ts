import { DASHBOARD_MIN_DATE, MODEL_NAME, q, one } from "./db.ts";
import { CATEGORY_HIERARCHY } from "../shared/labels.ts";

export type Filters = {
  platforms: string[];
  contentKinds: string[];
  predLabels: string[];
  hateTypes: string[];
  dateStart?: string;
  dateEnd?: string;
  search?: string;
  excludePolitical?: boolean;
};

export type FilterInput = Partial<Record<keyof Filters, string | string[] | undefined>>;

function asArray(value: string | string[] | undefined): string[] {
  if (!value) return [];
  const list = Array.isArray(value) ? value : String(value).split(",");
  return list.map((v) => v.trim()).filter(Boolean);
}

export function parseFilters(input: FilterInput): Filters {
  return {
    platforms: asArray(input.platforms),
    contentKinds: asArray(input.contentKinds),
    predLabels: asArray(input.predLabels),
    hateTypes: asArray(input.hateTypes),
    dateStart: input.dateStart ? String(input.dateStart) : undefined,
    dateEnd: input.dateEnd ? String(input.dateEnd) : undefined,
    search: input.search ? String(input.search) : undefined,
    excludePolitical: ["1", "true", "yes"].includes(String(input.excludePolitical ?? "").toLowerCase()),
  };
}

type Params = unknown[];

/** Cláusulas extras de filtro (aplicadas sobre o CTE `base`). */
function filterClauses(f: Filters, params: Params): string {
  const clauses: string[] = [];
  const bind = (value: unknown) => {
    params.push(value);
    return `$${params.length}`;
  };

  if (f.platforms.length) clauses.push(`platform = ANY(${bind(f.platforms)})`);
  if (f.contentKinds.length) clauses.push(`content_kind = ANY(${bind(f.contentKinds)})`);
  if (f.predLabels.length) clauses.push(`pred_label = ANY(${bind(f.predLabels)})`);
  if (f.hateTypes.length) clauses.push(`hate_types && ${bind(f.hateTypes)}::text[]`);
  if (f.dateStart) clauses.push(`published_at::date >= ${bind(f.dateStart)}::date`);
  if (f.dateEnd) clauses.push(`published_at::date <= ${bind(f.dateEnd)}::date`);
  if (f.search) clauses.push(`text_content ILIKE ${bind(`%${f.search}%`)}`);
  // "Retirar odio politico": sai o conteudo cujo UNICO tipo e o politico.
  // Politico + outro preconceito PERMANECE — por isso a igualdade exata de array,
  // e nao `&&` (que pegaria qualquer registro que contenha political).
  if (f.excludePolitical)
    clauses.push(`NOT COALESCE(hate_types = ARRAY['political']::text[], false)`);

  return clauses.length ? " AND " + clauses.join(" AND ") : "";
}

/**
 * CTE base do painel: a view de compatibilidade sobre periodo_eleicoes_1_turno_bert,
 * restrita à janela eleitoral e aos filtros globais.
 * Params fixos: $1 = modelo, $2 = data mínima.
 */
function withBase(f: Filters, extra?: (params: Params) => void) {
  const params: Params = [MODEL_NAME, DASHBOARD_MIN_DATE];
  const extraSql = filterClauses(f, params);
  extra?.(params);
  const cte = `
WITH base AS (
  SELECT
    analysis_id, content_kind, platform, external_id, pred_label,
    hate_probability, binary_score, hate_types, pred_category,
    category_probability, category_scores, published_at, author, language,
    text_content, title, url, post_key, root_post_key,
    is_reply, root_post_id
  FROM public.v_bert_hate_results
  WHERE model_name = $1
    AND status = 'success'
    AND published_at::date BETWEEN $2::date AND CURRENT_DATE
    ${extraSql}
)`;
  return { cte, params };
}

const GRAINS = new Set(["day", "week", "month", "year"]);
function safeGrain(grain: string | undefined, fallback = "month"): string {
  return grain && GRAINS.has(grain) ? grain : fallback;
}

/* ------------------------------------------------------------------ meta */

export async function getMeta() {
  const rows = await one<{
    platforms: string[];
    content_kinds: string[];
    pred_labels: string[];
    hate_types: string[];
    min_date: string | null;
    max_date: string | null;
    window_rows: string;
    total_rows: string;
  }>(
    `
    SELECT
      ARRAY(SELECT DISTINCT platform FROM public.v_bert_hate_results WHERE model_name = $1 ORDER BY platform) AS platforms,
      ARRAY(SELECT DISTINCT content_kind FROM public.v_bert_hate_results WHERE model_name = $1 ORDER BY content_kind) AS content_kinds,
      ARRAY(SELECT DISTINCT pred_label FROM public.v_bert_hate_results WHERE model_name = $1 AND pred_label IS NOT NULL ORDER BY pred_label) AS pred_labels,
      ARRAY(
        SELECT DISTINCT ht FROM public.v_bert_hate_results r
        CROSS JOIN LATERAL unnest(r.hate_types) AS ht
        WHERE r.model_name = $1 AND r.pred_label = 'hate' AND ht <> 'other'
        ORDER BY ht
      ) AS hate_types,
      (SELECT MIN(published_at)::date FROM public.v_bert_hate_results WHERE model_name = $1 AND status = 'success' AND published_at::date >= $2::date AND published_at::date <= CURRENT_DATE) AS min_date,
      (SELECT MAX(published_at)::date FROM public.v_bert_hate_results WHERE model_name = $1 AND status = 'success' AND published_at::date >= $2::date AND published_at::date <= CURRENT_DATE) AS max_date,
      (SELECT COUNT(*) FROM public.v_bert_hate_results WHERE model_name = $1 AND status = 'success' AND published_at::date BETWEEN $2::date AND CURRENT_DATE) AS window_rows,
      (SELECT COUNT(*) FROM public.v_bert_hate_results WHERE model_name = $1) AS total_rows
    `,
    [MODEL_NAME, DASHBOARD_MIN_DATE],
  );
  return {
    modelName: MODEL_NAME,
    minDate: rows?.min_date ?? null,
    maxDate: rows?.max_date ?? null,
    windowRows: Number(rows?.window_rows ?? 0),
    totalRows: Number(rows?.total_rows ?? 0),
    platforms: rows?.platforms ?? [],
    contentKinds: rows?.content_kinds ?? [],
    predLabels: rows?.pred_labels ?? [],
    hateTypes: rows?.hate_types ?? [],
    categoryHierarchy: CATEGORY_HIERARCHY,
    dashboardMinDate: DASHBOARD_MIN_DATE,
  };
}

/* -------------------------------------------------------------- overview */

export async function getOverview(f: Filters) {
  const { cte, params } = withBase(f);
  const current = await one<Record<string, unknown>>(
    `${cte}
    SELECT
      COUNT(*)::bigint AS total_content,
      COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
      COUNT(*) FILTER (WHERE pred_label = 'nao_hate')::bigint AS total_non_hate,
      ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent,
      COUNT(DISTINCT platform)::int AS total_platforms,
      COUNT(DISTINCT author) FILTER (WHERE author IS NOT NULL AND author <> '')::int AS total_authors,
      ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability,
      COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS total_posts,
      COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS total_comments
    FROM base`,
    params,
  );

  const daily = await q<{ day: string; total: number; hate: number }>(
    `${cte}
    SELECT published_at::date AS day,
           COUNT(*)::int AS total,
           COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS hate
    FROM base
    GROUP BY 1 ORDER BY 1`,
    params,
  );

  const types = await q<{ hate_type: string; total: number }>(
    `${cte}
    SELECT ht AS hate_type, COUNT(*)::int AS total
    FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
    WHERE pred_label = 'hate' AND ht <> 'other'
    GROUP BY 1 ORDER BY 2 DESC`,
    params,
  );

  // Comparativo com o período anterior de mesma duração.
  // A duração é medida pelo intervalo de datas observado (não pelo número de
  // dias com dados), senão buracos na série encolhem a janela anterior.
  const firstDay = daily[0]?.day;
  const lastDay = daily[daily.length - 1]?.day;
  const spanDays =
    firstDay && lastDay ? Math.round((Date.parse(lastDay) - Date.parse(firstDay)) / 86_400_000) + 1 : 0;

  let previous: Record<string, unknown> | undefined;
  if (spanDays > 0) {
    const prevEnd = new Date(`${firstDay}T00:00:00Z`);
    prevEnd.setUTCDate(prevEnd.getUTCDate() - 1);
    const prevStart = new Date(prevEnd);
    prevStart.setUTCDate(prevStart.getUTCDate() - (spanDays - 1));
    const prevFilters: Filters = { ...f, dateStart: undefined, dateEnd: undefined };
    const prevParams: Params = [
      MODEL_NAME,
      prevStart.toISOString().slice(0, 10),
    ];
    const prevExtra = filterClauses(prevFilters, prevParams);
    prevParams.push(prevEnd.toISOString().slice(0, 10));
    const prevEndIdx = prevParams.length;
    previous = await one<Record<string, unknown>>(
      `WITH prev AS (
        SELECT * FROM public.v_bert_hate_results
        WHERE model_name = $1
          AND status = 'success'
          AND published_at::date BETWEEN $2::date AND $${prevEndIdx}::date
          ${prevExtra}
      )
      SELECT
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent
      FROM prev`,
      prevParams,
    );
  }

  return { current, previous, daily, types };
}

/* ------------------------------------------------------------- platforms */

export async function getPlatforms(f: Filters) {
  const { cte, params } = withBase(f);
  const platforms = await q<Record<string, unknown>>(
    `${cte}
    SELECT platform,
      COUNT(*)::bigint AS total_content,
      COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
      ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent,
      ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability,
      COUNT(DISTINCT author) FILTER (WHERE author IS NOT NULL AND author <> '')::int AS total_authors,
      COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS total_posts,
      COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS total_comments
    FROM base GROUP BY platform ORDER BY total_content DESC`,
    params,
  );

  const kinds = await q<Record<string, unknown>>(
    `${cte}
    SELECT content_kind,
      COUNT(*)::bigint AS total_content,
      COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
      ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent
    FROM base GROUP BY content_kind ORDER BY total_content DESC`,
    params,
  );

  return { platforms, kinds };
}

/* ------------------------------------------------------------ categories */

export async function getCategories(f: Filters) {
  const { cte, params } = withBase(f);

  const frequency = await q<Record<string, unknown>>(
    `${cte}
    SELECT ht AS hate_type,
      COUNT(*)::int AS total_mentions,
      COUNT(*) FILTER (WHERE content_kind = 'post')::int AS post_mentions,
      COUNT(*) FILTER (WHERE content_kind = 'comment')::int AS comment_mentions,
      COUNT(DISTINCT platform)::int AS total_platforms,
      ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability
    FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
    WHERE pred_label = 'hate' AND ht <> 'other'
    GROUP BY 1 ORDER BY 2 DESC`,
    params,
  );

  const byPlatform = await q<{ platform: string; hate_type: string; total: number }>(
    `${cte}
    SELECT platform, ht AS hate_type, COUNT(*)::int AS total
    FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
    WHERE pred_label = 'hate' AND ht <> 'other'
    GROUP BY 1, 2 ORDER BY 3 DESC`,
    params,
  );

  const cooccurrence = await q<{ hate_type_a: string; hate_type_b: string; total: number }>(
    `${cte},
    typed AS (
      SELECT analysis_id, array_agg(DISTINCT ht ORDER BY ht) AS types
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
      GROUP BY analysis_id
    )
    SELECT a AS hate_type_a, b AS hate_type_b, COUNT(*)::int AS total
    FROM typed CROSS JOIN LATERAL unnest(types) a CROSS JOIN LATERAL unnest(types) b
    WHERE a < b
    GROUP BY 1, 2 ORDER BY 3 DESC`,
    params,
  );

  const hateRecords = await one<{ total: number }>(
    `${cte} SELECT COUNT(*)::int AS total FROM base WHERE pred_label = 'hate'`,
    params,
  );

  return { frequency, byPlatform, cooccurrence, totalHateRecords: hateRecords?.total ?? 0 };
}

/**
 * Probabilidade média por categoria — monta as métricas "pegando as hierarquias":
 * percorre CATEGORY_HIERARCHY e lê o score de cada categoria no jsonb category_scores.
 */
export async function getCategoryProbabilities(f: Filters) {
  const { cte, params } = withBase(f);
  params.push(CATEGORY_HIERARCHY);
  const idx = params.length;

  const rows = await q<Record<string, unknown>>(
    `${cte}
    SELECT cat AS category,
      COUNT(*)::int AS total,
      ROUND(AVG((category_scores ->> cat)::float8)::numeric, 4)::float8 AS avg_probability,
      ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (category_scores ->> cat)::float8)::numeric, 4)::float8 AS median_probability,
      ROUND(MAX((category_scores ->> cat)::float8)::numeric, 4)::float8 AS max_probability,
      COUNT(*) FILTER (WHERE (category_scores ->> cat)::float8 >= 0.5)::int AS above_half
    FROM base CROSS JOIN LATERAL unnest($${idx}::text[]) AS cat
    WHERE pred_label = 'hate' AND category_scores ? cat
    GROUP BY 1`,
    params,
  );

  const total = await one<{ total: number }>(
    `${cte} SELECT COUNT(*)::int AS total FROM base WHERE pred_label = 'hate'`,
    params.slice(0, -1),
  );

  return { rows, totalHate: total?.total ?? 0 };
}

/* -------------------------------------------------------------- temporal */

export async function getTemporal(f: Filters, grain: string) {
  const g = safeGrain(grain, "day");
  const { cte, params } = withBase(f);
  const series = await q<Record<string, unknown>>(
    `${cte}
    SELECT DATE_TRUNC('${g}', published_at)::date AS period,
      COUNT(*)::int AS total_content,
      COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS total_hate,
      ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent,
      ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability
    FROM base
    WHERE published_at IS NOT NULL
    GROUP BY 1 ORDER BY 1`,
    params,
  );
  return { grain: g, series };
}

export async function getToxicity(f: Filters, grain: string, limit: number) {
  const g = safeGrain(grain, "month");
  const { cte, params } = withBase(f);
  params.push(limit);
  const limitIdx = params.length;

  const series = await q<Record<string, unknown>>(
    `${cte},
    typed AS (
      SELECT DATE_TRUNC('${g}', published_at)::date AS period, ht AS hate_type, hate_probability
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND published_at IS NOT NULL AND ht <> 'other'
    ),
    top_types AS (
      SELECT hate_type FROM typed GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT $${limitIdx}
    ),
    period_totals AS (
      SELECT period, COUNT(*)::int AS period_total FROM typed GROUP BY 1
    )
    SELECT t.period, t.hate_type,
      COUNT(*)::int AS total_mentions,
      pt.period_total AS period_total_mentions,
      ROUND((100.0 * COUNT(*) / NULLIF(pt.period_total, 0))::numeric, 2)::float8 AS percent_mentions,
      ROUND(AVG(t.hate_probability)::numeric, 4)::float8 AS avg_toxicity
    FROM typed t
    INNER JOIN top_types tt ON tt.hate_type = t.hate_type
    INNER JOIN period_totals pt ON pt.period = t.period
    GROUP BY t.period, t.hate_type, pt.period_total
    ORDER BY t.period, t.hate_type`,
    params,
  );

  const summary = await q<Record<string, unknown>>(
    `${cte},
    typed AS (
      SELECT ht AS hate_type, hate_probability, platform, content_kind
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
    ),
    totals AS (SELECT COUNT(*)::int AS all_mentions FROM typed)
    SELECT t.hate_type,
      COUNT(*)::int AS total_mentions,
      ROUND((100.0 * COUNT(*) / NULLIF(MAX(totals.all_mentions), 0))::numeric, 2)::float8 AS percent_mentions,
      COUNT(DISTINCT t.platform)::int AS total_platforms,
      COUNT(*) FILTER (WHERE t.content_kind = 'post')::int AS post_mentions,
      COUNT(*) FILTER (WHERE t.content_kind = 'comment')::int AS comment_mentions,
      ROUND(AVG(t.hate_probability)::numeric, 4)::float8 AS avg_toxicity
    FROM typed t CROSS JOIN totals
    GROUP BY t.hate_type
    ORDER BY total_mentions DESC`,
    params.slice(0, -1),
  );

  return { grain: g, series, summary };
}

/* ----------------------------------------------------------------- terms */

const STOPWORDS = [
  "a","ao","aos","as","com","como","da","das","de","do","dos","e","em","era","essa","esse","esta","este","eu",
  "foi","mais","mas","me","muito","na","nao","nas","no","nos","o","os","ou","para","pela","pelo","por","pra",
  "pro","que","se","sem","ser","sua","sao","tem","um","uma","vai","voce","voces","ele","ela","eles","elas",
  "isso","isto","aquilo","aqui","ali","la","todo","toda","todos","todas","quem","qual","quais","quando","onde",
  "porque","assim","ainda","ja","ate","tambem","mesmo","mesma","mesmos","mesmas","meu","minha","meus","minhas",
  "seu","seus","dele","dela","deles","delas","tudo","nada","cada","sobre","entre","contra","apenas","agora",
  "hoje","dia","cara","tipo","coisa","gente","pessoa","pessoas","ter","vou","ta","esta","estava","estao","sera",
  "bem","pode","podem","podia","fazer","faz","fez","feito","nosso","nossa","nossos","nossas","suas","pois","sim",
  "nem","entao","foram","vamos","nunca","tempo","ano","anos","mundo","phone","esses","essas","desse","dessa",
  "desses","dessas","aquele","aquela","aqueles","aquelas","falar","fala","falou","quer","ver","sempre","kkkk",
  "kkkkk","kkk","rsrs","http","https","www","com","br","net","org","html","php","amp","utm","ref","t","co","bit",
  "ly","tinyurl","url","youtu","youtube","facebook","instagram","twitter","reddit","telegram","tiktok","whatsapp",
  "lula","bolsonaro","esquerda","flávio","flavio","so","tá","há",
  "vão","vao","vcs","vc","vai","vou","ne","né","eh","ta","tava","tinha","tinham","olha","veja","vejam",
  "ser","sou","somos","era","eram","foi","foram","será","sera","seria","seja","fosse","tivesse",
  "fica","ficar","ficou","deu","dar","dá","da","vem","vir","veio","quer","queria","quero","acho","acha",
  "pensa","pensei","sabe","sei","sabem","disse","diz","dizer","fala","falar","falou","falei",
  "user","more","see","the","and","you","for","are","was","with","this","that","from","have","but",
  "not","your","our","they","will","his","her","about","just","what","when","all","can","out",
];

export async function getTerms(f: Filters, limit: number) {
  const { cte, params } = withBase(f);
  params.push(STOPWORDS, limit);
  const stopIdx = params.length - 1;
  const limitIdx = params.length;

  const terms = await q<{ term: string; frequency: number }>(
    `${cte},
    tokens AS (
      SELECT lower(token) AS term,
             translate(lower(token),
               'áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ',
               'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC') AS normalized
      FROM base
      CROSS JOIN LATERAL regexp_split_to_table(
        regexp_replace(
          regexp_replace(COALESCE(text_content, ''), 'https?://[^[:space:]]+|www\\.[^[:space:]]+', ' ', 'gi'),
          '[^[:alnum:]#_]+', ' ', 'g'
        ), '\\s+'
      ) AS token
    )
    SELECT term, COUNT(*)::int AS frequency
    FROM tokens
    WHERE length(term) > 2
      AND NOT term = ANY($${stopIdx}::text[])
      AND NOT normalized = ANY($${stopIdx}::text[])
      AND term !~ '^[0-9]+$'
      AND term !~ '^[a-f0-9]{10,}$'
      AND term NOT LIKE 'http%'
      AND term NOT LIKE 'www%'
    GROUP BY term ORDER BY frequency DESC LIMIT $${limitIdx}`,
    params,
  );

  const termsHate = await q<{ term: string; frequency: number }>(
    `${cte},
    tokens AS (
      SELECT lower(token) AS term,
             translate(lower(token),
               'áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ',
               'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC') AS normalized
      FROM base
      CROSS JOIN LATERAL regexp_split_to_table(
        regexp_replace(
          regexp_replace(COALESCE(text_content, ''), 'https?://[^[:space:]]+|www\\.[^[:space:]]+', ' ', 'gi'),
          '[^[:alnum:]#_]+', ' ', 'g'
        ), '\\s+'
      ) AS token
      WHERE pred_label = 'hate'
    )
    SELECT term, COUNT(*)::int AS frequency
    FROM tokens
    WHERE length(term) > 2
      AND NOT term = ANY($${stopIdx}::text[])
      AND NOT normalized = ANY($${stopIdx}::text[])
      AND term !~ '^[0-9]+$'
      AND term !~ '^[a-f0-9]{10,}$'
      AND term NOT LIKE 'http%'
      AND term NOT LIKE 'www%'
    GROUP BY term ORDER BY frequency DESC LIMIT $${limitIdx}`,
    params,
  );

  return { terms, termsHate };
}

/* --------------------------------------------------------------- network */

export async function getNetwork(f: Filters, limit: number, minWeight: number) {
  const { cte, params } = withBase(f);
  params.push(minWeight, limit);
  const minIdx = params.length - 1;
  const limitIdx = params.length;

  const edges = await q<{ source: string; target: string; relation: string; total: number }>(
    `${cte},
    type_mentions AS (
      SELECT platform, content_kind, ht AS hate_type
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
    ),
    platform_edges AS (
      SELECT 'rede:' || platform AS source, 'tipo:' || hate_type AS target, 'rede_tipo' AS relation, COUNT(*)::int AS total
      FROM type_mentions GROUP BY 1, 2
    ),
    kind_edges AS (
      SELECT 'conteudo:' || content_kind AS source, 'tipo:' || hate_type AS target, 'conteudo_tipo' AS relation, COUNT(*)::int AS total
      FROM type_mentions GROUP BY 1, 2
    ),
    typed AS (
      SELECT analysis_id, array_agg(DISTINCT ht ORDER BY ht) AS types
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
      GROUP BY analysis_id
      HAVING COUNT(DISTINCT ht) >= 2
    ),
    cooc_edges AS (
      SELECT 'tipo:' || a AS source, 'tipo:' || b AS target, 'coocorrencia' AS relation, COUNT(*)::int AS total
      FROM typed CROSS JOIN LATERAL unnest(types) a CROSS JOIN LATERAL unnest(types) b
      WHERE a < b GROUP BY 1, 2
    )
    SELECT * FROM (
      SELECT * FROM platform_edges
      UNION ALL SELECT * FROM kind_edges
      UNION ALL SELECT * FROM cooc_edges
    ) edges
    WHERE total >= $${minIdx}
    ORDER BY total DESC
    LIMIT $${limitIdx}`,
    params,
  );

  return { edges };
}

/* --------------------------------------------------------------- authors */

export async function getAuthors(f: Filters, limit: number, minRecords: number) {
  const { cte, params } = withBase(f);
  params.push(minRecords, limit);
  const minIdx = params.length - 1;
  const limitIdx = params.length;

  const authors = await q<Record<string, unknown>>(
    `${cte},
    rows AS (
      SELECT md5(lower(trim(author))) AS author_hash, platform, content_kind, pred_label, hate_probability, published_at
      FROM base
      WHERE author IS NOT NULL AND trim(author) <> ''
        AND lower(author) NOT IN ('[deleted]', 'deleted', 'unknown')
    ),
    grouped AS (
      SELECT author_hash,
        COUNT(*)::int AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS total_hate,
        ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent,
        COUNT(DISTINCT platform)::int AS total_platforms,
        COUNT(*) FILTER (WHERE content_kind = 'post')::int AS total_posts,
        COUNT(*) FILTER (WHERE content_kind = 'comment')::int AS total_comments,
        ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability,
        MIN(published_at)::date AS first_seen,
        MAX(published_at)::date AS last_seen
      FROM rows GROUP BY author_hash HAVING COUNT(*) >= $${minIdx}
    )
    SELECT * FROM grouped
    ORDER BY total_hate DESC, total_content DESC
    LIMIT $${limitIdx}`,
    params,
  );

  const authorTypes = await q<{ author_hash: string; hate_type: string; total: number }>(
    `${cte},
    at AS (
      SELECT md5(lower(trim(author))) AS author_hash, ht AS hate_type
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
        AND author IS NOT NULL AND trim(author) <> ''
    ),
    grouped AS (
      SELECT author_hash, hate_type, COUNT(*)::int AS total
      FROM at GROUP BY 1, 2 HAVING COUNT(*) >= $${minIdx}
    )
    SELECT * FROM grouped ORDER BY total DESC LIMIT $${limitIdx}`,
    params,
  );

  return { authors, authorTypes };
}

/* ----------------------------------------------------------------- posts */

export async function getPosts(f: Filters, limit: number, minRecords: number) {
  const { cte, params } = withBase(f);
  params.push(minRecords, limit);
  const minIdx = params.length - 1;
  const limitIdx = params.length;

  const posts = await q<Record<string, unknown>>(
    `${cte},
    grouped AS (
      SELECT platform,
        COALESCE(root_post_key, post_key) AS post_id,
        COUNT(*)::int AS total_records,
        COUNT(*) FILTER (WHERE content_kind = 'post')::int AS total_posts,
        COUNT(*) FILTER (WHERE content_kind = 'comment')::int AS total_comments,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS total_hate,
        ROUND(100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate') / NULLIF(COUNT(*), 0), 2)::float8 AS hate_percent,
        ROUND(AVG(hate_probability)::numeric, 4)::float8 AS avg_hate_probability,
        MIN(published_at)::date AS first_published_at,
        MAX(published_at)::date AS last_published_at
      FROM base
      WHERE post_key IS NOT NULL
      GROUP BY 1, 2 HAVING COUNT(*) >= $${minIdx}
    )
    SELECT g.platform, g.post_id,
      p.external_id,
      COALESCE(NULLIF(p.title, ''), NULLIF(p.text_content, ''), '(sem título)') AS post_title,
      p.url,
      g.total_records, g.total_posts, g.total_comments, g.total_hate, g.hate_percent,
      g.avg_hate_probability, g.first_published_at, g.last_published_at
    FROM grouped g
    LEFT JOIN (
      SELECT post_key, MAX(external_id) AS external_id, MAX(title) AS title, MAX(url) AS url, MAX(text_content) AS text_content
      FROM base WHERE content_kind = 'post' GROUP BY post_key
    ) p ON p.post_key = g.post_id
    ORDER BY g.total_hate DESC, g.total_records DESC
    LIMIT $${limitIdx}`,
    params,
  );

  return { posts };
}

/* --------------------------------------------------------------- records */

export async function getRecords(f: Filters, page: number, pageSize: number) {
  const { cte, params } = withBase(f);
  const offset = (Math.max(page, 1) - 1) * pageSize;
  params.push(pageSize, offset);

  const rows = await q<Record<string, unknown>>(
    `${cte}
    SELECT analysis_id, external_id, platform, content_kind, pred_label,
      hate_probability, binary_score, hate_types, pred_category, category_probability,
      category_scores, published_at,
      LEFT(regexp_replace(COALESCE(text_content, ''), '\\s+', ' ', 'g'), 700) AS text_excerpt
    FROM base
    ORDER BY published_at DESC NULLS LAST, analysis_id DESC
    LIMIT $${params.length - 1} OFFSET $${params.length}`,
    params,
  );

  const total = await one<{ total: number }>(
    `${cte} SELECT COUNT(*)::int AS total FROM base`,
    params.slice(0, -2),
  );

  return { rows, total: total?.total ?? 0, page, pageSize };
}

export async function getRecordsForPost(postKey: string, f: Filters, page: number, pageSize: number) {
  const { cte, params } = withBase(f);
  params.push(postKey);
  const keyIdx = params.length;
  const offset = (Math.max(page, 1) - 1) * pageSize;
  params.push(pageSize, offset);

  return q<Record<string, unknown>>(
    `${cte}
    SELECT analysis_id, platform, content_kind, pred_label, hate_probability, binary_score,
      hate_types, pred_category, category_probability, category_scores, published_at,
      LEFT(regexp_replace(COALESCE(text_content, ''), '\\s+', ' ', 'g'), 700) AS text_excerpt
    FROM base
    WHERE COALESCE(root_post_key, post_key) = $${keyIdx}
    ORDER BY hate_probability DESC NULLS LAST, published_at DESC NULLS LAST
    LIMIT $${params.length - 1} OFFSET $${params.length}`,
    params,
  );
}

/* --------------------------------------------------------------- quality */

export async function getQuality(f: Filters) {
  const { cte, params } = withBase(f);
  const row = await one<Record<string, unknown>>(
    `${cte},
    duplicates AS (
      SELECT md5(lower(trim(text_content))) AS h, COUNT(*) AS n
      FROM base WHERE text_content IS NOT NULL AND trim(text_content) <> ''
      GROUP BY 1 HAVING COUNT(*) > 1
    )
    SELECT
      COUNT(*)::int AS total,
      COUNT(*) FILTER (WHERE text_content IS NULL OR trim(text_content) = '')::int AS empty_text,
      COUNT(*) FILTER (WHERE published_at IS NULL)::int AS missing_date,
      COUNT(*) FILTER (WHERE published_at::date > CURRENT_DATE)::int AS future_date,
      COUNT(*) FILTER (WHERE pred_label IS NULL)::int AS null_label,
      (SELECT COUNT(*) FROM duplicates)::int AS duplicate_groups,
      COALESCE((SELECT SUM(n) FROM duplicates), 0)::int AS duplicate_rows
    FROM base`,
    params,
  );
  return { row };
}

/* -------------------------------------------------------- intersectionality */

export async function getIntersectionality(f: Filters) {
  const { cte, params } = withBase(f);
  const rows = await q<Record<string, unknown>>(
    `${cte},
    typed AS (
      SELECT analysis_id, array_agg(DISTINCT ht ORDER BY ht) AS types
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
      GROUP BY analysis_id
    ),
    all_types AS (
      SELECT DISTINCT ht AS hate_type
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
    ),
    pair_counts AS (
      SELECT a AS hate_type_a, b AS hate_type_b, COUNT(*)::int AS total
      FROM typed CROSS JOIN LATERAL unnest(types) a CROSS JOIN LATERAL unnest(types) b
      WHERE a < b GROUP BY 1, 2
    ),
    single_counts AS (
      SELECT ht AS hate_type, COUNT(*)::int AS single_count
      FROM base CROSS JOIN LATERAL unnest(hate_types) AS ht
      WHERE pred_label = 'hate' AND ht <> 'other'
      GROUP BY 1
    )
    SELECT t1.hate_type AS hate_type_a, t2.hate_type AS hate_type_b,
      COALESCE(pc.total, 0)::int AS total_cooccurrences,
      COALESCE(sc1.single_count, 0)::int AS count_a,
      COALESCE(sc2.single_count, 0)::int AS count_b,
      CASE
        WHEN t1.hate_type = t2.hate_type THEN 100.0
        WHEN LEAST(COALESCE(sc1.single_count, 0), COALESCE(sc2.single_count, 0)) > 0
          THEN ROUND((100.0 * COALESCE(pc.total, 0) / NULLIF(LEAST(COALESCE(sc1.single_count, 0), COALESCE(sc2.single_count, 0)), 0))::numeric, 2)::float8
        ELSE 0.0
      END AS overlap_percentage
    FROM all_types t1
    CROSS JOIN all_types t2
    LEFT JOIN pair_counts pc
      ON (pc.hate_type_a = t1.hate_type AND pc.hate_type_b = t2.hate_type)
      OR (pc.hate_type_a = t2.hate_type AND pc.hate_type_b = t1.hate_type)
    LEFT JOIN single_counts sc1 ON sc1.hate_type = t1.hate_type
    LEFT JOIN single_counts sc2 ON sc2.hate_type = t2.hate_type
    ORDER BY t1.hate_type, t2.hate_type`,
    params,
  );
  return { rows };
}

/* ----------------------------------------------------------- threads */

/**
 * Dinâmica de thread: o ódio se concentra em respostas?
 * Respostas (is_reply) × primeiro nível, tamanho da thread e posts raiz
 * que mais atraem hostilidade.
 */
export async function getThreads(f: Filters, limit: number) {
  const { cte, params } = withBase(f);

  const split = await q<Record<string, unknown>>(
    `${cte}
    SELECT content_kind,
      COALESCE(is_reply, false) AS is_reply,
      COUNT(*)::int AS n,
      COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS hate
    FROM base
    GROUP BY 1, 2
    ORDER BY 1, 2`,
    params,
  );

  const sizes = await q<Record<string, unknown>>(
    `${cte},
    roots AS (
      SELECT root_post_id,
        COUNT(*)::int AS comments,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS hate
      FROM base
      WHERE content_kind = 'comment' AND root_post_id IS NOT NULL
      GROUP BY 1
    )
    SELECT
      CASE
        WHEN comments = 1 THEN '1'
        WHEN comments <= 5 THEN '2–5'
        WHEN comments <= 20 THEN '6–20'
        WHEN comments <= 100 THEN '21–100'
        WHEN comments <= 500 THEN '101–500'
        ELSE '500+'
      END AS faixa,
      MIN(comments)::int AS ordem,
      COUNT(*)::int AS threads,
      SUM(comments)::int AS comentarios,
      SUM(hate)::int AS odiosos
    FROM roots
    GROUP BY 1
    ORDER BY ordem`,
    params,
  );

  const limitParam = `$${params.length + 1}`;
  const top = await q<Record<string, unknown>>(
    `${cte},
    posts AS (
      SELECT post_key, title, text_content FROM base WHERE content_kind = 'post'
    ),
    roots AS (
      SELECT root_post_id, root_post_key,
        COUNT(*)::int AS comments,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS hate,
        COUNT(DISTINCT author)::int AS autores
      FROM base
      WHERE content_kind = 'comment' AND root_post_id IS NOT NULL
      GROUP BY 1, 2
    ),
    top AS (
      SELECT * FROM roots ORDER BY hate DESC, comments DESC LIMIT ${limitParam}
    )
    SELECT t.root_post_id, t.root_post_key, t.comments, t.hate, t.autores,
      ROUND((100.0 * t.hate / NULLIF(t.comments, 0))::numeric, 2)::float8 AS pct,
      LEFT(COALESCE(p.title, ''), 180) AS root_title,
      LEFT(COALESCE(p.text_content, ''), 400) AS root_text
    FROM top t
    LEFT JOIN posts p ON p.post_key = t.root_post_key
    ORDER BY t.hate DESC, t.comments DESC`,
    [...params, limit],
  );

  return { split, sizes, top };
}

/* ----------------------------------------------------------- limiar */

/** Sensibilidade ao limiar de decisão sobre hate_probability. */
export async function getThreshold(f: Filters) {
  const { cte, params } = withBase(f);

  const buckets = await q<Record<string, unknown>>(
    `${cte}
    SELECT width_bucket(hate_probability, 0, 1, 10) AS bucket,
      COUNT(*)::int AS n
    FROM base
    WHERE hate_probability IS NOT NULL
    GROUP BY 1
    ORDER BY 1`,
    params,
  );

  const curve = await q<Record<string, unknown>>(
    `${cte}
    SELECT ROUND(t.threshold::numeric, 2)::float8 AS threshold,
      COUNT(*) FILTER (WHERE base.hate_probability >= t.threshold)::int AS n
    FROM base
    CROSS JOIN generate_series(0.05::numeric, 0.95::numeric, 0.05::numeric) AS t(threshold)
    WHERE base.hate_probability IS NOT NULL
    GROUP BY 1
    ORDER BY 1`,
    params,
  );

  // Onde o modelo de fato decide: `pred_label` vem de `binary_label`, não de um
  // corte em 0,50. Expor as bordas reais evita rótulo errado na página.
  const cut = await one<Record<string, unknown>>(
    `${cte}
    SELECT
      COUNT(*) FILTER (WHERE pred_label = 'hate')::int AS n_hate,
      COUNT(*) FILTER (WHERE pred_label = 'nao_hate')::int AS n_not_hate,
      MIN(hate_probability) FILTER (WHERE pred_label = 'hate')::float8 AS min_hate,
      MAX(hate_probability) FILTER (WHERE pred_label = 'nao_hate')::float8 AS max_not_hate
    FROM base
    WHERE hate_probability IS NOT NULL`,
    params,
  );

  return { buckets, curve, cut };
}
