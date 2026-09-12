import plotly.graph_objects as go
import streamlit as st

from components.charts import CATEGORY_PALETTE, MINT, PRIMARY, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    MODEL_NAME,
    get_hate_type_frequency,
    get_overview_metrics,
    get_platform_analysis,
)


st.set_page_config(page_title="Panorama Multirrede | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Panorama multirrede",
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
        ("Discurso de ódio", format_int(metrics["total_hate"])),
        ("Sem discurso de ódio", format_int(metrics["total_non_hate"])),
        ("Taxa de discurso de ódio", format_pct(metrics["hate_percent"])),
        ("Posts", format_int(metrics["total_posts"])),
    ]
)

platform_df = get_platform_analysis(filters)
social_df = platform_df.loc[platform_df["platform_group"] == "social_network"].copy()
messaging_df = platform_df.loc[platform_df["platform_group"] == "instant_messaging"].copy()


def render_platform_panel(title, subtitle, data, color):
    section_header(title, subtitle)
    if data.empty:
        st.info("Sem dados para este grupo de plataformas.")
        return

    data = data.sort_values("hate_percent", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=data["hate_percent"],
            y=data["platform_label"],
            orientation="h",
            marker=dict(color=color),
            text=[f"{value:.2f}%" for value in data["hate_percent"]],
            textposition="auto",
            customdata=data[["total_content", "total_hate"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "% discurso de ódio: %{x:.2f}%<br>"
                "Conteúdos: %{customdata[0]:,.0f}<br>"
                "Discurso de ódio: %{customdata[1]:,.0f}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="% discurso de ódio",
        yaxis_title="Plataforma",
        showlegend=False,
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=10)
    st.plotly_chart(fig, width="stretch")


left, right = st.columns(2)

with left:
    render_platform_panel(
        "Apps de mensagens",
        "WhatsApp e Telegram analisados separadamente das redes sociais.",
        messaging_df,
        PRIMARY,
    )

with right:
    render_platform_panel(
        "Redes sociais",
        "Facebook, Reddit, TikTok, Twitter e YouTube no mesmo grupo analítico.",
        social_df,
        MINT,
    )

def render_type_panel(title, subtitle, platforms, height=390):
    section_header(title, subtitle)
    if not platforms:
        st.info("Sem plataformas neste grupo.")
        return

    type_df = get_hate_type_frequency({"platforms": platforms}, 10)
    if type_df.empty:
        st.info("Nenhuma tipologia encontrada neste grupo.")
        return

    type_df = type_df.sort_values("total_mentions", ascending=True)
    colors = [CATEGORY_PALETTE[idx % len(CATEGORY_PALETTE)] for idx in range(len(type_df))]
    fig = go.Figure(
        go.Bar(
            x=type_df["total_mentions"],
            y=type_df["hate_type_label"],
            orientation="h",
            marker=dict(color=colors),
            text=[format_int(value) for value in type_df["total_mentions"]],
            textposition="auto",
            customdata=type_df[["percent_of_mentions", "percent_of_hate_records"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Menções: %{x:,.0f}<br>"
                "% das menções: %{customdata[0]:.2f}%<br>"
                "% dos registros com discurso de ódio: %{customdata[1]:.2f}%<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        **base_plotly_layout(height=height, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Menções",
        yaxis_title="Tipo de preconceito",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


left, right = st.columns(2)

with left:
    render_type_panel(
        "Tipologias em apps de mensagens",
        "Frequência dos tipos em WhatsApp e Telegram.",
        messaging_df["platform"].tolist(),
    )

with right:
    render_type_panel(
        "Tipologias em redes sociais",
        "Frequência dos tipos em Facebook, Reddit, TikTok, Twitter e YouTube.",
        social_df["platform"].tolist(),
    )
