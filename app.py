import plotly.express as px
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_BLUE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, nav_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    MODEL_NAME,
    get_content_kind_analysis,
    get_hate_type_frequency,
    get_overview_metrics,
    get_platform_analysis,
    get_quality_metrics,
)


st.set_page_config(
    page_title="Radar de Ódio",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Visão geral",
    'Radar de <span class="hero-gradient">discurso de ódio</span>',
    (
        f"Painel multirrede baseado no PostgreSQL radar_odio e nas classificações do modelo "
        f"{MODEL_NAME}. As métricas carregam o banco completo, sem filtro global lateral."
    ),
)

metrics = get_overview_metrics(filters).iloc[0]
metric_grid(
    [
        ("Conteúdos", format_int(metrics["total_content"])),
        ("Hate", format_int(metrics["total_hate"])),
        ("Não hate", format_int(metrics["total_non_hate"])),
        ("Taxa hate", format_pct(metrics["hate_percent"])),
        ("Redes", format_int(metrics["total_platforms"])),
    ]
)

left, right = st.columns(2)

with left:
    section_header(
        "Prevalência por rede",
        "Percentual de hate com o volume absoluto como intensidade de cor.",
    )
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
            **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="% hate",
            yaxis_title="Rede social",
        )
        st.plotly_chart(fig, width="stretch")

with right:
    section_header(
        "Tipo de conteúdo",
        "Comparação entre posts e comentários no banco completo.",
    )
    kind_df = get_content_kind_analysis(filters)
    if kind_df.empty:
        st.info("Nenhum tipo de conteúdo disponível.")
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
            **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
            xaxis_title="Tipo",
            yaxis_title="% hate",
        )
        st.plotly_chart(fig, width="stretch")

section_header(
    "Tipologias principais",
    "Frequência dos tipos de discurso de ódio detectados pelo Gemma.",
)
type_df = get_hate_type_frequency(filters, 12)
if not type_df.empty:
    fig = px.bar(
        type_df,
        x="total_mentions",
        y="hate_type_label",
        orientation="h",
        color="hate_type_label",
        color_discrete_sequence=CATEGORY_PALETTE,
        text="total_mentions",
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        **base_plotly_layout(height=430, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Menções",
        yaxis_title="Tipo de hate",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

section_header(
    "Qualidade do corpus",
    "Indicadores metodológicos para leitura cautelosa dos resultados.",
)
quality = get_quality_metrics(filters).iloc[0]
metric_grid(
    [
        ("Sem texto", format_int(quality["empty_text_records"])),
        ("Sem data", format_int(quality["missing_date_records"])),
        ("Datas futuras", format_int(quality["future_date_records"])),
        ("Duplicados", format_int(quality["duplicate_rows"])),
    ]
)

section_header(
    "Páginas de análise",
    "As análises detalhadas ficam separadas por tema para manter o painel organizado.",
)
nav_grid(
    [
        ("1. Visão geral", "Resumo executivo, ranking de redes e tabela de registros recentes."),
        ("2. Redes sociais", "Volume, prevalência, fontes de coleta, idioma e tipos de conteúdo."),
        ("3. Categorias", "Tipologias Gemma, categorias, matriz rede x tipo e probabilidades."),
        ("4. Temporal", "Evolução por dia, semana, mês ou ano."),
        ("5. Busca", "Consulta textual com paginação no backend."),
        ("6. Léxico", "Termos frequentes e nuvem de palavras baseada em agregações SQL."),
        ("7. Rede", "Grafo de relações entre redes, tipos e coocorrências."),
        ("8. Autores", "Perfis anonimizados, atividade e concentração de hate."),
        ("9. Posts", "Threads/conteúdos com maior volume e registros associados."),
        ("10. NLI", "Camadas NLI layer 3 e layer 4."),
        ("11. Toxicidade por tipo", "Série temporal estilo baseline para os tipos de discurso de ódio."),
        ("12. Comentários e LLM", "Consulta de comentários com evidência e justificativa da Gemma."),
    ]
)
