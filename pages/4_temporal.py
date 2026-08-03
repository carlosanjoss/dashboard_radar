import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import get_category_temporal, get_temporal_analysis, get_temporal_type_trends


st.set_page_config(page_title="Temporal | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Série temporal",
    'Evolução <span class="hero-gradient">no tempo</span>',
    "Análise de volume, prevalência e variação das tipologias quando há data utilizável.",
)

grain_label = st.radio("Agrupamento", ["Mês", "Semana", "Dia", "Ano"], horizontal=True)
grain = {"Dia": "day", "Semana": "week", "Mês": "month", "Ano": "year"}[grain_label]

temporal_df = get_temporal_analysis(filters, grain)
if temporal_df.empty:
    st.info("Não há data utilizável no banco.")
    st.stop()

metric_grid(
    [
        ("Períodos", format_int(temporal_df["period"].nunique())),
        ("Conteúdos", format_int(temporal_df["total_content"].sum())),
        ("Hate", format_int(temporal_df["total_hate"].sum())),
        ("Taxa média", format_pct(temporal_df["hate_percent"].mean())),
    ]
)

section_header("Volume temporal", "Conteúdos totais e conteúdos hate ao longo do tempo.")
fig = px.line(
    temporal_df,
    x="period",
    y=["total_content", "total_hate"],
    markers=True,
    color_discrete_sequence=[SEQUENTIAL_BLUE[-1], SEQUENTIAL_WARM[-1]],
)
fig.update_traces(line=dict(width=3))
fig.update_layout(
    **base_plotly_layout(height=470, margin=dict(t=24, b=18, l=12, r=12)),
    xaxis_title="Período",
    yaxis_title="Conteúdos",
    legend_title="Série",
)
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header("Prevalência", "Percentual de hate ao longo do tempo.")
    fig = px.area(
        temporal_df,
        x="period",
        y="hate_percent",
        color_discrete_sequence=[SEQUENTIAL_WARM[-1]],
    )
    fig.update_layout(
        **base_plotly_layout(height=410, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Período",
        yaxis_title="% hate",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    section_header("Tipos no tempo", "Variação dos principais hate_types.")
    type_trends = get_temporal_type_trends(filters, grain, 6)
    if type_trends.empty:
        st.info("Sem tipos suficientes para série temporal.")
    else:
        fig = px.area(
            type_trends,
            x="period",
            y="total_mentions",
            color="hate_type_label",
            color_discrete_sequence=CATEGORY_PALETTE,
        )
        fig.update_layout(
            **base_plotly_layout(height=410, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Período",
            yaxis_title="Menções",
            legend_title="Tipo",
        )
        st.plotly_chart(fig, width="stretch")

section_header("Categorias Gemma no tempo", "Evolução das categorias preditas mais frequentes.")
category_temporal = get_category_temporal(filters, grain, 8)
if category_temporal.empty:
    st.info("Sem categorias temporais para exibir.")
else:
    pivot = category_temporal.pivot_table(
        index="pred_category_item",
        columns="period",
        values="total",
        fill_value=0,
    )
    fig = px.imshow(
        pivot,
        aspect="auto",
        text_auto=True,
        color_continuous_scale=SEQUENTIAL_BLUE,
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Período",
        yaxis_title="Categoria",
    )
    st.plotly_chart(fig, width="stretch")
