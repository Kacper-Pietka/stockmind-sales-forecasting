"""
StockMind — Sales Forecast App
Wersja Premium Light: jasny motyw inspirowany landing page,
niebiesko-zielona paleta, czyste karty, profesjonalny wygląd.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ─── Konfiguracja ───
API_URL = os.getenv("API_URL", "http://localhost:8000")
LOGO_PATH = Path(__file__).parent / "assets" / "stockmind_logo.png"

st.set_page_config(
    page_title="StockMind — Predict. Optimize. Grow.",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# PREMIUM AI SaaS COLORS
# ═══════════════════════════════════════════════════════════════════
NAVY = "#081225"
NAVY_LIGHT = "#0f172a"
BLUE = "#3b82f6"
CYAN = "#06b6d4"
GREEN = "#22c55e"
PURPLE = "#8b5cf6"
RED = "#ef4444"
ORANGE = "#f97316"

LIGHT_BG = "#f4f7fb"
CARD_BG = "rgba(255,255,255,0.78)"
BORDER = "rgba(255,255,255,0.18)"       # subtelna do glassmorphism
BORDER_SOLID = "#e2e8f0"                 # widoczna do białych kart

TEXT_DARK = "#0f172a"
TEXT_MUTED = "#64748b"

# Layout dla wszystkich wykresów Plotly
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=TEXT_DARK, family='Inter'),
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(
        bgcolor='white',
        font_size=14,
        font_family='Inter'
    )
)

# ═══════════════════════════════════════════════════════════════════
# CUSTOM CSS — premium light theme
# ═══════════════════════════════════════════════════════════════════

st.markdown(f"""
<style>

/* ============================================================
   GLOBAL
============================================================ */

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{display: none;}}
.stDeployButton {{display:none;}}

html, body, [class*="css"] {{
    font-family: Inter, sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.10), transparent 30%),
        radial-gradient(circle at top right, rgba(34,197,94,0.10), transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
}}

.main .block-container {{
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

/* ============================================================
   SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #081225 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}}

section[data-testid="stSidebar"] * {{
    color: white !important;
}}

section[data-testid="stSidebar"] .stMarkdown p {{
    color: #cbd5e1 !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.1) !important;
}}

section[data-testid="stSidebar"] [role="radiogroup"] label {{
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 6px;
    transition: all 0.25s ease;
    border: 1px solid transparent;
    background: transparent;
}}

section[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.06);
    transform: translateX(4px);
}}

/* ============================================================
   HERO BOX
============================================================ */

.hero-box {{
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #081225 0%, #172554 45%, #1d4ed8 100%);
    border-radius: 28px;
    padding: 42px;
    margin-bottom: 28px;
    box-shadow:
        0 10px 40px rgba(37,99,235,0.15),
        inset 0 1px 0 rgba(255,255,255,0.08);
}}

.hero-box::before {{
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    background: rgba(34,197,94,0.15);
    border-radius: 999px;
    top: -180px;
    right: -120px;
    filter: blur(40px);
    z-index: 1;
}}

.hero-title {{
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
    color: white;
    margin-bottom: 10px;
}}

.hero-subtitle {{
    color: rgba(255,255,255,0.75);
    font-size: 1.05rem;
    max-width: 700px;
}}

.stock-gradient {{
    background: linear-gradient(90deg, #60a5fa 0%, #22c55e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.hero-eyebrow {{
    font-size: 0.82rem;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.65);
    font-weight: 700;
    margin-bottom: 18px;
}}

.hero-chip {{
    background: rgba(255,255,255,0.10);
    color: white;
    padding: 10px 18px;
    border-radius: 999px;
    margin-right: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.12);
    display: inline-block;
    margin-bottom: 8px;
}}

/* ============================================================
   METRICS (Glassmorphism KPI cards)
============================================================ */

div[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.40);
    border-radius: 24px;
    padding: 26px;
    box-shadow:
        0 8px 24px rgba(15,23,42,0.05),
        inset 0 1px 0 rgba(255,255,255,0.6);
    transition: all 0.25s ease;
}}

div[data-testid="stMetric"]:hover {{
    transform: translateY(-4px);
    box-shadow:
        0 20px 40px rgba(37,99,235,0.10),
        inset 0 1px 0 rgba(255,255,255,0.8);
}}

div[data-testid="stMetric"] label {{
    color: {TEXT_MUTED} !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 700 !important;
}}

div[data-testid="stMetric"] > div:nth-child(2) {{
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    color: {TEXT_DARK} !important;
}}

/* ============================================================
   CARDS (Glass)
============================================================ */

.info-card,
.action-item,
[data-testid="stFileUploader"] {{
    background: rgba(255,255,255,0.72) !important;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.45) !important;
    border-radius: 24px !important;
    box-shadow:
        0 10px 30px rgba(15,23,42,0.05),
        inset 0 1px 0 rgba(255,255,255,0.5);
}}

.action-item {{
    padding: 18px;
    margin-bottom: 12px;
    transition: all 0.25s ease;
}}

.action-item:hover {{
    transform: translateY(-2px);
    box-shadow: 0 16px 30px rgba(15,23,42,0.08);
}}

.action-grow, .action-warn {{
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 18px;
}}

.action-grow {{
    background: linear-gradient(135deg, #ecfdf5 0%, rgba(255,255,255,0.7) 100%);
    border-left: 4px solid {GREEN};
}}

.action-warn {{
    background: linear-gradient(135deg, #fef2f2 0%, rgba(255,255,255,0.7) 100%);
    border-left: 4px solid {RED};
}}

/* ============================================================
   BUTTONS
============================================================ */

.stButton button {{
    border: none !important;
    background: linear-gradient(135deg, #2563eb 0%, #22c55e 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 8px 24px rgba(37,99,235,0.25);
    transition: all 0.25s ease;
}}

.stButton button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(37,99,235,0.30);
}}

.stDownloadButton button {{
    background: linear-gradient(135deg, {GREEN} 0%, #16a34a 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
}}

/* ============================================================
   CHIPS / BADGES
============================================================ */

.chip {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
    animation: pulseChip 2s infinite;
}}

@keyframes pulseChip {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.04); }}
    100% {{ transform: scale(1); }}
}}

.chip-up {{ background: #dcfce7; color: #15803d; }}
.chip-down {{ background: #fee2e2; color: #b91c1c; }}
.chip-stable {{ background: #dbeafe; color: #1e40af; }}

/* ============================================================
   DATE RANGE BOX
============================================================ */

.date-range-box {{
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 12px;
    padding: 10px 18px;
    color: {BLUE};
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 16px;
    display: inline-block;
    box-shadow: 0 4px 14px rgba(59,130,246,0.08);
}}

/* ============================================================
   TABLES
============================================================ */

.stDataFrame {{
    background: rgba(255,255,255,0.78) !important;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.45) !important;
    border-radius: 20px !important;
    overflow: hidden !important;
    box-shadow:
        0 10px 30px rgba(15,23,42,0.05),
        inset 0 1px 0 rgba(255,255,255,0.5);
}}

.stDataFrame thead tr th {{
    background: rgba(241,245,249,0.95) !important;
    color: {TEXT_DARK} !important;
    font-weight: 700 !important;
    border-bottom: 1px solid rgba(0,0,0,0.04) !important;
}}

.stDataFrame tbody tr td {{
    color: {TEXT_DARK} !important;
}}

.stDataFrame tbody tr:hover {{
    background: rgba(59,130,246,0.06) !important;
}}

[data-testid="stDataFrame"] > div {{
    background: transparent !important;
}}

/* ============================================================
   MULTISELECT TAGS — spokojne kolory
============================================================ */

.stMultiSelect [data-baseweb="tag"] {{
    background: #dbeafe !important;
    color: {NAVY} !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 14px !important;
    font-weight: 500 !important;
}}

.stMultiSelect [data-baseweb="tag"] span {{
    color: {NAVY} !important;
}}

.stMultiSelect [data-baseweb="tag"] svg {{
    fill: {NAVY} !important;
}}

.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}}

/* Wymuś ciemny tekst wewnątrz selectbox - wartość wybrana */
.stSelectbox [data-baseweb="select"] *,
.stMultiSelect [data-baseweb="select"] > div > div > div,
[data-baseweb="select"] [data-baseweb="tag"] span,
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] div[id*="select"] {{
    color: {TEXT_DARK} !important;
}}

/* Dropdown z opcjami selectboxa */
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"] {{
    color: {TEXT_DARK} !important;
    background: white !important;
}}

[data-baseweb="popover"] [role="option"]:hover {{
    background: #eff6ff !important;
}}

.stSelectbox label, .stMultiSelect label,
.stFileUploader label, .stTextInput label,
.stCheckbox label, .stRadio > label,
label[data-testid="stWidgetLabel"] {{
    color: {TEXT_DARK} !important;
    font-weight: 500;
}}

/* ============================================================
   FILE UPLOADER
============================================================ */

[data-testid="stFileUploader"] {{
    padding: 32px !important;
    border: 2px dashed rgba(59,130,246,0.25) !important;
}}

[data-testid="stFileUploader"] section {{
    background: transparent;
    border: none;
}}

[data-testid="stFileUploader"] section button {{
    background: linear-gradient(135deg, #2563eb 0%, #22c55e 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}

[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section span {{
    color: {TEXT_MUTED} !important;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,0.5) !important;
}}

/* ============================================================
   NAGŁÓWKI
============================================================ */

h1, h2, h3, h4, h5, h6 {{
    color: {TEXT_DARK} !important;
    font-weight: 700 !important;
}}

h1 {{ font-size: 2.2rem !important; }}

h2 {{
    font-size: 1.5rem !important;
    margin-top: 24px !important;
    border-left: 4px solid {BLUE};
    padding-left: 14px;
}}

h3 {{ font-size: 1.15rem !important; }}

h5, h6 {{
    font-size: 1rem !important;
    color: {TEXT_DARK} !important;
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}}

.stMarkdown p {{
    color: {TEXT_MUTED};
}}

/* Wymuś ciemny tekst dla pre/code w main content (nie sidebar) */
.main pre, .main code {{
    color: {TEXT_DARK} !important;
    background: #f1f5f9 !important;
}}

/* ============================================================
   SECTION HEADERS Z IKONAMI
============================================================ */

.section-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 34px;
    margin-bottom: 22px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(15,23,42,0.06);
}}

.section-icon {{
    width: 46px;
    height: 46px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(15,23,42,0.05);
}}

.section-icon-blue {{ background: linear-gradient(135deg, #dbeafe, #bfdbfe); }}
.section-icon-green {{ background: linear-gradient(135deg, #dcfce7, #bbf7d0); }}
.section-icon-orange {{ background: linear-gradient(135deg, #ffedd5, #fed7aa); }}
.section-icon-purple {{ background: linear-gradient(135deg, #ede9fe, #ddd6fe); }}

.section-title-text {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {TEXT_DARK};
    margin: 0;
}}

.section-subtitle {{
    font-size: 0.9rem;
    color: {TEXT_MUTED};
    margin: 0;
}}

/* ============================================================
   RECOMMENDATION CARD
============================================================ */

.rec-card {{
    background: linear-gradient(135deg, #081225 0%, #1d4ed8 100%);
    color: white;
    border-radius: 24px;
    padding: 32px;
    box-shadow:
        0 10px 40px rgba(37,99,235,0.25),
        inset 0 1px 0 rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}}

.rec-card::before {{
    content: "";
    position: absolute;
    width: 200px;
    height: 200px;
    background: rgba(34,197,94,0.18);
    border-radius: 999px;
    top: -80px;
    right: -60px;
    filter: blur(30px);
}}

.rec-card-label {{
    color: rgba(255,255,255,0.7);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 700;
    margin-bottom: 10px;
    position: relative;
    z-index: 2;
}}

.rec-card-value {{
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
    background: linear-gradient(90deg, #60a5fa 0%, #22c55e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 2;
}}

.rec-card-unit {{
    color: rgba(255,255,255,0.65);
    font-size: 0.9rem;
    margin-bottom: 22px;
    position: relative;
    z-index: 2;
}}

.rec-detail {{
    color: rgba(255,255,255,0.9);
    font-size: 0.9rem;
    margin-bottom: 8px;
    padding: 10px 0;
    border-top: 1px solid rgba(255,255,255,0.12);
    position: relative;
    z-index: 2;
}}

/* ============================================================
   CHARTS
============================================================ */

.js-plotly-plot {{
    border-radius: 20px !important;
    overflow: hidden;
}}

/* Wymuś ciemny tekst we wszystkich elementach Plotly */
.js-plotly-plot .plotly text {{
    fill: {TEXT_DARK} !important;
}}

.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text {{
    fill: {TEXT_DARK} !important;
    font-weight: 500 !important;
}}

.js-plotly-plot .plotly .xtitle,
.js-plotly-plot .plotly .ytitle {{
    fill: {TEXT_DARK} !important;
    font-weight: 600 !important;
}}

.js-plotly-plot .plotly .legend text {{
    fill: {TEXT_DARK} !important;
    font-weight: 500 !important;
}}

.js-plotly-plot .plotly .annotation-text,
.js-plotly-plot .plotly .annotation-text-g text {{
    fill: {TEXT_DARK} !important;
}}

/* ============================================================
   DIVIDER
============================================================ */

hr {{
    border-color: rgba(15,23,42,0.06) !important;
    margin: 24px 0 !important;
}}

/* ============================================================
   SCROLLBAR
============================================================ */

::-webkit-scrollbar {{
    width: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: rgba(59,130,246,0.35);
    border-radius: 999px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: rgba(59,130,246,0.55);
}}

::-webkit-scrollbar-track {{
    background: transparent;
}}

</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# HELPERY
# ═══════════════════════════════════════════════════════════════════

def fmt(value, decimals=2, suffix=""):
    """Formatowanie liczb z 2 miejscami po przecinku."""
    try:
        if value is None or pd.isna(value):
            return "—"
        v = float(value)
        if decimals == 0:
            return f"{v:,.0f}{suffix}".replace(",", " ")
        return f"{v:,.{decimals}f}{suffix}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


def trend_chip(trend: str) -> str:
    if "rosnący" in trend or "📈" in trend:
        return f'<span class="chip chip-up">📈 Rosnący</span>'
    elif "spadający" in trend or "📉" in trend:
        return f'<span class="chip chip-down">📉 Spadający</span>'
    elif "stabilny" in trend or "➡️" in trend:
        return f'<span class="chip chip-stable">➡️ Stabilny</span>'
    return f'<span class="chip chip-stable">{trend}</span>'


def get_forecast_period():
    start = datetime.now().date() + timedelta(days=1)
    end = start + timedelta(days=27)
    return f"{start.strftime('%d.%m')} – {end.strftime('%d.%m.%Y')}"


@st.cache_data(ttl=300)
def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=10)
        if not r.ok:
            return None
        try:
            return r.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Brak połączenia z systemem")
        st.stop()
    except Exception:
        return None


def api_post_file(endpoint: str, file_bytes: bytes, filename: str):
    """Wysyła plik do API. Bezpiecznie obsługuje wszystkie typy błędów."""
    try:
        files = {"file": (filename, file_bytes, "text/csv")}
        r = requests.post(f"{API_URL}{endpoint}", files=files, timeout=60)

        # Jeśli kod nie jest 2xx — pokaż szczegóły błędu
        if not r.ok:
            # Spróbuj wyciągnąć szczegóły z JSON-a, jeśli się da
            try:
                detail = r.json().get('detail', r.text)
            except (ValueError, requests.exceptions.JSONDecodeError):
                # Backend nie zwrócił JSON-a (np. 500 z HTML stack trace)
                detail = r.text[:500] if r.text else f"Pusty response (HTTP {r.status_code})"
            st.error(f"❌ Błąd serwera (HTTP {r.status_code}): {detail}")
            return None

        # Kod 2xx — spróbuj sparsować odpowiedź jako JSON
        try:
            return r.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            st.error(f"❌ Serwer zwrócił niepoprawną odpowiedź (nie JSON): {r.text[:300]}")
            return None

    except requests.exceptions.Timeout:
        st.error("❌ Timeout — serwer nie odpowiedział w 60 sekund. Spróbuj z mniejszym plikiem.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Brak połączenia z systemem ({API_URL})")
        return None
    except Exception as e:
        st.error(f"❌ Nieoczekiwany błąd: {type(e).__name__}: {str(e)[:200]}")
        return None


def render_header(title: str, caption: str = ""):
    """Premium hero box z logo PNG jako background-image + page header pod spodem."""
    import base64

    # Wstrzykuję logo jako CSS background-image (przez <style> w osobnym markdown)
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .hero-box {{
                background-image:
                    linear-gradient(135deg, rgba(8,18,37,0.95) 0%, rgba(23,37,84,0.75) 45%, rgba(29,78,216,0.5) 100%),
                    url("data:image/png;base64,{logo_b64}");
                background-repeat: no-repeat, no-repeat;
                background-position: center, right 40px center;
                background-size: cover, 340px auto;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    # Hero box - prosty HTML bez bazy64 w środku
    st.markdown(
        """
        <div class="hero-box">
            <div style="position:relative; z-index:2; max-width:55%;">
                <div class="hero-eyebrow">AI SALES FORECASTING PLATFORM</div>
                <div class="hero-title">
                    <span style='color:white;'>STOCK</span><span class="stock-gradient">MIND</span>
                </div>
                <div class="hero-subtitle">
                    Inteligentne prognozowanie sprzedaży, analiza trendów i optymalizacja magazynu
                    dla nowoczesnego e-commerce.
                </div>
                <div style='margin-top:28px;'>
                    <span class="hero-chip">📈 Forecast AI</span>
                    <span class="hero-chip">📦 Smart Inventory</span>
                    <span class="hero-chip">🔥 Trend Detection</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Page header — tytuł + okres
    st.markdown(f"<h1 style='margin-bottom: 4px;'>{title}</h1>", unsafe_allow_html=True)
    if caption:
        st.markdown(
            f"<p style='color: {TEXT_MUTED}; font-size: 1rem; margin-top: 0;'>{caption}</p>",
            unsafe_allow_html=True
        )
    st.markdown(
        f'<div class="date-range-box">📅 Okres prognozy: {get_forecast_period()}</div>',
        unsafe_allow_html=True
    )


# SVG ikony - czyste, profesjonalne
ICON_DASHBOARD = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>"""

ICON_TARGET = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>"""

ICON_CHART = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>"""

ICON_TABLE = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>"""

ICON_BOX = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>"""

ICON_CALENDAR = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>"""

ICON_LIGHTBULB = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21h6"/><path d="M12 17a5 5 0 0 0 5-5 5 5 0 0 0-10 0 5 5 0 0 0 5 5z"/><line x1="12" y1="21" x2="12" y2="17"/></svg>"""

ICON_TRAFFIC = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="18" r="2"/></svg>"""


def section_header(icon_svg: str, title: str, subtitle: str = "", color_class: str = "blue"):
    """Renderuje nagłówek sekcji z SVG ikoną w kolorowym tle."""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-icon section-icon-{color_class}">
                {icon_svg}
            </div>
            <div>
                <div class="section-title-text">{title}</div>
                {f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

health = api_get("/")
if not health or not health.get("artifacts_loaded"):
    st.error("⚠ System nie został jeszcze przygotowany.")
    st.info("Skontaktuj się z administratorem.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=200)

st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 28px;'>
        <div style='color: #94a3b8; font-size: 0.72rem; letter-spacing: 2.5px; font-weight: 600;'>
            PREDICT • OPTIMIZE • GROW
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    "<div style='color: #94a3b8; font-size: 0.78rem; text-transform: uppercase; "
    "letter-spacing: 1px; font-weight: 600; margin-bottom: 8px;'>Nawigacja</div>",
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Nawigacja",
    ["🏠 Przegląd magazynu", "🔍 Szczegóły kategorii", "📤 Analiza Twojego magazynu"],
    label_visibility="collapsed",
)

st.sidebar.divider()

st.sidebar.markdown(
    "<div style='color: #94a3b8; font-size: 0.78rem; text-transform: uppercase; "
    "letter-spacing: 1px; font-weight: 600; margin-bottom: 8px;'>Statystyki</div>",
    unsafe_allow_html=True
)
st.sidebar.metric("Kategorii w systemie", health.get("categories_count", 0))


# ═══════════════════════════════════════════════════════════════════
# STRONA 1: PRZEGLĄD MAGAZYNU
# ═══════════════════════════════════════════════════════════════════

if page == "🏠 Przegląd magazynu":
    render_header(
        "📦 Przegląd magazynu",
        "Prognoza zapotrzebowania na nadchodzące 4 tygodnie"
    )

    categories = api_get("/categories")
    if not categories:
        st.warning("Brak danych")
        st.stop()

    inv_df = pd.DataFrame(categories)

    # ── KPI ──
    section_header(ICON_DASHBOARD, "Kluczowe wskaźniki", "Stan magazynu na nadchodzący okres", "blue")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Kategorii w analizie", fmt(len(inv_df), decimals=0))
    with col2:
        st.metric(
            "Prognoza sprzedaży (4 tyg)",
            fmt(inv_df['forecast_total_4w'].sum(), decimals=0) + " szt"
        )
    with col3:
        st.metric(
            "Rekomendowany stan magazynu",
            fmt(
                (inv_df['forecast_total_4w'] + inv_df['safety_stock']).sum(),
                decimals=0
            ) + " szt"
        )
    with col4:
        st.metric(
            "Bufor bezpieczeństwa",
            fmt(inv_df['safety_stock'].sum(), decimals=0) + " szt"
        )

    st.divider()

    # ── SEKCJA: CO ROBIĆ TERAZ ──
    section_header(ICON_TARGET, "Co robić w najbliższych dniach", "Konkretne akcje na podstawie trendów rynku", "green")

    rising = inv_df[inv_df['trend'].str.contains('rosnący', na=False)].nlargest(3, 'forecast_total_4w')
    falling = inv_df[inv_df['trend'].str.contains('spadający', na=False)].nlargest(3, 'forecast_total_4w')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="action-grow">
                <h3 style='margin: 0 0 6px 0; color: {GREEN};'>📈 Zwiększ zapasy</h3>
                <p style='color: {TEXT_MUTED}; margin: 0; font-size: 0.9rem;'>
                    Sprzedaż rośnie — warto zamówić więcej niż zwykle
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not rising.empty:
            for _, row in rising.iterrows():
                st.markdown(
                    f"""
                    <div class="action-item">
                        <div style='color: {TEXT_DARK}; font-weight: 600; font-size: 1.05rem;'>
                            {row['category']}
                        </div>
                        <div style='color: {TEXT_MUTED}; font-size: 0.88rem; margin-top: 4px;'>
                            Prognoza: <strong style='color: {GREEN};'>{fmt(row['forecast_total_4w'], 0)} szt</strong>
                            ·  Zmiana: <strong style='color: {GREEN};'>+{fmt(abs(row.get('change_pct', 0)))}%</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Brak wyraźnie rosnących kategorii")

    with col2:
        st.markdown(
            f"""
            <div class="action-warn">
                <h3 style='margin: 0 0 6px 0; color: {RED};'>📉 Ostrożność z zamówieniami</h3>
                <p style='color: {TEXT_MUTED}; margin: 0; font-size: 0.9rem;'>
                    Sprzedaż spada — unikaj nadmiernych zapasów
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not falling.empty:
            for _, row in falling.iterrows():
                st.markdown(
                    f"""
                    <div class="action-item">
                        <div style='color: {TEXT_DARK}; font-weight: 600; font-size: 1.05rem;'>
                            {row['category']}
                        </div>
                        <div style='color: {TEXT_MUTED}; font-size: 0.88rem; margin-top: 4px;'>
                            Prognoza: <strong style='color: {RED};'>{fmt(row['forecast_total_4w'], 0)} szt</strong>
                            ·  Zmiana: <strong style='color: {RED};'>{fmt(row.get('change_pct', 0))}%</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("Brak wyraźnie spadających kategorii")

    st.divider()

    # ── Sytuacja na rynku ──
    section_header(ICON_CHART, "Sytuacja na rynku", "Trendy i top kategorie z prognozą sprzedaży", "blue")

    trend_counts = inv_df["trend"].value_counts().reset_index()
    trend_counts.columns = ["trend", "count"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("##### Rozkład trendów")
        fig_trend = px.pie(
            trend_counts, values="count", names="trend",
            color="trend",
            color_discrete_map={
                "rosnący 📈": GREEN,
                "stabilny ➡️": BLUE,
                "spadający 📉": RED,
                "b/d": "#94a3b8",
            },
            hole=0.55,
        )
        fig_trend.update_layout(
            height=320,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color=TEXT_DARK, size=12),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown("##### Top 10 kategorii — prognoza sprzedaży na 4 tygodnie")
        top_10 = inv_df.nlargest(10, "forecast_total_4w").copy()

        color_map = {
            "rosnący 📈": GREEN,
            "stabilny ➡️": BLUE,
            "spadający 📉": RED,
        }
        top_10['color'] = top_10['trend'].map(color_map).fillna("#94a3b8")

        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            x=top_10['forecast_total_4w'],
            y=top_10['category'],
            orientation='h',
            marker=dict(color=top_10['color']),
            text=top_10['forecast_total_4w'].round(0).astype(int).astype(str) + " szt",
            textposition='outside',
            textfont=dict(color=TEXT_DARK),
            hovertemplate="<b>%{y}</b><br>Prognoza: %{x:.0f} szt<extra></extra>"
        ))
        fig_top.update_layout(
            height=400,
            yaxis=dict(categoryorder="total ascending", gridcolor='rgba(0,0,0,0.05)'),
            xaxis=dict(title="Prognoza (sztuki)", gridcolor='rgba(0,0,0,0.05)'),
            margin=dict(l=10, r=80, t=10, b=10),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color=TEXT_DARK, size=11),
        )
        st.plotly_chart(fig_top, use_container_width=True)

    st.divider()

    # ── Tabela ──
    section_header(ICON_TABLE, "Pełna tabela kategorii", "Wszystkie kategorie z prognozami i stanami magazynowymi", "purple")

    col1, col2 = st.columns([1, 4])
    with col1:
        trend_filter = st.multiselect(
            "Filtruj trend:",
            options=sorted(inv_df["trend"].unique()),
            default=sorted(inv_df["trend"].unique()),
        )

    filtered = inv_df[inv_df["trend"].isin(trend_filter)].copy()

    display_df = pd.DataFrame({
        'Kategoria': filtered['category'],
        'Prognoza 4 tyg (szt)': filtered['forecast_total_4w'].round(2),
        'Średnio/tydzień (szt)': filtered['avg_weekly_demand'].round(2),
        'Bufor (szt)': filtered['safety_stock'].round(2),
        'Punkt zamówienia (szt)': filtered['reorder_point'].round(2),
        'Rekomendowany stan (szt)': filtered['recommended_stock_4w'].round(2),
        'Trend': filtered['trend'],
        'Zmiana %': filtered['change_pct'].round(2),
    }).sort_values('Prognoza 4 tyg (szt)', ascending=False)

    st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
# STRONA 2: SZCZEGÓŁY KATEGORII
# ═══════════════════════════════════════════════════════════════════

elif page == "🔍 Szczegóły kategorii":
    render_header(
        "🔍 Szczegóły kategorii",
        "Wybierz kategorię, żeby zobaczyć szczegółową prognozę"
    )

    categories = api_get("/categories")
    cat_names = sorted([c["category"] for c in categories])

    selected = st.selectbox("Wybierz kategorię:", cat_names, index=0)

    if selected:
        detail = api_get(f"/categories/{selected}")
        if not detail:
            st.warning("Brak danych")
            st.stop()

        summary = detail["summary"]
        weekly = pd.DataFrame(detail["weekly_forecast"])
        trend = detail.get("trend")

        st.markdown(
            f"<div style='margin-bottom: 20px;'>{trend_chip(summary.get('trend', ''))}</div>",
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Prognoza 4 tyg", fmt(summary['forecast_total_4w']) + " szt")
        col2.metric("Średnio/tydzień", fmt(summary['avg_weekly_demand']) + " szt")
        col3.metric("Bufor bezpieczeństwa", fmt(summary['safety_stock']) + " szt")
        col4.metric("Rekomendowany stan", fmt(summary['recommended_stock_4w']) + " szt")

        if trend:
            change = trend.get('change_pct', 0)
            change_color = GREEN if change > 0 else (RED if change < 0 else BLUE)
            st.markdown(
                f"""
                <div style='padding: 16px 22px; background: white; border: 1px solid {BORDER_SOLID};
                            border-left: 4px solid {change_color}; border-radius: 8px;
                            margin: 16px 0; box-shadow: 0 4px 12px rgba(15,23,42,0.06);'>
                    <strong style='color: {TEXT_DARK};'>Zmiana sprzedaży (4 tyg vs poprzednie 4 tyg):</strong>
                    <span style='color: {change_color}; font-size: 1.3rem; font-weight: 700; margin-left: 8px;'>
                        {fmt(change)}%
                    </span>
                    <span style='color: {TEXT_MUTED}; margin-left: 16px;'>
                        Punkt zamówienia: <strong style='color: {TEXT_DARK};'>{fmt(summary['reorder_point'])} szt</strong>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("##### 📅 Prognoza sprzedaży na następne 4 tygodnie")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=weekly["week_start"],
                y=weekly["forecast"].round(2),
                marker=dict(color=BLUE),
                text=weekly["forecast"].round(0).astype(int).astype(str) + " szt",
                textposition="outside",
                textfont=dict(color=TEXT_DARK),
                hovertemplate="<b>%{x}</b><br>Prognoza: %{y:.2f} szt<extra></extra>"
            ))
            fig.add_hline(
                y=summary["safety_stock"],
                line_dash="dash",
                line_color=RED,
                annotation_text=f"Bufor: {fmt(summary['safety_stock'], 0)} szt",
                annotation_position="right",
                annotation_font_color=RED,
            )
            fig.update_layout(
                xaxis=dict(title="Tydzień", gridcolor='rgba(0,0,0,0.05)'),
                yaxis=dict(title="Sztuki", gridcolor='rgba(0,0,0,0.05)'),
                height=400,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color=TEXT_DARK, size=11),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 💡 Rekomendacja")
            st.markdown(
                f"""
                <div class="rec-card">
                    <div class="rec-card-label">Rekomendowany stan magazynu</div>
                    <div class="rec-card-value">{fmt(summary['recommended_stock_4w'], 0)}</div>
                    <div class="rec-card-unit">sztuk na nadchodzące 4 tygodnie</div>
                    <div class="rec-detail">
                        🎯 Przewidywana sprzedaż: <strong>{fmt(summary['forecast_total_4w'], 0)} szt</strong>
                    </div>
                    <div class="rec-detail">
                        🛡️ Bufor bezpieczeństwa: <strong>{fmt(summary['safety_stock'], 0)} szt</strong>
                    </div>
                    <div class="rec-detail">
                        🚨 Zamów ponownie poniżej: <strong>{fmt(summary['reorder_point'], 0)} szt</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        st.markdown(f"##### 📦 Produkty w kategorii '{selected}'")
        products = api_get(f"/categories/{selected}/products?limit=100")
        if products:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Łącznie produktów", fmt(products["total_products"], 0))
                st.metric("Wyświetlanych", fmt(products["products_shown"], 0))
            with col2:
                # products["products"] to teraz lista obiektów {product_id, product_name}
                products_list = products["products"]
                if products_list and isinstance(products_list[0], dict):
                    # Nowy format - lista obiektów
                    products_df = pd.DataFrame(products_list)
                    # Zmień kolejność i nazwy kolumn
                    display_products = pd.DataFrame({
                        "Nazwa produktu": products_df.get("product_name", products_df.get("product_id", "")),
                        "Identyfikator": products_df.get("product_id", ""),
                    })
                else:
                    # Backward compat - stary format (lista stringów)
                    display_products = pd.DataFrame({"Identyfikator": products_list})
                st.dataframe(display_products, use_container_width=True, height=320, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
# STRONA 3: UPLOAD CSV
# ═══════════════════════════════════════════════════════════════════

elif page == "📤 Analiza Twojego magazynu":
    render_header(
        "📤 Analiza Twojego magazynu",
        "Wgraj listę produktów — system zwróci konkretne rekomendacje"
    )

    st.markdown(
        f"""
        <div style='padding: 18px 22px; background: white; border: 1px solid {BORDER_SOLID};
                    border-left: 4px solid {BLUE}; border-radius: 8px; margin: 16px 0;
                    box-shadow: 0 4px 12px rgba(15,23,42,0.06);'>
            <div style='color: #0f172a; font-weight: 700; font-size: 1rem; margin-bottom: 10px;'>
                📋 Format pliku CSV:
            </div>
            <div style='background: #f1f5f9; padding: 14px; border-radius: 6px;
                       color: #0f172a; font-size: 0.95rem; font-weight: 600;
                       border: 1px solid #e2e8f0; font-family: "Courier New", monospace;
                       line-height: 1.6; white-space: pre;'>product_id,current_stock
abc123def456,150
def789ghi012,42</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader("Wybierz plik CSV ze swoim magazynem:", type=["csv"])

    if uploaded:
        df_preview = pd.read_csv(uploaded)
        uploaded.seek(0)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("##### Podgląd wgranego pliku")
            st.dataframe(df_preview.head(10), use_container_width=True, hide_index=True)
        with col2:
            st.metric("Produktów w pliku", fmt(len(df_preview), 0))
            st.metric("Kolumny", fmt(len(df_preview.columns), 0))

        if st.button("🚀 Analizuj magazyn i wygeneruj rekomendacje", type="primary"):
            with st.spinner("Analizuję magazyn..."):
                result = api_post_file("/recommend", uploaded.getvalue(), uploaded.name)

            if result:
                st.success(f"✓ Przeanalizowano {result['total_products']} produktów")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Produktów łącznie", fmt(result["total_products"], 0))
                col2.metric("Rozpoznanych", fmt(result["known_products"], 0))
                col3.metric(
                    "Niestandardowych",
                    fmt(result["unknown_products"], 0),
                    help="Produkty spoza naszej bazy — użyto globalnych średnich"
                )
                col4.metric(
                    "Łącznie do zamówienia",
                    fmt(result['total_units_to_order'], 0) + " szt"
                )

                st.divider()

                section_header(ICON_TRAFFIC, "Sytuacja w Twoim magazynie", "Co należy zamówić, a czego jest za dużo", "blue")

                actions_df = pd.DataFrame(
                    list(result["actions_summary"].items()),
                    columns=["Akcja", "Liczba produktów"],
                )

                action_colors = {
                    "ZAMÓW PILNIE": RED,
                    "ZAMÓW": ORANGE,
                    "OBSERWUJ": "#f59e0b",
                    "OK": GREEN,
                    "NADWYŻKA": BLUE,
                    "BRAK_DANYCH": "#94a3b8",
                }

                col1, col2 = st.columns([1, 2])

                with col1:
                    fig_actions = px.bar(
                        actions_df,
                        x="Akcja",
                        y="Liczba produktów",
                        color="Akcja",
                        color_discrete_map=action_colors,
                        text="Liczba produktów"
                    )
                    fig_actions.update_traces(textposition='outside', textfont=dict(color=TEXT_DARK))
                    fig_actions.update_layout(
                        showlegend=False, height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=TEXT_DARK),
                        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                    )
                    st.plotly_chart(fig_actions, use_container_width=True)

                with col2:
                    recs_df = pd.DataFrame(result["recommendations"])
                    urgent = recs_df[recs_df["urgency"].isin(["high", "medium"])].head(10)

                    if not urgent.empty:
                        st.markdown(
                            f"<h4 style='color: {RED};'>🚨 Najpilniejsze do zamówienia (top 10)</h4>",
                            unsafe_allow_html=True
                        )
                        # Nazwa produktu (po polsku) zamiast hasha
                        # Fallback: jeśli brak product_name -> użyj product_id
                        if 'product_name' in urgent.columns:
                            product_display = urgent['product_name'].fillna(urgent['product_id']).astype(str).str[:40]
                        else:
                            product_display = urgent['product_id'].str[:20] + "..."

                        urgent_display = pd.DataFrame({
                            "Produkt": product_display,
                            "Kategoria": urgent['category'],
                            "Stan": urgent['current_stock'].round(2),
                            "Do zamówienia": urgent['units_to_order'].round(2),
                            "Akcja": urgent['action']
                        })
                        st.dataframe(urgent_display, use_container_width=True, height=360, hide_index=True)
                    else:
                        st.success("✅ Brak pilnych zamówień — wszystko OK")

                st.divider()

                with st.expander("ℹ️ Co oznaczają poszczególne akcje?"):
                    st.markdown("""
                    - **🚨 ZAMÓW PILNIE** — stan poniżej punktu zamówienia, **zamów już teraz**
                    - **🟠 ZAMÓW** — stan starczy na mniej niż 4 tygodnie, **zaplanuj zamówienie**
                    - **🟡 OBSERWUJ** — stan w okolicy bufora, **monitoruj sytuację**
                    - **✅ OK** — stan w normie, **nic nie trzeba robić**
                    - **🔵 NADWYŻKA** — ponad 2× zapotrzebowania, **wstrzymaj zamówienia**
                    """)

                st.divider()

                section_header(ICON_TABLE, "Pełne rekomendacje dla każdego produktu", "Filtruj i pobierz raport", "purple")

                col1, col2, col3 = st.columns(3)
                with col1:
                    action_filter = st.multiselect(
                        "Filtruj akcję:",
                        options=recs_df["action"].unique(),
                        default=recs_df["action"].unique(),
                    )
                with col2:
                    urgency_filter = st.multiselect(
                        "Pilność:",
                        options=recs_df["urgency"].unique(),
                        default=recs_df["urgency"].unique(),
                    )
                with col3:
                    source_filter = st.multiselect(
                        "Źródło danych:",
                        options=recs_df["data_source"].unique(),
                        default=recs_df["data_source"].unique(),
                    )

                filtered_recs = recs_df[
                    (recs_df["action"].isin(action_filter))
                    & (recs_df["urgency"].isin(urgency_filter))
                    & (recs_df["data_source"].isin(source_filter))
                ].copy()

                # Nazwa produktu - po polsku (fallback do hash gdy brak)
                if 'product_name' in filtered_recs.columns:
                    product_name_col = filtered_recs['product_name'].fillna(filtered_recs['product_id'])
                else:
                    product_name_col = filtered_recs['product_id']

                display_recs = pd.DataFrame({
                    "Produkt": product_name_col,
                    "Identyfikator": filtered_recs['product_id'],
                    "Kategoria": filtered_recs['category'],
                    "Stan obecny": filtered_recs['current_stock'].round(2),
                    "Prognoza 4 tyg": filtered_recs['forecast_total_4w'].round(2),
                    "Bufor": filtered_recs['safety_stock'].round(2),
                    "Punkt zamówienia": filtered_recs['reorder_point'].round(2),
                    "Rekomendowany stan": filtered_recs['recommended_stock_4w'].round(2),
                    "Do zamówienia": filtered_recs['units_to_order'].round(2),
                    "Trend": filtered_recs['trend'],
                    "Akcja": filtered_recs['action'],
                })

                st.dataframe(display_recs, use_container_width=True, height=500, hide_index=True)

                csv = display_recs.to_csv(index=False, encoding='utf-8').encode("utf-8")
                st.download_button(
                    label="💾 Pobierz raport jako CSV",
                    data=csv,
                    file_name=f"raport_magazyn_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                )
