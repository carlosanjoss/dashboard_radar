from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from wordcloud import WordCloud
except ModuleNotFoundError:
    WordCloud = None

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    CONTENT_KIND_LABELS,
    HATE_TYPE_LABELS,
    PLATFORM_LABELS,
    PRED_LABELS,
    get_filter_options,
    get_top_terms_sql,
)


st.set_page_config(page_title="Léxico | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()

render_hero(
    "Léxico",
    'Termos do <span class="hero-gradient">discurso de ódio</span>',
    (
        "Crie uma nuvem lexical focada nos conteúdos classificados como hate. "
        "Use os filtros para comparar redes, posts, comentários e tipos específicos de ódio."
    ),
)


def normalize_options(values):
    if values is None:
        return []
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [
        str(value)
        for value in values
        if value is not None and not pd.isna(value) and str(value).strip()
    ]


def build_label_map(values, labels):
    return {
        labels.get(value, value): value
        for value in values
        if value in labels or value
    }


filter_options = get_filter_options()
platforms = [
    platform
    for platform in normalize_options(filter_options.get("platforms"))
    if platform in PLATFORM_LABELS
]
content_kinds = [
    kind
    for kind in normalize_options(filter_options.get("content_kinds"))
    if kind in CONTENT_KIND_LABELS
]
pred_labels = [
    label
    for label in normalize_options(filter_options.get("pred_labels"))
    if label in PRED_LABELS
]
hate_types = [
    hate_type
    for hate_type in normalize_options(filter_options.get("hate_types"))
    if hate_type in HATE_TYPE_LABELS and hate_type != "other"
]

platform_map = build_label_map(platforms, PLATFORM_LABELS)
kind_map = build_label_map(content_kinds, CONTENT_KIND_LABELS)
pred_map = build_label_map(pred_labels, PRED_LABELS)
hate_type_map = build_label_map(hate_types, HATE_TYPE_LABELS)

section_header(
    "Filtros da wordcloud",
    "Por padrão, a nuvem usa apenas conteúdos classificados como hate. Altere a classificação se quiser comparar outros recortes.",
)

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    selected_platform_labels = st.multiselect(
        "Redes sociais",
        options=list(platform_map.keys()),
        default=list(platform_map.keys()),
        placeholder="Selecione uma ou mais redes",
    )
with row1_col2:
    default_pred_labels = ["Hate"] if "Hate" in pred_map else list(pred_map.keys())
    selected_pred_labels = st.multiselect(
        "Classificação",
        options=list(pred_map.keys()),
        default=default_pred_labels,
        placeholder="Selecione hate, não hate ou ambos",
    )

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    selected_kind_labels = st.multiselect(
        "Tipo de conteúdo",
        options=list(kind_map.keys()),
        default=list(kind_map.keys()),
        placeholder="Selecione posts e/ou comentários",
    )
with row2_col2:
    selected_hate_type_labels = st.multiselect(
        "Tipo de hate",
        options=list(hate_type_map.keys()),
        default=[],
        placeholder="Opcional: restrinja a um ou mais hate_types",
    )

row3_col1, row3_col2 = st.columns([2, 1])
with row3_col1:
    search_text = st.text_input(
        "Termo obrigatório no conteúdo",
        placeholder="Opcional: ex. mulher, política, religião. Vazio usa todo o texto filtrado.",
    )
with row3_col2:
    max_words = st.slider("Quantidade de palavras", min_value=40, max_value=220, value=140, step=20)

source_label = st.radio(
    "Fonte lexical",
    ["Evidência textual da LLM", "Texto completo"],
    horizontal=True,
)
text_source = "evidence" if source_label == "Evidência textual da LLM" else "content"

if not selected_platform_labels or not selected_pred_labels or not selected_kind_labels:
    st.warning("Selecione ao menos uma rede, uma classificação e um tipo de conteúdo para gerar a wordcloud.")
    st.stop()

selected_platforms = [platform_map[label] for label in selected_platform_labels]
selected_pred_values = [pred_map[label] for label in selected_pred_labels]
selected_kinds = [kind_map[label] for label in selected_kind_labels]
selected_hate_types = [hate_type_map[label] for label in selected_hate_type_labels]

filters = {}
if len(selected_platforms) != len(platforms):
    filters["platforms"] = selected_platforms
if len(selected_pred_values) != len(pred_labels):
    filters["pred_labels"] = selected_pred_values
if len(selected_kinds) != len(content_kinds):
    filters["content_kinds"] = selected_kinds
if selected_hate_types:
    filters["hate_types"] = selected_hate_types
if search_text.strip():
    filters["search_text"] = search_text.strip()

terms_df = get_top_terms_sql(filters, max_words, text_source=text_source)

if terms_df.empty:
    st.warning("Não há termos suficientes para gerar a visualização lexical com os filtros selecionados.")
    st.stop()

terms_df["term"] = terms_df["term"].astype(str)
terms_df["frequency"] = terms_df["frequency"].astype(int)

filter_summary = []
if len(selected_platforms) != len(platforms):
    filter_summary.append(f"redes: {', '.join(selected_platform_labels)}")
if len(selected_pred_values) != len(pred_labels):
    filter_summary.append(f"classificação: {', '.join(selected_pred_labels)}")
if len(selected_kinds) != len(content_kinds):
    filter_summary.append(f"conteúdo: {', '.join(selected_kind_labels)}")
if selected_hate_types:
    filter_summary.append(f"hate_types: {', '.join(selected_hate_type_labels)}")
if search_text.strip():
    filter_summary.append(f"contém: {search_text.strip()}")
filter_summary.append(f"fonte: {source_label}")

metric_grid(
    [
        ("Termos", format_int(len(terms_df))),
        ("Frequência total", format_int(terms_df["frequency"].sum())),
        ("Termo principal", terms_df.iloc[0]["term"]),
        ("Recorte", " · ".join(filter_summary) if filter_summary else "hate · banco completo"),
    ]
)

section_header("Wordcloud de hate", "O tamanho das palavras representa frequência nos conteúdos filtrados.")
freq = {
    row["term"]: int(row["frequency"])
    for _, row in terms_df.iterrows()
    if row["term"].strip()
}

if WordCloud is not None:
    try:
        wordcloud = WordCloud(
            width=1800,
            height=760,
            background_color="white",
            colormap="GnBu",
            max_words=max_words,
            prefer_horizontal=0.92,
            collocations=False,
            normalize_plurals=False,
            regexp=r"[\wÀ-ÿ#_]+",
        ).generate_from_frequencies(freq)
        st.image(wordcloud.to_image(), width="stretch")
    except Exception as exc:
        st.warning(
            "Não foi possível renderizar a nuvem de palavras como imagem. "
            f"Exibindo versão responsiva. Detalhe: {exc}"
        )
        WordCloud = None

if WordCloud is None:
    min_freq = int(terms_df["frequency"].min())
    max_freq = int(terms_df["frequency"].max())
    span = max(max_freq - min_freq, 1)
    tokens = []

    for idx, row in terms_df.head(max_words).iterrows():
        normalized = (int(row["frequency"]) - min_freq) / span
        size = 15 + normalized * 34
        color = CATEGORY_PALETTE[idx % len(CATEGORY_PALETTE)]
        tokens.append(
            (
                f'<span class="word-token" '
                f'style="font-size:{size:.1f}px;color:{color}" '
                f'title="{format_int(row["frequency"])} ocorrências">'
                f'{escape(row["term"])}</span>'
            )
        )

    st.markdown(
        '<div class="wordcloud-panel">' + "\n".join(tokens) + "</div>",
        unsafe_allow_html=True,
    )

section_header("Termos mais frequentes", "Tabela e barras para leitura quantitativa.")
top_df = terms_df.head(30)
fig = px.bar(
    top_df,
    x="frequency",
    y="term",
    orientation="h",
    color="frequency",
    text="frequency",
    color_continuous_scale=SEQUENTIAL_BLUE,
)
fig.update_traces(marker_line_width=0)
fig.update_layout(
    **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
    xaxis_title="Frequência",
    yaxis_title="Termo",
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, width="stretch")

st.dataframe(
    terms_df.rename(columns={"term": "Termo", "frequency": "Frequência"}),
    width="stretch",
    height=420,
)
