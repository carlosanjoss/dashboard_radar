import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_LAVENDER, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_nli_layer3_active_dimensions,
    get_nli_layer3_by_platform,
    get_nli_layer3_dimensions,
    get_nli_layer3_examples,
    get_nli_layer3_gemma_buckets,
    get_nli_layer3_primary_dimensions,
    get_nli_layer3_summary,
    get_nli_layer3_toxicity_labels,
    get_nli_layer4_dimensions,
    get_nli_layer4_summary,
)


st.set_page_config(page_title="NLI Layer 3 | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand("NLI layer 3 · pt-BR")

render_hero(
    "NLI Layer 3",
    'Análise semântica <span class="hero-gradient">intermediária</span>',
    (
        "Leitura dos resultados da view v_radar_nli_layer3_results: dimensões semânticas, "
        "toxicidade NLI, distribuição por rede e relação com a probabilidade de hate da Gemma."
    ),
)

layer3_summary = get_nli_layer3_summary().iloc[0]

metric_grid(
    [
        ("Registros NLI", format_int(layer3_summary["total_results"])),
        ("Redes", format_int(layer3_summary["total_platforms"])),
        ("Score primário médio", f"{float(layer3_summary['avg_primary_score'] or 0):.3f}"),
        ("Toxicidade média", f"{float(layer3_summary['avg_toxicity_score'] or 0):.3f}"),
    ]
)

labels_df = get_nli_layer3_toxicity_labels()
platform_df = get_nli_layer3_by_platform()
primary_df = get_nli_layer3_primary_dimensions(20)
dimensions_df = get_nli_layer3_dimensions()
active_df = get_nli_layer3_active_dimensions(20)
bucket_df = get_nli_layer3_gemma_buckets()

left, right = st.columns(2)

with left:
    section_header(
        "Distribuição de toxicidade NLI",
        "Volume e percentual por rótulo de toxicidade atribuído no layer 3.",
    )
    if labels_df.empty:
        st.info("Ainda não há rótulos de toxicidade NLI para exibir.")
    else:
        fig = px.bar(
            labels_df,
            x="toxicity_label",
            y="total_results",
            color="avg_toxicity_score",
            text="percent_results",
            color_continuous_scale=SEQUENTIAL_WARM,
            hover_data=["avg_toxicity_score", "avg_primary_score"],
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=400, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Rótulo NLI",
            yaxis_title="Registros",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Layer 3 por rede",
        "Toxicidade média e volume de resultados NLI por plataforma.",
    )
    if platform_df.empty:
        st.info("Ainda não há distribuição por rede.")
    else:
        fig = px.scatter(
            platform_df,
            x="total_results",
            y="avg_toxicity_score",
            size="total_results",
            color="avg_primary_score",
            text="platform_label",
            color_continuous_scale=SEQUENTIAL_BLUE,
            hover_data=["avg_gemma_hate_probability", "total_dimensions"],
        )
        fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="rgba(39,50,63,0.18)")))
        fig.update_layout(
            **base_plotly_layout(height=400, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros NLI",
            yaxis_title="Toxicidade média NLI",
        )
        st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header(
        "Dimensão primária",
        "Dimensão semântica dominante em cada comentário analisado pelo NLI layer 3.",
    )
    if primary_df.empty:
        st.info("Ainda não há dimensões primárias para exibir.")
    else:
        fig = px.bar(
            primary_df.sort_values("total_results", ascending=True),
            x="total_results",
            y="dimension",
            orientation="h",
            color="avg_toxicity_score",
            text="total_results",
            color_continuous_scale=SEQUENTIAL_WARM,
            hover_data=["avg_primary_score", "avg_gemma_hate_probability"],
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            **base_plotly_layout(height=470, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros",
            yaxis_title="Dimensão",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Scores médios por dimensão",
        "Média dos scores disponíveis no JSONB dimension_scores.",
    )
    if dimensions_df.empty:
        st.info("Ainda não há dimensões renderizáveis para layer 3.")
    else:
        fig = px.bar(
            dimensions_df.sort_values("avg_score", ascending=True),
            x="avg_score",
            y="dimension",
            orientation="h",
            color="avg_score",
            text="avg_score",
            color_continuous_scale=SEQUENTIAL_BLUE,
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.3f}")
        fig.update_layout(
            **base_plotly_layout(height=470, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Score médio",
            yaxis_title="Dimensão",
        )
        st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header(
        "Dimensões ativas",
        "Frequência das dimensões que ultrapassaram o limiar de ativação do layer 3.",
    )
    if active_df.empty:
        st.info("Nenhuma dimensão ativa registrada acima do limiar.")
    else:
        fig = px.bar(
            active_df.sort_values("total_results", ascending=True),
            x="total_results",
            y="dimension",
            orientation="h",
            color="percent_results",
            text="percent_results",
            color_continuous_scale=SEQUENTIAL_LAVENDER,
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros",
            yaxis_title="Dimensão ativa",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Gemma x NLI layer 3",
        "Toxicidade média NLI por faixa de probabilidade de hate da Gemma.",
    )
    if bucket_df.empty:
        st.info("Sem probabilidade Gemma associada aos resultados NLI.")
    else:
        fig = px.line(
            bucket_df,
            x="gemma_probability_bucket",
            y="avg_nli_toxicity",
            markers=True,
            text="total_results",
            color_discrete_sequence=[CATEGORY_PALETTE[0]],
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8), textposition="top center")
        fig.update_layout(
            **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Faixa de probabilidade Gemma",
            yaxis_title="Toxicidade média NLI",
        )
        st.plotly_chart(fig, width="stretch")

section_header(
    "Tabela técnica do Layer 3",
    "Agregação por rede para auditoria dos volumes, scores médios e rótulos de toxicidade.",
)
if not platform_df.empty:
    table = platform_df.rename(
        columns={
            "platform_label": "Rede",
            "total_results": "Registros",
            "total_dimensions": "Dimensões primárias",
            "avg_primary_score": "Score primário médio",
            "avg_toxicity_score": "Toxicidade média NLI",
            "avg_gemma_hate_probability": "Probabilidade Gemma média",
            "high_toxicity": "Alta",
            "medium_toxicity": "Média",
            "low_toxicity": "Baixa",
            "non_toxic": "Não tóxico",
        }
    )
    st.dataframe(
        table[
            [
                "Rede",
                "Registros",
                "Dimensões primárias",
                "Score primário médio",
                "Toxicidade média NLI",
                "Probabilidade Gemma média",
                "Alta",
                "Média",
                "Baixa",
                "Não tóxico",
            ]
        ],
        width="stretch",
        height=330,
    )

section_header(
    "Exemplos de maior toxicidade NLI",
    "Amostra para auditoria qualitativa; exemplos individuais não são evidência estatística.",
)
examples_df = get_nli_layer3_examples(50)
if examples_df.empty:
    st.info("Nenhum exemplo NLI disponível.")
else:
    examples = examples_df.rename(
        columns={
            "result_id": "ID",
            "platform_label": "Rede",
            "primary_dimension": "Dimensão primária",
            "primary_score": "Score primário",
            "toxicity_score": "Toxicidade NLI",
            "toxicity_label": "Rótulo NLI",
            "gemma_hate_probability": "Probabilidade Gemma",
            "text_excerpt": "Trecho",
            "created_at": "Criado em",
        }
    )
    st.dataframe(
        examples[
            [
                "ID",
                "Rede",
                "Dimensão primária",
                "Score primário",
                "Toxicidade NLI",
                "Rótulo NLI",
                "Probabilidade Gemma",
                "Trecho",
                "Criado em",
            ]
        ],
        width="stretch",
        height=520,
    )

with st.expander("Resumo secundário do Layer 4"):
    layer4_summary = get_nli_layer4_summary().iloc[0]
    metric_grid(
        [
            ("Layer 4 registros", format_int(layer4_summary["total_results"])),
            ("Layer 4 redes", format_int(layer4_summary["total_platforms"])),
            ("Score primário médio", f"{float(layer4_summary['avg_primary_score'] or 0):.3f}"),
        ]
    )
    layer4_dimensions = get_nli_layer4_dimensions()
    if layer4_dimensions.empty:
        st.info("Ainda não há dimensões renderizáveis para layer 4.")
    else:
        fig = px.bar(
            layer4_dimensions.sort_values("avg_score", ascending=True),
            x="avg_score",
            y="dimension",
            orientation="h",
            color="avg_score",
            text="avg_score",
            color_continuous_scale=SEQUENTIAL_LAVENDER,
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.3f}")
        fig.update_layout(
            **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Score médio",
            yaxis_title="Dimensão",
        )
        st.plotly_chart(fig, width="stretch")
