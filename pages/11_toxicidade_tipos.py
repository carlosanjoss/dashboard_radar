import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from components.charts import CATEGORY_PALETTE, SEQUENTIAL_WARM, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, format_pct, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    get_filter_options,
    get_hate_type_toxicity_summary,
    get_hate_type_toxicity_timeseries,
)


st.set_page_config(page_title="Toxicidade por Tipo | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()

options = get_filter_options()
min_date = options.get("min_date")
max_date = options.get("max_date")
latest_year = max_date.year if max_date else 2026

render_hero(
    "Toxicidade por tipo",
    'Evolução da <span class="hero-gradient">toxicidade</span>',
    (
        "Acompanhamento temporal da probabilidade média de hate por tipo de discurso de ódio. "
        "A leitura combina intensidade média e volume para evitar conclusões baseadas em poucos registros."
    ),
)

month_labels = ["Todo período", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
month_map = {label: idx for idx, label in enumerate(month_labels[1:], start=1)}
period_label = st.radio("Janela temporal", month_labels, horizontal=True)

if period_label == "Todo período":
    year = None
    month = None
    grain = "month"
    period_caption = (
        f"{min_date:%d/%m/%Y} a {max_date:%d/%m/%Y}"
        if min_date and max_date
        else "todo o período disponível"
    )
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
    limit=8,
)
summary_df = get_hate_type_toxicity_summary(
    filters={},
    year=year,
    month=month,
    limit=12,
)

if series_df.empty or summary_df.empty:
    st.info("Não há dados suficientes para montar a série de toxicidade nesse período.")
    st.stop()

series_df = series_df.copy()
series_df["period"] = pd.to_datetime(series_df["period"])

top_avg = summary_df.sort_values("avg_toxicity", ascending=False).iloc[0]
top_volume = summary_df.sort_values("total_mentions", ascending=False).iloc[0]
weighted_avg = (
    (series_df["avg_toxicity"] * series_df["total_mentions"]).sum()
    / max(series_df["total_mentions"].sum(), 1)
)

metric_grid(
    [
        ("Período", period_caption),
        ("Tipos analisados", format_int(summary_df["hate_type"].nunique())),
        ("Menções", format_int(summary_df["total_mentions"].sum())),
        ("Maior média", f"{top_avg['hate_type_label']} · {format_pct(top_avg['avg_toxicity'] * 100)}"),
        ("Maior volume", f"{top_volume['hate_type_label']} · {format_int(top_volume['total_mentions'])}"),
    ]
)

section_header(
    "Toxicidade média no tempo",
    "Linhas mostram a média de hate_probability por tipo; a linha pontilhada indica a média ponderada do período.",
)

palette = CATEGORY_PALETTE + ["#4E8A93", "#B88A9B", "#7D90A6", "#9A7A54"]
type_order = (
    summary_df.sort_values(["total_mentions", "avg_toxicity"], ascending=False)["hate_type"]
    .drop_duplicates()
    .tolist()
)
color_map = {hate_type: palette[idx % len(palette)] for idx, hate_type in enumerate(type_order)}

min_y = float(series_df["avg_toxicity"].min())
max_y = float(series_df["avg_toxicity"].max())
spread = max_y - min_y
padding = max(spread * 0.2, 0.025)
y_range = [max(0, min_y - padding), min(1, max_y + padding)]
if y_range[0] == y_range[1]:
    y_range = [max(0, y_range[0] - 0.03), min(1, y_range[1] + 0.03)]

fig = go.Figure()
markers_mode = "lines+markers" if series_df["period"].nunique() <= 18 else "lines"

for hate_type in type_order:
    group = series_df.loc[series_df["hate_type"] == hate_type].sort_values("period")
    if group.empty:
        continue
    label = group["hate_type_label"].iloc[0]
    fig.add_trace(
        go.Scatter(
            x=group["period"],
            y=group["avg_toxicity"],
            customdata=group[["total_mentions"]],
            mode=markers_mode,
            name=label,
            line=dict(color=color_map[hate_type], width=2.6),
            marker=dict(size=5, color=color_map[hate_type]),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Período: %{x|%d/%m/%Y}<br>"
                "Toxicidade média: %{y:.3f}<br>"
                "Menções: %{customdata[0]:,.0f}<extra></extra>"
            ),
        )
    )

fig.add_hline(
    y=weighted_avg,
    line_dash="dot",
    line_color="rgba(104,117,137,0.72)",
    line_width=1.4,
    annotation_text=f"Média ponderada: {weighted_avg:.3f}",
    annotation_position="top left",
    annotation_font=dict(size=11, color="#687589"),
)
line_layout = base_plotly_layout(height=560, margin=dict(t=58, b=36, l=14, r=18))
line_layout["legend"].update(
    {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "left",
        "x": 0,
        "title_text": "",
    }
)
line_layout.update(
    {
        "showlegend": True,
        "hovermode": "x unified",
        "yaxis_title": "Toxicidade média",
        "xaxis_title": "Período",
    }
)
fig.update_layout(**line_layout)
fig.update_yaxes(range=y_range, tickformat=".2f")
fig.update_xaxes(showgrid=False)
st.plotly_chart(fig, width="stretch")

st.caption(
    "Toxicidade é a média de hate_probability dos conteúdos classificados como hate pelo Gemma. "
    "A métrica é automatizada e pode conter falsos positivos e falsos negativos."
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
    section_header("Ranking por média", "Tipos com maior toxicidade média no período exibido.")
    ranking_df = summary_df.sort_values("avg_toxicity", ascending=False)
    bar = go.Figure(
        go.Bar(
            x=ranking_df["avg_toxicity"],
            y=ranking_df["hate_type_label"],
            orientation="h",
            marker=dict(color=ranking_df["avg_toxicity"], colorscale=SEQUENTIAL_WARM),
            text=[f"{value:.3f}" for value in ranking_df["avg_toxicity"]],
            textposition="outside",
        )
    )
    bar.update_layout(
        **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=28)),
        xaxis_title="Toxicidade média",
        yaxis_title="Tipo",
    )
    bar.update_yaxes(autorange="reversed")
    st.plotly_chart(bar, width="stretch")

with right:
    section_header("Tabela técnica", "Volume, cobertura de plataformas e distribuição por posts/comentários.")
    st.dataframe(
        summary_df.rename(
            columns={
                "hate_type_label": "Tipo",
                "total_mentions": "Menções",
                "total_platforms": "Redes",
                "post_mentions": "Posts",
                "comment_mentions": "Comentários",
                "avg_toxicity": "Toxicidade média",
            }
        )[["Tipo", "Menções", "Redes", "Posts", "Comentários", "Toxicidade média"]],
        width="stretch",
        height=420,
    )
