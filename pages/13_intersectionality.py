import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_hate_intensity_by_category,
    get_hate_type_intersectionality,
    get_hate_type_intersectionality_matrix,
)


st.set_page_config(page_title="Interseccionalidade | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Interseccionalidade & Intensidade",
    'Sobreposição <span class="hero-gradient">de preconceitos</span> e intensidade discursiva',
    "Análise da sobreposição entre tipos de preconceito, intensidade do discurso de ódio e dimensões discursivas.",
)

left, right = st.columns(2)

with left:
    section_header(
        "Intensidade do discurso de ódio por categoria",
        "Probabilidade média, mediana e distribuição por faixas de intensidade em cada categoria de preconceito."
    )
    intensity_df = get_hate_intensity_by_category(filters, 20)
    if intensity_df.empty:
        st.info("Sem dados de intensidade por categoria.")
    else:
        fig = px.bar(
            intensity_df,
            x="avg_hate_intensity",
            y="pred_category_item_label",
            orientation="h",
            color="avg_hate_intensity",
            text="total_hate",
            color_continuous_scale=SEQUENTIAL_WARM,
            labels={
                "avg_hate_intensity": "Intensidade média",
                "pred_category_item_label": "Categoria de preconceito",
                "total_hate": "Registros com discurso de ódio",
                "median_hate_intensity": "Intensidade mediana",
                "high_intensity_count": "Alta intensidade",
                "medium_intensity_count": "Média intensidade",
                "low_intensity_count": "Baixa intensidade",
                "avg_category_probability": "Probabilidade média da categoria",
            },
            hover_data=[
                "median_hate_intensity",
                "high_intensity_count",
                "medium_intensity_count",
                "low_intensity_count",
                "avg_category_probability"
            ],
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            **base_plotly_layout(height=500, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Intensidade média do discurso de ódio",
            yaxis_title="Categoria de preconceito",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Distribuição de intensidade por categoria",
        "Faixas de probabilidade de discurso de ódio: alta (≥0.8), média (0.5-0.8), baixa (<0.5)."
    )
    if intensity_df.empty:
        st.info("Sem dados para distribuição.")
    else:
        # Create stacked bar for intensity distribution
        plot_df = intensity_df.melt(
            id_vars=["pred_category_item_label"],
            value_vars=["high_intensity_count", "medium_intensity_count", "low_intensity_count"],
            var_name="faixa",
            value_name="quantidade"
        )
        plot_df["faixa_label"] = plot_df["faixa"].map({
            "high_intensity_count": "Alta (≥0.8)",
            "medium_intensity_count": "Média (0.5-0.8)",
            "low_intensity_count": "Baixa (<0.5)"
        })
        fig = px.bar(
            plot_df,
            x="quantidade",
            y="pred_category_item_label",
            orientation="h",
            color="faixa_label",
            color_discrete_map={
                "Alta (≥0.8)": SEQUENTIAL_WARM[-1],
                "Média (0.5-0.8)": SEQUENTIAL_WARM[2],
                "Baixa (<0.5)": SEQUENTIAL_WARM[0],
            },
            labels={
                "quantidade": "Quantidade de registros",
                "pred_category_item_label": "Categoria de preconceito",
                "faixa_label": "Faixa de intensidade",
            },
            text="quantidade",
        )
        fig.update_layout(
            **base_plotly_layout(height=500, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Quantidade de registros",
            yaxis_title="Categoria de preconceito",
            legend_title="Faixa de intensidade",
            barmode="stack",
        )
        st.plotly_chart(fig, width="stretch")

section_header(
    "Pares de preconceitos que aparecem juntos",
    "Tipos de preconceito identificados no mesmo registro. Sobreposição = coocorrências divididas pela menor contagem individual."
)
intersection_df = get_hate_type_intersectionality(filters, 25)
if intersection_df.empty:
    st.info("Não há coocorrências suficientes para análise de interseccionalidade.")
else:
    intersection_df["Par"] = intersection_df["hate_type_a_label"] + " + " + intersection_df["hate_type_b_label"]
    fig = px.bar(
        intersection_df,
        x="overlap_percentage_min",
        y="Par",
        orientation="h",
        color="total_cooccurrences",
        text="total_cooccurrences",
        color_continuous_scale=SEQUENTIAL_BLUE,
        hover_data=["count_a", "count_b", "overlap_percentage_max"],
        labels={
            "overlap_percentage_min": "Sobreposição (%)",
            "total_cooccurrences": "Coocorrências",
            "count_a": "Contagem do primeiro tipo",
            "count_b": "Contagem do segundo tipo",
            "overlap_percentage_max": "Sobreposição máxima (%)",
            "Par": "Par de preconceitos",
        },
    )
    fig.update_layout(
        **base_plotly_layout(height=500, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Sobreposição (%)",
        yaxis_title="Par de preconceitos",
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=10)
    st.plotly_chart(fig, width="stretch")

section_header(
    "Matriz de interseccionalidade",
    "Percentual de sobreposição entre todos os pares de tipos de preconceito. Diagonal = 100%."
)
matrix_df = get_hate_type_intersectionality_matrix(filters)
if matrix_df.empty:
    st.info("Sem dados para matriz de interseccionalidade.")
else:
    pivot = matrix_df.pivot_table(
        index="hate_type_a_label",
        columns="hate_type_b_label",
        values="overlap_percentage",
        fill_value=0,
    )
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=SEQUENTIAL_BLUE,
        text_auto=".1f",
        zmin=0,
        zmax=100,
    )
    fig.update_layout(
        **base_plotly_layout(height=600, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Tipo de preconceito",
        yaxis_title="Tipo de preconceito",
        coloraxis_colorbar_title="Sobreposição (%)",
    )
    st.plotly_chart(fig, width="stretch")

# Table for detailed inspection
with st.expander("Tabela detalhada de interseccionalidade"):
    if not intersection_df.empty:
        display_df = intersection_df.rename(columns={
            "hate_type_a_label": "Preconceito A",
            "hate_type_b_label": "Preconceito B",
            "total_cooccurrences": "Coocorrências",
            "count_a": "Contagem do preconceito A",
            "count_b": "Contagem do preconceito B",
            "overlap_percentage_min": "Sobreposição % (mín.)",
            "overlap_percentage_max": "Sobreposição % (máx.)",
        })[[
            "Preconceito A",
            "Preconceito B",
            "Coocorrências",
            "Contagem do preconceito A",
            "Contagem do preconceito B",
            "Sobreposição % (mín.)",
            "Sobreposição % (máx.)",
        ]]
        st.dataframe(display_df, width="stretch", height=400)
    else:
        st.info("Sem dados.")
