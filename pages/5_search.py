import math

import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_hate_type_frequency,
    get_platform_analysis,
    get_records_count,
    get_records_page,
)


st.set_page_config(page_title="Busca | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Busca investigativa",
    'Consulta <span class="hero-gradient">textual</span>',
    "Pesquise termos, expressões, nomes ou hashtags; se o campo ficar vazio, a tabela usa o banco completo.",
)

search_text = st.text_input(
    "Busca textual",
    placeholder="Digite um termo para filtrar, ou deixe vazio para ver o banco completo.",
)
if search_text.strip():
    filters = {"search_text": search_text.strip()}

total_records = get_records_count(filters)
platform_df = get_platform_analysis(filters)
type_df = get_hate_type_frequency(filters, 10)

metric_grid(
    [
        ("Resultados", format_int(total_records)),
        ("Redes", format_int(platform_df["platform"].nunique() if not platform_df.empty else 0)),
        ("Discurso de ódio", format_int(platform_df["total_hate"].sum() if not platform_df.empty else 0)),
        ("Tipos de preconceito", format_int(type_df["hate_type"].nunique() if not type_df.empty else 0)),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Resultados por rede", "Distribuição da busca entre plataformas.")
    if platform_df.empty:
        st.info("Sem resultados por rede.")
    else:
        fig = px.bar(
            platform_df,
            x="total_content",
            y="platform_label",
            orientation="h",
            color="hate_percent",
            text="total_content",
            color_continuous_scale=SEQUENTIAL_WARM,
            labels={
                "hate_percent": "Discurso de ódio (%)",
                "total_content": "Resultados",
                "platform_label": "Rede",
            },
        )
        fig.update_layout(
            **base_plotly_layout(height=380, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Resultados",
            yaxis_title="Rede",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header("Tipos encontrados", "Tipologias de preconceito associadas aos resultados da busca.")
    if type_df.empty:
        st.info("Sem tipologias no resultado.")
    else:
        fig = px.bar(
            type_df,
            x="total_mentions",
            y="hate_type_label",
            orientation="h",
            color="hate_type_label",
            color_discrete_sequence=CATEGORY_PALETTE,
            text="total_mentions",
        )
        fig.update_layout(
            **base_plotly_layout(height=380, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Menções",
            yaxis_title="Tipo de preconceito",
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch")

section_header("Resultados paginados", "Registros encontrados, com classificação e justificativa curta.")
page_size = st.selectbox("Registros por página", [25, 50, 100, 200], index=1)
total_pages = max(math.ceil(total_records / page_size), 1)
page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)
records_df = get_records_page(filters, page=page, page_size=page_size)
st.caption(f"Total: {format_int(total_records)} · página {page} de {total_pages}")

if records_df.empty:
    st.info("Nenhum registro para exibir.")
else:
    table = records_df.rename(
        columns={
            "platform_label": "Rede",
            "content_kind_label": "Tipo",
            "pred_label_label": "Classificação",
            "hate_probability": "Probabilidade de discurso de ódio",
            "hate_types_label": "Tipos de preconceito",
            "published_at": "Publicado em",
            "text_excerpt": "Trecho",
            "evidencia_textual": "Evidência",
            "justificativa_curta": "Justificativa",
        }
    )
    st.dataframe(
        table[
            [
                "Rede",
                "Tipo",
                "Classificação",
                "Probabilidade de discurso de ódio",
                "Tipos de preconceito",
                "Publicado em",
                "Trecho",
                "Evidência",
                "Justificativa",
            ]
        ],
        width="stretch",
        height=620,
    )
