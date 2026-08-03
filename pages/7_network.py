from collections import defaultdict

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import networkx as nx
except ModuleNotFoundError:
    nx = None

from components.charts import CATEGORY_PALETTE, MINT, LAVENDER, PRIMARY, base_plotly_layout
from components.styles import load_css
from components.ui import format_int, metric_grid, render_hero, render_sidebar_brand, section_header
from services.queries import (
    CONTENT_KIND_LABELS,
    HATE_TYPE_LABELS,
    PLATFORM_LABELS,
    get_semantic_network_edges,
)


st.set_page_config(page_title="Rede | Radar", layout="wide", initial_sidebar_state="expanded")

load_css()
render_sidebar_brand()
filters = {}

render_hero(
    "Rede semântica",
    'Relações <span class="hero-gradient">entre tipos</span>',
    "Grafo entre redes sociais, tipos de conteúdo, hate_types e coocorrências.",
)

limit = 260
min_weight = 5

edges_df = get_semantic_network_edges(filters, limit=limit, min_weight=min_weight)
if edges_df.empty:
    st.warning("Nenhuma relação encontrada no banco.")
    st.stop()


def node_group(node):
    prefix = node.split(":", 1)[0]
    if prefix in {"conteúdo", "conteudo", "conteÃºdo"}:
        return "conteudo"
    if prefix == "rede":
        return "rede"
    if prefix == "tipo":
        return "tipo"
    return "outro"


def node_label(node):
    prefix, value = node.split(":", 1)
    group = node_group(node)
    if group == "rede":
        return PLATFORM_LABELS.get(value, value)
    if group == "tipo":
        return HATE_TYPE_LABELS.get(value, value)
    if group == "conteudo":
        return CONTENT_KIND_LABELS.get(value, value)
    return value


def node_color(node):
    group = node_group(node)
    if group == "rede":
        return PRIMARY
    if group == "conteudo":
        return MINT
    return LAVENDER


def fallback_layout(nodes, strengths):
    grouped = defaultdict(list)
    for node in nodes:
        grouped[node_group(node)].append(node)

    x_positions = {
        "rede": -1.35,
        "conteudo": 0.0,
        "tipo": 1.35,
        "outro": 0.0,
    }
    positions = {}
    for group, items in grouped.items():
        ordered = sorted(items, key=lambda item: (-strengths[item], node_label(item)))
        count = len(ordered)
        for idx, node in enumerate(ordered):
            y = 0 if count == 1 else 1.0 - (2.0 * idx / (count - 1))
            positions[node] = (x_positions.get(group, 0.0), y)
    return positions


def build_layout(edges):
    nodes = sorted(set(edges["source"]).union(set(edges["target"])))
    strengths = defaultdict(float)
    degrees = defaultdict(int)

    for _, row in edges.iterrows():
        source = row["source"]
        target = row["target"]
        weight = float(row["total"])
        strengths[source] += weight
        strengths[target] += weight
        degrees[source] += 1
        degrees[target] += 1

    if nx is None:
        return nodes, strengths, degrees, fallback_layout(nodes, strengths)

    graph = nx.Graph()
    for _, row in edges.iterrows():
        graph.add_edge(row["source"], row["target"], weight=float(row["total"]))

    positions = nx.spring_layout(graph, k=0.75, iterations=80, seed=42)
    return list(graph.nodes()), strengths, degrees, positions


nodes, strengths, degrees, pos = build_layout(edges_df)

edge_x = []
edge_y = []
for _, row in edges_df.iterrows():
    x0, y0 = pos[row["source"]]
    x1, y1 = pos[row["target"]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=0.85, color="rgba(104,117,137,0.26)"),
    hoverinfo="none",
    mode="lines",
)

node_x = []
node_y = []
node_text = []
node_size = []
node_colors = []
hover_text = []

for node in nodes:
    x, y = pos[node]
    degree = degrees[node]
    strength = strengths[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node_label(node))
    node_size.append(min(17 + degree * 3 + strength ** 0.35, 48))
    node_colors.append(node_color(node))
    hover_text.append(f"{node_label(node)}<br>Conexões: {degree}<br>Peso: {int(strength)}")

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers+text",
    hoverinfo="text",
    hovertext=hover_text,
    text=node_text,
    textposition="top center",
    textfont=dict(size=10, color="#27323F", family="Inter, sans-serif"),
    marker=dict(
        showscale=False,
        color=node_colors,
        size=node_size,
        line=dict(width=1, color="rgba(39,50,63,0.18)"),
    ),
)

fig = go.Figure(data=[edge_trace, node_trace])
network_layout = base_plotly_layout(height=760, margin=dict(b=10, l=5, r=5, t=10), include_axes=False)
network_layout.update(
    {
        "showlegend": False,
        "hovermode": "closest",
        "xaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
        "yaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
    }
)
fig.update_layout(**network_layout)

section_header("Grafo de relações", "Azul = redes · verde = conteúdo · lavanda = tipos de hate.")
st.plotly_chart(fig, width="stretch")

metric_grid(
    [
        ("Nós", format_int(len(nodes))),
        ("Relações", format_int(len(edges_df))),
        ("Peso total", format_int(edges_df["total"].sum())),
        ("Tipos de relação", format_int(edges_df["relation"].nunique())),
    ]
)

left, right = st.columns(2)
with left:
    section_header("Relações mais fortes", "Arestas com maior peso no grafo.")
    st.dataframe(
        edges_df.head(80).assign(
            origem=edges_df["source"].map(node_label),
            destino=edges_df["target"].map(node_label),
        )[["origem", "destino", "relation", "total"]].rename(
            columns={
                "origem": "Origem",
                "destino": "Destino",
                "relation": "Relação",
                "total": "Peso",
            }
        ),
        width="stretch",
        height=420,
    )

with right:
    section_header("Distribuição por relação", "Peso agregado por tipo de aresta.")
    relation_df = edges_df.groupby("relation", as_index=False)["total"].sum()
    fig = px.bar(
        relation_df,
        x="relation",
        y="total",
        color="relation",
        text="total",
        color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_layout(
        **base_plotly_layout(height=420, margin=dict(t=24, b=18, l=12, r=12)),
        xaxis_title="Relação",
        yaxis_title="Peso",
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")
