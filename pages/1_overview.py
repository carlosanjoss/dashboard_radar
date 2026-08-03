import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    MODEL_NAME,
    get_content_kind_analysis,
    get_hate_type_frequency,
    get_overview_metrics,
    get_platform_analysis,
    get_quality_metrics,
    get_records_page,
)


st.set_page_config(page_title="Visão Geral | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Visão geral",
    'Panorama <span class="hero-gradient">multirrede</span>',
    (
        f"Resumo executivo das classificações {MODEL_NAME}, com volume, prevalência, "
        "tipologias principais e registros recentes."
    ),
)

metrics = get_overview_metrics(filters).iloc[0]
metric_grid(
    [
        ("Conteúdos", format_int(metrics["total_content"])),
        ("Hate", format_int(metrics["total_hate"])),
        ("Não hate", format_int(metrics["total_non_hate"])),
        ("Taxa hate", format_pct(metrics["hate_percent"])),
        ("Posts", format_int(metrics["total_posts"])),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Ranking por rede", "Percentual de hate e volume absoluto por plataforma.")
    platform_df = get_platform_analysis(filters)
    if platform_df.empty:
        st.info("Nenhuma rede encontrada no banco.")
    else:
        fig = px.bar(
            platform_df,
            x="hate_percent",
            y="platform_label",
            orientation="h",
            color="total_hate",
            text="hate_percent",
            color_continuous_scale=SEQUENTIAL_WARM,
            hover_data=["total_content", "total_hate", "low_sample"],
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="% hate",
            yaxis_title="Rede social",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header("Posts e comentários", "Comparação entre tipos de conteúdo.")
    kind_df = get_content_kind_analysis(filters)
    if kind_df.empty:
        st.info("Sem tipo de conteúdo no banco.")
    else:
        fig = px.bar(
            kind_df,
            x="content_kind_label",
            y="hate_percent",
            color="total_hate",
            text="hate_percent",
            color_continuous_scale=SEQUENTIAL_BLUE,
            hover_data=["total_content", "total_hate"],
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Tipo de conteúdo",
            yaxis_title="% hate",
        )
        st.plotly_chart(fig, width="stretch")

section_header("Tipologias principais", "Tipos de hate mais frequentes no banco completo.")
type_df = get_hate_type_frequency(filters, 15)
if type_df.empty:
    st.info("Nenhuma tipologia encontrada.")
else:
    fig = px.bar(
        type_df,
        x="total_mentions",
        y="hate_type_label",
        orientation="h",
        color="hate_type_label",
        text="total_mentions",
        color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        **base_plotly_layout(height=440, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Menções",
        yaxis_title="Tipo",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

section_header("Qualidade e limitações", "Sinais de qualidade do corpus e da classificação automática.")
quality = get_quality_metrics(filters).iloc[0]
metric_grid(
    [
        ("Sem texto", format_int(quality["empty_text_records"])),
        ("Sem data", format_int(quality["missing_date_records"])),
        ("Datas futuras", format_int(quality["future_date_records"])),
        ("Duplicados", format_int(quality["duplicate_rows"])),
    ]
)

section_header("Registros recentes", "Amostra textual do banco completo, com classificação e justificativa.")
records_df = get_records_page(filters, page=1, page_size=40)
if records_df.empty:
    st.info("Nenhum registro para exibir.")
else:
    table = records_df.rename(
        columns={
            "platform_label": "Rede",
            "content_kind_label": "Tipo",
            "pred_label_label": "Classificação",
            "hate_probability": "Probabilidade hate",
            "hate_types": "Tipos",
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
                "Probabilidade hate",
                "Tipos",
                "Publicado em",
                "Trecho",
                "Justificativa",
            ]
        ],
        width="stretch",
        height=520,
    )
