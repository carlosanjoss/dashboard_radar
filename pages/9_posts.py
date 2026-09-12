import plotly.express as px
import streamlit as st

from components.charts import SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import get_post_analysis, get_records_for_post


st.set_page_config(page_title="Posts | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Posts e threads",
    'Conteúdos <span class="hero-gradient">monitorados</span>',
    "Agrupamento por post raiz para localizar threads ou publicações com maior concentração de discurso de ódio.",
)

min_records = 1
limit = 300
posts_df = get_post_analysis(filters, limit=limit, min_records=min_records)
if posts_df.empty:
    st.warning("Nenhum post/thread encontrado no banco.")
    st.stop()

metric_grid(
    [
        ("Posts/threads", format_int(posts_df["post_id"].nunique())),
        ("Registros", format_int(posts_df["total_records"].sum())),
        ("Discurso de ódio", format_int(posts_df["total_hate"].sum())),
        ("Comentários", format_int(posts_df["total_comments"].sum())),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Threads com mais discurso de ódio", "Ranking por volume absoluto de registros com discurso de ódio.")
    top_df = posts_df.head(25)
    fig = px.bar(
        top_df,
        x="total_hate",
        y="post_title",
        orientation="h",
        color="hate_percent",
        text="total_hate",
        color_continuous_scale=SEQUENTIAL_WARM,
        hover_data=["platform_label", "total_records", "total_comments"],
        labels={
            "total_hate": "Discurso de ódio",
            "hate_percent": "Discurso de ódio (%)",
            "post_title": "Post/thread",
            "platform_label": "Rede",
            "total_records": "Registros",
            "total_comments": "Comentários",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=560, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Discurso de ódio",
        yaxis_title="Post/thread",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    section_header("Volume vs prevalência", "Relação entre total de registros e percentual de discurso de ódio.")
    fig = px.scatter(
        posts_df,
        x="total_records",
        y="hate_percent",
        size="total_hate",
        color="avg_hate_probability",
        hover_name="post_title",
        hover_data=["platform_label", "engagement_total"],
        color_continuous_scale=SEQUENTIAL_BLUE,
        labels={
            "hate_percent": "Discurso de ódio (%)",
            "avg_hate_probability": "Probabilidade média de discurso de ódio",
            "total_hate": "Discurso de ódio",
            "total_records": "Registros",
            "platform_label": "Rede",
            "engagement_total": "Engajamento",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=560, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Registros",
        yaxis_title="% discurso de ódio",
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%", dtick=10)
    st.plotly_chart(fig, width="stretch")

section_header("Explorar registros de um post", "Conteúdos classificados associados ao post/thread selecionado.")
post_options = {
    f"{row['platform_label']} · {row['post_title'][:110]}": int(row["post_id"])
    for _, row in posts_df.head(100).iterrows()
}
selected = st.selectbox("Post/thread", list(post_options.keys()))
records_df = get_records_for_post(post_options[selected], filters, page=1, page_size=100)
if records_df.empty:
    st.info("Nenhum registro associado encontrado.")
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
                "Justificativa",
            ]
        ],
        width="stretch",
        height=560,
    )
