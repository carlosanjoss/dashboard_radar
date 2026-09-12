import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_sidebar_brand, section_header
from services.queries import (
    get_filter_options,
    get_hate_type_toxicity_summary,
    get_hate_type_toxicity_timeseries,
)


st.set_page_config(page_title="Toxicidade por Tipo | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()

st.markdown(
    """
    <style>
    .toxicity-title {
        margin: 6px 0 18px;
    }

    .toxicity-title h1 {
        margin: 0 0 6px;
        color: #2A313B;
        font-size: clamp(27px, 2.6vw, 38px);
        font-weight: 820;
        line-height: 1.08;
        letter-spacing: 0;
    }

    .toxicity-title p {
        max-width: 920px;
        margin: 0;
        color: #5F6875;
        font-family: 'Source Sans 3', 'Inter', sans-serif;
        font-size: 15.8px;
        font-weight: 520;
        line-height: 1.48;
    }

    .toxicity-control-caption {
        margin: 16px 0 7px;
        color: #2F3542;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 0 !important;
        align-items: center;
        margin-bottom: 8px;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        min-height: 34px;
        margin: 0 !important;
        padding: 0.42rem 0.7rem !important;
        border: 1px solid #D8D0C6 !important;
        border-right-width: 0 !important;
        border-radius: 0 !important;
        background: rgba(255,255,255,0.92) !important;
        box-shadow: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:first-child {
        border-radius: 9px 0 0 9px !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:last-child {
        border-right-width: 1px !important;
        border-radius: 0 9px 9px 0 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #2F3033 !important;
        border-color: #2F3033 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {
        color: #FFFFFF !important;
        font-weight: 820 !important;
    }

    div[data-testid="stSelectbox"] > label {
        display: none;
    }

    div[data-testid="stSelectbox"] {
        margin-bottom: 24px;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 39px !important;
        border-radius: 6px !important;
        background: #FFFFFF !important;
        box-shadow: none !important;
    }

    .toxicity-chart-note {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin: -4px 0 24px;
        color: #525B66;
        font-family: 'Source Sans 3', 'Inter', sans-serif;
        font-size: 12px;
        line-height: 1.35;
    }

    .toxicity-chart-note strong {
        color: #2446A6;
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 820;
        letter-spacing: -0.02em;
    }

    .toxicity-context {
        margin: 6px 0 2px;
        color: #6B7481;
        font-family: 'Source Sans 3', 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 560;
    }

    @media (max-width: 760px) {
        .toxicity-chart-note {
            align-items: flex-start;
            flex-direction: column;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            border-right-width: 1px !important;
            border-radius: 9px !important;
            margin: 0 6px 6px 0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

options = get_filter_options()
min_date = options.get("min_date")
max_date = options.get("max_date")
latest_year = max_date.year if max_date else 2026

date_caption = (
    f"{min_date:%d/%m/%Y} a {max_date:%d/%m/%Y}"
    if min_date and max_date
    else "período disponível no banco"
)

st.markdown(
    f"""
<div class="toxicity-title">
  <h1>Toxicidade por tipo de ódio online</h1>
  <p>Evolução temporal da participação de cada tipo nas menções de ódio online, com leitura comparável por período e linha de referência opcional.</p>
  <div class="toxicity-context">Base analisada: {date_caption}</div>
</div>
""",
    unsafe_allow_html=True,
)

month_labels = ["Todo período", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
month_map = {label: idx for idx, label in enumerate(month_labels[1:], start=1)}

st.markdown('<div class="toxicity-control-caption">Janela temporal</div>', unsafe_allow_html=True)
period_label = st.radio(
    "Janela temporal",
    month_labels,
    horizontal=True,
    label_visibility="collapsed",
    key="toxicity_type_period",
)

baseline_choice = st.selectbox(
    "Selecionar baseline",
    ["Sem referência", "Linha média entre tipos"],
    label_visibility="collapsed",
    key="toxicity_type_baseline",
)

if period_label == "Todo período":
    year = None
    month = None
    grain = "month"
    period_caption = date_caption
else:
    year = latest_year
    month = month_map[period_label]
    grain = "day"
    period_caption = f"{period_label}/{latest_year}"

series_df = get_hate_type_toxicity_timeseries(
    filters={},
    grain=grain,
    year=year,
    month=month,
    limit=10,
)
summary_df = get_hate_type_toxicity_summary(
    filters={},
    year=year,
    month=month,
    limit=10,
)

if series_df.empty or summary_df.empty:
    st.info("Não há dados suficientes para montar a série de toxicidade nesse período.")
    st.stop()

series_df = series_df.copy()
series_df["period"] = pd.to_datetime(series_df["period"])
series_df["percent_mentions"] = series_df["percent_mentions"].fillna(0)

top_share = summary_df.sort_values("percent_mentions", ascending=False).iloc[0]
top_volume = summary_df.sort_values("total_mentions", ascending=False).iloc[0]
share_baseline = 100 / max(series_df["hate_type"].nunique(), 1)

type_order = (
    series_df.groupby("hate_type")["total_mentions"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)

toxicity_palette = [
    "#3B35E8",
    "#F9507A",
    "#8B5CF6",
    "#EAB308",
    "#008C9E",
    "#F97316",
    "#16A34A",
    "#0EA5E9",
    "#B7791F",
    "#DB2777",
]
color_map = {hate_type: toxicity_palette[idx % len(toxicity_palette)] for idx, hate_type in enumerate(type_order)}

y_range = [0, 100]
y_dtick = 10

min_period = series_df["period"].min()
max_period = series_df["period"].max()
span_days = max(1, int((max_period - min_period).days))
if grain == "day":
    right_padding_days = max(4, int(span_days * 0.045))
else:
    right_padding_days = max(24, int(span_days * 0.065))
x_range = [min_period, max_period + pd.Timedelta(days=right_padding_days)]

fig = go.Figure()
label_points = []

for hate_type in type_order:
    group = series_df.loc[series_df["hate_type"] == hate_type].sort_values("period")
    if group.empty:
        continue

    label = group["hate_type_label"].iloc[0]
    color = color_map[hate_type]

    fig.add_trace(
        go.Scatter(
            x=group["period"],
            y=group["percent_mentions"],
            customdata=group[["total_mentions", "period_total_mentions", "avg_toxicity"]],
            mode="lines",
            name=label,
            opacity=0.94,
            line=dict(color=color, width=2.55, shape="linear"),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Período: %{x|%d/%m/%Y}<br>"
                "Participação: %{y:.2f}%<br>"
                "Menções do tipo: %{customdata[0]:,.0f}<br>"
                "Menções no período: %{customdata[1]:,.0f}<br>"
                "Probabilidade média Gemma: %{customdata[2]:.3f}<extra></extra>"
            ),
        )
    )

    last_row = group.iloc[-1]
    label_points.append(
        {
            "label": label,
            "color": color,
            "y": float(last_row["percent_mentions"]),
        }
    )

if baseline_choice == "Linha média entre tipos":
    fig.add_hline(
        y=share_baseline,
        line_dash="dot",
        line_color="rgba(76, 84, 96, 0.42)",
        line_width=1.2,
        annotation_text=f"referência {share_baseline:.1f}%",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#525B66"),
    )

label_step = min(0.047, 0.74 / max(len(label_points), 1))
label_start = 0.96
for idx, item in enumerate(label_points):
    fig.add_annotation(
        x=1.035,
        y=label_start - idx * label_step,
        xref="paper",
        yref="paper",
        text=f"<b>{item['label']}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        xshift=10,
        bgcolor="rgba(255,255,255,0.82)",
        borderpad=2,
        font=dict(color=item["color"], size=10, family="Inter, Arial, sans-serif"),
    )

fig.add_annotation(
    x=0,
    y=1.08,
    xref="paper",
    yref="paper",
    text="<b>Participação nas menções*</b>",
    showarrow=False,
    xanchor="left",
    yanchor="bottom",
    font=dict(color="#2F3033", size=13, family="Inter, Arial, sans-serif"),
)

line_layout = base_plotly_layout(height=610, margin=dict(t=68, b=48, l=34, r=245))
line_layout.update(
    {
        "showlegend": False,
        "hovermode": "x unified",
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "yaxis_title": "",
        "xaxis_title": "",
    }
)
fig.update_layout(**line_layout)
fig.update_yaxes(
    range=y_range,
    ticksuffix="%",
    dtick=y_dtick,
    gridcolor="rgba(47, 53, 66, 0.10)",
    zeroline=False,
)
fig.update_xaxes(
    range=x_range,
    showgrid=False,
    tickangle=-90,
    tickformat="%d %b" if grain == "day" else "%b<br>%Y",
    dtick=3 * 24 * 60 * 60 * 1000 if grain == "day" else ("M6" if span_days > 900 else "M1"),
)

st.plotly_chart(fig, width="stretch")

st.markdown(
    """
<div class="toxicity-chart-note">
  <span><u>*Participação</u> mostra o percentual de menções de cada tipo dentro dos registros com discurso de ódio no período. A probabilidade média Gemma permanece na tabela técnica como indicador auxiliar.</span>
  <strong>RADAR</strong>
</div>
""",
    unsafe_allow_html=True,
)

section_header("Resumo do período", "Métricas de apoio para interpretar a série temporal exibida.")
metric_grid(
    [
        ("Período", period_caption),
        ("Tipos analisados", format_int(summary_df["hate_type"].nunique())),
        ("Menções", format_int(summary_df["total_mentions"].sum())),
        ("Maior participação", f"{top_share['hate_type_label']} · {format_pct(top_share['percent_mentions'])}"),
        ("Maior volume", f"{top_volume['hate_type_label']} · {format_int(top_volume['total_mentions'])}"),
    ]
)

section_header(
    "Volume por tipo",
    "Barras empilhadas mostram quantas menções sustentam cada ponto da série temporal.",
)
volume_fig = go.Figure()
for hate_type in type_order:
    group = series_df.loc[series_df["hate_type"] == hate_type].sort_values("period")
    if group.empty:
        continue
    label = group["hate_type_label"].iloc[0]
    volume_fig.add_trace(
        go.Bar(
            x=group["period"],
            y=group["total_mentions"],
            name=label,
            marker=dict(color=color_map[hate_type]),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Período: %{x|%d/%m/%Y}<br>"
                "Menções: %{y:,.0f}<extra></extra>"
            ),
        )
    )

volume_fig.update_layout(
    **base_plotly_layout(height=330, margin=dict(t=20, b=34, l=14, r=18)),
    barmode="stack",
    showlegend=False,
    yaxis_title="Menções",
    xaxis_title="Período",
)
volume_fig.update_xaxes(showgrid=False)
st.plotly_chart(volume_fig, width="stretch")

left, right = st.columns(2)

with left:
    section_header("Ranking por participação", "Tipos com maior peso percentual entre as menções do período exibido.")
    ranking_df = summary_df.sort_values("percent_mentions", ascending=False)
    bar = go.Figure(
        go.Bar(
            x=ranking_df["percent_mentions"],
            y=ranking_df["hate_type_label"],
            orientation="h",
            marker=dict(color=ranking_df["percent_mentions"], colorscale=SEQUENTIAL_WARM),
            text=[format_pct(value) for value in ranking_df["percent_mentions"]],
            textposition="outside",
        )
    )
    bar.update_layout(
        **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=28)),
        xaxis_title="% das menções",
        yaxis_title="Tipo",
    )
    bar.update_xaxes(range=[0, 100], ticksuffix="%", dtick=10)
    bar.update_yaxes(autorange="reversed")
    st.plotly_chart(bar, width="stretch")

with right:
    section_header("Tabela técnica", "Volume, cobertura de plataformas e distribuição por posts/comentários.")
    st.dataframe(
        summary_df.rename(
            columns={
                "hate_type_label": "Tipo",
                "total_mentions": "Menções",
                "percent_mentions": "% das menções",
                "total_platforms": "Redes",
                "post_mentions": "Posts",
                "comment_mentions": "Comentários",
                "avg_toxicity": "Toxicidade média",
            }
        )[["Tipo", "Menções", "% das menções", "Redes", "Posts", "Comentários", "Toxicidade média"]],
        width="stretch",
        height=420,
    )
