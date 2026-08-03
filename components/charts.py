CHART_TEMPLATE = "plotly_white"
CHART_FONT = "Inter, Source Sans 3, Arial, sans-serif"
CHART_TEXT = "#27323F"
CHART_MUTED = "#687589"
CHART_GRID = "rgba(104, 117, 137, 0.16)"
CHART_ZERO = "rgba(104, 117, 137, 0.24)"

PRIMARY = "#426C9D"
MINT = "#6FAF92"
LAVENDER = "#9F8AC2"
SLATE = "#687589"
SOFT_CORAL = "#C97575"
SAND = "#C8B696"
OFF_WHITE = "#F7F4EF"
CARD_BG = "#FFFFFF"
HIGHLIGHT = "#EDF5F2"

SEQUENTIAL_BLUE = [
    HIGHLIGHT,
    "#D8E6F8",
    PRIMARY,
]

SEQUENTIAL_MINT = [
    "#F1F8F5",
    MINT,
    PRIMARY,
]

SEQUENTIAL_LAVENDER = [
    OFF_WHITE,
    LAVENDER,
    PRIMARY,
]

SEQUENTIAL_WARM = [
    OFF_WHITE,
    LAVENDER,
    SOFT_CORAL,
]

CATEGORY_PALETTE = [
    PRIMARY,
    MINT,
    LAVENDER,
    SAND,
    SLATE,
    SOFT_CORAL,
    "#4E8A93",
    "#9A7A54",
    "#7D90A6",
    "#B88A9B",
]

HATE_COLOR = SOFT_CORAL
NON_HATE_COLOR = MINT

CATEGORY_COLOR_MAP = {
    "nao_hate": MINT,
    "misoginia": SOFT_CORAL,
    "masculinismo": SAND,
    "violencia_sexual": "#C9788D",
    "controle_reprodutivo": PRIMARY,
    "ataque_mulher_poder": LAVENDER,
}


def base_plotly_layout(
    height=None,
    margin=None,
    coloraxis_showscale=False,
    include_axes=True,
):
    layout = {
        "template": CHART_TEMPLATE,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": CHART_TEXT,
            "family": CHART_FONT,
        },
        "coloraxis_showscale": coloraxis_showscale,
        "legend": {
            "font": {
                "color": CHART_MUTED,
            },
        },
    }

    if include_axes:
        layout["xaxis"] = {
            "showgrid": False,
            "zerolinecolor": CHART_ZERO,
            "tickfont": {
                "size": 11,
                "color": CHART_MUTED,
            },
            "title_font": {
                "size": 12,
                "color": CHART_MUTED,
            },
        }
        layout["yaxis"] = {
            "gridcolor": CHART_GRID,
            "zerolinecolor": CHART_ZERO,
            "tickfont": {
                "size": 11,
                "color": CHART_MUTED,
            },
            "title_font": {
                "size": 12,
                "color": CHART_MUTED,
            },
        }

    if height is not None:
        layout["height"] = height

    if margin is not None:
        layout["margin"] = margin

    return layout
