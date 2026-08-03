import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_MINT, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_content_source_type_distribution,
    get_language_distribution,
    get_low_sample_platforms,
    get_platform_analysis,
    get_source_system_analysis,
)


st.set_page_config(page_title="Redes Sociais | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Redes sociais",
    'Análise <span class="hero-gradient">multiplataforma</span>',
    "Comparação do banco completo entre redes, fontes de coleta, tipos de conteúdo e tamanho das amostras.",
)

platform_df = get_platform_analysis(filters)
if platform_df.empty:
    st.info("Nenhuma rede encontrada no banco.")
    st.stop()

metric_grid(
    [
        ("Redes", format_int(platform_df["platform"].nunique())),
        ("Conteúdos", format_int(platform_df["total_content"].sum())),
        ("Hate", format_int(platform_df["total_hate"].sum())),
        ("Maior taxa", format_pct(platform_df["hate_percent"].max())),
    ]
)

left, right = st.columns(2)

with left:
    section_header("Volume por rede", "Conteúdos totais e conteúdos hate por plataforma.")
    long_df = platform_df.melt(
        id_vars=["platform_label"],
        value_vars=["total_content", "total_hate"],
        var_name="Métrica",
        value_name="Total",
    )
    long_df["Métrica"] = long_df["Métrica"].replace(
        {"total_content": "Conteúdos", "total_hate": "Hate"}
    )
    fig = px.bar(
        long_df,
        x="platform_label",
        y="Total",
        color="Métrica",
        barmode="group",
        color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Rede social",
        yaxis_title="Total",
        legend_title="Métrica",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    section_header("Prevalência", "Percentual de hate por plataforma.")
    fig = px.bar(
        platform_df,
        x="hate_percent",
        y="platform_label",
        orientation="h",
        color="hate_percent",
        text="hate_percent",
        color_continuous_scale=SEQUENTIAL_WARM,
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="% hate",
        yaxis_title="Rede social",
    )
    st.plotly_chart(fig, width="stretch")

section_header("Detalhes de coleta", "Fontes, tipos originais e idioma do banco completo.")
left, right = st.columns(2)

with left:
    source_df = get_source_system_analysis(filters, 30)
    if source_df.empty:
        st.info("Não há fonte de coleta disponível.")
    else:
        fig = px.bar(
            source_df,
            x="total_content",
            y="source_system",
            orientation="h",
            color="platform_label",
            hover_data=["total_hate", "hate_percent", "engagement_total"],
            color_discrete_sequence=CATEGORY_PALETTE,
        )
        fig.update_layout(
            **base_plotly_layout(height=460, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Conteúdos",
            yaxis_title="Fonte",
            legend_title="Rede",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    source_type_df = get_content_source_type_distribution(filters, 20)
    if source_type_df.empty:
        st.info("Não há tipo de conteúdo disponível.")
    else:
        fig = px.bar(
            source_type_df,
            x="total_content",
            y="source_content_type",
            orientation="h",
            color="content_kind_label",
            color_discrete_sequence=CATEGORY_PALETTE,
        )
        fig.update_layout(
            **base_plotly_layout(height=460, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Conteúdos",
            yaxis_title="Tipo informado",
            legend_title="Classe",
        )
        st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header("Idioma", "Distribuição linguística informada na coleta.")
    language_df = get_language_distribution(filters, 20)
    st.dataframe(
        language_df.rename(
            columns={
                "language": "Idioma",
                "total_content": "Conteúdos",
                "total_hate": "Hate",
                "hate_percent": "% hate",
            }
        ),
        width="stretch",
        height=320,
    )

with right:
    section_header("Amostras pequenas", "Redes com baixo volume exigem leitura cautelosa.")
    low_df = get_low_sample_platforms(filters)
    if low_df.empty:
        st.success("Nenhuma rede abaixo do limiar de 1.000 registros.")
    else:
        fig = px.bar(
            low_df,
            x="total_content",
            y="platform_label",
            orientation="h",
            color="hate_percent",
            text="total_content",
            color_continuous_scale=SEQUENTIAL_MINT,
        )
        fig.update_layout(
            **base_plotly_layout(height=320, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Conteúdos",
            yaxis_title="Rede",
        )
        st.plotly_chart(fig, width="stretch")
