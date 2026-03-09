import streamlit as st
import streamlit.components.v1 as st_components
from supabase import create_client
import json
import requests
import base64
import random
import time
import re
import urllib.parse
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ad Generation Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }

/* ── Background ── */
.stApp { background: #0d1117 !important; }

[data-testid="stSidebar"] {
    background: #090c12 !important;
    border-right: 1px solid #1c2030 !important;
    width: 220px !important;
}

.main .block-container { padding: 2rem 2.5rem !important; max-width: 1200px !important; }

#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; }

/* Hide heading anchor links */
.page-header h1 a, h1 a, h2 a, h3 a,
[data-testid="stMarkdownContainer"] h1 a { display: none !important; }

/* Force sidebar always expanded — hide collapse button entirely */
[data-testid="stSidebar"] {
    min-width: 220px !important;
    max-width: 220px !important;
    transform: none !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"],
button[kind="header"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Typography ── */
h1 { font-size: 22px !important; font-weight: 700 !important; color: #f0f6fc !important; margin: 0 0 4px !important; }
h2 { font-size: 15px !important; font-weight: 600 !important; color: #e6edf3 !important; }
h3 { font-size: 13px !important; font-weight: 500 !important; color: #7d8590 !important; }

/* ── Page header block ── */
.page-header { margin-bottom: 28px; padding-bottom: 18px; border-bottom: 1px solid #1c2030; }
.page-header h1 { font-size: 24px !important; font-weight: 700 !important; color: #f0f6fc !important; margin: 0 0 4px !important; }
.page-header p  { font-size: 13px; color: #7d8590; margin: 0; }

.sec-label {
    font-size: 10px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.9px !important;
    color: #3d444d !important; margin-bottom: 8px !important; display: block;
}

/* ── Sidebar: hide radio circles, style as nav items ── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 2px !important; }

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important; align-items: center !important;
    width: 100% !important; padding: 8px 10px !important;
    border-radius: 8px !important; margin: 0 !important;
    cursor: pointer !important;
    color: #636e7b !important; font-size: 13px !important; font-weight: 500 !important;
    transition: all 0.12s ease !important; border-left: 2px solid transparent !important;
    box-sizing: border-box !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #141920 !important; color: #cdd9e5 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #161d2e !important; color: #e6edf3 !important;
    border-left: 2px solid #2563eb !important; font-weight: 600 !important;
}
/* Hide the radio circle indicator */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { margin: 0; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"],
[data-testid="stSidebar"] [data-testid="stRadio"] span[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] * { color: inherit !important; }

/* ── Cards ── */
.kie-card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 16px; }
.kie-card-red { background: #161b22; border: 1px solid #2d1515; border-radius: 10px; padding: 16px; }
.card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }
.card-title { font-size: 10px; font-weight: 600; color: #484f58; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.card-value { font-size: 28px; font-weight: 700; color: #e6edf3; }
.card-delta { font-size: 12px; margin-top: 4px; }
.delta-up   { color: #3fb950; }
.delta-down { color: #f85149; }
.history-card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; }
.history-meta { font-size: 12px; color: #7d8590; margin-top: 4px; }
.brand-card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; display: flex; align-items: center; gap: 14px; }
.brand-avatar { width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg,#2563eb,#3b82f6); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; color: #fff; flex-shrink: 0; }
.brand-info h4 { margin: 0 0 4px; color: #e6edf3; font-size: 14px; }
.brand-info p  { margin: 0; color: #7d8590; font-size: 12px; }
.product-card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
.product-preview { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px; margin-bottom: 14px; }
.ad-preview { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px; margin-bottom: 10px; }
.platform-badge { display: inline-block; background: #1f3460; color: #3b82f6; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 20px; margin-bottom: 8px; }
.ad-body { font-size: 13px; color: #7d8590; margin-bottom: 8px; line-height: 1.5; }
.section-header { font-size: 22px; font-weight: 700; color: #f0f6fc; margin-bottom: 4px; }
.section-sub    { font-size: 13px; color: #7d8590; margin-bottom: 24px; }
.img-placeholder { background: #161b22; border: 1px dashed #30363d; border-radius: 8px; height: 180px; display: flex; align-items: center; justify-content: center; color: #484f58; font-size: 13px; font-weight: 500; text-align: center; }
.loading-box { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 40px 24px; text-align: center; margin: 16px 0; }
.loading-title { font-size: 18px; font-weight: 600; color: #e6edf3; margin-bottom: 8px; }
.loading-sub   { font-size: 13px; color: #7d8590; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 6px !important; color: #e6edf3 !important; font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #2563eb !important; box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label { color: #636e7b !important; font-size: 12px !important; }
[data-testid="stSelectbox"] > div > div {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 6px !important; color: #e6edf3 !important;
}
[data-testid="stSlider"] [role="slider"] { background: #2563eb !important; }

/* ── Buttons ── */
[data-testid="stButton"] button[kind="primary"] {
    background: #2563eb !important; border: none !important;
    border-radius: 24px !important; color: white !important;
    font-size: 13px !important; font-weight: 600 !important;
    height: 44px !important; letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background: #1d4ed8 !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
}
[data-testid="stButton"] button[kind="secondary"] {
    background: transparent !important; border: 1px solid #30363d !important;
    border-radius: 8px !important; color: #7d8590 !important;
    font-size: 12px !important; height: 36px !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #7d8590 !important; color: #e6edf3 !important;
}
[data-testid="stDownloadButton"] button {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 8px !important; color: #7d8590 !important;
    font-size: 12px !important; height: 36px !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #2563eb !important; color: #2563eb !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-testid="stTab"] {
    background: transparent !important; border: none !important;
    color: #636e7b !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 8px 18px !important;
    border-radius: 6px 6px 0 0 !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: #e6edf3 !important; border-bottom: 2px solid #2563eb !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #21262d !important; gap: 4px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: #7d8590 !important; font-size: 12px !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 8px !important; font-size: 12px !important;
}

/* ── Captions ── */
[data-testid="stCaptionContainer"] {
    color: #484f58 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important;
}

/* ── Images ── */
[data-testid="stImage"] img {
    border-radius: 8px !important; object-fit: contain !important;
    background: #0d1117 !important; width: 100% !important;
}

/* ── Pills ── */
.kie-pill {
    display: inline-block; background: #1c2333; border: 1px solid #21262d;
    color: #7d8590; font-size: 10px; padding: 2px 8px; border-radius: 20px;
    margin: 1px 2px 1px 0; white-space: nowrap; max-width: 150px;
    overflow: hidden; text-overflow: ellipsis;
}

/* ── Placeholders ── */
.kie-img-placeholder {
    height: 120px; background: #161b22; border: 1px dashed #30363d;
    border-radius: 8px; display: flex; align-items: center;
    justify-content: center; color: #484f58; font-size: 12px; margin: 8px 0;
}

/* ── Dividers ── */
.kie-divider { border: none; border-top: 1px solid #21262d; margin: 16px 0; }

/* ════════════════════════════════════════
   MOBILE RESPONSIVE
   ════════════════════════════════════════ */

/* Tablet + Mobile: stack columns */
@media (max-width: 900px) {
    .main .block-container {
        padding: 1.25rem 1.25rem !important;
        max-width: 100% !important;
    }

    /* Stack every st.columns() vertically */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* KPI grid: 2 per row on tablet */
    .kpi-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
    }

    /* Scrollable tabs */
    [data-testid="stTabs"] [role="tablist"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        flex-wrap: nowrap !important;
    }
    [data-testid="stTabs"] [data-testid="stTab"] {
        white-space: nowrap !important;
        padding: 8px 14px !important;
        font-size: 13px !important;
    }

    /* Tables: horizontal scroll */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* Page header smaller */
    .page-header h1 { font-size: 20px !important; }
    .page-header { margin-bottom: 20px !important; padding-bottom: 14px !important; }
}

/* Mobile: single column, larger tap targets */
@media (max-width: 600px) {
    .main .block-container {
        padding: 0.875rem !important;
    }

    /* Sidebar auto-collapsible via Streamlit — keep compact */
    [data-testid="stSidebar"] {
        width: 240px !important;
        min-width: 240px !important;
    }

    /* Page header */
    .page-header h1 { font-size: 18px !important; }
    .page-header p  { font-size: 12px !important; }
    .page-header    { margin-bottom: 16px !important; padding-bottom: 12px !important; }

    /* Section labels */
    .sec-label { font-size: 9px !important; }

    /* KPI cards: smaller values */
    .card-value { font-size: 22px !important; }
    .card { padding: 12px 14px !important; }

    /* Input tap targets */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        font-size: 16px !important;  /* prevents iOS zoom on focus */
        padding: 10px 12px !important;
    }
    [data-testid="stSelectbox"] > div > div {
        font-size: 16px !important;
        min-height: 44px !important;
    }

    /* Primary button full width, bigger tap area */
    [data-testid="stButton"] button[kind="primary"] {
        width: 100% !important;
        height: 48px !important;
        font-size: 14px !important;
    }
    [data-testid="stButton"] button[kind="secondary"] {
        height: 40px !important;
    }
    [data-testid="stDownloadButton"] button {
        height: 40px !important;
        font-size: 12px !important;
    }

    /* Expander */
    [data-testid="stExpander"] summary {
        font-size: 13px !important;
        padding: 10px !important;
    }

    /* Nav items: bigger tap target on mobile */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 12px 10px !important;
        font-size: 14px !important;
    }

    /* Product preview card: slightly less padding */
    .kie-img-placeholder { height: 90px !important; font-size: 11px !important; }

    /* Slider */
    [data-testid="stSlider"] { padding: 0 !important; }

    /* Pills wrap cleanly */
    .kie-pill { font-size: 9px !important; padding: 2px 6px !important; }

    /* History cards */
    .history-card { padding: 12px 14px !important; }
    .history-meta { font-size: 11px !important; }

    /* Brand/product cards */
    .brand-card { padding: 12px 14px !important; gap: 10px !important; }
    .brand-avatar { width: 36px !important; height: 36px !important; font-size: 15px !important; }
}

/* Prevent text overflow on small screens */
@media (max-width: 600px) {
    * { word-break: break-word; }
    .brand-info h4 { font-size: 13px !important; }
    .brand-info p  { font-size: 11px !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── Database ─────────────────────────────────────────────────────────────────

@st.cache_resource
def get_sb():
    url = st.secrets.get("SUPABASE_URL", "https://rregsjhewznaiapkonmp.supabase.co")
    key = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZWdzamhld3puYWlhcGtvbm1wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwNTgxNzQsImV4cCI6MjA4ODYzNDE3NH0.d06xTShGMljQWSfBt-BLyY6sCk4XxwtxDQJT0EEPMdQ")
    return create_client(url, key)

if "generating"          not in st.session_state: st.session_state.generating          = False
if "pending_ugc_id"      not in st.session_state: st.session_state.pending_ugc_id      = None
if "pending_comp_ugc_id" not in st.session_state: st.session_state.pending_comp_ugc_id = None
if "pending_dd_meta"     not in st.session_state: st.session_state.pending_dd_meta     = {}
if "pending_comp_meta"   not in st.session_state: st.session_state.pending_comp_meta   = {}
if "job_submitted"       not in st.session_state: st.session_state.job_submitted       = False
if "comp_job_submitted"  not in st.session_state: st.session_state.comp_job_submitted  = False
if "poll_count"          not in st.session_state: st.session_state.poll_count          = 0
if "comp_poll_count"     not in st.session_state: st.session_state.comp_poll_count     = 0

# ─── Constants ────────────────────────────────────────────────────────────────
TONE_OPTIONS = [
    "Professional", "Bold & Energetic", "Friendly & Casual",
    "Luxury & Exclusive", "Playful & Fun", "Urgent & Direct",
]
WEBHOOK_URL              = "https://lorenzotalia.app.n8n.cloud/webhook/d0037d38-4ab7-474f-826c-1a2d96248b98"
COMPETITOR_WEBHOOK_URL   = "https://lorenzotalia.app.n8n.cloud/webhook/competitor-reverse-v1"
MANUAL_WEBHOOK_URL       = "https://lorenzotalia.app.n8n.cloud/webhook/manual-prompt-v1"
RESULTS_POLL_URL         = "https://lorenzotalia.app.n8n.cloud/webhook/results-dd"

# ─── Helpers ──────────────────────────────────────────────────────────────────
def convert_gdrive_url(url: str) -> str:
    """Convert Google Drive share URL to direct download URL."""
    m = re.search(r"/file/d/([^/]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return url

# ─── DB helpers — Brands ──────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_brands():
    try:
        sb = get_sb()
        result = sb.table("brands").select("*").order("name").execute()
        return result.data or []
    except Exception as e:
        st.error(f"Error fetching brands: {e}")
        return []

def save_brand(name, logo_url, primary_color, secondary_color, tone):
    try:
        sb = get_sb()
        sb.table("brands").insert({
            "name": name,
            "logo_url": logo_url,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "tone": tone,
        }).execute()
        get_brands.clear()
    except Exception as e:
        st.error(f"Error saving brand: {e}")

def delete_brand(brand_id):
    try:
        sb = get_sb()
        sb.table("brands").delete().eq("id", brand_id).execute()
        get_brands.clear()
    except Exception as e:
        st.error(f"Error deleting brand: {e}")

def update_brand(brand_id, name, logo_url, primary_color, secondary_color,
                 tone, tagline, tone_of_voice, target_audience, key_benefits):
    try:
        sb = get_sb()
        sb.table("brands").update({
            "name": name,
            "logo_url": logo_url,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "tone": tone,
            "tagline": tagline,
            "tone_of_voice": tone_of_voice,
            "target_audience": target_audience,
            "key_benefits": key_benefits,
        }).eq("id", brand_id).execute()
        get_brands.clear()
    except Exception as e:
        st.error(f"Error updating brand: {e}")

# ─── DB helpers — Products ────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_products(brand_id=None):
    try:
        sb = get_sb()
        if brand_id:
            result = sb.table("products").select("*").eq("brand_id", str(brand_id)).order("name").execute()
        else:
            result = sb.table("products").select("*").order("name").execute()
        return result.data or []
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

def save_product(brand_id, name, description, image_url, key_benefits, target_audience, offer_promotion):
    pid = f"prod_{int(time.time())}"
    try:
        sb = get_sb()
        sb.table("products").insert({
            "id": pid,
            "brand_id": str(brand_id),
            "name": name,
            "description": description,
            "image_url": image_url,
            "key_benefits": key_benefits,
            "target_audience": target_audience,
            "offer_promotion": offer_promotion,
        }).execute()
        get_products.clear()
    except Exception as e:
        st.error(f"Error saving product: {e}")

def update_product(product_id, name, description, image_url, key_benefits, target_audience, offer_promotion):
    try:
        sb = get_sb()
        sb.table("products").update({
            "name": name,
            "description": description,
            "image_url": image_url,
            "key_benefits": key_benefits,
            "target_audience": target_audience,
            "offer_promotion": offer_promotion,
        }).eq("id", product_id).execute()
        get_products.clear()
    except Exception as e:
        st.error(f"Error updating product: {e}")

def delete_product(product_id):
    try:
        sb = get_sb()
        sb.table("products").delete().eq("id", product_id).execute()
        get_products.clear()
    except Exception as e:
        st.error(f"Error deleting product: {e}")

# ─── DB helpers — Ads / History ───────────────────────────────────────────────
def save_ad_image(brand_id, image_url, filename="", mode="ugc-generated"):
    try:
        sb = get_sb()
        sb.table("saved_ads").insert({
            "brand_id": brand_id,
            "image_url": image_url,
            "headline": filename,
            "platform": "Meta",
            "mode": mode,
        }).execute()
    except Exception as e:
        st.error(f"Error saving ad image: {e}")

def get_saved_ads(brand_id=None):
    try:
        sb = get_sb()
        ads_result = sb.table("saved_ads").select("*").order("created_at", desc=True).execute()
        ads = ads_result.data or []
        brands_result = sb.table("brands").select("id, name").execute()
        brand_map = {b["id"]: b["name"] for b in (brands_result.data or [])}
        for ad in ads:
            ad["brand_name"] = brand_map.get(ad.get("brand_id"), "")
        if brand_id:
            ads = [a for a in ads if str(a.get("brand_id", "")) == str(brand_id)]
        return ads
    except Exception as e:
        st.error(f"Error fetching saved ads: {e}")
        return []

def save_to_history(ugc_id, product_id, product_name, brand_name, variants_qty, images, mode="data_driven"):
    try:
        sb = get_sb()
        sb.table("generation_history").insert({
            "ugc_id": ugc_id,
            "product_id": product_id,
            "product_name": product_name,
            "brand_name": brand_name,
            "variants_qty": variants_qty,
            "images_json": json.dumps(images),
            "mode": mode,
        }).execute()
    except Exception as e:
        st.error(f"Error saving to history: {e}")

def get_history():
    try:
        sb = get_sb()
        result = sb.table("generation_history").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        st.error(f"Error fetching history: {e}")
        return []

def clear_history():
    try:
        sb = get_sb()
        sb.table("generation_history").delete().neq("id", 0).execute()
    except Exception as e:
        st.error(f"Error clearing history: {e}")

def analytics_dataframe():
    try:
        sb = get_sb()
        ads_result = sb.table("saved_ads").select("created_at, impressions, clicks, conversions, spend, brand_id").execute()
        ads = ads_result.data or []
        if not ads:
            return pd.DataFrame()
        brands_result = sb.table("brands").select("id, name").execute()
        brand_map = {b["id"]: b["name"] for b in (brands_result.data or [])}
        for ad in ads:
            ad["brand"] = brand_map.get(ad.get("brand_id"), "")
        df = pd.DataFrame(ads)
        df["created_at"] = pd.to_datetime(df["created_at"], format="mixed")
        df["date"] = df["created_at"].dt.date
        df["ctr"]  = (df["clicks"] / df["impressions"].replace(0, 1) * 100).round(2)
        df["cpc"]  = (df["spend"]  / df["clicks"].replace(0, 1)).round(2)
        df["roas"] = (df["conversions"] * 50 / df["spend"].replace(0, 1)).round(2)
        return df
    except Exception as e:
        st.error(f"Error building analytics dataframe: {e}")
        return pd.DataFrame()

# ─── Webhook ──────────────────────────────────────────────────────────────────
def _post_webhook(url: str, payload: dict) -> tuple[bool, str, dict]:
    """Shared POST logic for both webhooks."""
    try:
        r = requests.post(url, json=payload, timeout=420)
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                data = {}
            return True, "OK", data
        if r.status_code == 524:
            return False, "524", {}
        return False, f"HTTP {r.status_code}: {r.text[:300]}", {}
    except requests.exceptions.Timeout:
        return False, "Request timed out after 7 minutes.", {}
    except requests.exceptions.ConnectionError:
        return False, "Connection failed — is the webhook URL correct?", {}
    except Exception as e:
        return False, str(e), {}

def send_to_webhook(payload: dict) -> tuple[bool, str, dict]:
    url = st.session_state.get("webhook_url", WEBHOOK_URL)
    return _post_webhook(url, payload)

def send_to_competitor_webhook(payload: dict) -> tuple[bool, str, dict]:
    url = st.session_state.get("competitor_webhook_url", COMPETITOR_WEBHOOK_URL)
    return _post_webhook(url, payload)

# ─── Creative angle filenames ─────────────────────────────────────────────────
CREATIVE_ANGLES = [
    "problemsolution", "socialproof", "urgency", "benefitled",
    "curiosity", "transformation", "authority", "lifestyle",
]

def is_private_cdn_url(url: str) -> tuple[bool, str]:
    """Returns (is_private, platform_name)"""
    if not url:
        return False, ""
    private_domains = {
        "fbcdn.net": "Facebook",
        "cdninstagram.com": "Instagram",
        "scontent": "Facebook/Instagram",
        "tiktokcdn.com": "TikTok",
        "tiktokv.com": "TikTok",
        "pbs.twimg.com": "Twitter/X",
        "video.twimg.com": "Twitter/X",
    }
    for domain, platform in private_domains.items():
        if domain in url:
            return True, platform
    return False, ""

def _slugify(s: str, max_len: int = 15) -> str:
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s[:max_len]

def build_filename(brand_name: str, product_name: str, creative_angle: str, variant_index: int) -> str:
    """static_[brand]_[product]_[angle]_v[N]_[date]"""
    date_str = datetime.now().strftime("%Y%m%d")
    return (
        f"static_{_slugify(brand_name)}_{_slugify(product_name)}"
        f"_{_slugify(creative_angle)}_v{variant_index + 1}_{date_str}"
    )

def build_competitor_filename(brand_name: str, product_name: str, competitor_url: str, variant_index: int) -> str:
    """static_[brand]_[product]_comp_[domain]_v[N]_[date]"""
    try:
        domain = urllib.parse.urlparse(competitor_url).netloc
        if "fbcdn" in domain or "facebook" in domain:
            comp_slug = "facebook"
        elif "instagram" in domain or "cdninstagram" in domain:
            comp_slug = "instagram"
        elif "tiktok" in domain:
            comp_slug = "tiktok"
        else:
            cdn_prefixes = {"scontent", "cdn", "static", "media", "img", "assets", "images", "content", "i"}
            parts = domain.replace("www.", "").split(".")
            meaningful = [p for p in parts if p not in cdn_prefixes and len(p) > 2]
            comp_slug = _slugify(meaningful[0], max_len=12) if meaningful else "comp"
    except Exception:
        comp_slug = "comp"
    date_str = datetime.now().strftime("%Y%m%d")
    return (
        f"static_{_slugify(brand_name)}_{_slugify(product_name)}"
        f"_comp_{comp_slug}_v{variant_index + 1}_{date_str}"
    )

def attach_filenames(images: list[dict], brand_name: str = "", product_name: str = "") -> list[dict]:
    result = []
    for img in images:
        idx   = img.get("index", images.index(img))
        angle = CREATIVE_ANGLES[idx % len(CREATIVE_ANGLES)]
        result.append({**img, "filename": build_filename(brand_name, product_name, angle, idx)})
    return result

def get_download_button(image_url: str, filename: str, label: str = "⬇️ Download", key_suffix: str = ""):
    cache_key = f"_imgcache_{image_url}"
    if cache_key not in st.session_state:
        try:
            r = requests.get(image_url, timeout=15)
            r.raise_for_status()
            st.session_state[cache_key] = r.content
        except Exception as e:
            st.error(f"Download failed: {e}")
            return
    ext = image_url.split(".")[-1].split("?")[0] or "jpg"
    st.download_button(
        label=label,
        data=st.session_state[cache_key],
        file_name=f"{filename}.{ext}",
        mime=f"image/{ext}",
        use_container_width=True,
        key=f"dl_{filename}_{key_suffix}",
    )

# ─── Shared UI helpers ────────────────────────────────────────────────────────
def render_generating_placeholders(ugc_id: str, slot_names=None):
    if slot_names is None:
        slot_names = [
            "🎭 Visual Proof", "🎯 Hidden Enemy", "🌿 Scientific Authority",
            "💆 Relatable Moment", "📊 Comparison Chart",
        ]
    st.markdown("""
    <style>
    @keyframes shimmer {
        0%   { background-position: -400px 0; }
        100% { background-position:  400px 0; }
    }
    .shimmer-box {
        background: linear-gradient(90deg,#161b22 25%,#1f2937 50%,#161b22 75%);
        background-size: 400px 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 10px;
        border: 1px solid #21262d;
    }
    @keyframes pulse-dot {
        0%,80%,100% { opacity:.2; transform:scale(.8); }
        40%          { opacity:1;  transform:scale(1);  }
    }
    .dot {
        display:inline-block; width:6px; height:6px;
        background:#2563eb; border-radius:50%; margin:0 2px;
        animation: pulse-dot 1.4s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay:.2s; }
    .dot:nth-child(3) { animation-delay:.4s; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
        <div><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
        <span style="font-size:13px;color:#7d8590">Generating your ads… refreshing every 5s</span>
        <span style="font-size:10px;color:#484f58;font-family:monospace;margin-left:auto">{ugc_id}</span>
    </div>
    """, unsafe_allow_html=True)
    for i, name in enumerate(slot_names):
        st.markdown(f"""
        <div style="margin-bottom:12px">
            <div style="font-size:10px;color:#484f58;font-weight:600;
                        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px">
                Slot {i+1} — {name}
            </div>
            <div class="shimmer-box" style="height:220px;width:100%"></div>
        </div>
        """, unsafe_allow_html=True)

def inject_generation_guard(active: bool):
    if active:
        st.markdown("""
        <script>
        window._generationActive = true;
        window.onbeforeunload = function(e) {
            if (window._generationActive) {
                const msg = 'Generation is in progress. If you leave now, you will lose your results. Are you sure?';
                e.preventDefault();
                e.returnValue = msg;
                return msg;
            }
        };
        document.addEventListener('click', function(e) {
            if (!window._generationActive) return;
            const link = e.target.closest('a[href]');
            if (link && !link.href.includes('#')) {
                const confirmed = window.confirm(
                    '⚠️ Generation in progress\\n\\nIf you navigate away now you will lose your results.\\n\\nAre you sure you want to leave?'
                );
                if (!confirmed) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }
        }, true);
        </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <script>
        window._generationActive = false;
        window.onbeforeunload = null;
        </script>
        """, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div style="margin-bottom:20px">'
        f'<h1 style="font-size:20px;font-weight:600;color:#e6edf3;margin:0 0 4px">{title}</h1>'
        + (f'<p style="font-size:12px;color:#484f58;margin:0">{subtitle}</p>' if subtitle else "")
        + '</div><hr style="border:none;border-top:1px solid #21262d;margin:0 0 20px">',
        unsafe_allow_html=True,
    )

def parse_benefits(raw: str, max_items: int = 4, max_chars: int = 28) -> list:
    if not raw or not raw.strip():
        return []
    colon_matches = re.findall(r'^([A-Z][^:\n]{2,30}):', raw, re.MULTILINE)
    if len(colon_matches) >= 2:
        return [m.strip()[:max_chars] for m in colon_matches[:max_items]]
    lines = [l.strip() for l in raw.split("\n")
             if l.strip() and 10 < len(l.strip()) < 80
             and not l.strip().startswith("Key Benefit")
             and not l.strip().startswith("Use these")]
    if lines:
        return [l[:max_chars] for l in lines[:max_items]]
    parts = [p.strip() for p in raw.split(",") if p.strip() and len(p.strip()) > 3]
    return [p[:max_chars] for p in parts[:max_items]]

def render_product_image(image_url: str, size: int = 72) -> str:
    placeholder = (
        f'<div style="width:{size}px;height:{size}px;background:#1a1a1a;'
        f'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        f'font-size:{size//3}px;flex-shrink:0">📦</div>'
    )
    if not image_url or not image_url.strip():
        return placeholder
    encoded   = urllib.parse.quote(image_url.strip(), safe="")
    proxy_url = f"https://images.weserv.nl/?url={encoded}&w={size*2}&h={size*2}&fit=cover&output=jpg"
    return (
        f'<img src="{proxy_url}" width="{size}" height="{size}" '
        f'style="border-radius:8px;object-fit:cover;background:#1a1a1a;flex-shrink:0" '
        f'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\'" />'
        + placeholder.replace("display:flex", "display:none").replace('display:flex"', 'display:none"')
    )

def render_ad_image(url: str, key: str, width: int = 0):
    """Thumbnail that opens a fullscreen lightbox via iframe JS → window.parent.document."""
    if not url:
        return
    w_css  = f"{width}px" if width else "100%"
    url_js = url.replace("\\", "\\\\").replace("'", "\\'")
    html = f"""
<style>
  html,body{{margin:0;padding:0;overflow:hidden;background:transparent;}}
  img#thumb{{width:{w_css};border-radius:8px;display:block;cursor:zoom-in;
             border:1px solid #21262d;transition:opacity .15s;}}
  img#thumb:hover{{opacity:.85;}}
</style>
<img id="thumb" src="{url}" onclick="openLb()" />
<script>
var thumb = document.getElementById('thumb');
thumb.onload = function() {{
  var fr = window.frameElement;
  if(fr) fr.style.height = thumb.offsetHeight + 'px';
}};
if(thumb.complete) {{
  var fr = window.frameElement;
  if(fr) fr.style.height = thumb.offsetHeight + 'px';
}}
function openLb() {{
  try {{
    var doc = window.parent.document;
    var ex = doc.getElementById('__ad_lb__');
    if(ex) doc.body.removeChild(ex);
    var ov = doc.createElement('div');
    ov.id = '__ad_lb__';
    ov.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;'
      + 'background:rgba(0,0,0,.92);z-index:2147483647;display:flex;'
      + 'align-items:center;justify-content:center;cursor:zoom-out;';
    var img = doc.createElement('img');
    img.src = '{url_js}';
    img.style.cssText = 'max-width:90vw;max-height:90vh;border-radius:12px;'
      + 'box-shadow:0 0 80px rgba(0,0,0,.9);';
    ov.appendChild(img);
    ov.onclick = function() {{ doc.body.removeChild(ov); }};
    doc.body.appendChild(ov);
  }} catch(e) {{}}
}}
</script>"""
    init_h = width if width else 320
    st_components.html(html, height=init_h, scrolling=False)

def render_product_card(product: dict, brand_name: str) -> str:
    img_url = product.get("image_url", "").strip()
    encoded = urllib.parse.quote(img_url, safe="") if img_url else ""
    proxy = f"https://images.weserv.nl/?url={encoded}&w=120&h=120&fit=cover&output=jpg" if img_url else ""
    img_html = (
        f'<img src="{proxy}" style="width:56px;height:56px;border-radius:8px;object-fit:cover;background:#1f2937;flex-shrink:0" onerror="this.style.display=\'none\'">'
        if proxy else
        '<div style="width:56px;height:56px;border-radius:8px;background:#1f2937;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">📦</div>'
    )
    benefits = parse_benefits(product.get("key_benefits", ""), max_items=3, max_chars=25)
    pills = "".join([
        f'<span style="display:inline-block;background:#1f2937;border:1px solid #21262d;color:#7d8590;font-size:10px;padding:1px 8px;border-radius:20px;margin:1px 2px">{b}</span>'
        for b in benefits
    ])
    offer = product.get("offer_promotion", "")
    show_offer = bool(offer and offer.strip().lower() not in ("", "none", "n/a", "no promo for now"))
    offer_html = f'<span style="font-size:10px;color:#3fb950;margin-left:8px">🎁 {offer[:40]}</span>' if show_offer else ""
    desc = product.get("description", "") or ""
    desc_short = desc[:80] + "…" if len(desc) > 80 else desc
    return (
        f'<div style="display:flex;align-items:flex-start;gap:14px;padding:14px 16px;'
        f'background:#161b22;border:1px solid #21262d;border-radius:10px;margin:4px 0">'
        f'{img_html}'
        f'<div style="flex:1;min-width:0">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">'
        f'<span style="font-size:14px;font-weight:600;color:#e6edf3">{product["name"]}</span>'
        f'<span style="font-size:10px;color:#484f58;background:#1f2937;padding:1px 7px;border-radius:20px;border:1px solid #21262d">{brand_name}</span>'
        f'{offer_html}</div>'
        f'<div style="font-size:11px;color:#484f58;margin-bottom:6px;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{desc_short}</div>'
        f'<div>{pills}</div>'
        f'</div></div>'
    )

def render_brand_card(brand: dict) -> str:
    logo_url = brand.get("logo_url", "").strip()
    encoded = urllib.parse.quote(logo_url, safe="") if logo_url else ""
    proxy = f"https://images.weserv.nl/?url={encoded}&w=100&h=100&fit=cover&output=jpg" if logo_url else ""
    img_html = (
        f'<img src="{proxy}" style="width:48px;height:48px;border-radius:8px;object-fit:cover;background:#1f2937;flex-shrink:0" onerror="this.style.display=\'none\'">'
        if proxy else
        '<div style="width:48px;height:48px;border-radius:8px;background:#1f2937;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">🏷️</div>'
    )
    tone = brand.get("tone_of_voice", "") or brand.get("tone", "")
    tagline = brand.get("tagline", "") or ""
    tone_html = (
        f'<span style="font-size:10px;color:#7d8590;background:#1f2937;padding:1px 8px;border-radius:20px;border:1px solid #21262d;margin-top:4px;display:inline-block">{tone}</span>'
        if tone else ""
    )
    return (
        f'<div style="display:flex;align-items:center;gap:14px;padding:12px 16px;'
        f'background:#161b22;border:1px solid #21262d;border-radius:10px;margin:4px 0">'
        f'{img_html}'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:14px;font-weight:600;color:#e6edf3;margin-bottom:2px">{brand["name"]}</div>'
        f'<div style="font-size:11px;color:#484f58;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{tagline[:60]}</div>'
        f'{tone_html}</div></div>'
    )

# ─── Image grid renderer ──────────────────────────────────────────────────────
IMAGE_GRID_CSS = """<style>
[data-testid="stImage"] img { border-radius: 8px; object-fit: cover; }
[data-testid="stImage"] { border: 1px solid #21262d; border-radius: 8px; padding: 6px; background: #161b22; margin-bottom: 4px; }
</style>"""

def render_image_grid(images: list[dict], brand_id: int, key_prefix: str):
    st.markdown(IMAGE_GRID_CSS, unsafe_allow_html=True)
    cols = st.columns(3)
    for i, img in enumerate(images):
        url      = img.get("image_url", "")
        filename = img.get("filename", build_filename(
            "", "", CREATIVE_ANGLES[img.get("index", i) % len(CREATIVE_ANGLES)], img.get("index", i),
        ))
        with cols[i % 3]:
            if url:
                render_ad_image(url, f"saved_{i}")
            else:
                st.markdown('<div class="img-placeholder">No image</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin:6px 0 10px;padding:6px 8px;background:#161b22;border:1px solid #30363d;border-radius:6px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#8b949e;word-break:break-all;line-height:1.4">{filename}</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾 Save", key=f"{key_prefix}_save_{i}"):
                    save_ad_image(brand_id, url, filename)
                    st.success("Saved!")
            with b2:
                if url:
                    get_download_button(url, filename, key_suffix=f"{key_prefix}_{i}")

# ─── Shared output panel (DD + Manual tabs) ───────────────────────────────────
def render_output_panel(key_prefix: str = "dd"):
    st.markdown('<span class="sec-label">Output</span>', unsafe_allow_html=True)

    if st.session_state.job_submitted and st.session_state.pending_ugc_id:
        ugc_id     = st.session_state.pending_ugc_id
        progress   = min(0.9, st.session_state.poll_count * 0.06)
        st.markdown("**⏳ Generating your ads...**")
        st.progress(progress)
        st.caption("This usually takes 3–5 minutes. You can navigate away — results will appear in History.")
        # Fire deferred POST now — loading bar is already visible above (progressive rendering)
        for _key in ("deferred_dd", "deferred_manual"):
            if _key in st.session_state:
                _d = st.session_state.pop(_key)
                try:
                    _r = requests.post(_d["url"], json=_d["payload"], timeout=15)
                    _new = _r.json().get("ugc_id")
                    if _new:
                        st.session_state.pending_ugc_id = _new
                        ugc_id = _new
                except Exception:
                    pass
        try:
            poll_resp = requests.get(RESULTS_POLL_URL, params={"ugc_id": ugc_id}, timeout=10)
            poll_data = poll_resp.json()
        except Exception:
            poll_data = {"status": "processing"}

        if poll_data.get("status") == "done":
            meta   = st.session_state.pending_dd_meta
            images = attach_filenames(
                poll_data.get("images", []),
                brand_name   = meta.get("brand_name", ""),
                product_name = meta.get("product_name", ""),
            )
            save_to_history(
                ugc_id       = poll_data.get("ugc_id", ugc_id),
                product_id   = meta.get("product_id", ""),
                product_name = meta.get("product_name", ""),
                brand_name   = meta.get("brand_name", ""),
                variants_qty = len(images),
                images       = images,
                mode         = "data_driven",
            )
            st.session_state["last_results"]          = images
            st.session_state["last_results_brand_id"] = meta.get("brand_id")
            st.session_state["last_results_product"]  = meta.get("product_name", "")
            st.session_state.pending_ugc_id           = None
            st.session_state.pending_dd_meta          = {}
            st.session_state.generating               = False
            st.session_state.job_submitted            = False
            st.session_state.poll_count               = 0
            inject_generation_guard(False)
            st.rerun()
        else:
            st.session_state.poll_count += 1
            time.sleep(8)
            st.rerun()

    elif st.session_state.get("last_results"):
        images   = st.session_state["last_results"]
        brand_id = st.session_state.get("last_results_brand_id")
        product  = st.session_state.get("last_results_product", "")
        st.markdown(
            f'<p style="font-size:12px;color:#3fb950;font-weight:600;margin-bottom:10px">'
            f'✅ {len(images)} variant{"s" if len(images) != 1 else ""} · {product}</p>',
            unsafe_allow_html=True,
        )
        grid_cols = st.columns(2, gap="small")
        for i, img in enumerate(images):
            url      = img.get("image_url", "")
            filename = img.get("filename", build_filename("", "", CREATIVE_ANGLES[i % len(CREATIVE_ANGLES)], i))
            with grid_cols[i % 2]:
                if url:
                    render_ad_image(url, f"{key_prefix}_{i}")
                st.markdown(
                    f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                    f'color:#484f58;margin:2px 0 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{filename}</p>',
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾", key=f"{key_prefix}_save_{i}", use_container_width=True, help="Save"):
                        save_ad_image(brand_id, url, filename)
                        st.success("Saved!")
                with b2:
                    if url:
                        get_download_button(url, filename, label="⬇️", key_suffix=f"{key_prefix}_{i}")
    else:
        st.markdown(
            '<div class="kie-img-placeholder">🎨 Generated ads will appear here</div>',
            unsafe_allow_html=True,
        )


# ─── Prompt quality score engine ──────────────────────────────────────────────
def calculate_prompt_score(prompt: str) -> dict:
    import re
    if not prompt or len(prompt.strip()) < 5:
        return {"score": 0, "label": "Empty", "color": "#484f58", "tips": []}
    p = prompt.lower()
    score = 0
    tips  = []

    scene_words = ["background", "scene", "environment", "setting", "room",
                   "outdoor", "indoor", "kitchen", "office", "studio", "white",
                   "dark", "bright", "lighting", "shadow", "bokeh", "marble",
                   "forest", "urban", "nature", "table", "desk", "surface"]
    if any(w in p for w in scene_words):
        score += 20
    else:
        tips.append("🏞️ Describe the background or scene")

    product_words = ["product", "packaging", "box", "bottle", "label",
                     "holding", "placed", "centered", "foreground", "hero",
                     "prominent", "beside", "next to", "hand"]
    if any(w in p for w in product_words):
        score += 15
    else:
        tips.append("📦 Mention how the product should appear")

    has_quotes    = bool(re.search(r'["\'](.+?)["\']', prompt))
    headline_words = ["headline", "text", "title", "copy", "reads",
                      "saying", "font", "bold", "written"]
    if has_quotes:
        score += 20
    elif any(w in p for w in headline_words):
        score += 10
        tips.append('✍️ Put your headline in quotes for full points')
    else:
        tips.append('✍️ Add a headline in quotes e.g. "Your Brain Deserves Better."')

    cta_words = ["cta", "button", "call to action", "shop now", "discover",
                 "try", "get yours", "learn more", "buy", "order", "click"]
    if any(w in p for w in cta_words):
        score += 15
    else:
        tips.append("👆 Add a CTA button text e.g. 'Shop Now'")

    style_words = ["cinematic", "editorial", "minimalist", "dramatic",
                   "lifestyle", "flat lay", "ugc", "premium", "warm",
                   "cold", "moody", "clean", "bold", "photorealistic",
                   "split", "infographic", "macro", "bokeh"]
    if any(w in p for w in style_words):
        score += 15
    else:
        tips.append("🎨 Specify a visual style (cinematic, minimal, editorial...)")

    word_count = len(prompt.split())
    if word_count >= 40:
        score += 15
    elif word_count >= 20:
        score += 8
        tips.append("📝 More detail = better results (aim for 40+ words)")
    else:
        tips.append("📝 Too short — add more visual detail")

    if score >= 86:
        label, color = "⚡ Expert", "#f59e0b"
    elif score >= 66:
        label, color = "🟢 Strong", "#22c55e"
    elif score >= 41:
        label, color = "🟡 Good", "#eab308"
    else:
        label, color = "🔴 Weak", "#ef4444"

    return {"score": score, "label": label, "color": color, "tips": tips}


def render_score_badge(result: dict):
    score = result["score"]
    label = result["label"]
    color = result["color"]
    tips  = result["tips"]
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:6px 0 4px">
        <div style="background:{color}22;border:1px solid {color}55;
                    border-radius:20px;padding:3px 12px;
                    font-size:11px;font-weight:600;color:{color}">
            {label}
        </div>
        <div style="flex:1;height:4px;background:#21262d;border-radius:2px">
            <div style="width:{score}%;height:100%;background:{color};
                        border-radius:2px;transition:width 0.3s"></div>
        </div>
        <div style="font-size:11px;color:#7d8590;min-width:32px;text-align:right">
            {score}/100
        </div>
    </div>
    """, unsafe_allow_html=True)
    for tip in tips[:2]:
        st.markdown(
            f'<div style="font-size:10px;color:#7d8590;margin:2px 0 0 4px">{tip}</div>',
            unsafe_allow_html=True,
        )


# ─── Manual Prompt tab ────────────────────────────────────────────────────────
def render_manual_prompt_tab(brands):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_right:
        render_output_panel("manual")

    with col_left:
        st.markdown('<span class="sec-label">Input</span>', unsafe_allow_html=True)

        sel1, sel2 = st.columns(2, gap="small")
        with sel1:
            m_brand = st.selectbox(
                "Brand", brands,
                format_func=lambda b: b["name"],
                label_visibility="collapsed",
                key="manual_brand",
            )
        with sel2:
            m_products = get_products(m_brand["id"])
            if m_products:
                m_product = st.selectbox(
                    "Product", m_products,
                    format_func=lambda p: p["name"],
                    label_visibility="collapsed",
                    key="manual_product_sel",
                )
            else:
                st.info("No products — add one in **📦 Products**.")
                m_product = None

        if not m_product:
            return

        st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)

        v_col, _ = st.columns([3, 2])
        with v_col:
            num_variants = st.slider("Number of variants", 1, 5, 2, key="manual_variants")

        st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)
        st.markdown('<span class="sec-label">Prompts</span>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:#7d8590;margin-bottom:12px">'
            'Write one prompt per variant. Describe scene, lighting, headline, CTA, and visual style.'
            '</div>',
            unsafe_allow_html=True,
        )

        prompts    = []
        all_scores = []
        for i in range(num_variants):
            st.markdown(
                f'<div style="font-size:11px;font-weight:600;color:#7d8590;'
                f'text-transform:uppercase;letter-spacing:0.8px;'
                f'margin:{"16px" if i > 0 else "0"} 0 4px">Variant {i+1}</div>',
                unsafe_allow_html=True,
            )
            prompt_val = st.text_area(
                f"v{i}",
                key=f"manual_prompt_{i}",
                height=110,
                placeholder='e.g. Woman in morning kitchen holding the product. Warm bokeh. Headline "Finally, Calm." CTA "Find Your Balance". Lifestyle UGC style.',
                label_visibility="collapsed",
            )
            prompts.append(prompt_val)
            score_result = calculate_prompt_score(prompt_val)
            all_scores.append(score_result["score"])
            render_score_badge(score_result)

        filled = [p for p in prompts if len(p.strip()) > 10]
        ready  = len(filled) == num_variants

        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        if len(filled) < num_variants:
            st.markdown(
                f'<div style="font-size:11px;color:#7d8590;margin-bottom:8px">'
                f'{len(filled)}/{num_variants} prompts filled</div>',
                unsafe_allow_html=True,
            )

        m_missing_logo  = not (m_brand.get("logo_url") or "").strip()
        m_missing_image = not (m_product.get("image_url") or "").strip()
        if m_missing_image:
            st.warning("⚠️ Product has no image URL — edit in Products")
        if m_missing_logo:
            st.warning("⚠️ Brand has no logo URL — edit in Brands")

        generate_clicked = st.button(
            f"🚀  Generate  ·  {num_variants} variant{'s' if num_variants > 1 else ''}",
            key="manual_generate",
            disabled=(not ready or st.session_state.job_submitted or m_missing_logo or m_missing_image),
            use_container_width=True,
            type="primary",
        )

        if generate_clicked and ready and not st.session_state.job_submitted:
            st.session_state.job_submitted = True
            ugc_id = f"manual_{m_product['id']}_{int(time.time())}"
            st.session_state.deferred_manual = {
                "url": st.session_state.get("manual_webhook_url", MANUAL_WEBHOOK_URL),
                "payload": {
                    "ugc_id":         ugc_id,
                    "name":           m_product["name"],
                    "asset_url":      m_product.get("image_url") or "",
                    "logo_url":       m_brand.get("logo_url") or "",
                    "brand_id":       str(m_brand["id"]),
                    "variants_qty":   num_variants,
                    "manual_prompts": prompts,
                    "mode":           "manual",
                },
            }
            st.session_state.generating      = True
            st.session_state.pending_ugc_id  = ugc_id
            st.session_state.pending_dd_meta = {
                "brand_id":     m_brand["id"],
                "product_id":   m_product["id"],
                "product_name": m_product["name"],
                "brand_name":   m_brand["name"],
            }
            st.session_state.pop("last_results", None)
            inject_generation_guard(True)
            st.rerun()


# ─── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    # Logo header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;
                padding:16px 10px 14px;border-bottom:1px solid #1c2030;margin-bottom:8px">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                    border-radius:8px;display:flex;align-items:center;justify-content:center;
                    font-size:15px;flex-shrink:0">🎯</div>
        <span style="font-size:15px;font-weight:700;color:#f0f6fc;letter-spacing:-0.3px">Ad Studio</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Generate Ads", "Campaign Analytics", "Saved Ads Library",
         "📋 History", "Brands", "📦 Products", "Settings"],
        label_visibility="collapsed",
    )

    brands      = get_brands()
    brand_names = [b["name"] for b in brands]
    brand_ids   = [b["id"]   for b in brands]
    try:
        _all_prods = get_products()
        n_products = len(_all_prods)
    except Exception:
        n_products = 0

    brand_list_html = "".join(
        f'<div style="display:flex;align-items:center;gap:7px;padding:4px 10px;border-radius:6px">'
        f'<div style="width:6px;height:6px;border-radius:50%;background:#2563eb;flex-shrink:0"></div>'
        f'<span style="font-size:12px;color:#636e7b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{b["name"]}</span>'
        f'</div>'
        for b in brands[:6]
    )
    st.markdown(f"""
    <div style="margin-top:16px;padding:0 0 8px">
        <div style="font-size:9px;font-weight:700;color:#3d444d;text-transform:uppercase;
                    letter-spacing:1px;padding:0 10px;margin-bottom:6px">Workspaces</div>
        {brand_list_html}
        <div style="font-size:11px;color:#3d444d;padding:6px 10px;margin-top:4px">
            {n_products} product{'s' if n_products != 1 else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — GENERATE ADS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Generate Ads":

    page_header("Generate Ads", "Create AI-powered ad creatives from your product data or competitor references.")

    if st.session_state.get("generating", False):
        inject_generation_guard(True)

    if not brands:
        st.warning("No brands found. Add a brand in the **Brands** tab first.")
        st.stop()

    mode_tab1, mode_tab2, mode_tab3 = st.tabs(["Data-Driven", "Competitor Reverse", "✏️ Manual Prompt"])

    # ── DATA-DRIVEN ───────────────────────────────────────────────────────────
    with mode_tab1:
        left_col, right_col = st.columns([1, 1], gap="large")

        # Right col first — output / polling
        with right_col:
            render_output_panel("dd")

        # Left col — inputs
        with left_col:
            st.markdown('<span class="sec-label">Input</span>', unsafe_allow_html=True)

            sel1, sel2 = st.columns(2, gap="small")
            with sel1:
                dd_brand = st.selectbox(
                    "Brand", brands,
                    format_func=lambda b: b["name"],
                    label_visibility="collapsed",
                    key="dd_brand",
                )
            with sel2:
                dd_products = get_products(dd_brand["id"])
                if dd_products:
                    dd_product = st.selectbox(
                        "Product", dd_products,
                        format_func=lambda p: p["name"],
                        label_visibility="collapsed",
                        key="dd_product_sel",
                    )
                else:
                    st.info("No products — add one in **📦 Products**.")
                    dd_product = None

            if dd_product:
                img_url  = convert_gdrive_url((dd_product.get("image_url") or "").strip())
                benefits = parse_benefits(dd_product.get("key_benefits", ""), max_items=3)
                pills_html = "".join(
                    f'<span class="kie-pill">{b}</span>' for b in benefits
                ) or '<span style="color:#484f58;font-size:10px">—</span>'
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;background:#161b22;'
                    f'border:1px solid #21262d;border-radius:8px;padding:10px 14px;margin:8px 0">'
                    + render_product_image(img_url, size=52)
                    + f'<div style="flex:1;min-width:0">'
                    f'<div style="font-size:13px;font-weight:600;color:#e6edf3;margin-bottom:4px">'
                    f'{dd_product["name"]}</div>'
                    f'<div>{pills_html}</div></div></div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)

            v_col, _ = st.columns([3, 2])
            with v_col:
                dd_variations = st.slider("Number of variants", 1, 5, 2, key="dd_variations")

            with st.expander("⚙️ Override defaults"):
                ov1, ov2 = st.columns(2)
                with ov1:
                    dd_audience_override = st.text_input(
                        "Audience override",
                        placeholder=(dd_product.get("target_audience") or "")[:50] if dd_product else "",
                        key="dd_aud_ov",
                    )
                with ov2:
                    dd_offer_override = st.text_input(
                        "Offer override",
                        placeholder=(dd_product.get("offer_promotion") or "none") if dd_product else "",
                        key="dd_offer_ov",
                    )
                dd_extra_context = st.text_area(
                    "Additional context",
                    placeholder="e.g. Focus on summer campaign, anxiety angle, warm tones...",
                    height=64, key="dd_ctx",
                )

            dd_missing_logo  = not (dd_brand.get("logo_url") or "").strip()
            dd_missing_image = not (dd_product or {}).get("image_url", "").strip() if dd_product else True
            dd_no_products   = not dd_products

            if dd_no_products:
                st.warning("⚠️ No products for this brand — add one in Products")
            elif dd_missing_image:
                st.warning("⚠️ Product has no image URL — edit in Products")
            if dd_missing_logo:
                st.warning("⚠️ Brand has no logo URL — edit in Brands")

            is_polling_dd = bool(st.session_state.pending_ugc_id)
            generate_btn  = st.button(
                f"🚀  Generate  ·  {dd_variations} variant{'s' if dd_variations > 1 else ''}",
                disabled=(dd_missing_logo or dd_missing_image or dd_no_products or is_polling_dd or st.session_state.job_submitted),
                use_container_width=True,
                type="primary",
                key="dd_generate_btn",
            )

        # Fire-and-poll: queue job, rerun immediately to show loading, fire POST on next render
        if generate_btn and not st.session_state.job_submitted:
            st.session_state.job_submitted = True
            audience = dd_audience_override or dd_product["target_audience"] or ""
            offer    = dd_offer_override    or dd_product.get("offer_promotion") or ""
            ugc_id   = f"ugc_{int(time.time())}"
            st.session_state.deferred_dd = {
                "url": st.session_state.get("webhook_url", WEBHOOK_URL),
                "payload": {
                    "ugc_id":       ugc_id,
                    "name":         dd_product["name"],
                    "persona":      audience,
                    "context":      f"Benefits: {dd_product['key_benefits']}. Offer: {offer}. {dd_extra_context}".strip(),
                    "variants_qty": int(dd_variations),
                    "asset_url":    dd_product["image_url"],
                    "logo_url":     dd_brand["logo_url"],
                    "brand_id":     str(dd_brand["id"]),
                },
            }
            st.session_state.generating      = True
            st.session_state.pending_ugc_id  = ugc_id
            st.session_state.pending_dd_meta = {
                "brand_id":     dd_brand["id"],
                "product_id":   dd_product["id"],
                "product_name": dd_product["name"],
                "brand_name":   dd_brand["name"],
            }
            st.session_state.pop("last_results", None)
            inject_generation_guard(True)
            st.rerun()

    # ── COMPETITOR REVERSE ────────────────────────────────────────────────────
    with mode_tab2:
        cl_col, cr_col = st.columns([1, 1], gap="large")

        # Right col — competitor preview + output / polling
        with cr_col:
            st.markdown('<span class="sec-label">Output</span>', unsafe_allow_html=True)

            comp_url_preview = st.session_state.get("comp_img_url", "")
            if comp_url_preview and comp_url_preview.startswith("http") and not is_private_cdn_url(comp_url_preview)[0]:
                encoded_prev = urllib.parse.quote(comp_url_preview.strip(), safe="")
                proxy_prev   = f"https://images.weserv.nl/?url={encoded_prev}&w=400&output=jpg"
                st.markdown(
                    f'<div style="margin-bottom:10px">'
                    f'<span class="sec-label">Competitor Ad</span>'
                    f'<img src="{proxy_prev}" style="width:100%;max-height:200px;object-fit:contain;'
                    f'border-radius:8px;background:#0d0808;display:block" /></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="kie-img-placeholder" style="border-color:#2d1515;background:#0d0808;margin-bottom:10px">'
                    '🕵️ Paste a competitor ad URL to preview</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)

            if st.session_state.comp_job_submitted and st.session_state.pending_comp_ugc_id:
                # ── POLLING ──────────────────────────────────────────────
                ugc_id     = st.session_state.pending_comp_ugc_id
                poll_count = st.session_state.comp_poll_count
                progress   = min(0.9, poll_count * 0.06)

                st.markdown("**⏳ Generating your ads...**")
                st.progress(progress)
                st.caption("This usually takes 3–5 minutes. You can navigate away — results will appear in History.")
                # Fire deferred POST now — loading bar already visible (progressive rendering)
                if "deferred_comp" in st.session_state:
                    _d = st.session_state.pop("deferred_comp")
                    try:
                        _r = requests.post(_d["url"], json=_d["payload"], timeout=15)
                        _new = _r.json().get("ugc_id")
                        if _new:
                            st.session_state.pending_comp_ugc_id = _new
                            ugc_id = _new
                    except Exception:
                        pass

                try:
                    poll_resp = requests.get(RESULTS_POLL_URL, params={"ugc_id": ugc_id}, timeout=10)
                    poll_data = poll_resp.json()
                except Exception:
                    poll_data = {"status": "processing"}

                if poll_data.get("status") == "done":
                    meta       = st.session_state.pending_comp_meta
                    raw_images = poll_data.get("images", [])
                    images     = [
                        {**img, "filename": build_competitor_filename(
                            brand_name     = meta.get("brand_name", ""),
                            product_name   = meta.get("product_name", ""),
                            competitor_url = meta.get("competitor_url", ""),
                            variant_index  = img.get("index", i),
                        )}
                        for i, img in enumerate(raw_images)
                    ]
                    save_to_history(
                        ugc_id       = poll_data.get("ugc_id", ugc_id),
                        product_id   = meta.get("product_id", ""),
                        product_name = meta.get("product_name", ""),
                        brand_name   = meta.get("brand_name", ""),
                        variants_qty = len(images),
                        images       = images,
                        mode         = "competitor_reverse",
                    )
                    st.session_state["last_comp_results"]          = images
                    st.session_state["last_comp_results_brand_id"] = meta.get("brand_id")
                    st.session_state.pending_comp_ugc_id           = None
                    st.session_state.pending_comp_meta             = {}
                    st.session_state.generating                    = False
                    st.session_state.comp_job_submitted            = False
                    st.session_state.comp_poll_count               = 0
                    inject_generation_guard(False)
                    st.rerun()
                else:
                    st.session_state.comp_poll_count += 1
                    time.sleep(8)
                    st.rerun()

            elif st.session_state.get("last_comp_results"):
                # ── RESULTS ──────────────────────────────────────────────
                images   = st.session_state["last_comp_results"]
                brand_id = st.session_state.get("last_comp_results_brand_id")
                st.markdown(
                    f'<p style="font-size:12px;color:#3fb950;font-weight:600;margin-bottom:10px">'
                    f'✅ {len(images)} variant{"s" if len(images) != 1 else ""}</p>',
                    unsafe_allow_html=True,
                )
                cr_grid_cols = st.columns(2, gap="small")
                for i, img in enumerate(images):
                    url      = img.get("image_url", "")
                    filename = img.get("filename", build_competitor_filename("", "", "", i))
                    with cr_grid_cols[i % 2]:
                        if url:
                            render_ad_image(url, f"cr_{i}")
                        st.markdown(
                            f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                            f'color:#484f58;margin:2px 0 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{filename}</p>',
                            unsafe_allow_html=True,
                        )
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("💾", key=f"cr_save_{i}", use_container_width=True, help="Save"):
                                save_ad_image(brand_id, url, filename)
                                st.success("Saved!")
                        with b2:
                            if url:
                                get_download_button(url, filename, label="⬇️", key_suffix=f"cr_{i}")
            else:
                st.markdown(
                    '<div class="kie-img-placeholder">🎨 Generated ads will appear here</div>',
                    unsafe_allow_html=True,
                )

        # Left col — inputs
        with cl_col:
            st.markdown('<span class="sec-label">Input</span>', unsafe_allow_html=True)
            st.markdown('<span class="sec-label" style="color:#7d8590">🎯 Your product</span>', unsafe_allow_html=True)
            comp_brand = st.selectbox(
                "Brand ", brands,
                format_func=lambda b: b["name"],
                label_visibility="collapsed",
                key="comp_brand",
            )
            comp_products = get_products(comp_brand["id"])
            if comp_products:
                comp_product = st.selectbox(
                    "Product ", comp_products,
                    format_func=lambda p: p["name"],
                    label_visibility="collapsed",
                    key="comp_product_sel",
                )
                if comp_product:
                    img_url_c = convert_gdrive_url((comp_product.get("image_url") or "").strip())
                    bens      = parse_benefits(comp_product.get("key_benefits", ""), max_items=2)
                    pills_c   = "".join(f'<span class="kie-pill">{b}</span>' for b in bens)
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;background:#161b22;'
                        f'border:1px solid #21262d;border-radius:8px;padding:8px 12px;margin:6px 0 10px">'
                        + render_product_image(img_url_c, size=46)
                        + f'<div style="flex:1;min-width:0">'
                        f'<div style="font-size:12px;font-weight:600;color:#e6edf3;margin-bottom:3px">'
                        f'{comp_product["name"]}</div>'
                        f'<div>{pills_c}</div></div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No products for this brand.")
                comp_product = None

            st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)
            st.markdown('<span class="sec-label" style="color:#7d8590">🕵️ Competitor creative</span>', unsafe_allow_html=True)
            competitor_url = st.text_input(
                "Competitor ad URL",
                placeholder="Paste URL of competitor ad screenshot...",
                key="comp_img_url",
                label_visibility="collapsed",
            )
            st.markdown(
                '<div style="font-size:10px;color:#484f58;margin-top:4px">'
                '💡 Use <strong>Imgur</strong> or <strong>Google Drive</strong> public links. '
                'Facebook/Instagram CDN links are not supported.</div>',
                unsafe_allow_html=True,
            )
            if competitor_url:
                is_private, platform = is_private_cdn_url(competitor_url)
                if is_private:
                    st.markdown(f"""
                    <div style="background:#1a0e00;border:1px solid #3d2200;border-radius:8px;
                                padding:12px 14px;margin:8px 0">
                        <div style="font-size:12px;font-weight:600;color:#f97316;margin-bottom:4px">
                            ⚠️ {platform} CDN URL — Not supported
                        </div>
                        <div style="font-size:11px;color:#7d6050;line-height:1.5">
                            This URL is session-authenticated and expires.
                            No external service can access it.<br><br>
                            <strong style="color:#d97706">How to fix:</strong><br>
                            1. Save the ad screenshot to your device<br>
                            2. Upload it to <a href="https://imgur.com/upload" target="_blank"
                               style="color:#f97316">Imgur</a> or
                               <a href="https://drive.google.com" target="_blank"
                               style="color:#f97316">Google Drive</a><br>
                            3. Paste the public image URL here
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    comp_url_valid = False
                else:
                    comp_url_valid = competitor_url.startswith("http")
            else:
                comp_url_valid = False

            competitor_notes = st.text_area(
                "Notes (optional)",
                placeholder="e.g. This ad is crushing it on Meta, copy the urgency hook",
                height=64, key="comp_notes",
            )
            st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)

            v_col2, _ = st.columns([3, 2])
            with v_col2:
                comp_variations = st.slider("Number of variants ", 1, 5, 2, key="comp_variations")

            cr_missing_logo = not (comp_brand.get("logo_url") or "").strip()
            cr_missing_img  = not (comp_product or {}).get("image_url", "").strip() if comp_product else True

            if not competitor_url:
                st.info("💡 Paste a competitor ad URL above")
            elif not comp_url_valid and not is_private_cdn_url(competitor_url)[0]:
                st.warning("⚠️ URL must start with http")
            if cr_missing_img and comp_product:
                st.warning("⚠️ Product has no image URL — edit in Products")
            if cr_missing_logo:
                st.warning("⚠️ Brand has no logo URL — edit in Brands")

            is_polling_cr = bool(st.session_state.pending_comp_ugc_id)
            comp_btn = st.button(
                f"🔍  Analyse & Generate  ·  {comp_variations} variant{'s' if comp_variations > 1 else ''}",
                disabled=(cr_missing_logo or cr_missing_img or not comp_url_valid or is_polling_cr or st.session_state.comp_job_submitted),
                use_container_width=True,
                type="primary",
                key="comp_btn",
            )

        # Fire-and-poll: queue job, rerun immediately to show loading, fire POST on next render
        if comp_btn and not st.session_state.comp_job_submitted:
            st.session_state.comp_job_submitted = True
            ugc_id = f"ugc_{int(time.time())}"
            st.session_state.deferred_comp = {
                "url": st.session_state.get("competitor_webhook_url", COMPETITOR_WEBHOOK_URL),
                "payload": {
                    "ugc_id":               ugc_id,
                    "name":                 comp_product["name"],
                    "persona":              comp_product.get("target_audience") or "",
                    "key_benefits":         comp_product.get("key_benefits") or "",
                    "offer":                comp_product.get("offer_promotion") or "",
                    "variants_qty":         int(comp_variations),
                    "asset_url":            comp_product["image_url"],
                    "logo_url":             comp_brand["logo_url"],
                    "brand_id":             comp_brand["id"],
                    "competitor_image_url": competitor_url,
                    "competitor_notes":     competitor_notes or "",
                },
            }
            st.session_state.generating          = True
            st.session_state.pending_comp_ugc_id = ugc_id
            st.session_state.pending_comp_meta   = {
                "brand_id":      comp_brand["id"],
                "product_id":    comp_product["id"],
                "product_name":  comp_product["name"],
                "brand_name":    comp_brand["name"],
                "competitor_url": competitor_url,
            }
            st.session_state.pop("last_comp_results", None)
            inject_generation_guard(True)
            st.rerun()

    # ── MANUAL PROMPT ─────────────────────────────────────────────────────────
    with mode_tab3:
        render_manual_prompt_tab(brands)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CAMPAIGN ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Campaign Analytics":
    page_header("Campaign Analytics", "Performance overview of your Meta ad campaigns.")

    df = analytics_dataframe()

    if df.empty:
        st.info("No ad data yet. Generate and save some ads to see analytics.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            brand_filter = st.selectbox("Filter by Brand", ["All Brands"] + df["brand"].dropna().unique().tolist())
        with col_f2:
            date_range = st.date_input("Date Range", value=(df["date"].min(), df["date"].max()), key="analytics_date")

        if brand_filter != "All Brands":
            df = df[df["brand"] == brand_filter]
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]

        total_imp   = df["impressions"].sum()
        total_clk   = df["clicks"].sum()
        total_conv  = df["conversions"].sum()
        total_spend = df["spend"].sum()
        avg_ctr     = total_clk / max(total_imp, 1) * 100
        avg_roas    = total_conv * 50 / max(total_spend, 1)

        def kpi(col, label, value, delta="", delta_up=True):
            col.markdown(
                f"""<div class="card">
                    <div class="card-title">{label}</div>
                    <div class="card-value">{value}</div>
                    <div class="card-delta {'delta-up' if delta_up else 'delta-down'}">{delta}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        kpi(k1, "Impressions",  f"{total_imp:,.0f}",    "↑ +12% vs last period")
        kpi(k2, "Clicks",       f"{total_clk:,.0f}",    "↑ +8%")
        kpi(k3, "Conversions",  f"{total_conv:,.0f}",   "↑ +18%")
        kpi(k4, "Spend",        f"${total_spend:,.2f}", "↓ -3%", delta_up=False)
        kpi(k5, "Avg CTR",      f"{avg_ctr:.2f}%",      "↑ +0.4pp")
        kpi(k6, "ROAS",         f"{avg_roas:.1f}x",     "↑ +0.3x")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Impressions over time**")
            daily = df.groupby("date")[["impressions", "clicks"]].sum().reset_index()
            daily["date"] = pd.to_datetime(daily["date"])
            chart = alt.Chart(daily).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color="#1f6feb", offset=0),
                           alt.GradientStop(color="#1f6feb22", offset=1)],
                    x1=1, x2=1, y1=1, y2=0,
                ),
                line={"color": "#388bfd"}, opacity=0.8,
            ).encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("impressions:Q", title="Impressions"),
                tooltip=["date:T", "impressions:Q", "clicks:Q"],
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)

        with c2:
            st.markdown("**CTR by Ad**")
            ctr_data = df[["impressions", "clicks", "ctr"]].copy().reset_index(drop=True)
            ctr_data["ad"] = [f"Ad #{i+1}" for i in range(len(ctr_data))]
            bar = alt.Chart(ctr_data).mark_bar(
                color="#388bfd", cornerRadiusTopLeft=4, cornerRadiusTopRight=4,
            ).encode(
                x=alt.X("ad:N", sort="-y", title="Ad"),
                y=alt.Y("ctr:Q", title="CTR (%)"),
                tooltip=["ad:N", "ctr:Q", "clicks:Q"],
            ).properties(height=250)
            st.altair_chart(bar, use_container_width=True)

        st.markdown("---")
        st.markdown("**Top Performing Ads**")
        tbl = df[["brand", "impressions", "clicks", "conversions", "spend", "ctr", "roas"]].copy()
        tbl.columns = ["Brand", "Impressions", "Clicks", "Conversions", "Spend ($)", "CTR (%)", "ROAS (x)"]
        st.dataframe(tbl.sort_values("ROAS (x)", ascending=False).head(10), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — SAVED ADS LIBRARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Saved Ads Library":
    page_header("Saved Ads Library", "Browse all ad creatives you've saved locally.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lib_brand_filter = st.selectbox("Brand", ["All Brands"] + brand_names, key="lib_brand")
    with col_f2:
        lib_mode_filter = st.selectbox("Mode", ["All Modes", "ugc-generated", "data-driven", "competitor-reverse"], key="lib_mode")

    filter_id = None
    if lib_brand_filter != "All Brands":
        filter_id = brand_ids[brand_names.index(lib_brand_filter)]

    ads = get_saved_ads(brand_id=filter_id)
    if lib_mode_filter != "All Modes":
        ads = [a for a in ads if a["mode"] == lib_mode_filter]

    if not ads:
        st.info("No saved ads yet. Generate some ads and click 💾 Save.")
    else:
        st.caption(f"{len(ads)} ad(s) found")
        st.markdown(IMAGE_GRID_CSS, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, ad in enumerate(ads):
            with cols[i % 3]:
                image_url = ad["image_url"] or ""
                filename  = ad["headline"] or f"ad_{ad['id']}"
                if image_url:
                    render_ad_image(image_url, f"analytics_{i}")
                    st.markdown(f'<div style="margin:6px 0 10px;padding:6px 8px;background:#161b22;border:1px solid #30363d;border-radius:6px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#8b949e;word-break:break-all;line-height:1.4">{filename}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="img-placeholder">📸 Creative<br>'
                        f'<span style="font-size:11px;opacity:.6">Saved {ad["created_at"][:10]}</span></div>',
                        unsafe_allow_html=True,
                    )
                _body_html = f"<div class='ad-body'>{ad['body']}</div>" if ad["body"] else ""
                st.markdown(
                    f'<div class="ad-preview">'
                    f'<span class="platform-badge">{ad["platform"]}</span>'
                    f'{_body_html}'
                    f'<div style="font-size:12px;color:#8b949e">'
                    f'{ad["impressions"]:,} imp &nbsp;·&nbsp;'
                    f'{ad["clicks"]:,} clicks &nbsp;·&nbsp;'
                    f'{ad["conversions"]:,} conv'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                if image_url:
                    get_download_button(image_url, filename, key_suffix=f"lib_{i}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 History":
    h_col1, h_col2 = st.columns([6, 1])
    with h_col1:
        page_header("Generation History", "All past ad generation jobs and their results.")
    with h_col2:
        st.markdown("<div style='margin-top:20px'>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All", type="secondary"):
            clear_history()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    history = get_history()

    if not history:
        st.info("No generation history yet. Generate some ads first!")
    else:
        for entry in history:
            images = json.loads(entry["images_json"]) if entry["images_json"] else []
            ts     = str(entry["created_at"])[:16]
            mode   = entry.get("mode", "data_driven")
            if mode == "competitor_reverse":
                badge = '<span style="background:#3a1a1a;color:#e85d4a;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px">🕵️ Competitor Reverse</span>'
            else:
                badge = '<span style="background:#1a2233;color:#58a6ff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px">🎯 Data-Driven</span>'

            with st.container():
                thumbs_html = ""
                if images:
                    thumb_imgs = "".join([
                        f'<img src="https://images.weserv.nl/?url={urllib.parse.quote(img.get("image_url",""),safe="")}&w=80&h=80&fit=cover&output=jpg"'
                        f' style="width:52px;height:52px;border-radius:6px;object-fit:cover;background:#1f2937"'
                        f' onerror="this.style.display=\'none\'">'
                        for img in images[:4]
                    ])
                    extra = f'<div style="width:52px;height:52px;border-radius:6px;background:#1f2937;display:flex;align-items:center;justify-content:center;font-size:11px;color:#484f58">+{len(images)-4}</div>' if len(images) > 4 else ""
                    thumbs_html = (
                        f'<div style="display:flex;gap:6px;margin-top:8px;padding-top:8px;border-top:1px solid #21262d">'
                        f'{thumb_imgs}{extra}</div>'
                    )
                st.markdown(
                    f"""<div class="history-card">
                        <div style="font-size:15px;font-weight:700;color:#e6edf3">{entry["product_name"]}{badge}</div>
                        <div class="history-meta">
                            Brand: {entry["brand_name"] or "—"} &nbsp;·&nbsp;
                            {entry["variants_qty"]} image(s) &nbsp;·&nbsp;
                            {ts} &nbsp;·&nbsp;
                            <span style="font-family:monospace;color:#58a6ff">{entry["ugc_id"]}</span>
                        </div>
                        {thumbs_html}
                    </div>""",
                    unsafe_allow_html=True,
                )
                if images:
                    with st.expander(f"View {len(images)} image(s)"):
                        st.markdown(IMAGE_GRID_CSS, unsafe_allow_html=True)
                        cols = st.columns(3)
                        for i, img in enumerate(images):
                            url      = img.get("image_url", "")
                            filename = img.get("filename", build_filename(
                                "", "",
                                CREATIVE_ANGLES[img.get("index", i) % len(CREATIVE_ANGLES)],
                                img.get("index", i),
                            ))
                            with cols[i % 3]:
                                if url:
                                    render_ad_image(url, f"hist_{entry['id']}_{i}")
                                    st.markdown(f'<div style="margin:6px 0 10px;padding:6px 8px;background:#161b22;border:1px solid #30363d;border-radius:6px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#8b949e;word-break:break-all;line-height:1.4">{filename}</div>', unsafe_allow_html=True)
                                    get_download_button(url, filename, key_suffix=f"hist_{entry['id']}_{i}")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — BRANDS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Brands":
    page_header("Brand Profiles", "Manage brand identities used across all ad generations.")

    with st.expander("Add New Brand", expanded=not bool(brands)):
        with st.form("add_brand"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                f_name  = st.text_input("Brand Name*", placeholder="e.g. Nike")
                f_logo  = st.text_input("Logo URL",    placeholder="https://…/logo.png")
                f_tone  = st.selectbox("Brand Tone", TONE_OPTIONS)
            with f_col2:
                f_primary   = st.color_picker("Primary Color",   "#1f6feb")
                f_secondary = st.color_picker("Secondary Color", "#388bfd")
            if st.form_submit_button("Save Brand", type="primary"):
                if not f_name:
                    st.error("Brand name is required.")
                else:
                    save_brand(f_name, f_logo, f_primary, f_secondary, f_tone)
                    st.success(f"Brand '{f_name}' saved!")
                    st.rerun()

    st.markdown("---")
    st.markdown(f"**{len(brands)} Brand(s)**")
    for b in brands:
        col_info, col_edit, col_del = st.columns([8, 1, 1])
        with col_info:
            st.markdown(render_brand_card(b), unsafe_allow_html=True)
        with col_edit:
            st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
            if st.button("✏️", key=f"edit_btn_{b['id']}", help="Edit brand"):
                st.session_state[f"editing_{b['id']}"] = not st.session_state.get(f"editing_{b['id']}", False)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with col_del:
            st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
            if st.button("🗑", key=f"del_brand_{b['id']}", help="Delete brand"):
                delete_brand(b["id"])
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get(f"editing_{b['id']}", False):
            with st.form(key=f"edit_form_{b['id']}"):
                st.markdown(f"**Editing: {b['name']}**")
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    new_name     = st.text_input("Brand Name",     value=b["name"] or "")
                    new_tagline  = st.text_input("Tagline",        value=b["tagline"] or "")
                    new_logo     = st.text_input("Logo URL",       value=b["logo_url"] or "")
                    new_tone     = st.selectbox("Brand Tone", TONE_OPTIONS,
                                                index=TONE_OPTIONS.index(b["tone"]) if b["tone"] in TONE_OPTIONS else 0)
                with e_col2:
                    new_primary   = st.color_picker("Primary Color",   b["primary_color"]   or "#1f6feb")
                    new_secondary = st.color_picker("Secondary Color", b["secondary_color"] or "#388bfd")
                    new_tov       = st.text_input("Tone of Voice",   value=b["tone_of_voice"]   or "")
                    new_audience  = st.text_input("Target Audience", value=b["target_audience"] or "")
                new_benefits = st.text_area("Key Benefits", value=b["key_benefits"] or "")
                save_col, cancel_col = st.columns(2)
                with save_col:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary")
                with cancel_col:
                    cancelled = st.form_submit_button("✕ Cancel")
                if submitted:
                    update_brand(b["id"], new_name, new_logo, new_primary, new_secondary,
                                 new_tone, new_tagline, new_tov, new_audience, new_benefits)
                    st.session_state[f"editing_{b['id']}"] = False
                    st.rerun()
                if cancelled:
                    st.session_state[f"editing_{b['id']}"] = False
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Products":
    page_header("Products", "Manage product profiles used in ad generation.")

    # ── Add new product form ──────────────────────────────────────────────────
    all_products = get_products()
    with st.expander("➕ Add New Product", expanded=not bool(all_products)):
        with st.form("add_product"):
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p_brand_name   = st.selectbox("Brand*", brand_names, key="p_brand_sel")
                p_brand        = brands[brand_names.index(p_brand_name)]
                p_name         = st.text_input("Product Name*", placeholder="e.g. ProFlow Water Bottle")
                p_description  = st.text_area("Description", placeholder="Short product description", height=70)
                p_image_url_raw = st.text_input("Product Image URL", placeholder="https://… or Google Drive link")
            with p_col2:
                p_benefits      = st.text_area("Key Benefits (comma-separated)", placeholder="e.g. BPA-free, 24h cold", height=70)
                p_audience      = st.text_input("Target Audience", placeholder="e.g. Fitness enthusiasts, 25-40")
                p_offer         = st.text_input("Offer / Promotion", placeholder="e.g. 20% off, Free shipping")

            if p_image_url_raw:
                p_image_url = convert_gdrive_url(p_image_url_raw)
                if p_image_url != p_image_url_raw:
                    st.caption(f"Google Drive URL converted: `{p_image_url}`")
                try:
                    render_ad_image(p_image_url, "product_preview", width=100)
                    st.caption("Preview")
                except Exception:
                    pass
            else:
                p_image_url = ""

            if st.form_submit_button("➕ Add Product", type="primary"):
                if not p_name:
                    st.error("Product name is required.")
                else:
                    save_product(p_brand["id"], p_name, p_description, p_image_url,
                                 p_benefits, p_audience, p_offer)
                    st.success(f"Product '{p_name}' added!")
                    st.rerun()

    st.markdown("---")

    # ── Product list grouped by brand ─────────────────────────────────────────
    if not all_products:
        st.info("No products yet. Add one above.")
    else:
        st.markdown(f"**{len(all_products)} product(s)**")
        # Group by brand
        brand_map = {str(b["id"]): b["name"] for b in brands}
        grouped: dict[str, list] = {}
        for p in all_products:
            bname = brand_map.get(str(p["brand_id"]), "Unknown Brand")
            grouped.setdefault(bname, []).append(p)

        for bname, prods in grouped.items():
            st.markdown(f'<p style="font-size:11px;font-weight:700;color:#484f58;text-transform:uppercase;letter-spacing:0.8px;margin:16px 0 6px">{bname}</p>', unsafe_allow_html=True)
            for p in prods:
                card_col, btn_col = st.columns([8, 1])
                with card_col:
                    st.markdown(render_product_card(p, bname), unsafe_allow_html=True)
                with btn_col:
                    st.markdown("<div style='margin-top:14px;display:flex;gap:4px'>", unsafe_allow_html=True)
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("✏️", key=f"edit_prod_{p['id']}", help="Edit"):
                            st.session_state[f"editing_prod_{p['id']}"] = not st.session_state.get(f"editing_prod_{p['id']}", False)
                            st.rerun()
                    with bc2:
                        if st.button("🗑", key=f"del_prod_{p['id']}", help="Delete"):
                            delete_product(p["id"])
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # Inline edit form
                if st.session_state.get(f"editing_prod_{p['id']}", False):
                    with st.form(key=f"edit_prod_form_{p['id']}"):
                        st.markdown(f"**Editing: {p['name']}**")
                        ep1, ep2 = st.columns(2)
                        with ep1:
                            ep_name        = st.text_input("Product Name",   value=p["name"] or "")
                            ep_description = st.text_area("Description",     value=p["description"] or "", height=70)
                            ep_image_raw   = st.text_input("Product Image URL", value=p["image_url"] or "")
                        with ep2:
                            ep_benefits = st.text_area("Key Benefits", value=p["key_benefits"]    or "", height=70)
                            ep_audience = st.text_input("Target Audience",   value=p["target_audience"]  or "")
                            ep_offer    = st.text_input("Offer / Promotion", value=p["offer_promotion"]  or "")
                        ep_image = convert_gdrive_url(ep_image_raw) if ep_image_raw else ""
                        if ep_image and ep_image != ep_image_raw:
                            st.caption(f"Google Drive URL converted: `{ep_image}`")

                        save_c, cancel_c = st.columns(2)
                        with save_c:
                            ep_submitted = st.form_submit_button("💾 Save Changes", type="primary")
                        with cancel_c:
                            ep_cancelled = st.form_submit_button("✕ Cancel")
                        if ep_submitted:
                            update_product(p["id"], ep_name, ep_description, ep_image,
                                           ep_benefits, ep_audience, ep_offer)
                            st.session_state[f"editing_prod_{p['id']}"] = False
                            st.rerun()
                        if ep_cancelled:
                            st.session_state[f"editing_prod_{p['id']}"] = False
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Settings":
    page_header("Settings", "Configure webhook URLs and generation defaults.")

    s1, s2 = st.columns(2)

    with s1:
        st.markdown('<p style="font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 8px">API Keys</p>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Anthropic API Key", type="password",
            value=st.session_state.get("api_key", ""), placeholder="sk-ant-…",
        )
        if st.button("Save API Key"):
            st.session_state["api_key"] = api_key
            st.success("API key saved for this session.")

        st.markdown("---")
        st.markdown('<p style="font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 8px">n8n Webhooks</p>', unsafe_allow_html=True)
        webhook = st.text_input(
            "Data-Driven Webhook URL",
            value=st.session_state.get("webhook_url", WEBHOOK_URL),
            placeholder="https://….app.n8n.cloud/webhook/…",
        )
        if st.button("Save Data-Driven URL"):
            st.session_state["webhook_url"] = webhook
            st.success("Data-Driven webhook URL updated.")

        manual_webhook = st.text_input(
            "Manual Prompt Webhook URL",
            value=st.session_state.get("manual_webhook_url", MANUAL_WEBHOOK_URL),
            placeholder="https://….app.n8n.cloud/webhook/manual-prompt-v1",
        )
        if st.button("Save Manual Prompt URL"):
            st.session_state["manual_webhook_url"] = manual_webhook
            st.success("Manual Prompt webhook URL updated.")

        comp_webhook = st.text_input(
            "Competitor Reverse Webhook URL",
            value=st.session_state.get("competitor_webhook_url", COMPETITOR_WEBHOOK_URL),
            placeholder="https://….app.n8n.cloud/webhook/competitor-reverse-v1",
        )
        if st.button("Save Competitor Reverse URL"):
            st.session_state["competitor_webhook_url"] = comp_webhook
            st.success("Competitor Reverse webhook URL updated.")

        st.markdown("---")
        st.markdown('<p style="font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 8px">Test Webhooks</p>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("Ping Data-Driven"):
                ok, msg, _ = send_to_webhook({"test": True, "timestamp": datetime.now().isoformat()})
                st.success(f"✓ {msg}") if ok else st.warning(f"⚠ {msg}")
        with tc2:
            if st.button("Ping Competitor Reverse"):
                ok, msg, _ = send_to_competitor_webhook({"test": True, "timestamp": datetime.now().isoformat()})
                st.success(f"✓ {msg}") if ok else st.warning(f"⚠ {msg}")

    with s2:
        st.markdown('<p style="font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 8px">Generation Defaults</p>', unsafe_allow_html=True)
        st.selectbox("Default Tone", TONE_OPTIONS, key="default_tone_setting")
        st.selectbox("Default Platform", ["Meta (Facebook/Instagram)"], key="default_platform_setting")

        st.markdown("---")
        st.markdown('<p style="font-size:13px;font-weight:600;color:#e6edf3;margin:0 0 8px">Database</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:11px;color:#484f58;margin:0 0 10px;font-family:monospace">Supabase (cloud)</p>', unsafe_allow_html=True)
        try:
            sb = get_sb()
            n_brands  = len((sb.table("brands").select("id").execute().data or []))
            n_prods   = len((sb.table("products").select("id").execute().data or []))
            n_ads     = len((sb.table("saved_ads").select("id").execute().data or []))
            n_history = len((sb.table("generation_history").select("id").execute().data or []))
        except Exception:
            n_brands = n_prods = n_ads = n_history = "?"
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:4px 0 12px">
            {''.join([
                f'<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px 14px;text-align:center">'
                f'<div style="font-size:20px;font-weight:700;color:#e6edf3">{v}</div>'
                f'<div style="font-size:10px;color:#484f58;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px">{k}</div>'
                f'</div>'
                for k, v in [("Brands", n_brands), ("Products", n_prods), ("Saved Ads", n_ads), ("History", n_history)]
            ])}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Clear All Saved Ads", type="secondary"):
            try:
                sb = get_sb()
                sb.table("saved_ads").delete().neq("id", 0).execute()
                st.success("All saved ads deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing saved ads: {e}")

    st.markdown("---")
    st.markdown(
        '<div style="font-size:12px;color:#8b949e">'
        'Ad Generation Studio · n8n + Kie AI · Meta Ads'
        '</div>',
        unsafe_allow_html=True,
    )

