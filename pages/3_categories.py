import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_MINT, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_hate_type_by_platform,
    get_hate_type_cooccurrence,
    get_hate_type_frequency,
    get_pred_category_distribution,
    get_probability_by_category,
)


st.set_page_config(page_title="Categorias de Preconceito | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Categorias de preconceito",
    'Tipologias <span class="hero-gradient">de preconceito</span>',
    "Mapa das tipologias de ódio online e das categorias de preconceito preditas pelo modelo.",
)

type_df = get_hate_type_frequency(filters, 30)
category_df = get_pred_category_distribution(filters, 30)

metric_grid(
    [
        ("Tipos de preconceito", format_int(type_df["hate_type"].nunique() if not type_df.empty else 0)),
        ("Menções", format_int(type_df["total_mentions"].sum() if not type_df.empty else 0)),
        ("Categorias de preconceito", format_int(category_df["pred_category_item_label"].nunique() if not category_df.empty else 0)),
        ("Categoria de preconceito principal", category_df.iloc[0]["pred_category_item_label"] if not category_df.empty else "sem dados"),
    ]
)

section_header("Tipos de preconceito", "Frequência absoluta e percentual de cada tipo de preconceito.")
if type_df.empty:
    st.info("Nenhum tipo de preconceito encontrado.")
else:
    fig = px.bar(
        type_df,
        x="total_mentions",
        y="hate_type_label",
        orientation="h",
        color="percent_of_mentions",
        text="total_mentions",
        color_continuous_scale=SEQUENTIAL_WARM,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        **base_plotly_layout(height=470, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Menções",
        yaxis_title="Tipo",
    )
    st.plotly_chart(fig, width="stretch")

section_header("Rede x tipo de preconceito", "Matriz de distribuição das tipologias por plataforma.")
type_platform_df = get_hate_type_by_platform(filters)
if type_platform_df.empty:
    st.info("Sem dados para montar a matriz.")
else:
    pivot = type_platform_df.pivot_table(
        index="hate_type_label",
        columns="platform_label",
        values="total_mentions",
        fill_value=0,
    )
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=SEQUENTIAL_MINT,
        text_auto=True,
    )
    fig.update_layout(
        **base_plotly_layout(height=520, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Rede",
        yaxis_title="Tipo",
    )
    st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header("Coocorrência", "Tipos que aparecem juntos no mesmo registro.")
    cooc_df = get_hate_type_cooccurrence(filters, 25)
    if cooc_df.empty:
        st.info("Não há coocorrências suficientes.")
    else:
        cooc_df["Par"] = cooc_df["hate_type_a_label"] + " + " + cooc_df["hate_type_b_label"]
        fig = px.bar(
            cooc_df,
            x="total_cooccurrences",
            y="Par",
            orientation="h",
            color="total_cooccurrences",
            text="total_cooccurrences",
            color_continuous_scale=SEQUENTIAL_WARM,
        )
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Coocorrências",
            yaxis_title="Par",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header("Probabilidade média", "Média de probabilidade por categoria de preconceito predita.")
    prob_df = get_probability_by_category(filters, 20)
    if prob_df.empty:
        st.info("Sem probabilidade por categoria de preconceito.")
    else:
        fig = px.scatter(
            prob_df,
            x="total",
            y="avg_hate_probability",
            size="total",
            color="pred_category_item_label",
            hover_data=["avg_category_probability"],
            color_discrete_sequence=CATEGORY_PALETTE,
            labels={
                "total": "Ocorrências",
                "avg_hate_probability": "Probabilidade média de discurso de ódio",
                "avg_category_probability": "Probabilidade média da categoria",
                "pred_category_item_label": "Categoria de preconceito",
            },
        )
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Ocorrências",
            yaxis_title="Probabilidade média de discurso de ódio",
            legend_title="Categoria de preconceito",
        )
        st.plotly_chart(fig, width="stretch")
