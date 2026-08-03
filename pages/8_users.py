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
        ("Hate", format_int(authors_df["total_hate"].sum())),
        ("Redes médias", f"{authors_df['total_platforms'].mean():.2f}".replace(".", ",")),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Perfis com mais hate", "Ranking por volume absoluto de conteúdos classificados como hate.")
    top_df = authors_df.head(25)
    fig = px.bar(
        top_df,
        x="total_hate",
        y="profile_id",
        orientation="h",
        color="hate_percent",
        text="total_hate",
        color_continuous_scale=SEQUENTIAL_WARM,
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Hate",
        yaxis_title="Perfil",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    section_header("Atividade vs prevalência", "Relação entre volume total e percentual de hate por perfil.")
    fig = px.scatter(
        authors_df,
        x="total_content",
        y="hate_percent",
        size="total_hate",
        color="avg_hate_probability",
        hover_name="profile_id",
        hover_data=["total_platforms", "engagement_total"],
        color_continuous_scale=SEQUENTIAL_BLUE,
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Conteúdos",
        yaxis_title="% hate",
    )
    st.plotly_chart(fig, width="stretch")

section_header("Tipologias por perfil", "Tipos de hate mais frequentes entre perfis anonimizados.")
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
    )
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        legend_title="Tipo",
    )
    st.plotly_chart(fig, width="stretch")

section_header("Tabela de perfis", "Dados agregados; hash interno permanece oculto.")
st.dataframe(
    authors_df.drop(columns=["author_hash"]).rename(
        columns={
            "profile_id": "Perfil",
            "total_content": "Conteúdos",
            "total_hate": "Hate",
            "hate_percent": "% hate",
            "total_platforms": "Redes",
            "total_posts": "Posts",
            "total_comments": "Comentários",
            "avg_hate_probability": "Probabilidade média",
            "engagement_total": "Engajamento",
        }
    ),
    width="stretch",
    height=520,
)
