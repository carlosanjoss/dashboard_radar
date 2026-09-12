import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import get_author_analysis, get_author_type_distribution


st.set_page_config(page_title="Autores | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Autores anonimizados",
    'Perfis <span class="hero-gradient">e atividade</span>',
    "Análise agregada por autor anonimizado. Identificadores pessoais não são exibidos.",
)

min_records = 1
limit = 300
authors_df = get_author_analysis(filters, limit=limit, min_records=min_records)
if authors_df.empty:
    st.warning("Nenhum perfil encontrado no banco.")
    st.stop()

metric_grid(
    [
        ("Perfis", format_int(authors_df["profile_id"].nunique())),
        ("Conteúdos", format_int(authors_df["total_content"].sum())),
        ("Discurso de ódio", format_int(authors_df["total_hate"].sum())),
        ("Redes médias", f"{authors_df['total_platforms'].mean():.2f}".replace(".", ",")),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Perfis com mais discurso de ódio", "Ranking por volume absoluto de conteúdos classificados como discurso de ódio.")
    top_df = authors_df.head(25)
    fig = px.bar(
        top_df,
        x="total_hate",
        y="profile_id",
        orientation="h",
        color="hate_percent",
        text="total_hate",
        color_continuous_scale=SEQUENTIAL_WARM,
        labels={
            "total_hate": "Discurso de ódio",
            "hate_percent": "Discurso de ódio (%)",
            "profile_id": "Perfil",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Discurso de ódio",
        yaxis_title="Perfil",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    section_header("Atividade vs prevalência", "Relação entre volume total e percentual de discurso de ódio por perfil.")
    fig = px.scatter(
        authors_df,
        x="total_content",
        y="hate_percent",
        size="total_hate",
        color="avg_hate_probability",
        hover_name="profile_id",
        hover_data=["total_platforms", "engagement_total"],
        color_continuous_scale=SEQUENTIAL_BLUE,
        labels={
            "total_content": "Conteúdos",
            "hate_percent": "Discurso de ódio (%)",
            "avg_hate_probability": "Probabilidade média de discurso de ódio",
            "total_hate": "Discurso de ódio",
            "total_platforms": "Redes",
            "engagement_total": "Engajamento",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Conteúdos",
        yaxis_title="% discurso de ódio",
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%", dtick=10)
    st.plotly_chart(fig, width="stretch")

section_header("Tipologias por perfil", "Tipos de preconceito mais frequentes entre perfis anonimizados.")
author_types = get_author_type_distribution(filters, limit=100, min_records=min_records)
if author_types.empty:
    st.info("Sem tipologias suficientes por perfil.")
else:
    type_summary = (
        author_types.groupby("hate_type_label", as_index=False)["total_mentions"]
        .sum()
        .sort_values("total_mentions", ascending=False)
    )
    fig = px.pie(
        type_summary,
        names="hate_type_label",
        values="total_mentions",
        hole=0.55,
        color_discrete_sequence=CATEGORY_PALETTE,
        labels={
            "hate_type_label": "Tipo de preconceito",
            "total_mentions": "Menções",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        legend_title="Tipo",
    )
    st.plotly_chart(fig, width="stretch")
