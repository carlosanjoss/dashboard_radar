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
    nav_items = [
        ("Início", "./"),
        ("Plataformas", "./plataformas"),
        ("Categorias de preconceito", "./categories"),
        ("Temporal", "./temporal"),
        ("Busca", "./search"),
        ("Nuvem de palavras", "./wordcloud"),
        ("Rede", "./network"),
        ("Posts", "./posts"),
        ("NLI", "./nli_layers"),
        ("Toxicidade tipos", "./toxicidade_tipos"),
        ("Comentários analisados", "./comentarios_llm"),
        ("Interseccionalidade", "./intersectionality"),
    ]
    links = "\n".join(
        f'<a class="top-nav-link" href="{href}" target="_self">{label}</a>'
        for label, href in nav_items
    )
    st.markdown(
        f"""
<div class="radar-topbar">
  <a class="top-brand" href="./" target="_self" aria-label="Radar início">
    <span class="top-brand-text">
      <span class="top-brand-title">RADAR</span>
      <span class="top-brand-kicker">{kicker}</span>
    </span>
  </a>
  <div class="top-nav-links">
    {links}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_hero(eyebrow, title, subtitle):
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-copy">
    <div class="hero-eyebrow">{eyebrow}</div>
    <div class="hero-title">{title}</div>
    <div class="hero-sub">{subtitle}</div>
    <div class="hero-chips">
      <span>Multirrede</span>
      <span>Gemma 3:4b</span>
      <span>Português Brasil</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(title, subtitle):
    st.markdown(
        f"""
<div class="section-card">
  <div>
    <div class="section-title">{title}</div>
    <div class="section-sub">{subtitle}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(title, value):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-topline">
    <span class="metric-title">{title}</span>
  </div>
  <div class="metric-value">{value}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_grid(cards):
    max_columns = 4
    for start in range(0, len(cards), max_columns):
        row = cards[start : start + max_columns]
        columns = st.columns(len(row))
        for col, (title, value) in zip(columns, row):
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
