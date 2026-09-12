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
            --bg: #F6F1EA;
            --bg-deep: #EEE7DD;
            --surface: rgba(255, 255, 255, 0.88);
            --surface-solid: #FFFFFF;
            --surface-soft: #F9FBF8;
            --surface-mint: #EAF3F0;
            --surface-lavender: #F0ECF7;
            --primary: #4D74A6;
            --primary-strong: #315B86;
            --primary-soft: #E5EDF7;
            --mint: #75B79A;
            --mint-strong: #4D876F;
            --mint-soft: #EAF5F0;
            --lavender: #A596C8;
            --lavender-strong: #7C6EAD;
            --sand: #CDBA9D;
            --coral: #C97878;
            --text: #24303D;
            --muted: #647287;
            --muted-soft: #8995A5;
            --border: #E3DDD4;
            --border-strong: #D4CABF;
            --radius-sm: 16px;
            --radius: 24px;
            --radius-lg: 32px;
            --radius-xl: 42px;
            --shadow-soft: 0 14px 34px rgba(36, 48, 61, 0.08);
            --shadow-card: 0 24px 64px rgba(36, 48, 61, 0.105);
            --shadow-float: 0 34px 80px rgba(36, 48, 61, 0.12);
            --shadow-focus: 0 0 0 4px rgba(77, 116, 166, 0.15);
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
                radial-gradient(circle at -8% -10%, rgba(117, 183, 154, 0.28), transparent 410px),
                radial-gradient(circle at 104% 2%, rgba(165, 150, 200, 0.28), transparent 420px),
                radial-gradient(circle at 58% 106%, rgba(77, 116, 166, 0.12), transparent 520px),
                linear-gradient(180deg, #FBFAF7 0%, var(--bg) 45%, var(--bg-deep) 100%);
        }

        section[data-testid="stMain"] {
            background: transparent;
        }

        section[data-testid="stMain"] > div:first-child,
        .main .block-container,
        div[data-testid="stAppViewContainer"] .block-container {
            max-width: 1440px;
            padding: 2rem 2.35rem 3.8rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 1.12rem;
        }

        div[data-testid="column"] {
            min-width: 0;
        }

        h1, h2, h3, h4, h5, h6,
        p, label, span, div {
            color: inherit;
        }

        .radar-topbar {
            position: sticky;
            top: 10px;
            z-index: 999;
            display: flex;
            align-items: center;
            gap: 14px;
            width: 100%;
            margin: 0 0 26px;
            padding: 10px 12px 10px 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 18px 44px rgba(36, 48, 61, 0.10);
            backdrop-filter: blur(18px);
        }

        .top-brand {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            min-width: max-content;
            padding: 5px 11px 5px 5px;
            border-radius: 999px;
            color: var(--text) !important;
            text-decoration: none !important;
            background: linear-gradient(135deg, rgba(234,245,240,0.92), rgba(229,237,247,0.82));
        }

        .top-brand-mark {
            display: grid;
            place-items: center;
            width: 38px;
            height: 38px;
            border-radius: 999px;
            color: #FFFFFF;
            background:
                radial-gradient(circle at 30% 24%, rgba(255,255,255,0.92), transparent 33%),
                linear-gradient(135deg, var(--primary), var(--mint));
            font-size: 17px;
            font-weight: 820;
            box-shadow: 0 10px 22px rgba(77, 116, 166, 0.18);
        }

        .top-brand-text {
            display: grid;
            gap: 2px;
            line-height: 1;
        }

        .top-brand-title {
            color: var(--text);
            font-size: 15px;
            font-weight: 840;
            letter-spacing: 0.02em;
        }

        .top-brand-kicker {
            color: var(--muted);
            font-size: 8.5px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .top-nav-links {
            display: flex;
            align-items: center;
            gap: 7px;
            min-width: 0;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 4px 2px 4px 0;
            scrollbar-width: thin;
        }

        .top-nav-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 34px;
            padding: 8px 13px;
            border: 1px solid transparent;
            border-radius: 999px;
            color: var(--muted) !important;
            font-size: 12px;
            font-weight: 760;
            line-height: 1;
            text-decoration: none !important;
            white-space: nowrap;
            transition: background-color 140ms ease, color 140ms ease, transform 140ms ease;
        }

        .top-nav-link:hover {
            transform: translateY(-1px);
            border-color: rgba(77, 116, 166, 0.14);
            background: linear-gradient(90deg, var(--primary-soft), var(--mint-soft));
            color: var(--primary-strong) !important;
        }

        .hero {
            position: relative;
            isolation: isolate;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 230px;
            gap: 28px;
            align-items: center;
            min-height: 278px;
            margin: 0 0 32px;
            padding: 40px 44px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.82);
            border-radius: var(--radius-xl);
            background:
                linear-gradient(135deg, rgba(255,255,255,0.94) 0%, rgba(234,245,240,0.86) 54%, rgba(240,236,247,0.78) 100%);
            box-shadow: var(--shadow-float);
            backdrop-filter: blur(18px);
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: 1px;
            border-radius: calc(var(--radius-xl) - 1px);
            border: 1px solid rgba(255, 255, 255, 0.58);
            pointer-events: none;
            z-index: -1;
        }

        .hero-aura {
            position: absolute;
            border-radius: 999px;
            pointer-events: none;
            filter: blur(2px);
            z-index: -2;
        }

        .hero-aura-one {
            right: -98px;
            top: -120px;
            width: 350px;
            height: 350px;
            background: radial-gradient(circle, rgba(77, 116, 166, 0.22), transparent 67%);
        }

        .hero-aura-two {
            left: 38%;
            bottom: -180px;
            width: 430px;
            height: 300px;
            background: radial-gradient(circle, rgba(117, 183, 154, 0.20), transparent 68%);
        }

        .hero-copy {
            position: relative;
            z-index: 2;
        }

        .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            gap: 8px;
            margin-bottom: 16px;
            padding: 9px 14px 9px 10px;
            border: 1px solid rgba(117, 183, 154, 0.34);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.72);
            color: var(--mint-strong);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.08em;
            line-height: 1.1;
            text-transform: uppercase;
            box-shadow: 0 10px 28px rgba(36, 48, 61, 0.06);
        }

        .hero-pulse {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: var(--mint);
            box-shadow: 0 0 0 6px rgba(117, 183, 154, 0.16);
        }

        .hero-title {
            max-width: 980px;
            margin-bottom: 12px;
            color: var(--text);
            font-size: clamp(32px, 3vw, 48px);
            font-weight: 820;
            line-height: 1.02;
            letter-spacing: 0;
        }

        .hero-gradient {
            color: var(--primary-strong);
            background: linear-gradient(95deg, var(--primary-strong), var(--mint-strong) 55%, var(--lavender-strong));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-sub {
            max-width: 890px;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 500;
            line-height: 1.58;
        }

        .hero-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 22px;
        }

        .hero-chips span {
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            padding: 8px 13px;
            border: 1px solid rgba(227, 221, 212, 0.9);
            border-radius: 999px;
            background: rgba(255,255,255,0.68);
            color: var(--muted);
            font-size: 11.5px;
            font-weight: 760;
            box-shadow: 0 8px 18px rgba(36, 48, 61, 0.045);
        }

        .hero-visual {
            position: relative;
            width: 210px;
            height: 210px;
            justify-self: end;
            border-radius: 999px;
            background:
                radial-gradient(circle, rgba(255,255,255,0.96) 0 24%, rgba(234,245,240,0.76) 25% 44%, rgba(229,237,247,0.78) 45% 64%, rgba(255,255,255,0.42) 65% 100%);
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.72),
                0 26px 58px rgba(77, 116, 166, 0.16);
        }

        .radar-orbit,
        .radar-core {
            position: absolute;
            border-radius: 999px;
        }

        .radar-orbit {
            inset: 22px;
            border: 1px solid rgba(77, 116, 166, 0.18);
        }

        .orbit-two {
            inset: 52px;
            border-color: rgba(117, 183, 154, 0.28);
        }

        .orbit-three {
            inset: 82px;
            border-color: rgba(165, 150, 200, 0.32);
        }

        .radar-core {
            left: 50%;
            top: 50%;
            width: 18px;
            height: 18px;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, var(--primary), var(--mint));
            box-shadow: 0 0 0 14px rgba(77, 116, 166, 0.09);
        }

        .metric-card {
            position: relative;
            min-height: 132px;
            padding: 20px 20px 19px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(145deg, rgba(255,255,255,0.96), rgba(248,251,248,0.84)),
                var(--surface-solid);
            box-shadow: var(--shadow-soft);
            backdrop-filter: blur(16px);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            inset: auto 18px 0;
            height: 4px;
            border-radius: 999px 999px 0 0;
            background: linear-gradient(90deg, var(--primary), var(--mint), var(--lavender));
            opacity: 0.74;
        }

        .metric-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 255, 255, 0.95);
            box-shadow: var(--shadow-card);
        }

        .metric-glow {
            position: absolute;
            right: -34px;
            top: -38px;
            width: 132px;
            height: 132px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(117, 183, 154, 0.22), transparent 68%);
            pointer-events: none;
        }

        .metric-topline {
            position: relative;
            display: flex;
            align-items: center;
            gap: 9px;
            margin-bottom: 16px;
            z-index: 1;
        }

        .metric-dot {
            width: 13px;
            height: 13px;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--primary), var(--mint));
            box-shadow: 0 0 0 5px rgba(77, 116, 166, 0.10);
            flex: 0 0 auto;
        }

        .metric-title {
            color: var(--muted);
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.075em;
            line-height: 1.3;
            text-transform: uppercase;
        }

        .metric-value {
            position: relative;
            color: var(--text);
            font-size: clamp(24px, 2.1vw, 34px);
            font-weight: 820;
            line-height: 1.02;
            letter-spacing: 0;
            overflow-wrap: anywhere;
            z-index: 1;
        }

        .section-card {
            display: flex;
            align-items: center;
            width: fit-content;
            max-width: 100%;
            margin: 34px 0 17px;
            padding: 14px 20px;
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.70);
            box-shadow: 0 12px 30px rgba(36, 48, 61, 0.055);
            backdrop-filter: blur(14px);
        }

        .section-title {
            color: var(--text);
            font-size: 16.5px;
            font-weight: 800;
            line-height: 1.12;
            letter-spacing: 0;
        }

        .section-sub {
            margin-top: 4px;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 13.5px;
            font-weight: 550;
            line-height: 1.38;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 18px;
            margin-top: 20px;
        }

        .feature-item,
        .nav-card {
            position: relative;
            min-height: 136px;
            padding: 20px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(145deg, rgba(255,255,255,0.94), rgba(249,251,248,0.84)),
                var(--surface-solid);
            box-shadow: var(--shadow-soft);
            transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        .nav-card:hover,
        .feature-item:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-card);
        }

        .nav-card::after {
            content: "";
            position: absolute;
            right: -34px;
            bottom: -42px;
            width: 140px;
            height: 140px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(165, 150, 200, 0.16), transparent 68%);
            pointer-events: none;
        }

        .nav-card-title {
            position: relative;
            color: var(--text);
            font-size: 14.5px;
            font-weight: 800;
            margin-bottom: 7px;
            z-index: 1;
        }

        .nav-card-desc {
            position: relative;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 13px;
            line-height: 1.5;
            z-index: 1;
        }

        .baseline-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            margin: 8px 0 23px;
        }

        .baseline-pill {
            padding: 9px 14px;
            border: 1px solid rgba(227, 221, 212, 0.88);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.76);
            color: var(--muted);
            font-size: 11.5px;
            font-weight: 780;
            box-shadow: 0 8px 18px rgba(36, 48, 61, 0.045);
        }

        .baseline-pill.active {
            background: linear-gradient(135deg, var(--text), #35465A);
            border-color: rgba(36, 48, 61, 0.82);
            color: #FFFFFF;
        }

        .llm-card {
            min-height: 186px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(145deg, rgba(255,255,255,0.96), rgba(248,251,248,0.86)),
                var(--surface-solid);
            box-shadow: var(--shadow-soft);
        }

        .llm-label {
            margin-bottom: 10px;
            color: var(--muted);
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.075em;
            text-transform: uppercase;
        }

        .llm-text {
            color: var(--text);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 14.8px;
            line-height: 1.62;
            white-space: pre-wrap;
        }

        .wordcloud-panel {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 13px 22px;
            min-height: 390px;
            padding: 42px 38px;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-xl);
            background:
                radial-gradient(circle at 20% 12%, rgba(117, 183, 154, 0.20), transparent 250px),
                radial-gradient(circle at 82% 82%, rgba(165, 150, 200, 0.18), transparent 280px),
                rgba(255, 255, 255, 0.88);
            box-shadow: var(--shadow-card);
        }

        .word-token {
            display: inline-block;
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-weight: 780;
            line-height: 1;
            opacity: 0.94;
            transition: opacity 140ms ease, transform 140ms ease;
        }

        .word-token:hover {
            opacity: 1;
            transform: translateY(-2px);
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.92), rgba(246,241,234,0.94)) !important;
            border-right: 1px solid rgba(227, 221, 212, 0.9) !important;
            box-shadow: 18px 0 50px rgba(36, 48, 61, 0.055);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 1.35rem;
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
            margin: 18px 0 !important;
        }

        .sidebar-lockup {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .sidebar-mark {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            border-radius: 19px;
            background:
                radial-gradient(circle at 30% 24%, rgba(255,255,255,0.92), transparent 33%),
                linear-gradient(135deg, var(--primary), var(--mint));
            color: #FFFFFF;
            font-size: 19px;
            font-weight: 820;
            box-shadow: 0 16px 32px rgba(77, 116, 166, 0.18);
        }

        .sidebar-brand {
            color: var(--text);
            font-size: 21px;
            font-weight: 840;
            letter-spacing: 0.01em;
            line-height: 1;
        }

        .sidebar-kicker,
        .sidebar-label,
        .sidebar-source-label {
            color: var(--muted);
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.075em;
            text-transform: uppercase;
        }

        .sidebar-kicker {
            margin-top: 7px;
        }

        .sidebar-source {
            margin: 0 0 22px;
            padding: 16px;
            border: 1px solid rgba(255, 255, 255, 0.74);
            border-radius: 24px;
            background:
                linear-gradient(145deg, rgba(234,245,240,0.88), rgba(255,255,255,0.74));
            box-shadow: 0 14px 34px rgba(36, 48, 61, 0.07);
        }

        .sidebar-source-title {
            margin-top: 8px;
            color: var(--text);
            font-size: 12.8px;
            font-weight: 790;
            line-height: 1.25;
        }

        .sidebar-source-meta {
            margin-top: 5px;
            color: var(--muted);
            font-family: 'Source Sans 3', 'Inter', sans-serif;
            font-size: 12px;
            line-height: 1.38;
        }

        [data-testid="stSidebarNav"] ul {
            gap: 6px;
        }

        [data-testid="stSidebarNav"] a,
        [data-testid="stNavItem"] a,
        nav[aria-label="Navigation"] a {
            min-height: 38px;
            border-radius: 999px !important;
            color: var(--muted) !important;
            font-weight: 720 !important;
            transition: background-color 150ms ease, color 150ms ease, transform 150ms ease;
        }

        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stNavItem"] a:hover,
        nav[aria-label="Navigation"] a:hover {
            transform: translateX(1px);
            background: rgba(229, 237, 247, 0.86) !important;
            color: var(--text) !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stNavItem"] a[aria-current="page"],
        nav[aria-label="Navigation"] a[aria-current="page"] {
            background:
                linear-gradient(90deg, rgba(229,237,247,0.98), rgba(234,245,240,0.96)) !important;
            color: var(--primary-strong) !important;
            font-weight: 820 !important;
            box-shadow: 0 10px 24px rgba(77, 116, 166, 0.09);
        }

        .stSelectbox label,
        .stSlider label,
        .stTextInput label,
        .stCheckbox label,
        .stRadio label,
        .stMultiSelect label,
        .stNumberInput label,
        .stDateInput label {
            color: var(--muted) !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        textarea,
        input {
            min-height: 42px;
            border-color: rgba(227, 221, 212, 0.96) !important;
            border-radius: 999px !important;
            background: rgba(255, 255, 255, 0.88) !important;
            color: var(--text) !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 8px 20px rgba(36, 48, 61, 0.035) !important;
        }

        textarea {
            border-radius: 24px !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stNumberInput"] input:hover,
        div[data-testid="stDateInput"] input:hover,
        textarea:hover,
        input:hover {
            border-color: rgba(77, 116, 166, 0.48) !important;
        }

        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stDateInput"] input:focus,
        textarea:focus,
        input:focus {
            border-color: rgba(77, 116, 166, 0.72) !important;
            box-shadow: var(--shadow-focus) !important;
        }

        div[data-baseweb="select"] * {
            color: var(--text) !important;
        }

        div[data-baseweb="tag"] {
            border-radius: 999px !important;
            background: var(--primary-soft) !important;
        }

        div[data-testid="stTextInput"] input::placeholder,
        textarea::placeholder {
            color: #9AA4B1 !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 0.52rem;
        }

        div[data-testid="stRadio"] label {
            border: 1px solid rgba(227, 221, 212, 0.95);
            border-radius: 999px;
            background: rgba(255,255,255,0.74);
            padding: 0.38rem 0.72rem;
            box-shadow: 0 8px 18px rgba(36, 48, 61, 0.035);
        }

        div[data-testid="stRadio"] label:hover {
            border-color: rgba(77, 116, 166, 0.36);
            background: #FFFFFF;
        }

        div[data-testid="stSlider"] [role="slider"] {
            background: var(--primary) !important;
            box-shadow: var(--shadow-focus) !important;
        }

        div[data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.78) !important;
            border-radius: var(--radius-lg) !important;
            background: rgba(255, 255, 255, 0.90);
            box-shadow: var(--shadow-soft);
        }

        div[data-testid="stDataFrame"] * {
            font-family: 'Inter', 'Source Sans 3', sans-serif !important;
        }

        div[data-testid="stPlotlyChart"] {
            position: relative;
            overflow: hidden;
            padding: 18px;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(145deg, rgba(255,255,255,0.94), rgba(249,251,248,0.84));
            box-shadow: var(--shadow-soft);
        }

        div[data-testid="stImage"] {
            overflow: hidden;
            padding: 16px;
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(145deg, rgba(255,255,255,0.94), rgba(249,251,248,0.84));
            box-shadow: var(--shadow-soft);
        }

        div[data-testid="stAlert"] {
            border-radius: 24px !important;
            border-width: 1px !important;
            box-shadow: 0 12px 28px rgba(36, 48, 61, 0.055);
        }

        .stButton > button,
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            min-height: 42px;
            border: 1px solid rgba(77, 116, 166, 0.36) !important;
            border-radius: 999px !important;
            background: linear-gradient(135deg, var(--primary), var(--primary-strong)) !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 12px !important;
            font-weight: 800 !important;
            padding: 0.62rem 1.16rem !important;
            box-shadow: 0 14px 28px rgba(77, 116, 166, 0.18) !important;
            transition: transform 140ms ease, box-shadow 140ms ease, filter 140ms ease;
        }

        .stButton > button:hover,
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-2px);
            filter: saturate(1.04);
            box-shadow: 0 18px 36px rgba(77, 116, 166, 0.21) !important;
        }

        div[data-testid="stExpander"] {
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.78) !important;
            border-radius: var(--radius-lg) !important;
            background: rgba(255, 255, 255, 0.88) !important;
            box-shadow: var(--shadow-soft);
        }

        div[data-testid="stExpander"] summary {
            font-weight: 800 !important;
            color: var(--text) !important;
        }

        div[data-testid="stTabs"] [role="tablist"] {
            gap: 9px;
            border-bottom: 0 !important;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            min-height: 38px;
            border: 1px solid rgba(227, 221, 212, 0.95) !important;
            border-radius: 999px !important;
            background: rgba(255,255,255,0.72) !important;
            color: var(--muted) !important;
            font-weight: 790 !important;
            padding: 0.42rem 0.88rem !important;
            box-shadow: 0 8px 18px rgba(36, 48, 61, 0.035);
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            border-color: rgba(77, 116, 166, 0.28) !important;
            background: linear-gradient(90deg, var(--primary-soft), var(--mint-soft)) !important;
            color: var(--primary-strong) !important;
        }

        hr {
            border: none !important;
            border-top: 1px solid rgba(212, 202, 191, 0.80) !important;
            margin: 28px 0 !important;
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
            border: 1px solid rgba(227, 221, 212, 0.95) !important;
            border-radius: 999px !important;
            background: rgba(255, 255, 255, 0.88) !important;
            color: var(--muted) !important;
            box-shadow: var(--shadow-soft) !important;
        }

        section[data-testid="stSidebar"],
        button[data-testid="stSidebarCollapsedControl"],
        button[kind="header"][data-testid="baseButton-header"] {
            display: none !important;
            visibility: hidden !important;
        }

        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            border: 2px solid transparent;
            border-radius: 999px;
            background: #C6BCAE;
            background-clip: padding-box;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #B8AD9F;
            background-clip: padding-box;
        }

        /* Visual skin inspired by the provided modern dashboard reference. */
        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(255,255,255,0.42), transparent 340px),
                radial-gradient(circle at 96% 0%, rgba(255,255,255,0.34), transparent 380px),
                linear-gradient(135deg, #CDE9DF 0%, #DDF0EA 48%, #C7E4DA 100%) !important;
        }

        section[data-testid="stMain"] > div:first-child,
        .main .block-container,
        div[data-testid="stAppViewContainer"] .block-container {
            max-width: 1450px;
            margin-top: 1.25rem;
            margin-bottom: 1.6rem;
            padding: 1.15rem 1.25rem 2rem;
            border: 1px solid rgba(255, 255, 255, 0.76);
            border-radius: 30px;
            background: #F4F5F3;
            box-shadow: 0 24px 56px rgba(32, 89, 74, 0.20);
        }

        .radar-topbar {
            top: 12px;
            gap: 12px;
            margin-bottom: 18px;
            padding: 11px 13px;
            border: 0;
            border-radius: 28px;
            background: #2D866D;
            box-shadow: 0 18px 38px rgba(28, 96, 77, 0.22);
        }

        .top-brand {
            background: rgba(255,255,255,0.10);
            color: #FFFFFF !important;
        }

        .top-brand-mark {
            width: 34px;
            height: 34px;
            background: #FFFFFF;
            color: #2D866D;
            box-shadow: none;
        }

        .top-brand-title {
            color: #FFFFFF;
            font-size: 14px;
        }

        .top-brand-kicker {
            color: rgba(255,255,255,0.68);
        }

        .top-nav-links {
            gap: 5px;
        }

        .top-nav-link {
            min-height: 32px;
            padding: 8px 11px;
            color: rgba(255,255,255,0.78) !important;
            font-size: 11.5px;
            font-weight: 760;
        }

        .top-nav-link:hover {
            border-color: transparent;
            background: rgba(255,255,255,0.18);
            color: #FFFFFF !important;
        }

        .hero {
            min-height: 208px;
            margin-bottom: 22px;
            padding: 30px 34px;
            border: 0;
            border-radius: 24px;
            background: #FFFFFF;
            box-shadow: 0 12px 26px rgba(34, 66, 58, 0.07);
        }

        .hero-eyebrow {
            background: #EAF6F2;
            color: #2D866D;
            box-shadow: none;
        }

        .hero-pulse {
            background: #2D866D;
            box-shadow: 0 0 0 6px rgba(45, 134, 109, 0.13);
        }

        .hero-title {
            font-size: clamp(30px, 2.7vw, 43px);
        }

        .hero-gradient {
            background: linear-gradient(95deg, #2D866D, #3F9F88 52%, #6D71C6);
            background-clip: text;
            -webkit-background-clip: text;
        }

        .hero-sub {
            font-size: 15.5px;
        }

        .hero-chips span {
            border-color: #E5EAE7;
            background: #F4F8F6;
            box-shadow: none;
        }

        .hero-visual {
            background:
                radial-gradient(circle, rgba(255,255,255,0.96) 0 24%, rgba(219,239,232,0.82) 25% 44%, rgba(238,241,239,0.82) 45% 100%);
            box-shadow: 0 18px 38px rgba(45, 134, 109, 0.12);
        }

        .metric-card,
        .feature-item,
        .nav-card,
        .llm-card,
        div[data-testid="stPlotlyChart"],
        div[data-testid="stImage"],
        div[data-testid="stDataFrame"],
        div[data-testid="stExpander"] {
            border: 0 !important;
            border-radius: 20px !important;
            background: #FFFFFF !important;
            box-shadow: 0 10px 24px rgba(34, 66, 58, 0.075) !important;
        }

        .metric-card {
            min-height: 116px;
            padding: 18px 18px 17px;
        }

        .metric-glow {
            background: radial-gradient(circle, rgba(45, 134, 109, 0.13), transparent 68%);
        }

        .metric-dot {
            background: linear-gradient(135deg, #2D866D, #7FCDBB);
            box-shadow: 0 0 0 5px rgba(45, 134, 109, 0.10);
        }

        .metric-card::after {
            height: 3px;
            background: linear-gradient(90deg, #2D866D, #7FCDBB, #7B76D1);
        }

        .section-card {
            margin: 26px 0 14px;
            padding: 10px 18px;
            border: 0;
            background: #FFFFFF;
            box-shadow: 0 9px 20px rgba(34, 66, 58, 0.06);
        }

        .section-title {
            font-size: 15.8px;
        }

        .section-sub {
            font-size: 12.8px;
        }

        div[data-testid="stPlotlyChart"] {
            padding: 16px;
        }

        .stButton > button,
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            border: 0 !important;
            background: #2D866D !important;
            box-shadow: 0 10px 20px rgba(45, 134, 109, 0.18) !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        textarea,
        input {
            border-color: #E1E8E4 !important;
            background: #FFFFFF !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stDateInput"] input:focus,
        textarea:focus,
        input:focus {
            border-color: rgba(45, 134, 109, 0.62) !important;
            box-shadow: 0 0 0 4px rgba(45, 134, 109, 0.12) !important;
        }

        .top-brand-mark,
        .hero-aura,
        .hero-pulse,
        .hero-visual,
        .radar-orbit,
        .radar-core,
        .metric-glow,
        .metric-dot,
        .section-mark,
        .nav-card-mark,
        .sidebar-mark {
            display: none !important;
        }

        .nav-card::after {
            content: none !important;
            display: none !important;
        }

        .hero {
            grid-template-columns: minmax(0, 1fr) !important;
        }

        .top-brand {
            padding: 8px 14px !important;
        }

        .metric-topline {
            gap: 0 !important;
            margin-bottom: 12px !important;
        }

        @media (max-width: 980px) {
            section[data-testid="stMain"] > div:first-child,
            .main .block-container,
            div[data-testid="stAppViewContainer"] .block-container {
                margin-top: 0.8rem;
                padding: 0.9rem 0.9rem 2.2rem;
                border-radius: 24px;
            }

            .radar-topbar {
                align-items: flex-start;
                border-radius: 22px;
                flex-direction: column;
            }

            .hero {
                grid-template-columns: 1fr;
                min-height: auto;
                padding: 30px 24px;
                border-radius: 32px;
            }

            .hero-visual {
                display: none;
            }

            .hero-title {
            font-size: 30px;
            }

            .hero-sub {
                font-size: 15px;
            }

            .metric-card {
                min-height: 116px;
                border-radius: 28px;
            }

            .section-card {
                width: 100%;
                align-items: flex-start;
                border-radius: 28px;
            }

            div[data-testid="stPlotlyChart"],
            div[data-testid="stImage"],
            div[data-testid="stDataFrame"] {
                border-radius: 28px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
