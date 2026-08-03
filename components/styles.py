import streamlit as st


def load_css():
    st.markdown(
        """
        <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;500;600;700&display=swap"
            rel="stylesheet"
        >

        <style>
        :root {
            --bg: #F7F4EF;
            --bg-soft: #FAF8F4;
            --surface: #FFFFFF;
            --surface-soft: #F4F7F5;
            --primary: #426C9D;
            --primary-soft: #E8EFF8;
            --mint: #6FAF92;
            --mint-soft: #EDF5F2;
            --lavender: #9F8AC2;
            --slate: #687589;
            --text: #27323F;
            --muted: #6C757D;
            --border: #E6E1DC;
            --border-strong: #D5CDC4;
            --danger-soft: #C97575;
            --radius: 8px;
            --shadow: 0 8px 18px rgba(39, 50, 63, 0.055);
            --shadow-flat: 0 1px 2px rgba(39, 50, 63, 0.045);
        }

        *, *::before, *::after {
            box-sizing: border-box;
        }

        html, body, .stApp {
            font-family: 'Inter', 'Source Sans 3', system-ui, sans-serif !important;
            color: var(--text);
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
        }

        .stApp {
            min-height: 100vh;
            overflow-x: hidden;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.42), rgba(255,255,255,0) 260px),
                var(--bg);
        }

        section[data-testid="stMain"] > div:first-child,
        .main .block-container,
        div[data-testid="stAppViewContainer"] .block-container {
            max-width: 1360px;
            padding: 1.45rem 2rem 3.2rem;
        }

        h1, h2, h3, h4, h5, h6,
        p, label, span, div {
            color: inherit;
        }

        .hero {
            padding: 8px 0 22px;
            margin: 0 0 20px;
            border-bottom: 1px solid var(--border);
        }

        .hero-orb {
            display: none;
        }

        .hero-eyebrow {
            display: inline-flex;
            width: fit-content;
            margin-bottom: 9px;
            padding: 4px 9px;
            border-radius: 999px;
            background: var(--mint-soft);
            border: 1px solid rgba(111, 175, 146, 0.26);
            color: #476F62;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.06em;
            line-height: 1.2;
            text-transform: uppercase;
        }

        .hero-title {
            max-width: 900px;
            margin-bottom: 8px;
            color: var(--text);
            font-size: clamp(27px, 2.8vw, 39px);
            font-weight: 760;
            line-height: 1.12;
            letter-spacing: 0;
        }

        .hero-gradient {
            color: var(--primary);
            background: none;
            -webkit-text-fill-color: currentColor;
        }

        .hero-sub {
            max-width: 880px;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 15.5px;
            font-weight: 500;
            line-height: 1.55;
        }

        .metric-card {
            min-height: 98px;
            padding: 16px 17px 15px;
            border-radius: var(--radius);
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            box-shadow: var(--shadow-flat);
        }

        .metric-card::before {
            display: none;
        }

        .metric-title {
            margin-bottom: 8px;
            color: var(--slate);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.06em;
            line-height: 1.3;
            text-transform: uppercase;
        }

        .metric-value {
            color: var(--text);
            font-size: clamp(23px, 2.2vw, 32px);
            font-weight: 760;
            line-height: 1.08;
            letter-spacing: 0;
            overflow-wrap: anywhere;
        }

        .section-card {
            padding: 0 0 10px;
            margin: 20px 0 12px;
            background: transparent;
            border-bottom: 1px solid var(--border);
        }

        .section-title {
            margin-bottom: 4px;
            color: var(--text);
            font-size: 17px;
            font-weight: 750;
            line-height: 1.25;
            letter-spacing: 0;
        }

        .section-sub {
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 13.5px;
            font-weight: 550;
            line-height: 1.45;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .feature-item,
        .nav-card {
            padding: 14px 15px;
            border-radius: var(--radius);
            background: var(--surface);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-flat);
        }

        .nav-card-title {
            color: var(--text);
            font-size: 14px;
            font-weight: 740;
            margin-bottom: 4px;
        }

        .nav-card-desc {
            color: var(--muted);
            font-size: 12.5px;
            line-height: 1.45;
        }

        .baseline-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin: 6px 0 18px;
        }

        .baseline-pill {
            padding: 7px 11px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--slate);
            font-size: 12px;
            font-weight: 700;
        }

        .baseline-pill.active {
            background: var(--text);
            border-color: var(--text);
            color: #FFFFFF;
        }

        .llm-card {
            min-height: 165px;
            padding: 18px;
            border-radius: var(--radius);
            background: var(--surface);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-flat);
        }

        .llm-label {
            margin-bottom: 8px;
            color: var(--slate);
            font-size: 11px;
            font-weight: 750;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .llm-text {
            color: var(--text);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.55;
            white-space: pre-wrap;
        }

        .wordcloud-panel {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 10px 18px;
            min-height: 360px;
            padding: 34px 30px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: var(--shadow-flat);
        }

        .word-token {
            display: inline-block;
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-weight: 700;
            line-height: 1;
            opacity: 0.95;
        }

        section[data-testid="stSidebar"] {
            background: #FFFFFF !important;
            border-right: 1px solid var(--border) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 1.1rem;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: var(--text) !important;
        }

        section[data-testid="stSidebar"] hr {
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 16px 0 !important;
        }

        .sidebar-brand {
            color: var(--text);
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0;
            padding: 4px 0 0;
        }

        .sidebar-kicker,
        .sidebar-label,
        .sidebar-source-label {
            color: var(--slate);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .sidebar-kicker {
            margin-top: 2px;
            margin-bottom: 14px;
        }

        .sidebar-source {
            margin: 0 0 18px;
            padding: 12px 12px 11px;
            border-radius: var(--radius);
            background: var(--bg-soft);
            border: 1px solid var(--border);
        }

        .sidebar-source-title {
            margin-top: 6px;
            color: var(--text);
            font-size: 13px;
            font-weight: 720;
            line-height: 1.25;
        }

        .sidebar-source-meta {
            margin-top: 3px;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 12.5px;
            line-height: 1.35;
        }

        [data-testid="stSidebarNav"] a,
        [data-testid="stNavItem"] a,
        nav[aria-label="Navigation"] a {
            border-radius: var(--radius) !important;
            color: var(--slate) !important;
            font-weight: 650 !important;
        }

        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stNavItem"] a:hover,
        nav[aria-label="Navigation"] a:hover {
            background: var(--primary-soft) !important;
            color: var(--text) !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stNavItem"] a[aria-current="page"],
        nav[aria-label="Navigation"] a[aria-current="page"] {
            background: var(--primary-soft) !important;
            color: var(--primary) !important;
            font-weight: 760 !important;
        }

        .stSelectbox label,
        .stSlider label,
        .stTextInput label,
        .stCheckbox label,
        .stRadio label,
        .stMultiSelect label,
        .stNumberInput label {
            color: var(--slate) !important;
            font-size: 12px !important;
            font-weight: 710 !important;
            letter-spacing: 0.03em !important;
            text-transform: uppercase !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        textarea,
        input {
            border-radius: var(--radius) !important;
            border-color: var(--border) !important;
            background: var(--surface) !important;
            color: var(--text) !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stNumberInput"] input:hover,
        textarea:hover,
        input:hover {
            border-color: rgba(66, 108, 157, 0.48) !important;
        }

        div[data-baseweb="select"] * {
            color: var(--text) !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #9AA4B2 !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 0.45rem;
        }

        div[data-testid="stRadio"] label {
            background: rgba(255,255,255,0.76);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.28rem 0.52rem;
        }

        div[data-testid="stRadio"] label:hover {
            border-color: rgba(66, 108, 157, 0.36);
            background: #FFFFFF;
        }

        div[data-testid="stSlider"] [role="slider"] {
            background: var(--primary) !important;
            box-shadow: 0 0 0 4px rgba(66, 108, 157, 0.12) !important;
        }

        div[data-testid="stDataFrame"] {
            overflow: hidden;
            border-radius: var(--radius) !important;
            border: 1px solid var(--border) !important;
            box-shadow: var(--shadow-flat);
            background: var(--surface);
        }

        div[data-testid="stPlotlyChart"] {
            padding: 10px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: var(--shadow-flat);
            overflow: hidden;
        }

        div[data-testid="stImage"] {
            padding: 10px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: var(--shadow-flat);
        }

        div[data-testid="stAlert"] {
            border-radius: var(--radius) !important;
            border-width: 1px !important;
        }

        .stButton > button,
        div[data-testid="stButton"] > button {
            border-radius: var(--radius) !important;
            border: 1px solid rgba(66, 108, 157, 0.42) !important;
            background: var(--primary) !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 730 !important;
            padding: 0.48rem 1rem !important;
            box-shadow: none !important;
        }

        div[data-testid="stExpander"] {
            border-radius: var(--radius) !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            box-shadow: var(--shadow-flat);
            overflow: hidden;
        }

        div[data-testid="stTabs"] button {
            color: var(--slate) !important;
            font-weight: 650 !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--primary) !important;
        }

        hr {
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 20px 0 !important;
        }

        #MainMenu,
        footer,
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        button[data-testid="stSidebarCollapsedControl"],
        button[kind="header"][data-testid="baseButton-header"] {
            border-radius: var(--radius) !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            color: var(--slate) !important;
            box-shadow: var(--shadow-flat) !important;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: #CFC8C1;
            border-radius: 999px;
            border: 2px solid transparent;
            background-clip: padding-box;
        }

        @media (max-width: 900px) {
            section[data-testid="stMain"] > div:first-child,
            .main .block-container,
            div[data-testid="stAppViewContainer"] .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-title {
                font-size: 30px;
            }

            .metric-card {
                min-height: 92px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
