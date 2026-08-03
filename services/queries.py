from __future__ import annotations

from datetime import date
from functools import lru_cache

import pandas as pd

from services.database import run_query


MODEL_NAME = "gemma3:4b"
EXPECTED_PLATFORMS = [
    "facebook",
    "reddit",
    "telegram",
    "tiktok",
    "twitter",
    "whatsapp",
    "youtube",
]

HATE_TYPE_LABELS = {
    "ageism": "Etarismo",
    "aporophobia": "Aporofobia",
    "body_shame": "Ataque ao corpo",
    "capacitism": "Capacitismo",
    "lgbtphobia": "LGBTfobia",
    "misogyny": "Misoginia",
    "other": "Outros",
    "political": "Ódio político",
    "racism": "Racismo",
    "religious_intolerance": "Intolerância religiosa",
    "xenophobia": "Xenofobia",
}
EXCLUDED_HATE_TYPES = {"other"}

PLATFORM_LABELS = {
    "facebook": "Facebook",
    "reddit": "Reddit",
    "telegram": "Telegram",
    "tiktok": "TikTok",
    "twitter": "Twitter",
    "whatsapp": "WhatsApp",
    "youtube": "YouTube",
}

CONTENT_KIND_LABELS = {
    "post": "Post",
    "comment": "Comentário",
}

PRED_LABELS = {
    "hate": "Hate",
    "nao_hate": "Não hate",
}


def _base_sql(include_status_filter=True, include_text=False, include_dates=False):
    status_filter = "AND r.status = 'success'" if include_status_filter else ""
    needs_join = include_text or include_dates

    join_sql = ""
    if needs_join:
        join_sql = """
        LEFT JOIN public.posts p
            ON r.source_post_id = p.id
        LEFT JOIN public.comments c
            ON r.source_comment_id = c.id
        """

    if needs_join:
        date_columns = """
            COALESCE(p.published_at, c.published_at) AS published_at,
            COALESCE(p.collected_at, c.collected_at) AS collected_at,
        """
    else:
        date_columns = """
            NULL::timestamp AS published_at,
            NULL::timestamp AS collected_at,
        """

    if include_text:
        text_columns = """
            COALESCE(p.author, c.author) AS author,
            COALESCE(p.author_id, c.author_id) AS author_id,
            COALESCE(p.language, c.language) AS language,
            COALESCE(p.content_type, c.content_type) AS source_content_type,
            COALESCE(p.source_system, c.source_system) AS source_system,
            COALESCE(NULLIF(p.title, ''), NULLIF(p.text, ''), NULLIF(c.text, '')) AS text_content,
            COALESCE(p.url, NULL::text) AS url,
            COALESCE(p.like_count, c.like_count, 0) AS like_count,
            COALESCE(p.share_count, 0) AS share_count,
            COALESCE(p.comment_count, 0) AS comment_count,
            COALESCE(p.retweet_count, 0) AS retweet_count,
            COALESCE(p.reply_count, c.reply_count, 0) AS reply_count,
            COALESCE(p.quote_count, 0) AS quote_count,
            COALESCE(p.view_count, 0) AS view_count,
            (
                COALESCE(p.like_count, c.like_count, 0)
                + COALESCE(p.share_count, 0)
                + COALESCE(p.comment_count, 0)
                + COALESCE(p.retweet_count, 0)
                + COALESCE(p.reply_count, c.reply_count, 0)
                + COALESCE(p.quote_count, 0)
                + COALESCE(p.view_count, 0)
            )::bigint AS engagement_total,
            md5(lower(trim(COALESCE(NULLIF(p.text, ''), NULLIF(p.title, ''), NULLIF(c.text, ''), '')))) AS text_hash
        """
    else:
        text_columns = """
            NULL::text AS author,
            NULL::text AS author_id,
            NULL::text AS language,
            NULL::text AS source_content_type,
            NULL::text AS source_system,
            NULL::text AS text_content,
            NULL::text AS url,
            0::bigint AS like_count,
            0::bigint AS share_count,
            0::bigint AS comment_count,
            0::bigint AS retweet_count,
            0::bigint AS reply_count,
            0::bigint AS quote_count,
            0::bigint AS view_count,
            0::bigint AS engagement_total,
            NULL::text AS text_hash
        """

    return f"""
        SELECT
            r.analysis_id,
            r.run_id,
            r.content_kind,
            lower(r.platform)::text AS platform,
            r.external_id,
            r.source_post_id,
            r.source_comment_id,
            r.root_post_id,
            r.parent_comment_id,
            r.parent_external_id,
            r.is_reply,
            r.depth,
            r.status,
            r.pred_label,
            r.pred_hate,
            r.hate_probability::double precision AS hate_probability,
            COALESCE(r.hate_types, ARRAY[]::text[]) AS hate_types,
            r.pred_category,
            r.category_probability::double precision AS category_probability,
            COALESCE(r.categories, ARRAY[]::text[]) AS categories,
            r.alvo_identificado,
            r.evidencia_textual,
            r.justificativa_curta,
            r.model_name,
            r.prompt_version,
            r.inference_seconds::double precision AS inference_seconds,
            r.reused_from_analysis_id,
            r.analyzed_at,
            {date_columns}
            {text_columns}
        FROM public.v_gemma_hate_results r
        {join_sql}
        WHERE r.model_name = :model_name
        {status_filter}
    """


def _clean_filters(filters=None):
    filters = filters or {}

    def normalize_list(value):
        if value in (None, "", "Todas", "Todos", []):
            return []
        if isinstance(value, str):
            return [value]
        return [item for item in value if item not in (None, "", "Todas", "Todos")]

    return {
        "platforms": [item.lower() for item in normalize_list(filters.get("platforms"))],
        "content_kinds": normalize_list(filters.get("content_kinds")),
        "pred_labels": normalize_list(filters.get("pred_labels")),
        "hate_types": [
            item for item in normalize_list(filters.get("hate_types"))
            if item not in EXCLUDED_HATE_TYPES
        ],
        "date_start": filters.get("date_start"),
        "date_end": filters.get("date_end"),
        "search_text": (filters.get("search_text") or "").strip(),
    }


def _where_sql(filters=None, alias="b"):
    filters = _clean_filters(filters)
    clauses = []
    params = {"model_name": MODEL_NAME}

    if filters["platforms"]:
        clauses.append(f"{alias}.platform = ANY(:platforms)")
        params["platforms"] = filters["platforms"]

    if filters["content_kinds"]:
        clauses.append(f"{alias}.content_kind = ANY(:content_kinds)")
        params["content_kinds"] = filters["content_kinds"]

    if filters["pred_labels"]:
        clauses.append(f"{alias}.pred_label = ANY(:pred_labels)")
        params["pred_labels"] = filters["pred_labels"]

    if filters["hate_types"]:
        clauses.append(
            f"{alias}.hate_types && CAST(:hate_types AS text[])"
        )
        params["hate_types"] = filters["hate_types"]

    if filters["date_start"]:
        clauses.append(f"{alias}.published_at::date >= :date_start")
        params["date_start"] = filters["date_start"]

    if filters["date_end"]:
        clauses.append(f"{alias}.published_at::date <= :date_end")
        params["date_end"] = filters["date_end"]

    if filters["search_text"]:
        clauses.append(f"{alias}.text_content ILIKE :search_text")
        params["search_text"] = f"%{filters['search_text']}%"

    if not clauses:
        return "", params

    return "WHERE " + "\n  AND ".join(clauses), params


def _has_date_filter(filters=None):
    filters = _clean_filters(filters)
    return bool(filters["date_start"] or filters["date_end"])


def _has_text_filter(filters=None):
    filters = _clean_filters(filters)
    return bool(filters["search_text"])


def _filtered_cte(filters=None, include_text=False, include_dates=False):
    include_text = include_text or _has_text_filter(filters)
    include_dates = include_dates or include_text or _has_date_filter(filters)
    where_sql, params = _where_sql(filters, "b")
    query = f"""
    WITH base AS (
        {_base_sql(include_text=include_text, include_dates=include_dates)}
    ),
    filtered AS (
        SELECT *
        FROM base b
        {where_sql}
    )
    """
    return query, params


def _add_labels(df):
    if "hate_types" in df.columns:
        def clean_hate_types(value):
            if isinstance(value, (list, tuple)):
                return [item for item in value if item not in EXCLUDED_HATE_TYPES]
            return value

        df["hate_types"] = df["hate_types"].apply(clean_hate_types)

    if "platform" in df.columns:
        df["platform_label"] = df["platform"].map(PLATFORM_LABELS).fillna(df["platform"])

    if "content_kind" in df.columns:
        df["content_kind_label"] = (
            df["content_kind"].map(CONTENT_KIND_LABELS).fillna(df["content_kind"])
        )

    if "pred_label" in df.columns:
        df["pred_label_label"] = df["pred_label"].map(PRED_LABELS).fillna(df["pred_label"])

    if "hate_type" in df.columns:
        df["hate_type_label"] = df["hate_type"].map(HATE_TYPE_LABELS).fillna(df["hate_type"])

    if "hate_type_a" in df.columns:
        df["hate_type_a_label"] = (
            df["hate_type_a"].map(HATE_TYPE_LABELS).fillna(df["hate_type_a"])
        )

    if "hate_type_b" in df.columns:
        df["hate_type_b_label"] = (
            df["hate_type_b"].map(HATE_TYPE_LABELS).fillna(df["hate_type_b"])
        )

    return df


def get_database_label():
    return run_query("SELECT current_database() AS database_name").iloc[0]["database_name"]


@lru_cache(maxsize=1)
def get_filter_options():
    options = {
        "platforms": EXPECTED_PLATFORMS,
        "content_kinds": list(CONTENT_KIND_LABELS.keys()),
        "pred_labels": list(PRED_LABELS.keys()),
        "hate_types": [key for key in HATE_TYPE_LABELS if key not in EXCLUDED_HATE_TYPES],
        "min_date": None,
        "max_date": None,
    }

    summary_query = """
    SELECT
        ARRAY(
            SELECT DISTINCT lower(platform)::text
            FROM public.v_gemma_hate_summary
            WHERE model_name = :model_name
            ORDER BY lower(platform)::text
        ) AS platforms,
        ARRAY(
            SELECT DISTINCT content_kind
            FROM public.v_gemma_hate_summary
            WHERE model_name = :model_name
            ORDER BY content_kind
        ) AS content_kinds,
        ARRAY(
            SELECT DISTINCT pred_label
            FROM public.v_gemma_hate_summary
            WHERE model_name = :model_name
              AND pred_label IS NOT NULL
            ORDER BY pred_label
        ) AS pred_labels
    """

    try:
        summary = run_query(summary_query, {"model_name": MODEL_NAME}).iloc[0].to_dict()
        for key in ("platforms", "content_kinds", "pred_labels"):
            if summary.get(key):
                options[key] = summary[key]
    except Exception:
        pass

    hate_type_query = """
    SELECT ARRAY(
        SELECT DISTINCT hate_type
        FROM (
            SELECT unnest(COALESCE(hate_types, ARRAY[]::text[])) AS hate_type
            FROM public.v_gemma_hate_results
            WHERE model_name = :model_name
              AND status = 'success'
              AND pred_label = 'hate'
        ) t
        WHERE hate_type IS NOT NULL
          AND hate_type <> 'other'
        ORDER BY hate_type
    ) AS hate_types
    """

    try:
        hate_types = run_query(hate_type_query, {"model_name": MODEL_NAME}).iloc[0]["hate_types"]
        if hate_types:
            options["hate_types"] = hate_types
    except Exception:
        pass

    date_query = """
    SELECT
        MIN(COALESCE(p.published_at, c.published_at))::date AS min_date,
        MAX(COALESCE(p.published_at, c.published_at))::date AS max_date
    FROM public.v_gemma_hate_results r
    LEFT JOIN public.posts p
        ON r.source_post_id = p.id
    LEFT JOIN public.comments c
        ON r.source_comment_id = c.id
    WHERE r.model_name = :model_name
      AND r.status = 'success'
      AND COALESCE(p.published_at, c.published_at)::date <= CURRENT_DATE
    """

    fallback_date_query = """
    SELECT
        MIN(analyzed_at)::date AS min_date,
        MAX(analyzed_at)::date AS max_date
    FROM public.v_gemma_hate_results
    WHERE model_name = :model_name
      AND status = 'success'
      AND analyzed_at::date <= CURRENT_DATE
    """

    for query in (date_query, fallback_date_query):
        try:
            dates = run_query(query, {"model_name": MODEL_NAME}).iloc[0].to_dict()
            if dates.get("min_date") and dates.get("max_date"):
                options["min_date"] = dates["min_date"]
                options["max_date"] = dates["max_date"]
                break
        except Exception:
            continue

    return options


def get_overview_metrics(filters=None):
    cte, params = _filtered_cte(filters, include_dates=True)
    query = f"""
    {cte}
    SELECT
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        COUNT(*) FILTER (WHERE pred_label = 'nao_hate')::bigint AS total_non_hate,
        COUNT(*) FILTER (WHERE pred_label IS NULL)::bigint AS total_without_label,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent,
        COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS total_posts,
        COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS total_comments,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE content_kind = 'post' AND pred_label = 'hate')
            / NULLIF(COUNT(*) FILTER (WHERE content_kind = 'post'), 0),
            2
        )::double precision AS post_hate_percent,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE content_kind = 'comment' AND pred_label = 'hate')
            / NULLIF(COUNT(*) FILTER (WHERE content_kind = 'comment'), 0),
            2
        )::double precision AS comment_hate_percent,
        COUNT(DISTINCT platform)::integer AS total_platforms,
        MIN(published_at)::date AS min_date,
        MAX(published_at)::date AS max_date
    FROM filtered
    """
    return run_query(query, params)


def get_platform_analysis(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte}
    SELECT
        platform,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        COUNT(*) FILTER (WHERE pred_label = 'nao_hate')::bigint AS total_non_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent,
        COUNT(*) < 1000 AS low_sample
    FROM filtered
    GROUP BY platform
    ORDER BY hate_percent DESC NULLS LAST, total_hate DESC
    """
    return _add_labels(run_query(query, params))


def get_content_kind_analysis(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte}
    SELECT
        content_kind,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent
    FROM filtered
    GROUP BY content_kind
    ORDER BY total_content DESC
    """
    return _add_labels(run_query(query, params))


def get_platform_kind_comparison(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte}
    SELECT
        platform,
        COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS posts_total,
        COUNT(*) FILTER (WHERE content_kind = 'post' AND pred_label = 'hate')::bigint AS posts_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE content_kind = 'post' AND pred_label = 'hate')
            / NULLIF(COUNT(*) FILTER (WHERE content_kind = 'post'), 0),
            2
        )::double precision AS posts_hate_percent,
        COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS comments_total,
        COUNT(*) FILTER (WHERE content_kind = 'comment' AND pred_label = 'hate')::bigint AS comments_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE content_kind = 'comment' AND pred_label = 'hate')
            / NULLIF(COUNT(*) FILTER (WHERE content_kind = 'comment'), 0),
            2
        )::double precision AS comments_hate_percent
    FROM filtered
    GROUP BY platform
    ORDER BY platform
    """
    return _add_labels(run_query(query, params))


def get_hate_type_frequency(filters=None, limit=30):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    hate_records AS (
        SELECT COUNT(*)::double precision AS total_hate_records
        FROM filtered
        WHERE pred_label = 'hate'
    ),
    type_mentions AS (
        SELECT hate_type
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
    ),
    mention_total AS (
        SELECT COUNT(*)::double precision AS total_mentions
        FROM type_mentions
    )
    SELECT
        hate_type,
        COUNT(*)::bigint AS total_mentions,
        ROUND(
            (
                100.0 * COUNT(*)
                / NULLIF((SELECT total_mentions FROM mention_total), 0)
            )::numeric,
            2
        )
            ::double precision AS percent_of_mentions,
        ROUND(
            (
                100.0 * COUNT(*)
                / NULLIF((SELECT total_hate_records FROM hate_records), 0)
            )::numeric,
            2
        )
            ::double precision AS percent_of_hate_records
    FROM type_mentions
    WHERE hate_type <> 'other'
    GROUP BY hate_type
    ORDER BY total_mentions DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_hate_type_by_platform(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte},
    type_mentions AS (
        SELECT
            platform,
            unnest(hate_types) AS hate_type
        FROM filtered
        WHERE pred_label = 'hate'
    )
    SELECT
        platform,
        hate_type,
        COUNT(*)::bigint AS total_mentions
    FROM type_mentions
    WHERE hate_type <> 'other'
    GROUP BY platform, hate_type
    ORDER BY platform, total_mentions DESC
    """
    return _add_labels(run_query(query, params))


def get_dominant_hate_type_by_platform(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte},
    type_mentions AS (
        SELECT platform, unnest(hate_types) AS hate_type
        FROM filtered
        WHERE pred_label = 'hate'
    ),
    ranked AS (
        SELECT
            platform,
            hate_type,
            COUNT(*)::bigint AS total_mentions,
            ROW_NUMBER() OVER (
                PARTITION BY platform
                ORDER BY COUNT(*) DESC, hate_type
            ) AS rn
        FROM type_mentions
        WHERE hate_type <> 'other'
        GROUP BY platform, hate_type
    )
    SELECT platform, hate_type, total_mentions
    FROM ranked
    WHERE rn = 1
    ORDER BY total_mentions DESC
    """
    return _add_labels(run_query(query, params))


def get_hate_type_cooccurrence(filters=None, limit=30):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    typed AS (
        SELECT
            analysis_id,
            ARRAY(
                SELECT DISTINCT item
                FROM unnest(hate_types) item
                WHERE item IS NOT NULL
                  AND item <> 'other'
                ORDER BY item
            ) AS types
        FROM filtered
        WHERE pred_label = 'hate'
          AND cardinality(array_remove(hate_types, 'other')) >= 2
    )
    SELECT
        a AS hate_type_a,
        b AS hate_type_b,
        COUNT(*)::bigint AS total_cooccurrences
    FROM typed
    CROSS JOIN LATERAL unnest(types) a
    CROSS JOIN LATERAL unnest(types) b
    WHERE a < b
    GROUP BY a, b
    ORDER BY total_cooccurrences DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_hate_type_by_content_kind(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte},
    type_mentions AS (
        SELECT
            content_kind,
            unnest(hate_types) AS hate_type
        FROM filtered
        WHERE pred_label = 'hate'
    )
    SELECT
        content_kind,
        hate_type,
        COUNT(*)::bigint AS total_mentions
    FROM type_mentions
    WHERE hate_type <> 'other'
    GROUP BY content_kind, hate_type
    ORDER BY content_kind, total_mentions DESC
    """
    return _add_labels(run_query(query, params))


def get_temporal_analysis(filters=None, grain="month"):
    grain = grain if grain in {"day", "week", "month", "year"} else "month"
    cte, params = _filtered_cte(filters, include_dates=True)
    query = f"""
    {cte}
    SELECT
        DATE_TRUNC('{grain}', published_at)::date AS period,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent
    FROM filtered
    WHERE published_at IS NOT NULL
    GROUP BY period
    ORDER BY period
    """
    return run_query(query, params)


def get_temporal_type_trends(filters=None, grain="month", limit=6):
    grain = grain if grain in {"day", "week", "month", "year"} else "month"
    cte, params = _filtered_cte(filters, include_dates=True)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    top_types AS (
        SELECT hate_type, COUNT(*) AS total
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
        GROUP BY hate_type
        ORDER BY total DESC
        LIMIT :limit
    ),
    exploded AS (
        SELECT
            DATE_TRUNC('{grain}', published_at)::date AS period,
            hate_type
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND published_at IS NOT NULL
          AND hate_type <> 'other'
    )
    SELECT
        e.period,
        e.hate_type,
        COUNT(*)::bigint AS total_mentions
    FROM exploded e
    INNER JOIN top_types t
        ON t.hate_type = e.hate_type
    GROUP BY e.period, e.hate_type
    ORDER BY e.period, total_mentions DESC
    """
    return _add_labels(run_query(query, params))


def get_quality_metrics(filters=None):
    cte, params = _filtered_cte(filters, include_text=True)
    query = f"""
    {cte},
    duplicates AS (
        SELECT text_hash, COUNT(*) AS total_rows
        FROM filtered
        WHERE text_content IS NOT NULL
          AND trim(text_content) <> ''
        GROUP BY text_hash
        HAVING COUNT(*) > 1
    ),
    errors AS (
        SELECT
            COUNT(*) FILTER (WHERE status <> 'success')::bigint AS total_errors,
            COUNT(*) FILTER (WHERE pred_label IS NULL)::bigint AS total_null_labels
        FROM public.v_gemma_hate_results
        WHERE model_name = :model_name
    )
    SELECT
        COUNT(*)::bigint AS total_filtered,
        COUNT(*) FILTER (WHERE text_content IS NULL OR trim(text_content) = '')::bigint
            AS empty_text_records,
        COUNT(*) FILTER (WHERE published_at IS NULL)::bigint AS missing_date_records,
        COUNT(*) FILTER (WHERE published_at::date > CURRENT_DATE)::bigint AS future_date_records,
        (SELECT COUNT(*) FROM duplicates)::bigint AS duplicate_groups,
        COALESCE((SELECT SUM(total_rows) FROM duplicates), 0)::bigint AS duplicate_rows,
        (SELECT total_errors FROM errors)::bigint AS model_error_records,
        (SELECT total_null_labels FROM errors)::bigint AS null_label_records
    FROM filtered
    """
    return run_query(query, params)


def get_low_sample_platforms(filters=None, threshold=1000):
    cte, params = _filtered_cte(filters)
    params["threshold"] = int(threshold)
    query = f"""
    {cte}
    SELECT
        platform,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent
    FROM filtered
    GROUP BY platform
    HAVING COUNT(*) < :threshold
    ORDER BY total_content ASC
    """
    return _add_labels(run_query(query, params))


def get_evidence_examples(filters=None, limit_per_type=2):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit_per_type"] = int(limit_per_type)
    query = f"""
    {cte},
    exploded AS (
        SELECT
            hate_type,
            platform,
            content_kind,
            hate_probability,
            evidencia_textual,
            justificativa_curta,
            left(regexp_replace(COALESCE(text_content, ''), '\\s+', ' ', 'g'), 420)
                AS text_excerpt,
            ROW_NUMBER() OVER (
                PARTITION BY hate_type
                ORDER BY hate_probability DESC NULLS LAST, analyzed_at DESC NULLS LAST
            ) AS rn
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
          AND text_content IS NOT NULL
    )
    SELECT
        hate_type,
        platform,
        content_kind,
        hate_probability,
        evidencia_textual,
        justificativa_curta,
        text_excerpt
    FROM exploded
    WHERE rn <= :limit_per_type
    ORDER BY hate_type, hate_probability DESC NULLS LAST
    """
    return _add_labels(run_query(query, params))


def get_records_page(filters=None, page=1, page_size=50):
    page = max(int(page), 1)
    page_size = max(min(int(page_size), 500), 10)
    offset = (page - 1) * page_size
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = page_size
    params["offset"] = offset
    query = f"""
    {cte}
    SELECT
        analysis_id,
        external_id,
        source_post_id,
        source_comment_id,
        platform,
        content_kind,
        pred_label,
        hate_probability,
        hate_types,
        pred_category,
        category_probability,
        alvo_identificado,
        published_at,
        analyzed_at,
        left(regexp_replace(COALESCE(text_content, ''), '\\s+', ' ', 'g'), 700)
            AS text_excerpt,
        evidencia_textual,
        justificativa_curta
    FROM filtered
    ORDER BY analyzed_at DESC NULLS LAST, analysis_id DESC
    LIMIT :limit
    OFFSET :offset
    """
    return _add_labels(run_query(query, params))


def get_records_count(filters=None):
    cte, params = _filtered_cte(filters)
    query = f"""
    {cte}
    SELECT COUNT(*)::bigint AS total
    FROM filtered
    """
    return int(run_query(query, params).iloc[0]["total"])


def get_hate_type_toxicity_timeseries(
    filters=None,
    grain="month",
    year=None,
    month=None,
    limit=8,
):
    grain = grain if grain in {"day", "week", "month", "year"} else "month"
    cte, params = _filtered_cte(filters, include_dates=True)
    params["limit"] = int(limit)

    date_clause = ""
    if year:
        params["year"] = int(year)
        date_clause += " AND EXTRACT(YEAR FROM published_at) = :year"

    if month:
        params["month"] = int(month)
        date_clause += " AND EXTRACT(MONTH FROM published_at) = :month"

    query = f"""
    {cte},
    typed AS (
        SELECT
            DATE_TRUNC('{grain}', published_at)::date AS period,
            hate_type,
            hate_probability
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND published_at IS NOT NULL
          AND published_at::date <= CURRENT_DATE
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
          {date_clause}
    ),
    top_types AS (
        SELECT hate_type, COUNT(*) AS total
        FROM typed
        GROUP BY hate_type
        ORDER BY total DESC
        LIMIT :limit
    )
    SELECT
        t.period,
        t.hate_type,
        COUNT(*)::bigint AS total_mentions,
        ROUND(AVG(t.hate_probability)::numeric, 4)::double precision AS avg_toxicity
    FROM typed t
    INNER JOIN top_types tt
        ON tt.hate_type = t.hate_type
    GROUP BY t.period, t.hate_type
    ORDER BY t.period, t.hate_type
    """
    return _add_labels(run_query(query, params))


def get_hate_type_toxicity_summary(filters=None, year=None, month=None, limit=12):
    cte, params = _filtered_cte(filters, include_dates=True)
    params["limit"] = int(limit)

    date_clause = ""
    if year:
        params["year"] = int(year)
        date_clause += " AND EXTRACT(YEAR FROM published_at) = :year"

    if month:
        params["month"] = int(month)
        date_clause += " AND EXTRACT(MONTH FROM published_at) = :month"

    query = f"""
    {cte},
    typed AS (
        SELECT
            hate_type,
            hate_probability,
            platform,
            content_kind
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND published_at IS NOT NULL
          AND published_at::date <= CURRENT_DATE
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
          {date_clause}
    )
    SELECT
        hate_type,
        COUNT(*)::bigint AS total_mentions,
        COUNT(DISTINCT platform)::integer AS total_platforms,
        COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS post_mentions,
        COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS comment_mentions,
        ROUND(AVG(hate_probability)::numeric, 4)::double precision AS avg_toxicity
    FROM typed
    GROUP BY hate_type
    ORDER BY avg_toxicity DESC NULLS LAST, total_mentions DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_top_terms_sql(filters=None, limit=80, text_source="evidence"):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    source_expression = (
        "COALESCE(NULLIF(evidencia_textual, ''), text_content)"
        if text_source == "evidence"
        else "text_content"
    )
    stopwords = [
        "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do",
        "dos", "e", "em", "era", "essa", "esse", "esta", "este", "eu",
        "foi", "mais", "mas", "me", "muito", "na", "n?o", "nas", "no",
        "nos", "o", "os", "ou", "para", "pela", "pelo", "por", "pra",
        "pro", "que", "se", "sem", "ser", "sua", "s?o", "tem", "um",
        "uma", "vai", "voc?", "voc?s", "ele", "ela", "eles", "elas",
        "isso", "isto", "aquilo", "aqui", "ali", "l?", "todo", "toda",
        "todos", "todas", "quem", "qual", "quais", "quando", "onde",
        "porque", "porqu?", "assim", "ainda", "j?", "at?", "tamb?m",
        "mesmo", "mesma", "mesmos", "mesmas", "meu", "minha", "meus",
        "minhas", "seu", "seus", "dele", "dela", "deles", "delas",
        "tudo", "nada", "cada", "sobre", "entre", "contra", "apenas",
        "agora", "hoje", "dia", "cara", "tipo", "coisa", "gente",
        "pessoa", "pessoas", "ter", "vou", "t?", "ta", "est?", "estava",
        "estao", "est?o", "ser?", "bem", "pode", "podem", "podia",
        "fazer", "faz", "fez", "feito", "nosso", "nossa", "nossos",
        "nossas", "suas", "pois", "sim", "nem", "ent?o", "foram",
        "vamos", "nunca", "tempo", "ano", "anos", "mundo", "phone",
        "nao", "sao", "voce", "voces", "esta", "estao", "sera", "ate",
        "tambem", "ja", "la", "ta", "entao",
        "esses", "essas", "desse", "dessa", "desses", "dessas", "aquele",
        "aquela", "aqueles", "aquelas", "falar", "fala", "falou", "quer",
        "ver", "sempre", "kkkk", "kkkkk", "kkk", "rsrs",
        "http", "https", "www", "com", "br", "net", "org", "html", "php",
        "amp", "utm", "utm_source", "utm_medium", "utm_campaign", "ref",
        "t", "co", "bit", "ly", "tinyurl", "youtu", "youtube", "facebook",
        "instagram", "twitter", "reddit", "telegram", "tiktok", "whatsapp",
    ]

    params["stopwords"] = stopwords
    query = f"""
    {cte},
    tokens AS (
        SELECT
            lower(token) AS term,
            translate(
                lower(token),
                'áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ',
                'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC'
            ) AS normalized_term
        FROM filtered
        CROSS JOIN LATERAL regexp_split_to_table(
            regexp_replace(
                regexp_replace(
                    COALESCE({source_expression}, ''),
                    'https?://[^[:space:]]+|www\\.[^[:space:]]+',
                    ' ',
                    'gi'
                ),
                '[^[:alnum:]#_]+',
                ' ',
                'g'
            ),
            '\\s+'
        ) AS token
    )
    SELECT
        term,
        COUNT(*)::bigint AS frequency
    FROM tokens
    WHERE length(term) > 2
      AND NOT term = ANY(:stopwords)
      AND NOT normalized_term = ANY(:stopwords)
      AND term !~ '^[0-9]+$'
      AND term !~ '^(http|https|www|com|br|net|org|html|php|amp|utm|ref|t|co|bit|ly|youtu|youtube)$'
      AND term !~ '^[a-f0-9]{10,}$'
      AND term NOT LIKE 'http%'
      AND term NOT LIKE 'www%'
    GROUP BY term
    ORDER BY frequency DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_pred_category_distribution(filters=None, limit=30):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    categories AS (
        SELECT
            trim(token) AS pred_category_item
        FROM filtered
        CROSS JOIN LATERAL regexp_split_to_table(
            CASE
                WHEN pred_category IS NULL OR pred_category = 'None'
                    THEN 'Sem categoria'
                ELSE pred_category
            END,
            '\\s*;\\s*'
        ) AS token
    )
    SELECT
        pred_category_item,
        COUNT(*)::bigint AS total,
        ROUND(
            (100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0))::numeric,
            2
        )::double precision AS percent_total
    FROM categories
    WHERE pred_category_item <> ''
    GROUP BY pred_category_item
    ORDER BY total DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_pred_category_by_platform(filters=None, limit=120):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    categories AS (
        SELECT
            platform,
            trim(token) AS pred_category_item
        FROM filtered
        CROSS JOIN LATERAL regexp_split_to_table(
            CASE
                WHEN pred_category IS NULL OR pred_category = 'None'
                    THEN 'Sem categoria'
                ELSE pred_category
            END,
            '\\s*;\\s*'
        ) AS token
    )
    SELECT
        platform,
        pred_category_item,
        COUNT(*)::bigint AS total
    FROM categories
    WHERE pred_category_item <> ''
    GROUP BY platform, pred_category_item
    ORDER BY total DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_category_temporal(filters=None, grain="month", limit=8):
    grain = grain if grain in {"day", "week", "month", "year"} else "month"
    cte, params = _filtered_cte(filters, include_dates=True)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    categories AS (
        SELECT
            DATE_TRUNC('{grain}', published_at)::date AS period,
            trim(token) AS pred_category_item
        FROM filtered
        CROSS JOIN LATERAL regexp_split_to_table(
            CASE
                WHEN pred_category IS NULL OR pred_category = 'None'
                    THEN 'Sem categoria'
                ELSE pred_category
            END,
            '\\s*;\\s*'
        ) AS token
        WHERE published_at IS NOT NULL
    ),
    top_categories AS (
        SELECT pred_category_item, COUNT(*) AS total
        FROM categories
        GROUP BY pred_category_item
        ORDER BY total DESC
        LIMIT :limit
    )
    SELECT
        c.period,
        c.pred_category_item,
        COUNT(*)::bigint AS total
    FROM categories c
    INNER JOIN top_categories t
        ON t.pred_category_item = c.pred_category_item
    GROUP BY c.period, c.pred_category_item
    ORDER BY c.period, total DESC
    """
    return run_query(query, params)


def get_probability_by_category(filters=None, limit=20):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    query = f"""
    {cte},
    categories AS (
        SELECT
            trim(token) AS pred_category_item,
            hate_probability,
            category_probability
        FROM filtered
        CROSS JOIN LATERAL regexp_split_to_table(
            CASE
                WHEN pred_category IS NULL OR pred_category = 'None'
                    THEN 'Sem categoria'
                ELSE pred_category
            END,
            '\\s*;\\s*'
        ) AS token
    )
    SELECT
        pred_category_item,
        COUNT(*)::bigint AS total,
        ROUND(AVG(hate_probability)::numeric, 4)::double precision AS avg_hate_probability,
        ROUND(AVG(category_probability)::numeric, 4)::double precision AS avg_category_probability
    FROM categories
    WHERE pred_category_item <> ''
    GROUP BY pred_category_item
    ORDER BY total DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_source_system_analysis(filters=None, limit=30):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    query = f"""
    {cte}
    SELECT
        platform,
        COALESCE(NULLIF(source_system, ''), 'não informado') AS source_system,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent,
        ROUND(AVG(hate_probability)::numeric, 4)::double precision AS avg_hate_probability,
        SUM(engagement_total)::bigint AS engagement_total
    FROM filtered
    GROUP BY platform, source_system
    ORDER BY total_content DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_language_distribution(filters=None, limit=20):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    query = f"""
    {cte}
    SELECT
        COALESCE(NULLIF(language, ''), 'não informado') AS language,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent
    FROM filtered
    GROUP BY language
    ORDER BY total_content DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_content_source_type_distribution(filters=None, limit=20):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    query = f"""
    {cte}
    SELECT
        COALESCE(NULLIF(source_content_type, ''), content_kind, 'não informado')
            AS source_content_type,
        content_kind,
        COUNT(*)::bigint AS total_content,
        COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
            / NULLIF(COUNT(*), 0),
            2
        )::double precision AS hate_percent
    FROM filtered
    GROUP BY source_content_type, content_kind
    ORDER BY total_content DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_author_analysis(filters=None, limit=100, min_records=3):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    params["min_records"] = int(min_records)
    query = f"""
    {cte},
    author_rows AS (
        SELECT
            md5(lower(trim(COALESCE(NULLIF(author_id, ''), NULLIF(author, ''))))) AS author_hash,
            platform,
            content_kind,
            pred_label,
            hate_probability,
            engagement_total
        FROM filtered
        WHERE COALESCE(NULLIF(author_id, ''), NULLIF(author, '')) IS NOT NULL
          AND lower(COALESCE(author, '')) NOT IN ('[deleted]', 'deleted', 'unknown')
    ),
    grouped AS (
        SELECT
            author_hash,
            COUNT(*)::bigint AS total_content,
            COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
                / NULLIF(COUNT(*), 0),
                2
            )::double precision AS hate_percent,
            COUNT(DISTINCT platform)::integer AS total_platforms,
            COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS total_posts,
            COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS total_comments,
            ROUND(AVG(hate_probability)::numeric, 4)::double precision AS avg_hate_probability,
            SUM(engagement_total)::bigint AS engagement_total
        FROM author_rows
        GROUP BY author_hash
        HAVING COUNT(*) >= :min_records
    )
    SELECT
        'PERFIL_' || lpad(ROW_NUMBER() OVER (
            ORDER BY total_hate DESC, total_content DESC
        )::text, 4, '0') AS profile_id,
        author_hash,
        total_content,
        total_hate,
        hate_percent,
        total_platforms,
        total_posts,
        total_comments,
        avg_hate_probability,
        engagement_total
    FROM grouped
    ORDER BY total_hate DESC, total_content DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_author_type_distribution(filters=None, limit=80, min_records=3):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    params["min_records"] = int(min_records)
    query = f"""
    {cte},
    author_types AS (
        SELECT
            md5(lower(trim(COALESCE(NULLIF(author_id, ''), NULLIF(author, ''))))) AS author_hash,
            hate_type
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND COALESCE(NULLIF(author_id, ''), NULLIF(author, '')) IS NOT NULL
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
    ),
    grouped AS (
        SELECT
            author_hash,
            hate_type,
            COUNT(*)::bigint AS total_mentions
        FROM author_types
        GROUP BY author_hash, hate_type
        HAVING COUNT(*) >= :min_records
    )
    SELECT
        author_hash,
        hate_type,
        total_mentions
    FROM grouped
    ORDER BY total_mentions DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_post_analysis(filters=None, limit=100, min_records=3):
    cte, params = _filtered_cte(filters, include_text=True)
    params["limit"] = int(limit)
    params["min_records"] = int(min_records)
    query = f"""
    {cte},
    grouped AS (
        SELECT
            platform,
            COALESCE(root_post_id, source_post_id) AS post_id,
            COUNT(*)::bigint AS total_records,
            COUNT(*) FILTER (WHERE content_kind = 'post')::bigint AS total_posts,
            COUNT(*) FILTER (WHERE content_kind = 'comment')::bigint AS total_comments,
            COUNT(*) FILTER (WHERE pred_label = 'hate')::bigint AS total_hate,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE pred_label = 'hate')
                / NULLIF(COUNT(*), 0),
                2
            )::double precision AS hate_percent,
            ROUND(AVG(hate_probability)::numeric, 4)::double precision AS avg_hate_probability,
            SUM(engagement_total)::bigint AS engagement_total,
            MIN(published_at)::date AS first_published_at,
            MAX(published_at)::date AS last_published_at
        FROM filtered
        WHERE COALESCE(root_post_id, source_post_id) IS NOT NULL
        GROUP BY platform, post_id
        HAVING COUNT(*) >= :min_records
    )
    SELECT
        g.platform,
        g.post_id,
        p.external_id,
        left(regexp_replace(COALESCE(NULLIF(p.title, ''), NULLIF(p.text, ''), '(sem título)'), '\\s+', ' ', 'g'), 220)
            AS post_title,
        p.url,
        g.total_records,
        g.total_posts,
        g.total_comments,
        g.total_hate,
        g.hate_percent,
        g.avg_hate_probability,
        g.engagement_total,
        g.first_published_at,
        g.last_published_at
    FROM grouped g
    LEFT JOIN public.posts p
        ON p.id = g.post_id
    ORDER BY total_hate DESC, total_records DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, params))


def get_records_for_post(post_id, filters=None, page=1, page_size=50):
    page = max(int(page), 1)
    page_size = max(min(int(page_size), 500), 10)
    offset = (page - 1) * page_size
    cte, params = _filtered_cte(filters, include_text=True)
    params["post_id"] = int(post_id)
    params["limit"] = page_size
    params["offset"] = offset
    query = f"""
    {cte}
    SELECT
        analysis_id,
        platform,
        content_kind,
        pred_label,
        hate_probability,
        hate_types,
        pred_category,
        published_at,
        left(regexp_replace(COALESCE(text_content, ''), '\\s+', ' ', 'g'), 700)
            AS text_excerpt,
        evidencia_textual,
        justificativa_curta
    FROM filtered
    WHERE COALESCE(root_post_id, source_post_id) = :post_id
    ORDER BY hate_probability DESC NULLS LAST, analyzed_at DESC NULLS LAST
    LIMIT :limit
    OFFSET :offset
    """
    return _add_labels(run_query(query, params))


def get_semantic_network_edges(filters=None, limit=200, min_weight=5):
    cte, params = _filtered_cte(filters)
    params["limit"] = int(limit)
    params["min_weight"] = int(min_weight)
    query = f"""
    {cte},
    type_mentions AS (
        SELECT
            platform,
            content_kind,
            hate_type
        FROM filtered
        CROSS JOIN LATERAL unnest(hate_types) AS ht(hate_type)
        WHERE pred_label = 'hate'
          AND cardinality(hate_types) > 0
          AND hate_type <> 'other'
    ),
    platform_edges AS (
        SELECT
            'rede:' || platform AS source,
            'tipo:' || hate_type AS target,
            'rede_tipo' AS relation,
            COUNT(*)::bigint AS total
        FROM type_mentions
        GROUP BY platform, hate_type
    ),
    kind_edges AS (
        SELECT
            'conteúdo:' || content_kind AS source,
            'tipo:' || hate_type AS target,
            'conteudo_tipo' AS relation,
            COUNT(*)::bigint AS total
        FROM type_mentions
        GROUP BY content_kind, hate_type
    ),
    typed AS (
        SELECT
            analysis_id,
            ARRAY(
                SELECT DISTINCT item
                FROM unnest(hate_types) item
                WHERE item IS NOT NULL
                  AND item <> 'other'
                ORDER BY item
            ) AS types
        FROM filtered
        WHERE pred_label = 'hate'
          AND cardinality(array_remove(hate_types, 'other')) >= 2
    ),
    cooc_edges AS (
        SELECT
            'tipo:' || a AS source,
            'tipo:' || b AS target,
            'coocorrencia' AS relation,
            COUNT(*)::bigint AS total
        FROM typed
        CROSS JOIN LATERAL unnest(types) a
        CROSS JOIN LATERAL unnest(types) b
        WHERE a < b
        GROUP BY a, b
    )
    SELECT *
    FROM (
        SELECT * FROM platform_edges
        UNION ALL
        SELECT * FROM kind_edges
        UNION ALL
        SELECT * FROM cooc_edges
    ) edges
    WHERE total >= :min_weight
    ORDER BY total DESC
    LIMIT :limit
    """
    return run_query(query, params)


def get_nli_layer3_summary():
    query = """
    SELECT
        COUNT(*)::bigint AS total_results,
        COUNT(DISTINCT platform)::integer AS total_platforms,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score,
        ROUND(AVG(toxicity_score)::numeric, 4)::double precision AS avg_toxicity_score
    FROM public.v_radar_nli_layer3_results
    """
    return run_query(query)


def get_nli_layer3_dimensions():
    query = """
    SELECT
        e.key AS dimension,
        ROUND(AVG((e.value #>> '{}')::double precision)::numeric, 4)::double precision
            AS avg_score,
        COUNT(*)::bigint AS total_mentions
    FROM public.v_radar_nli_layer3_results r
    CROSS JOIN LATERAL jsonb_each(COALESCE(r.dimension_scores, '{}'::jsonb)) e
    WHERE jsonb_typeof(e.value) IN ('number', 'string')
      AND (e.value #>> '{}') ~ '^-?[0-9]+(\\.[0-9]+)?$'
    GROUP BY e.key
    ORDER BY avg_score DESC NULLS LAST
    """
    return run_query(query)


def get_nli_layer3_by_platform():
    query = """
    SELECT
        lower(platform)::text AS platform,
        COUNT(*)::bigint AS total_results,
        COUNT(DISTINCT primary_dimension)::integer AS total_dimensions,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score,
        ROUND(AVG(toxicity_score)::numeric, 4)::double precision AS avg_toxicity_score,
        ROUND(AVG(gemma_hate_probability)::numeric, 4)::double precision
            AS avg_gemma_hate_probability,
        COUNT(*) FILTER (WHERE toxicity_label = 'alta')::bigint AS high_toxicity,
        COUNT(*) FILTER (WHERE toxicity_label = 'media')::bigint AS medium_toxicity,
        COUNT(*) FILTER (WHERE toxicity_label = 'baixa')::bigint AS low_toxicity,
        COUNT(*) FILTER (WHERE toxicity_label = 'nao_toxico')::bigint AS non_toxic
    FROM public.v_radar_nli_layer3_results
    GROUP BY lower(platform)::text
    ORDER BY avg_toxicity_score DESC NULLS LAST, total_results DESC
    """
    return _add_labels(run_query(query))


def get_nli_layer3_primary_dimensions(limit=20):
    query = """
    SELECT
        primary_dimension AS dimension,
        COUNT(*)::bigint AS total_results,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score,
        ROUND(AVG(toxicity_score)::numeric, 4)::double precision AS avg_toxicity_score,
        ROUND(AVG(gemma_hate_probability)::numeric, 4)::double precision
            AS avg_gemma_hate_probability
    FROM public.v_radar_nli_layer3_results
    WHERE primary_dimension IS NOT NULL
    GROUP BY primary_dimension
    ORDER BY total_results DESC, avg_primary_score DESC NULLS LAST
    LIMIT :limit
    """
    return run_query(query, {"limit": int(limit)})


def get_nli_layer3_toxicity_labels():
    query = """
    SELECT
        COALESCE(NULLIF(toxicity_label, ''), 'sem_label') AS toxicity_label,
        COUNT(*)::bigint AS total_results,
        ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2)::double precision
            AS percent_results,
        ROUND(AVG(toxicity_score)::numeric, 4)::double precision AS avg_toxicity_score,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score
    FROM public.v_radar_nli_layer3_results
    GROUP BY COALESCE(NULLIF(toxicity_label, ''), 'sem_label')
    ORDER BY avg_toxicity_score DESC NULLS LAST, total_results DESC
    """
    return run_query(query)


def get_nli_layer3_active_dimensions(limit=20):
    query = """
    WITH exploded AS (
        SELECT unnest(active_dimensions) AS dimension
        FROM public.v_radar_nli_layer3_results
        WHERE active_dimensions IS NOT NULL
          AND cardinality(active_dimensions) > 0
    )
    SELECT
        dimension,
        COUNT(*)::bigint AS total_results,
        ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM public.v_radar_nli_layer3_results), 0), 2)
            ::double precision AS percent_results
    FROM exploded
    WHERE dimension IS NOT NULL
    GROUP BY dimension
    ORDER BY total_results DESC
    LIMIT :limit
    """
    return run_query(query, {"limit": int(limit)})


def get_nli_layer3_gemma_buckets():
    query = """
    SELECT
        CASE
            WHEN gemma_hate_probability IS NULL THEN 'sem_probabilidade'
            WHEN gemma_hate_probability < 0.25 THEN '0.00-0.24'
            WHEN gemma_hate_probability < 0.50 THEN '0.25-0.49'
            WHEN gemma_hate_probability < 0.75 THEN '0.50-0.74'
            ELSE '0.75-1.00'
        END AS gemma_probability_bucket,
        COUNT(*)::bigint AS total_results,
        ROUND(AVG(toxicity_score)::numeric, 4)::double precision AS avg_nli_toxicity,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score
    FROM public.v_radar_nli_layer3_results
    GROUP BY gemma_probability_bucket
    ORDER BY gemma_probability_bucket
    """
    return run_query(query)


def get_nli_layer3_examples(limit=40):
    query = """
    SELECT
        result_id,
        lower(platform)::text AS platform,
        primary_dimension,
        ROUND(primary_score::numeric, 4)::double precision AS primary_score,
        ROUND(toxicity_score::numeric, 4)::double precision AS toxicity_score,
        toxicity_label,
        ROUND(gemma_hate_probability::numeric, 4)::double precision AS gemma_hate_probability,
        left(regexp_replace(COALESCE(text_snapshot, ''), '\\s+', ' ', 'g'), 700) AS text_excerpt,
        created_at
    FROM public.v_radar_nli_layer3_results
    ORDER BY toxicity_score DESC NULLS LAST, primary_score DESC NULLS LAST, result_id DESC
    LIMIT :limit
    """
    return _add_labels(run_query(query, {"limit": int(limit)}))


def get_nli_layer4_summary():
    query = """
    SELECT
        COUNT(*)::bigint AS total_results,
        COUNT(DISTINCT platform)::integer AS total_platforms,
        ROUND(AVG(primary_score)::numeric, 4)::double precision AS avg_primary_score
    FROM public.v_radar_nli_layer4_results
    """
    return run_query(query)


def get_nli_layer4_dimensions():
    query = """
    SELECT
        e.key AS dimension,
        ROUND(AVG((e.value #>> '{}')::double precision)::numeric, 4)::double precision
            AS avg_score,
        COUNT(*)::bigint AS total_mentions
    FROM public.v_radar_nli_layer4_results r
    CROSS JOIN LATERAL jsonb_each(COALESCE(r.dimension_scores, '{}'::jsonb)) e
    WHERE jsonb_typeof(e.value) IN ('number', 'string')
      AND (e.value #>> '{}') ~ '^-?[0-9]+(\\.[0-9]+)?$'
    GROUP BY e.key
    ORDER BY avg_score DESC NULLS LAST
    """
    return run_query(query)


def build_interpretive_report(filters=None):
    metrics = get_overview_metrics(filters).iloc[0]
    platforms = get_platform_analysis(filters)
    content_kind = get_content_kind_analysis(filters)
    top_types = get_hate_type_frequency(filters, 5)
    quality = get_quality_metrics(filters).iloc[0]
    low_sample = get_low_sample_platforms(filters)

    lines = []
    lines.append("### Principais achados")

    total = int(metrics["total_content"])
    hate = int(metrics["total_hate"])
    hate_pct = float(metrics["hate_percent"] or 0)
    lines.append(
        f"- Foram analisados {total:,} conteúdos classificados pelo modelo {MODEL_NAME}; "
        f"{hate:,} foram rotulados como discurso de ódio ({hate_pct:.2f}%)."
    )

    if not platforms.empty:
        top_pct = platforms.sort_values(
            ["hate_percent", "total_hate"], ascending=[False, False]
        ).iloc[0]
        top_abs = platforms.sort_values("total_hate", ascending=False).iloc[0]
        lines.append(
            f"- A maior prevalência proporcional aparece em "
            f"{top_pct['platform_label']} ({float(top_pct['hate_percent'] or 0):.2f}%). "
            f"Em volume absoluto, {top_abs['platform_label']} concentra "
            f"{int(top_abs['total_hate']):,} ocorrências de hate."
        )

    if not content_kind.empty:
        kind_text = []
        for _, row in content_kind.iterrows():
            kind_text.append(
                f"{row['content_kind_label']}: {float(row['hate_percent'] or 0):.2f}%"
            )
        lines.append("- Comparação por tipo de conteúdo: " + "; ".join(kind_text) + ".")

    if not top_types.empty:
        types_text = ", ".join(
            [
                f"{row['hate_type_label']} ({int(row['total_mentions']):,})"
                for _, row in top_types.iterrows()
            ]
        )
        lines.append(f"- Os tipos de ódio mais frequentes são: {types_text}.")

    lines.append("")
    lines.append("### Interpretação cautelosa")
    lines.append(
        "- As taxas devem ser lidas junto com o volume absoluto. Redes com amostra pequena "
        "podem aparecer com percentuais instáveis e não devem sustentar conclusões fortes."
    )

    if not low_sample.empty:
        small = ", ".join(
            [
                f"{row['platform_label']} ({int(row['total_content']):,} registros)"
                for _, row in low_sample.iterrows()
            ]
        )
        lines.append(f"- Amostras pequenas detectadas: {small}.")

    lines.append("")
    lines.append("### Qualidade e limitações")
    lines.append(
        "- A classificação é automatizada por modelo de linguagem e pode conter falsos "
        "positivos e falsos negativos; os resultados devem ser tratados como evidências "
        "analíticas, não como julgamento definitivo de cada conteúdo."
    )
    lines.append(
        f"- Foram identificados {int(quality['duplicate_rows']):,} registros em grupos de "
        f"textos duplicados, distribuídos em {int(quality['duplicate_groups']):,} grupos; "
        "isso pode inflar volumes e frequências."
    )
    lines.append(
        f"- Registros sem data utilizável: {int(quality['missing_date_records']):,}; "
        f"registros com data futura em relação ao dia de execução: "
        f"{int(quality['future_date_records']):,}."
    )
    lines.append(
        f"- Erros ou rótulos ausentes reportados pela camada Gemma: "
        f"{int(quality['model_error_records']):,} erros e "
        f"{int(quality['null_label_records']):,} rótulos nulos."
    )

    return "\n".join(lines)
