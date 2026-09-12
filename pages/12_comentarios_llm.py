import math
from html import escape

import pandas as pd
import streamlit as st

from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import PLATFORM_LABELS, get_filter_options, get_records_count, get_records_page


st.set_page_config(page_title="Comentários Analisados | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()

render_hero(
    "Comentários analisados",
    'Consulta de <span class="hero-gradient">classificações</span>',
    (
        "Consulte comentários classificados pelo modelo, com evidência textual, alvo identificado "
        "e justificativa curta para apoiar auditoria humana."
    ),
)


def _normalize_options(values):
    if values is None:
        return []
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [
        str(value)
        for value in values
        if value is not None and not pd.isna(value) and str(value).strip()
    ]


filter_options = get_filter_options()
available_platforms = [
    platform
    for platform in _normalize_options(filter_options.get("platforms"))
    if platform in PLATFORM_LABELS
]
platform_label_to_key = {
    PLATFORM_LABELS.get(platform, platform.title()): platform
    for platform in available_platforms
}
platform_labels = list(platform_label_to_key.keys())

filter_col, search_col = st.columns([1.1, 1.9])

with filter_col:
    selected_platform_labels = st.multiselect(
        "Plataformas",
        options=platform_labels,
        default=platform_labels,
        placeholder="Selecione uma ou mais plataformas",
    )

with search_col:
    search_text = st.text_input(
        "Buscar em comentários",
        placeholder="Digite um termo, expressão ou deixe vazio para listar comentários classificados.",
    )

if not selected_platform_labels:
    st.warning("Selecione ao menos uma plataforma para consultar os comentários.")
    st.stop()

selected_platforms = [platform_label_to_key[label] for label in selected_platform_labels]
filters = {"content_kinds": ["comment"]}

if len(selected_platforms) != len(available_platforms):
    filters["platforms"] = selected_platforms

if search_text.strip():
    filters["search_text"] = search_text.strip()

total_records = get_records_count(filters)
metric_grid(
    [
        ("Comentários", format_int(total_records)),
        ("Redes consultadas", format_int(len(selected_platforms))),
        ("Modelo", "gemma3:4b"),
    ]
)

section_header(
    "Comentários classificados",
    "Tabela paginada com conteúdo, classificação, tipos de preconceito detectados e explicação do modelo.",
)
page_size = st.selectbox("Comentários por página", [10, 25, 50, 100], index=1)
total_pages = max(math.ceil(total_records / page_size), 1)
page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

comments_df = get_records_page(filters, page=page, page_size=page_size)
st.caption(
    f"Total: {format_int(total_records)} comentários · página {page} de {total_pages} · "
    f"redes: {', '.join(selected_platform_labels)}"
)

if comments_df.empty:
    st.info("Nenhum comentário encontrado.")
    st.stop()


def format_types(value):
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value or "")


table = comments_df.copy()
table["hate_types_text"] = table["hate_types_label"].apply(format_types)
table_display = table.rename(
    columns={
        "analysis_id": "ID análise",
        "platform_label": "Rede",
        "pred_label_label": "Classificação",
        "hate_probability": "Probabilidade de discurso de ódio",
        "hate_types_text": "Tipos de preconceito",
        "pred_category_label": "Categoria de preconceito",
        "published_at": "Publicado em",
        "text_excerpt": "Comentário",
        "evidencia_textual": "Evidência",
        "justificativa_curta": "Justificativa",
    }
)
table_display["Probabilidade de discurso de ódio"] = table_display["Probabilidade de discurso de ódio"].apply(
    lambda value: format_pct(float(value or 0) * 100)
)

st.dataframe(
    table_display[
        [
            "ID análise",
            "Rede",
            "Classificação",
            "Probabilidade de discurso de ódio",
            "Tipos de preconceito",
            "Categoria de preconceito",
            "Publicado em",
            "Comentário",
            "Evidência",
            "Justificativa",
        ]
    ],
    width="stretch",
    height=520,
)

section_header(
    "Por que o modelo classificou assim?",
    "Selecione um comentário da página atual para ler a evidência, a justificativa e o alvo apontados pelo modelo.",
)
options = {
    (
        f"{row['analysis_id']} · {row['platform_label']} · "
        f"{row['pred_label_label']} · {str(row['text_excerpt'])[:90]}"
    ): row["analysis_id"]
    for _, row in table.iterrows()
}
selected_label = st.selectbox("Comentário", list(options.keys()))
selected_id = options[selected_label]
row = table.loc[table["analysis_id"] == selected_id].iloc[0]

comment_text = escape(str(row["text_excerpt"] or "(sem texto)"))
evidence_text = escape(str(row["evidencia_textual"] or "Sem evidência textual registrada."))
reason_text = escape(str(row["justificativa_curta"] or "Sem justificativa registrada."))
target_text = escape(str(row["alvo_identificado"] or "Nenhum alvo específico registrado."))

metric_grid(
    [
        ("Classificação", row["pred_label_label"]),
        ("Probabilidade de discurso de ódio", format_pct(float(row["hate_probability"] or 0) * 100)),
        ("Categoria de preconceito", row["pred_category_label"] or "sem categoria"),
        ("Tipos de preconceito", format_types(row["hate_types_label"]) or "sem tipo"),
    ]
)

left, right = st.columns(2)

with left:
    st.markdown(
        f"""
<div class="llm-card">
<div class="llm-label">Comentário analisado</div>
<div class="llm-text">{comment_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
<div class="llm-card">
<div class="llm-label">Evidência textual apontada</div>
<div class="llm-text">{evidence_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

left, right = st.columns(2)

with left:
    st.markdown(
        f"""
<div class="llm-card">
<div class="llm-label">Justificativa curta do modelo</div>
<div class="llm-text">{reason_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
<div class="llm-card">
<div class="llm-label">Alvo identificado</div>
<div class="llm-text">{target_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )
