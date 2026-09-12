import plotly.express as px
import streamlit as st

from components.charts import SEQUENTIAL_BLUE, SEQUENTIAL_LAVENDER, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_nli_layer3_active_dimensions,
    get_nli_layer3_by_platform,
    get_nli_layer3_dimensions,
    get_nli_layer3_examples,
    get_nli_layer3_primary_dimensions,
    get_nli_layer3_summary,
    get_nli_layer3_toxicity_labels,
    get_nli_layer4_active_dimensions,
    get_nli_layer4_by_platform,
    get_nli_layer4_construct_scores,
    get_nli_layer4_dimensions,
    get_nli_layer4_primary_dimensions,
    get_nli_layer4_summary,
)

# Tradução das dimensões semânticas NLI para português
NLI_DIMENSION_LABELS = {
    # Layer 3
    "dehumanization": "Desumanização",
    "disrespect": "Desrespeito",
    "exclusion": "Exclusão",
    "humiliation": "Humilhação",
    "identity_attack": "Ataque à identidade",
    "insult": "Insulto",
    "threat": "Ameaça",
    "violence": "Violência",
    # Layer 4
    "authoritarianism": "Autoritarismo",
    "factualization": "Factualização",
    "masculinism": "Masculinismo",
    "revictimization": "Revitimização",
    "social_dominance": "Dominância social",
}

NLI_CONSTRUCT_LABELS = {
    "authoritarianism.authority_submission": "Autoritarismo · submissão à autoridade",
    "authoritarianism.exclusionary_conventionalism": "Autoritarismo · convencionalismo excludente",
    "authoritarianism.punitive_aggression": "Autoritarismo · agressão punitiva",
    "dehumanization.animalizing": "Desumanização · animalização",
    "dehumanization.mechanistic": "Desumanização · mecanização",
    "dehumanization.moral_disengagement": "Desumanização · desengajamento moral",
    "factualization.categorical_factualization": "Factualização · categórica",
    "factualization.suspicious_factualization": "Factualização · suspeita",
    "masculinism.antifeminism": "Masculinismo · antifeminismo",
    "masculinism.emasculation": "Masculinismo · emasculação",
    "masculinism.male_supremacy": "Masculinismo · supremacia masculina",
    "masculinism.resentment": "Masculinismo · ressentimento",
    "revictimization.harm_denial": "Revitimização · negação de dano",
    "revictimization.minority_blaming": "Revitimização · culpa da minoria",
    "revictimization.victim_offender_reversal": "Revitimização · inversão vítima-ofensor",
    "social_dominance.hierarchy_naturalization": "Dominância social · naturalização da hierarquia",
}


def translate_dimension(dim: str) -> str:
    """Traduz nome da dimensão NLI para português."""
    return NLI_DIMENSION_LABELS.get(dim, dim)


def translate_construct(construct: str) -> str:
    """Traduz construtos compostos do layer 4."""
    if construct in NLI_CONSTRUCT_LABELS:
        return NLI_CONSTRUCT_LABELS[construct]
    return construct.replace(".", " · ").replace("_", " ")


st.set_page_config(page_title="NLI Layers | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand("NLI layers · pt-BR")

render_hero(
    "NLI Layers",
    '<span class="hero-gradient">Análise semântica</span>',
    (
        "Leitura dos resultados NLI intermediários e avançados: dimensões semânticas, "
        "construtos discursivos, distribuição por rede e relação com a probabilidade de discurso de ódio da Gemma."
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

left, right = st.columns(2)

with left:
    section_header(
        "Dimensão primária",
        "Dimensão semântica dominante em cada comentário analisado pelo NLI layer 3.",
    )
    if primary_df.empty:
        st.info("Ainda não há dimensões primárias para exibir.")
    else:
        primary_df = primary_df.copy()
        primary_df["dimension_pt"] = primary_df["dimension"].apply(translate_dimension)
        fig = px.bar(
            primary_df.sort_values("total_results", ascending=True),
            x="total_results",
            y="dimension_pt",
            orientation="h",
            color="avg_toxicity_score",
            text="total_results",
            color_continuous_scale=SEQUENTIAL_WARM,
            hover_data=["avg_primary_score", "avg_gemma_hate_probability"],
            labels={
                "avg_toxicity_score": "Toxicidade média NLI",
                "avg_primary_score": "Score primário médio",
                "avg_gemma_hate_probability": "Probabilidade de discurso de ódio (Gemma)",
                "dimension_pt": "Dimensão",
                "total_results": "Registros",
            },
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
        dimensions_df = dimensions_df.copy()
        dimensions_df["dimension_pt"] = dimensions_df["dimension"].apply(translate_dimension)
        fig = px.bar(
            dimensions_df.sort_values("avg_score", ascending=True),
            x="avg_score",
            y="dimension_pt",
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

section_header(
    "Dimensões ativas",
    "Frequência das dimensões que ultrapassaram o limiar de ativação do layer 3.",
)
if active_df.empty:
    st.info("Nenhuma dimensão ativa registrada acima do limiar.")
else:
    active_df = active_df.copy()
    active_df["dimension_pt"] = active_df["dimension"].apply(translate_dimension)
    fig = px.bar(
        active_df.sort_values("total_results", ascending=True),
        x="total_results",
        y="dimension_pt",
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

layer4_summary = get_nli_layer4_summary().iloc[0]
layer4_platform_df = get_nli_layer4_by_platform()
layer4_primary_df = get_nli_layer4_primary_dimensions(20)
layer4_dimensions = get_nli_layer4_dimensions()
layer4_active_df = get_nli_layer4_active_dimensions(20)
layer4_constructs = get_nli_layer4_construct_scores(30)

section_header(
    "NLI Layer 4",
    "Camada de construtos discursivos: autoritarismo, desumanização, factualização, masculinismo, revitimização e dominância social.",
)
metric_grid(
    [
        ("Layer 4 registros", format_int(layer4_summary["total_results"])),
        ("Redes", format_int(layer4_summary["total_platforms"])),
        ("Dimensões primárias", format_int(layer4_summary["total_primary_dimensions"])),
        ("Score primário médio", f"{float(layer4_summary['avg_primary_score'] or 0):.3f}"),
    ]
)

left, right = st.columns(2)

with left:
    section_header(
        "Dimensão primária Layer 4",
        "Construto dominante em cada conteúdo analisado na camada 4.",
    )
    if layer4_primary_df.empty:
        st.info("Ainda não há dimensões primárias para layer 4.")
    else:
        layer4_primary_df = layer4_primary_df.copy()
        layer4_primary_df["dimension_pt"] = layer4_primary_df["dimension"].apply(translate_dimension)
        fig = px.bar(
            layer4_primary_df.sort_values("total_results", ascending=True),
            x="total_results",
            y="dimension_pt",
            orientation="h",
            color="avg_primary_score",
            text="total_results",
            color_continuous_scale=SEQUENTIAL_WARM,
            hover_data=["percent_results", "avg_gemma_hate_probability"],
            labels={
                "avg_primary_score": "Score primário médio",
                "percent_results": "% dos registros",
                "avg_gemma_hate_probability": "Probabilidade de discurso de ódio (Gemma)",
                "dimension_pt": "Dimensão",
                "total_results": "Registros",
            },
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros",
            yaxis_title="Dimensão",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Scores médios Layer 4",
        "Média dos scores por dimensão em dimension_scores.",
    )
    if layer4_dimensions.empty:
        st.info("Ainda não há scores de dimensão para layer 4.")
    else:
        layer4_dimensions = layer4_dimensions.copy()
        layer4_dimensions["dimension_pt"] = layer4_dimensions["dimension"].apply(translate_dimension)
        fig = px.bar(
            layer4_dimensions.sort_values("avg_score", ascending=True),
            x="avg_score",
            y="dimension_pt",
            orientation="h",
            color="avg_score",
            text="avg_score",
            color_continuous_scale=SEQUENTIAL_BLUE,
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.3f}")
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Score médio",
            yaxis_title="Dimensão",
        )
        st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header(
        "Layer 4 por rede",
        "Volume e score primário médio por plataforma.",
    )
    if layer4_platform_df.empty:
        st.info("Ainda não há distribuição por rede para layer 4.")
    else:
        fig = px.scatter(
            layer4_platform_df,
            x="total_results",
            y="avg_primary_score",
            size="total_results",
            color="avg_gemma_hate_probability",
            text="platform_label",
            color_continuous_scale=SEQUENTIAL_LAVENDER,
            hover_data=["total_dimensions"],
            labels={
                "avg_gemma_hate_probability": "Probabilidade de discurso de ódio (Gemma)",
                "total_results": "Registros",
                "avg_primary_score": "Score primário médio",
                "platform_label": "Rede",
                "total_dimensions": "Dimensões",
            },
        )
        fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="rgba(36,48,61,0.18)")))
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros layer 4",
            yaxis_title="Score primário médio",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Dimensões ativas Layer 4",
        "Frequência das dimensões acima do limiar de ativação.",
    )
    if layer4_active_df.empty:
        st.info("Nenhuma dimensão ativa registrada para layer 4.")
    else:
        layer4_active_df = layer4_active_df.copy()
        layer4_active_df["dimension_pt"] = layer4_active_df["dimension"].apply(translate_dimension)
        fig = px.bar(
            layer4_active_df.sort_values("total_results", ascending=True),
            x="total_results",
            y="dimension_pt",
            orientation="h",
            color="percent_results",
            text="percent_results",
            color_continuous_scale=SEQUENTIAL_LAVENDER,
        )
        fig.update_traces(marker_line_width=0, texttemplate="%{text:.2f}%")
        fig.update_layout(
            **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Registros",
            yaxis_title="Dimensão ativa",
        )
        st.plotly_chart(fig, width="stretch")

section_header(
    "Construtos Layer 4",
    "Médias dos subconstructos em construct_scores, úteis para interpretar o mecanismo discursivo dominante.",
)
if layer4_constructs.empty:
    st.info("Ainda não há construct_scores renderizáveis para layer 4.")
else:
    layer4_constructs = layer4_constructs.copy()
    layer4_constructs["construct_pt"] = layer4_constructs["construct"].apply(translate_construct)
    layer4_constructs["dimension_pt"] = layer4_constructs["dimension"].apply(translate_dimension)
    fig = px.bar(
        layer4_constructs.sort_values("avg_score", ascending=True).tail(18),
        x="avg_score",
        y="construct_pt",
        orientation="h",
        color="dimension_pt",
        text="avg_score",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data=["total_mentions"],
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{text:.3f}")
    fig.update_layout(
        **base_plotly_layout(height=620, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Score médio",
        yaxis_title="Construto",
        legend_title="Dimensão",
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
            "avg_gemma_hate_probability": "Probabilidade média de discurso de ódio (Gemma)",
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
                "Probabilidade média de discurso de ódio (Gemma)",
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
            "gemma_hate_probability": "Probabilidade de discurso de ódio (Gemma)",
            "text_excerpt": "Trecho",
            "created_at": "Criado em",
        }
    )
    # Traduz dimensão primária nos exemplos
    examples["Dimensão primária"] = examples["Dimensão primária"].apply(translate_dimension)
    st.dataframe(
        examples[
            [
                "ID",
                "Rede",
                "Dimensão primária",
                "Score primário",
                "Toxicidade NLI",
                "Rótulo NLI",
                "Probabilidade de discurso de ódio (Gemma)",
                "Trecho",
                "Criado em",
            ]
        ],
        width="stretch",
        height=520,
    )
