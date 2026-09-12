import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_platform_analysis,
)


st.set_page_config(page_title="Plataformas | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Plataformas",
    'Plataformas sociais e <span class="hero-gradient">apps de mensagens</span>',
    (
        "Comparação do banco completo separando plataformas sociais abertas de apps de mensagens. "
        "WhatsApp e Telegram são tratados como apps de mensagens; as demais fontes ficam em plataformas sociais."
    ),
)

platform_df = get_platform_analysis(filters)
if platform_df.empty:
    st.info("Nenhuma plataforma encontrada no banco.")
    st.stop()

social_df = platform_df.loc[platform_df["platform_group"] == "social_network"].copy()
messaging_df = platform_df.loc[platform_df["platform_group"] == "instant_messaging"].copy()

metric_grid(
    [
        ("Plataformas sociais", format_int(social_df["platform"].nunique())),
        ("Apps de mensagens", format_int(messaging_df["platform"].nunique())),
        ("Conteúdo", format_int(platform_df["total_content"].sum())),
        ("Discurso de ódio", format_int(platform_df["total_hate"].sum())),
        ("Maior taxa", format_pct(platform_df["hate_percent"].max())),
    ]
)

section_header(
    "Resumo por tipo de plataforma",
    "Comparação agregada entre plataformas sociais e apps de mensagens.",
)
group_summary = (
    platform_df.groupby("platform_group_label", as_index=False)
    .agg(
        total_content=("total_content", "sum"),
        total_hate=("total_hate", "sum"),
        total_non_hate=("total_non_hate", "sum"),
        platforms=("platform", "nunique"),
    )
)
group_summary["hate_percent"] = (
    100 * group_summary["total_hate"] / group_summary["total_content"].replace(0, float("nan"))
).fillna(0)

left, right = st.columns(2)

with left:
    group_plot_df = group_summary.rename(
        columns={
            "total_content": "Conteúdo",
            "total_hate": "Discurso de ódio",
        }
    )
    fig = px.bar(
        group_plot_df,
        x="platform_group_label",
        y=["Conteúdo", "Discurso de ódio"],
        barmode="group",
        color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_layout(
        **base_plotly_layout(height=360, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Tipo de plataforma",
        yaxis_title="Conteúdo",
        legend_title="Métrica",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    fig = px.bar(
        group_summary,
        x="hate_percent",
        y="platform_group_label",
        orientation="h",
        color="hate_percent",
        text="hate_percent",
        color_continuous_scale=SEQUENTIAL_WARM,
        labels={
            "hate_percent": "Discurso de ódio (%)",
            "platform_group_label": "Tipo de plataforma",
        },
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
    fig.update_layout(
        **base_plotly_layout(height=360, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="% discurso de ódio",
        yaxis_title="Tipo de plataforma",
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=10)
    st.plotly_chart(fig, width="stretch")


def render_platform_group(title, subset):
    if subset.empty:
        st.info(f"Não há dados para {title.lower()}.")
        return

    left_col, right_col = st.columns(2)
    with left_col:
        section_header(f"Volume: {title}", "Conteúdo total e conteúdo com discurso de ódio por plataforma.")
        long_df = subset.melt(
            id_vars=["platform_label"],
            value_vars=["total_content", "total_hate"],
            var_name="Métrica",
            value_name="Total",
        )
        long_df["Métrica"] = long_df["Métrica"].replace(
            {"total_content": "Conteúdo", "total_hate": "Discurso de ódio"}
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
            xaxis_title="Plataforma",
            yaxis_title="Total",
            legend_title="Métrica",
        )
        st.plotly_chart(fig, width="stretch")

    with right_col:
        section_header(f"Prevalência: {title}", "Percentual de discurso de ódio por plataforma no grupo.")
        fig = px.bar(
            subset,
            x="hate_percent",
            y="platform_label",
            orientation="h",
            color="hate_percent",
            text="hate_percent",
            color_continuous_scale=SEQUENTIAL_WARM,
            labels={
                "hate_percent": "Discurso de ódio (%)",
                "platform_label": "Plataforma",
            },
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="% discurso de ódio",
            yaxis_title="Plataforma",
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=10)
        st.plotly_chart(fig, width="stretch")


social_tab, messaging_tab = st.tabs(["Plataformas sociais", "Apps de mensagens"])

with social_tab:
    render_platform_group("Plataformas sociais", social_df)

with messaging_tab:
    render_platform_group("Apps de mensagens", messaging_df)
