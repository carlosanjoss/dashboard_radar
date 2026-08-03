import streamlit as st


def format_int(value):
    if value is None:
        value = 0
    return f"{int(value):,}".replace(",", ".")


def format_pct(value):
    if value is None:
        value = 0
    return f"{float(value):.2f}%".replace(".", ",")


def render_sidebar_brand(kicker="análise Gemma · pt-BR"):
    st.sidebar.markdown(
        f"""
<div class="sidebar-brand">RADAR</div>
<div class="sidebar-kicker">{kicker}</div>
<div class="sidebar-source">
<div class="sidebar-source-label">Fonte dos dados</div>
<div class="sidebar-source-title">PostgreSQL · radar_odio</div>
<div class="sidebar-source-meta">v_gemma_hate_results · gemma3:4b</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_hero(eyebrow, title, subtitle):
    st.markdown(
        f"""
<div class="hero">
<div class="hero-orb"></div>
<div class="hero-eyebrow">{eyebrow}</div>
<div class="hero-title">{title}</div>
<div class="hero-sub">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(title, subtitle):
    st.markdown(
        f"""
<div class="section-card">
<div class="section-title">{title}</div>
<div class="section-sub">{subtitle}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(title, value):
    st.markdown(
        f"""
<div class="metric-card">
<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_grid(cards):
    columns = st.columns(len(cards))
    for col, (title, value) in zip(columns, cards):
        with col:
            metric_card(title, value)


def nav_grid(items):
    cards = []
    for title, description in items:
        cards.append(
            f"""
<div class="nav-card">
<div class="nav-card-title">{title}</div>
<div class="nav-card-desc">{description}</div>
</div>
"""
        )
    st.markdown(
        '<div class="feature-grid">' + "\n".join(cards) + "</div>",
        unsafe_allow_html=True,
    )
