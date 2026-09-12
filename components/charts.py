CHART_TEMPLATE = "plotly_white"
CHART_FONT = "Inter, Source Sans 3, Arial, sans-serif"
CHART_TEXT = "#24303D"
CHART_MUTED = "#63746F"
CHART_GRID = "rgba(67, 94, 86, 0.12)"
CHART_ZERO = "rgba(67, 94, 86, 0.22)"

PRIMARY = "#2D866D"
MINT = "#7FCDBB"
LAVENDER = "#7B76D1"
SLATE = "#63746F"
SOFT_CORAL = "#F17373"
SAND = "#F2A93B"
TEAL = "#1EA4A6"
ROSE = "#C45B91"
SAGE = "#9BC56E"
OFF_WHITE = "#F4F5F3"
CARD_BG = "#FFFFFF"
HIGHLIGHT = "#E7F4EF"

SEQUENTIAL_BLUE = [
    HIGHLIGHT,
    "#CDEADF",
    "#2D866D",
]

SEQUENTIAL_MINT = [
    "#EFF9F5",
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
    TEAL,
    LAVENDER,
    SAND,
    SOFT_CORAL,
    SAGE,
    ROSE,
    SLATE,
    "#4B9DD8",
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
            "size": 11,
        },
        "coloraxis_showscale": coloraxis_showscale,
        "legend": {
            "orientation": "v",
            "bgcolor": "rgba(255,255,255,0.82)",
            "bordercolor": "rgba(225,232,228,0.9)",
            "borderwidth": 0,
            "font": {
                "color": CHART_MUTED,
                "size": 11,
            },
        },
        "hoverlabel": {
            "bgcolor": CARD_BG,
            "bordercolor": "rgba(230,225,220,0.95)",
            "font": {
                "color": CHART_TEXT,
                "family": CHART_FONT,
                "size": 11,
            },
        },
    }

    if include_axes:
        layout["xaxis"] = {
            "showgrid": False,
            "showline": False,
            "zerolinecolor": CHART_ZERO,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": CHART_MUTED,
            },
            "title_font": {
                "size": 11,
                "color": CHART_MUTED,
            },
        }
        layout["yaxis"] = {
            "gridcolor": CHART_GRID,
            "showline": False,
            "zerolinecolor": CHART_ZERO,
            "automargin": True,
            "tickfont": {
                "size": 10,
                "color": CHART_MUTED,
            },
            "title_font": {
                "size": 11,
                "color": CHART_MUTED,
            },
        }

    if height is not None:
        layout["height"] = height

    if margin is not None:
        layout["margin"] = margin

    return layout
