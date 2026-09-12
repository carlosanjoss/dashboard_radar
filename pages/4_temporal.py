import plotly.express as px
import streamlit as st

from components.charts import SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import get_category_temporal, get_temporal_analysis


st.set_page_config(page_title="Temporal | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()

# Event presets for trigger events
EVENT_PRESETS = {
    "Nenhum": None,
    "Eleições 2022 - 1º turno (out/2022)": ("2022-10-02", "2022-10-31"),
    "Eleições 2022 - 2º turno (out/2022)": ("2022-10-30", "2022-11-15"),
    "Posse presidencial (jan/2023)": ("2023-01-01", "2023-01-31"),
    "8 de Janeiro (jan/2023)": ("2023-01-08", "2023-01-20"),
}

render_hero(
    "Série temporal",
    'Evolução <span class="hero-gradient">no tempo</span>',
    "Análise de volume, prevalência e variação das tipologias quando há data utilizável.",
)

event_col, grain_col = st.columns([1.4, 1])
with event_col:
    selected_preset = st.selectbox(
        "Evento-gatilho",
        options=list(EVENT_PRESETS.keys()),
        index=0,
        help="Aplica filtro de data automaticamente para eventos conhecidos",
    )

preset_dates = EVENT_PRESETS[selected_preset]
filters = {}
if preset_dates:
    filters["date_start"] = preset_dates[0]
    filters["date_end"] = preset_dates[1]
    st.info(f"Período selecionado: {preset_dates[0]} a {preset_dates[1]}")

with grain_col:
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
        ("Discurso de ódio", format_int(temporal_df["total_hate"].sum())),
        ("Taxa média de discurso de ódio", format_pct(temporal_df["hate_percent"].mean())),
    ]
)

section_header("Volume temporal", "Conteúdos totais e conteúdos com discurso de ódio ao longo do tempo.")
temporal_plot_df = temporal_df.rename(
    columns={
        "total_content": "Conteúdos",
        "total_hate": "Discurso de ódio",
    }
)
fig = px.line(
    temporal_plot_df,
    x="period",
    y=["Conteúdos", "Discurso de ódio"],
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

section_header("Categorias de preconceito no tempo", "Evolução das categorias de preconceito preditas mais frequentes.")
category_temporal = get_category_temporal(filters, grain, 8)
if category_temporal.empty:
    st.info("Sem categorias temporais para exibir.")
else:
    pivot = category_temporal.pivot_table(
        index="pred_category_item_label",
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
        yaxis_title="Categoria de preconceito",
    )
    st.plotly_chart(fig, width="stretch")
