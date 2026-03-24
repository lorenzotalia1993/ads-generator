import streamlit as st
import streamlit.components.v1 as st_components
from supabase import create_client
import json
import requests
import base64
import hashlib
import random
import time
import re
import urllib.parse
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AdFrameLab",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,700;1,300&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════════════
   DESIGN TOKENS  — light mode (default)
   Dark mode overrides live in body.adfl-dark {}
═══════════════════════════════════════════════════════ */
:root {
  /* Page backgrounds */
  --bg:         #F3F4F6;
  --bg-s:       #F3F4F6;
  --bg-e:       #FFFFFF;
  --bg-hover:   #ECEEF0;
  --bg-input:   #FFFFFF;

  /* Card surfaces */
  --card-bg:    #FFFFFF;
  --card-bd:    #E8EAED;
  --card-sh:    0 1px 3px rgba(0,0,0,0.06);

  /* Sidebar */
  --side-bg:         #FAFAFA;
  --side-border:     #EAEAEA;
  --side-text:       #6B7280;
  --side-text-h:     #111827;
  --side-active-bg:  #EEF2FF;
  --side-active-tx:  #1D4ED8;
  --side-hover-bg:   #ECEEF0;

  /* Accent */
  --p:    #C8F060;
  --p2:   #D4F570;

  /* Status */
  --green: #22C55E;
  --rose:  #EF4444;
  --amber: #F59E0B;
  --blue:  #3B82F6;

  /* Text hierarchy */
  --tx:   #111827;
  --tx2:  #6B7280;
  --tx3:  #9CA3AF;

  /* Borders */
  --bd:   #E5E7EB;
  --bd-h: #D1D5DB;

  /* Radii */
  --r:    12px;
  --r-sm: 8px;
}

/* ── Dark mode token overrides ── */
body.adfl-dark {
  --bg:         #0F172A;
  --bg-s:       #0F172A;
  --bg-e:       #1E293B;
  --bg-hover:   #334155;
  --bg-input:   #1E293B;
  --card-bg:    #1E293B;
  --card-bd:    #334155;
  --card-sh:    0 1px 4px rgba(0,0,0,0.4);
  --side-bg:         #111827;
  --side-border:     #1F2937;
  --side-text:       #94A3B8;
  --side-text-h:     #F1F5F9;
  --side-active-bg:  rgba(99,102,241,0.18);
  --side-active-tx:  #A5B4FC;
  --side-hover-bg:   #1F2937;
  --tx:   #F1F5F9;
  --tx2:  #94A3B8;
  --tx3:  #64748B;
  --bd:   #334155;
  --bd-h: #475569;
}

/* ─── Base ─────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, sans-serif !important;
  letter-spacing: -0.01em;
}
.stApp { background: var(--bg) !important; }
.main .block-container {
  padding: 0.75rem 2rem 2rem !important;
  max-width: 1440px !important;
  background: var(--bg) !important;
}

/* Hide chrome */
#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stHeader"],
[data-testid="stAppViewBlockContainer"] > [data-testid="stHeader"],
header[data-testid="stHeader"] { display: none !important; }
.page-header h1 a, h1 a, h2 a, h3 a,
[data-testid="stMarkdownContainer"] h1 a { display: none !important; }
/* Hide hamburger menu; keep only the «/» collapse arrows */
button[kind="header"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ─── Remove all top dead space from Streamlit shell ── */
.stApp > header,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
/* Kill every top padding/margin Streamlit adds above the content */
.stApp [data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stAppViewContainer"] > section.main,
[data-testid="stAppViewContainer"] > [data-testid="stMain"] { padding-top: 0 !important; }
.main > div:first-child { padding-top: 0 !important; }
.main .block-container,
[data-testid="stMainBlockContainer"] { padding-top: 0.75rem !important; margin-top: 0 !important; }
/* Streamlit 1.5x adds a gap via stVerticalBlockBorderWrapper at root level */
[data-testid="stVerticalBlockBorderWrapper"]:first-child { padding-top: 0 !important; margin-top: 0 !important; }

/* ─── Typography ───────────────────────────────────── */
h1 {
  font-family: 'Fraunces', serif !important;
  font-size: 22px !important; font-weight: 700 !important;
  color: var(--tx) !important; margin: 0 0 4px !important;
  letter-spacing: -0.02em !important;
}
h2 {
  font-family: 'Fraunces', serif !important;
  font-size: 15px !important; font-weight: 600 !important;
  color: var(--tx) !important; letter-spacing: -0.02em !important;
}
h3 { font-size: 12px !important; font-weight: 500 !important; color: var(--tx2) !important; }

[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] strong { color: var(--tx) !important; }

/* ─── Page header ──────────────────────────────────── */
.page-header {
  margin-bottom: 32px; padding-bottom: 20px;
  border-bottom: 1px solid var(--bd); position: relative;
}
.page-header::after {
  content: ''; position: absolute; bottom: -1px; left: 0;
  width: 40px; height: 3px; background: var(--p); border-radius: 2px;
}
.page-header h1 {
  font-family: 'Fraunces', serif !important;
  font-size: 28px !important; font-weight: 700 !important;
  color: var(--tx) !important; margin: 0 0 6px !important;
  letter-spacing: -0.02em !important;
}
.page-header p { font-size: 14px; color: var(--tx2); margin: 0; }
.sec-label {
  font-family: 'DM Mono', monospace !important;
  font-size: 10px !important; font-weight: 500 !important;
  text-transform: uppercase !important; letter-spacing: 0.1em !important;
  color: var(--tx3) !important; margin-bottom: 8px !important; display: block;
}

/* ─── Sidebar shell ────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--side-bg) !important;
  border-right: 1px solid var(--side-border) !important;
  color: var(--side-text) !important;
}
[data-testid="stSidebar"] * { color: inherit; text-align: left !important; }

/* Strip ALL Streamlit default spacing from sidebar — every layer */
[data-testid="stSidebar"] .stVerticalBlock,
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  gap: 0 !important; padding: 0 !important;
  align-items: stretch !important; width: 100% !important;
}
[data-testid="stSidebar"] .element-container {
  margin: 0 !important; padding: 0 !important; min-height: 0 !important; width: 100% !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown > div { margin: 0 !important; padding: 0 !important; width: 100% !important; }
[data-testid="stSidebar"] .block-container { padding: 0 !important; width: 100% !important; }
/* Zero lateral padding on outer wrapper divs (do NOT make them flex) */
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"] section {
  padding-left: 0 !important; padding-right: 0 !important;
}
/* Make ONLY the content wrapper a flex column so footer is pushed to bottom */
[data-testid="stSidebarContent"] {
  display: flex !important; flex-direction: column !important;
  height: 100% !important; overflow-y: auto !important;
  padding-left: 0 !important; padding-right: 0 !important;
  justify-content: flex-start !important; align-items: stretch !important;
}
.sb-flex-spacer { flex: 1 1 auto; min-height: 32px; display: block; }
/* Ensure the spacer's Streamlit wrapper also expands */
[data-testid="stSidebar"] .element-container:has(.sb-flex-spacer) { flex: 1 1 auto !important; min-height: 32px !important; }

/* ─── Sidebar nav — buttons ────────────────────────── */
[data-testid="stSidebar"] .element-container,
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] .stButton > div,
[data-testid="stSidebar"] .stButton > div > div {
  margin: 0 !important; padding: 0 !important; width: 100% !important;
}
[data-testid="stSidebar"] .stButton button {
  display: flex !important;
  text-align: left !important; justify-content: flex-start !important; align-items: center !important;
  border: none !important; border-radius: 6px !important;
  font-size: 12.5px !important; font-weight: 400 !important;
  height: 34px !important; padding: 0 12px !important;
  width: 100% !important; box-shadow: none !important;
  transform: none !important; letter-spacing: 0 !important;
  font-family: 'Inter', sans-serif !important; transition: background 0.1s, color 0.1s !important;
  line-height: 1 !important;
}
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span {
  font-size: 12.5px !important; line-height: 1 !important;
}
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
  background: transparent !important; color: var(--side-text) !important;
}
[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
  background: var(--side-hover-bg) !important; color: var(--side-text-h) !important;
  transform: none !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"] {
  background: var(--side-active-bg) !important; color: var(--side-active-tx) !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
  background: var(--side-active-bg) !important; opacity: 0.9 !important;
  transform: none !important; filter: none !important;
}

/* ─── Sidebar HTML nav links ───────────────────────── */
[data-testid="stSidebar"] a.sb-nav-link {
  display: flex !important; align-items: center !important;
  width: 100% !important; box-sizing: border-box !important;
  padding: 0 12px !important; height: 34px !important;
  border-radius: 6px !important; text-decoration: none !important;
  font-size: 12.5px !important; font-family: 'Inter', sans-serif !important;
  letter-spacing: 0 !important; line-height: 1 !important;
  transition: background 0.1s, color 0.1s !important;
}
[data-testid="stSidebar"] a.sb-nav-link:hover {
  background: var(--side-hover-bg) !important;
  color: var(--side-text-h) !important;
}
[data-testid="stSidebar"] a.sb-nav-active {
  background: var(--side-active-bg) !important;
  color: var(--side-active-tx) !important;
  font-weight: 600 !important;
}

/* ─── Nav labels / divider ─────────────────────────── */
.nav-cat {
  font-family: 'Inter', sans-serif !important; font-size: 9.5px !important;
  font-weight: 700 !important; color: var(--tx2) !important;
  text-transform: uppercase !important; letter-spacing: 0.08em !important;
  padding: 12px 12px 3px !important; display: block !important;
  line-height: 1 !important;
}
/* First nav-cat — tighter top since logo is above */
.sb-logo-wrap + * .nav-cat:first-child { padding-top: 8px !important; }
.nav-divider {
  border: none; height: 1px; background: var(--side-border); margin: 6px 0;
}
.sb-logo-wrap  { border-bottom: 1px solid var(--side-border) !important; margin-bottom: 8px !important; }
.sb-logo-brand { color: var(--side-text-h) !important; font-family:'Inter',sans-serif !important; }
.sb-user-name  { color: var(--side-text-h) !important; }
.sb-user-role  { color: var(--tx3) !important; }
.sb-user-dots  { color: var(--tx3) !important; }

/* ─── Cards ────────────────────────────────────────── */
.kie-card, .card, .history-card, .brand-card,
.product-card, .product-preview, .ad-preview,
.home-quick-card, .home-activity-row, .user-row,
.loading-box {
  background: var(--card-bg); border: 1px solid var(--card-bd);
  border-radius: var(--r);
}
.kie-card         { padding: 18px; }
.kie-card-red     { background: rgba(239,68,68,0.04); border: 1px solid rgba(239,68,68,0.2); border-radius: var(--r); padding: 18px; }
.card             { padding: 18px 22px; margin-bottom: 12px; }
.card-title       { font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 500; color: var(--tx3); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.card-value       { font-family: 'Fraunces', serif; font-size: 34px; font-weight: 700; color: var(--tx); letter-spacing: -0.03em; }
.card-delta       { font-size: 12px; margin-top: 4px; }
.delta-up         { color: var(--green); }
.delta-down       { color: var(--rose); }
.history-card     { padding: 16px 20px; margin-bottom: 8px; }
.history-meta     { font-size: 12px; color: var(--tx2); margin-top: 4px; }
.brand-card       { padding: 14px 18px; margin-bottom: 10px; display: flex; align-items: center; gap: 14px; }
.brand-avatar     { width: 44px; height: 44px; border-radius: 10px; background: var(--bg-hover); border: 1px solid var(--bd); display: flex; align-items: center; justify-content: center; font-size: 18px; color: var(--tx); flex-shrink: 0; }
.brand-info h4    { margin: 0 0 4px; color: var(--tx); font-size: 14px; font-weight: 600; }
.brand-info p     { margin: 0; color: var(--tx2); font-size: 12px; }
.product-card     { padding: 12px 16px; margin-bottom: 8px; border-radius: var(--r-sm); }
.product-preview, .ad-preview { padding: 14px; margin-bottom: 10px; border-radius: var(--r-sm); }
.platform-badge   { display: inline-block; background: var(--bg-hover); color: var(--tx2); font-size: 10px; font-weight: 500; padding: 3px 10px; border-radius: 20px; margin-bottom: 8px; border: 1px solid var(--bd); letter-spacing: 0.3px; font-family: 'DM Mono', monospace; }
.ad-body          { font-size: 13px; color: var(--tx2); margin-bottom: 8px; line-height: 1.6; }
.section-header   { font-family: 'Fraunces', serif; font-size: 24px; font-weight: 700; color: var(--tx); margin-bottom: 4px; letter-spacing: -0.02em; }
.section-sub      { font-size: 13px; color: var(--tx2); margin-bottom: 24px; }
.img-placeholder  { background: var(--bg-s); border: 1px dashed var(--bd-h); border-radius: var(--r-sm); height: 180px; display: flex; align-items: center; justify-content: center; color: var(--tx3); font-size: 13px; text-align: center; }
.loading-box      { padding: 48px 24px; text-align: center; margin: 16px 0; }
.loading-title    { font-family: 'Fraunces', serif; font-size: 20px; font-weight: 700; color: var(--tx); margin-bottom: 8px; letter-spacing: -0.02em; }
.loading-sub      { font-size: 13px; color: var(--tx2); }
.home-quick-card  { padding: 24px; cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s; }
.home-quick-card:hover { border-color: var(--bd-h); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
.home-quick-icon  { width: 44px; height: 44px; background: var(--bg-hover); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-bottom: 14px; }
.home-quick-title { font-family: 'Fraunces', serif; font-size: 15px; font-weight: 700; color: var(--tx); letter-spacing: -0.02em; margin-bottom: 5px; }
.home-quick-sub   { font-size: 12.5px; color: var(--tx2); line-height: 1.5; }
.home-activity-row { display: flex; align-items: center; gap: 12px; padding: 11px 16px; margin-bottom: 6px; transition: border-color 0.12s; }
.home-activity-row:hover { border-color: var(--bd-h); }
.home-activity-dot  { width: 7px; height: 7px; border-radius: 50%; background: var(--p); flex-shrink: 0; }
.home-activity-name { font-size: 13px; color: var(--tx); font-weight: 500; flex: 1; }
.home-activity-meta { font-family: 'DM Mono', monospace; font-size: 10.5px; color: var(--tx3); }
.user-row   { display: flex; align-items: center; gap: 12px; padding: 12px 16px; margin-bottom: 6px; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--p); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: #1A1A1A; flex-shrink: 0; font-family: 'Inter', sans-serif; }
.user-role-badge { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase; font-family: 'DM Mono', monospace; }
.role-admin { background: #1A1A1A; color: #C8F060; }
.role-user  { background: var(--bg-hover); color: var(--tx2); border: 1px solid var(--bd); }

/* ─── Creative card ────────────────────────────────── */
.creative-card  { border-radius: 10px; overflow: hidden; border: 1px solid var(--card-bd); cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; background: var(--card-bg); margin-bottom: 12px; }
.creative-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.creative-thumb { aspect-ratio: 4/5; position: relative; overflow: hidden; }
.creative-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.creative-info  { padding: 10px 12px; background: var(--card-bg); border-top: 1px solid var(--card-bd); }
.creative-title { font-size: 12px; font-weight: 600; color: var(--tx); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
.creative-meta  { display: flex; align-items: center; gap: 6px; }
.creative-plat  { font-family: 'DM Mono', monospace; font-size: 9.5px; color: var(--tx3); background: var(--bg-hover); border: 1px solid var(--bd); padding: 1px 7px; border-radius: 4px; }

/* ─── Image/library card info ──────────────────────── */
.card-info-wrap  { background: var(--card-bg); }
.card-info-title { font-size: 10.5px; font-weight: 600; color: var(--tx); font-family: 'Inter', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-info-date  { font-size: 9px; color: var(--tx3); font-family: 'DM Mono', monospace; margin-top: 1px; }

/* ═══════════════════════════════════════════════════════
   FORM SYSTEM — inputs, selects, labels — both themes
   Placeholder: uses --tx2 (not --tx3) for WCAG compliance
═══════════════════════════════════════════════════════ */

/* ── BaseWeb wrappers: set bg + color at every level ── */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"] {
  background: var(--bg-input) !important;
  color: var(--tx) !important;
  border-color: var(--bd) !important;
}

/* ── Native input / textarea ──────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: var(--bg-input) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r-sm) !important;
  color: var(--tx) !important;
  -webkit-text-fill-color: var(--tx) !important;
  font-size: 13px !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color 0.15s !important;
  caret-color: var(--tx) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--bd-h) !important;
  outline: none !important;
  color: var(--tx) !important;
  -webkit-text-fill-color: var(--tx) !important;
}

/* ── Placeholder: --tx2 = sufficient contrast both themes */
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder {
  color: var(--tx2) !important;
  -webkit-text-fill-color: var(--tx2) !important;
  opacity: 1 !important;
}

/* ── Password toggle icon container ──────────────── */
[data-testid="stTextInput"] [data-baseweb="input"] > div:last-child,
[data-testid="stTextInput"] [data-baseweb="input"] button,
[data-testid="stTextInput"] [data-baseweb="input"] svg {
  background: transparent !important;
  color: var(--tx2) !important;
  fill: var(--tx2) !important;
}

/* ── Autofill override ────────────────────────────── */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-text-fill-color: var(--tx) !important;
  -webkit-box-shadow: 0 0 0 1000px var(--bg-input) inset !important;
  box-shadow: 0 0 0 1000px var(--bg-input) inset !important;
  caret-color: var(--tx) !important;
}

/* ── Disabled / readonly ──────────────────────────── */
[data-testid="stTextInput"] input:disabled,
[data-testid="stTextArea"] textarea:disabled,
[data-testid="stNumberInput"] input:disabled {
  background: var(--bg-hover) !important;
  color: var(--tx2) !important;
  -webkit-text-fill-color: var(--tx2) !important;
  opacity: 1 !important;
}
[data-testid="stTextInput"] input:read-only,
[data-testid="stTextArea"] textarea:read-only {
  background: var(--bg-hover) !important;
  color: var(--tx2) !important;
  -webkit-text-fill-color: var(--tx2) !important;
}

/* ── Form labels ──────────────────────────────────── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label { color: var(--tx) !important; font-size: 13px !important; font-weight: 500 !important; }
/* Checkbox + radio labels — readable in both themes */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label span,
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] p,
[data-testid="stRadio"] label span,
[data-testid="stRadio"] p { color: var(--tx) !important; font-size: 13px !important; }

/* ── Selectbox trigger ────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: var(--bg-input) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r-sm) !important;
  color: var(--tx) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div { color: var(--tx) !important; }
[data-testid="stSelectbox"] > div > div:hover { border-color: var(--bd-h) !important; }

/* ── Selectbox dropdown popup (renders in portal) ─── */
[data-baseweb="popover"],
[data-baseweb="popover"] > div {
  background: var(--bg-input) !important;
  border: 1px solid var(--bd) !important;
  border-radius: var(--r-sm) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important;
}
[data-baseweb="menu"],
[role="listbox"] {
  background: var(--bg-input) !important;
}
[data-baseweb="option"],
[role="option"] {
  background: var(--bg-input) !important;
  color: var(--tx) !important;
  font-size: 13px !important;
  font-family: 'Inter', sans-serif !important;
}
[data-baseweb="option"]:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
  background: var(--bg-hover) !important;
  color: var(--tx) !important;
}

/* ── Dark mode explicit overrides ─────────────────── */
body.adfl-dark [data-testid="stTextInput"] input,
body.adfl-dark [data-testid="stTextArea"] textarea,
body.adfl-dark [data-testid="stNumberInput"] input {
  background: var(--bg-input) !important;
  color: var(--tx) !important;
  -webkit-text-fill-color: var(--tx) !important;
  border-color: var(--bd) !important;
}
body.adfl-dark [data-testid="stTextInput"] input::placeholder,
body.adfl-dark [data-testid="stTextArea"] textarea::placeholder,
body.adfl-dark [data-testid="stNumberInput"] input::placeholder {
  color: var(--tx2) !important;
  -webkit-text-fill-color: var(--tx2) !important;
  opacity: 1 !important;
}
body.adfl-dark [data-testid="stTextInput"] [data-baseweb="input"],
body.adfl-dark [data-testid="stTextInput"] [data-baseweb="base-input"],
body.adfl-dark [data-testid="stTextInput"] [data-baseweb="input"] > div {
  background: var(--bg-input) !important;
  color: var(--tx) !important;
}
body.adfl-dark input:-webkit-autofill,
body.adfl-dark input:-webkit-autofill:hover,
body.adfl-dark input:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--tx) !important;
  -webkit-box-shadow: 0 0 0 1000px var(--bg-input) inset !important;
}
body.adfl-dark [data-baseweb="option"],
body.adfl-dark [role="option"] {
  background: var(--bg-input) !important;
  color: var(--tx) !important;
}
body.adfl-dark [data-baseweb="option"]:hover,
body.adfl-dark [role="option"]:hover {
  background: var(--bg-hover) !important;
}
body.adfl-dark [data-baseweb="popover"],
body.adfl-dark [data-baseweb="popover"] > div,
body.adfl-dark [data-baseweb="menu"],
body.adfl-dark [role="listbox"] {
  background: var(--bg-input) !important;
  border-color: var(--bd) !important;
}
body.adfl-dark [data-testid="stCheckbox"] label,
body.adfl-dark [data-testid="stCheckbox"] label span,
body.adfl-dark [data-testid="stCheckbox"] p,
body.adfl-dark [data-testid="stSelectbox"] [data-baseweb="select"] span,
body.adfl-dark [data-testid="stSelectbox"] [data-baseweb="select"] div { color: var(--tx) !important; }

/* ─── Checkbox — see JS below for runtime overrides ── */
[data-baseweb="checkbox"] > div {
  background-color: #FFFFFF !important;
  border: 2px solid #D1D5DB !important;
  border-radius: 4px !important;
}
[data-baseweb="checkbox"] svg { color: #1A1A1A !important; fill: #1A1A1A !important; }
body.adfl-dark [data-baseweb="checkbox"] > div {
  background-color: #1E293B !important;
  border-color: #475569 !important;
}
body.adfl-dark [data-baseweb="checkbox"] svg { color: #F1F5F9 !important; fill: #F1F5F9 !important; }
[data-testid="stSlider"] [role="slider"] {
  background: var(--tx) !important; box-shadow: 0 0 0 3px rgba(200,240,96,0.25) !important;
}
[data-testid="stExpander"] {
  background: var(--card-bg) !important; border: 1px solid var(--card-bd) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stExpander"] summary { color: var(--tx2) !important; font-size: 12px !important; font-weight: 500 !important; }
[data-testid="stExpander"] summary span { color: var(--tx) !important; font-weight: 500 !important; }

/* ─── Buttons ──────────────────────────────────────── */
[data-testid="stButton"] button[kind="primary"] {
  background: var(--tx) !important; border: none !important;
  border-radius: var(--r-sm) !important; color: var(--bg) !important;
  font-size: 13px !important; font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
  height: 40px !important; letter-spacing: -0.01em !important;
  transition: all 0.15s !important; box-shadow: none !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
  opacity: 0.85 !important; transform: translateY(-1px) !important;
  box-shadow: var(--card-sh) !important;
}
[data-testid="stButton"] button[kind="primary"]:active { transform: translateY(0) !important; }
[data-testid="stButton"] button[kind="secondary"] {
  background: transparent !important; border: 1px solid var(--bd) !important;
  border-radius: var(--r-sm) !important; color: var(--tx2) !important;
  font-size: 12px !important; font-weight: 500 !important; height: 36px !important;
  font-family: 'Inter', sans-serif !important; transition: all 0.12s !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
  border-color: var(--bd-h) !important; color: var(--tx) !important;
  background: var(--bg-hover) !important;
}
[data-testid="stDownloadButton"] button {
  background: var(--card-bg) !important; border: 1px solid var(--bd) !important;
  border-radius: var(--r-sm) !important; color: var(--tx2) !important;
  font-size: 12px !important; height: 36px !important; transition: all 0.12s !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--bd-h) !important; color: var(--tx) !important;
  background: var(--bg-hover) !important;
}
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],
button[kind="primaryFormSubmit"] {
  background: var(--tx) !important; border: none !important;
  border-radius: var(--r-sm) !important; color: var(--bg) !important;
  font-size: 13px !important; font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
  height: 40px !important; letter-spacing: -0.01em !important;
  transition: all 0.15s !important; box-shadow: none !important;
  width: 100% !important;
}

/* ─── Tabs ─────────────────────────────────────────── */
[data-testid="stTabs"] [data-testid="stTab"] {
  background: transparent !important; border: none !important;
  color: var(--tx2) !important; font-size: 13px !important;
  font-weight: 500 !important; padding: 10px 20px !important;
  border-radius: 8px 8px 0 0 !important; transition: all 0.12s !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:hover { color: var(--tx) !important; background: var(--bg-hover) !important; }
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] { color: var(--tx) !important; font-weight: 600 !important; border-bottom: 2px solid var(--tx) !important; }
[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid var(--bd) !important; gap: 2px !important; }

/* ─── Misc ─────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: rgba(200,240,96,0.06) !important; border: 1px solid rgba(200,240,96,0.3) !important;
  border-radius: var(--r-sm) !important; font-size: 12px !important; color: var(--tx) !important;
}
[data-testid="stCaptionContainer"] { color: var(--tx3) !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; }
[data-testid="stImage"] img { border-radius: var(--r-sm) !important; object-fit: contain !important; width: 100% !important; border: 1px solid var(--bd) !important; }
[data-testid="stProgressBar"] > div > div { background: var(--p) !important; border-radius: 4px !important; }
[data-testid="stProgressBar"] > div { background: var(--bd) !important; border-radius: 4px !important; }
[data-testid="stDataFrame"] {
  background: var(--card-bg) !important; border: 1px solid var(--card-bd) !important;
  border-radius: var(--r-sm) !important; overflow: hidden !important;
}
[data-testid="stDataFrame"] iframe { background: var(--card-bg) !important; color-scheme: light !important; }
[data-testid="stDataFrame"] > div { background: var(--card-bg) !important; }
.kie-pill { display: inline-block; background: var(--bg-hover); border: 1px solid var(--bd); color: var(--tx2); font-size: 10px; padding: 2px 9px; border-radius: 20px; margin: 1px 2px 1px 0; white-space: nowrap; max-width: 150px; overflow: hidden; text-overflow: ellipsis; font-family: 'DM Mono', monospace; }
.kie-img-placeholder { height: 120px; background: var(--bg-s); border: 1px dashed var(--bd-h); border-radius: var(--r-sm); display: flex; align-items: center; justify-content: center; color: var(--tx3); font-size: 12px; margin: 8px 0; }
.kie-divider { border: none; height: 1px; background: var(--bd); margin: 18px 0; }

/* ─── Login ────────────────────────────────────────── */
.login-wrap { display: flex; align-items: center; justify-content: center; min-height: 80vh; }
.login-card { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 16px; padding: 48px 44px; width: 100%; max-width: 420px; box-shadow: var(--card-sh); }
.login-logo { width: 48px; height: 48px; background: #1A1A1A; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin: 0 auto 24px; color: #C8F060; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 800; letter-spacing: -0.05em; }
.login-title { font-family: 'Fraunces', serif; font-size: 26px; font-weight: 700; color: var(--tx); letter-spacing: -0.02em; text-align: center; margin-bottom: 4px; }
.login-sub { font-size: 13px; color: var(--tx2); text-align: center; margin-bottom: 32px; }

/* ─── Home stats ───────────────────────────────────── */
.home-stat { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 12px; padding: 18px 20px; box-shadow: var(--card-sh); }
.home-stat-val { font-family: 'Fraunces', serif; font-size: 42px; font-weight: 700; color: var(--tx); letter-spacing: -0.03em; line-height: 1; }
.home-stat-label { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--tx3); font-weight: 500; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.1em; }

/* ─── KPI cards ────────────────────────────────────── */
.kpi-card { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 12px; padding: 16px 18px; box-shadow: var(--card-sh); display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.kpi-label { font-family: 'Inter', sans-serif; font-size: 12px; color: var(--tx2); font-weight: 500; margin-bottom: 6px; }
.kpi-value { font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: var(--tx); letter-spacing: -0.03em; line-height: 1; }
.kpi-delta { font-size: 11px; font-weight: 500; margin-top: 4px; }
.kpi-delta-up   { color: #10B981; }
.kpi-delta-flat { color: var(--tx3); }

/* ─── Analytics cards ──────────────────────────────── */
.analytics-card { background: var(--card-bg); border: 1px solid var(--card-bd); border-radius: 12px; padding: 18px 20px; box-shadow: var(--card-sh); margin-bottom: 12px; }
.analytics-card-title { font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: var(--tx); margin-bottom: 2px; }
.analytics-card-sub   { font-family: 'Inter', sans-serif; font-size: 12px; color: var(--tx3); margin-bottom: 14px; }
.range-pill       { display: inline-flex; background: var(--bg-hover); border-radius: 6px; padding: 3px; margin-bottom: 14px; gap: 2px; }
.range-pill span  { font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 4px; cursor: pointer; color: var(--tx2); font-family: 'Inter', sans-serif; }
.range-pill span.active { background: var(--card-bg); color: var(--tx); box-shadow: var(--card-sh); font-weight: 600; }
.chart-stat-row   { display: flex; gap: 24px; padding-top: 14px; border-top: 1px solid var(--bd); margin-top: 10px; }
.chart-stat-item  { flex: 1; }
.chart-stat-label { font-size: 11px; color: var(--tx3); font-family: 'Inter', sans-serif; margin-bottom: 2px; }
.chart-stat-value { font-size: 18px; font-weight: 700; color: var(--tx); font-family: 'Inter', sans-serif; letter-spacing: -0.02em; }

/* ─── Top Brands card ──────────────────────────────── */
.brand-row-item  { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--bd); }
.brand-row-item:last-child { border-bottom: none; }
.brand-dot       { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.brand-row-name  { font-size: 13px; font-weight: 500; color: var(--tx); flex: 1; font-family: 'Inter', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.brand-row-bar-wrap { width: 70px; height: 4px; background: var(--bg-hover); border-radius: 2px; }
.brand-row-bar   { height: 4px; border-radius: 2px; }
.brand-row-count { font-size: 12px; font-weight: 600; color: var(--tx); font-family: 'DM Mono', monospace; min-width: 24px; text-align: right; }

/* ─── Altair charts ────────────────────────────────── */
.vega-embed { background: var(--card-bg) !important; border-radius: 8px; }
.vega-embed canvas { background: transparent !important; }
[data-testid="stArrowVegaLiteChart"] { background: var(--card-bg) !important; border-radius: 8px !important; }

/* ─── Users ────────────────────────────────────────── */
.nav-badge-new { display: inline-block; background: var(--tx); color: var(--bg-e); font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 20px; letter-spacing: 0.5px; margin-left: 6px; vertical-align: middle; font-family: 'Inter', sans-serif; }

/* ─── Responsive ───────────────────────────────────── */
@media (max-width: 900px) { .main .block-container { padding: 1.25rem !important; max-width: 100% !important; } .page-header h1 { font-size: 22px !important; } }
@media (max-width: 600px) { .main .block-container { padding: 0.875rem !important; } .page-header h1 { font-size: 20px !important; } }

/* ─── Streamlit app shell — force light bg in all modes ─── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stAppViewContainer"] > section { background: var(--bg) !important; }

/* Ensure no dark top area bleeds in */
[data-testid="stAppViewContainer"] > div:first-child { background: var(--bg) !important; }

/* ─── Sidebar button border kill (beats global secondary border rule) ── */
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:focus,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:focus,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:active,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:active {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

/* ─── Mobile / responsive ──────────────────────────── */
/* Make the collapse arrow always visible and tap-friendly */
[data-testid="stSidebarCollapseButton"] button {
  width: 36px !important; height: 36px !important;
  min-width: 36px !important; padding: 0 !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
}

@media (max-width: 768px) {
  /* Content padding */
  .main .block-container,
  [data-testid="stMainBlockContainer"] {
    padding: 0.5rem 1rem 1.5rem !important;
  }

  /* KPI cards: 2 columns on tablet */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: calc(50% - 8px) !important;
  }

  /* Card values slightly smaller */
  .card-value { font-size: 26px !important; }

  /* Sidebar overlays on mobile (Streamlit default), ensure it's full height */
  [data-testid="stSidebar"] {
    position: fixed !important; z-index: 999 !important;
    height: 100dvh !important;
  }

  /* Sidebar collapse arrow: larger tap target */
  [data-testid="stSidebarCollapseButton"] {
    position: fixed !important; top: 8px !important; left: 8px !important;
    z-index: 1000 !important;
  }

  /* Nav links: taller tap target on mobile */
  [data-testid="stSidebar"] a.sb-nav-link {
    height: 40px !important; font-size: 13.5px !important;
  }

  /* Page headers */
  .page-header h1 { font-size: 22px !important; }
}

@media (max-width: 480px) {
  /* Stack KPI cards to 1 column on phone */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 100% !important;
  }

  .main .block-container,
  [data-testid="stMainBlockContainer"] {
    padding: 0.5rem 0.75rem 1rem !important;
  }

  .card-value { font-size: 22px !important; }
}

/* ─── Dark mode: Streamlit component overrides ─────── */
body.adfl-dark .stApp,
body.adfl-dark [data-testid="stAppViewContainer"],
body.adfl-dark [data-testid="stMain"],
body.adfl-dark [data-testid="stMainBlockContainer"] { background: var(--bg) !important; }
body.adfl-dark .main .block-container { background: var(--bg) !important; }
body.adfl-dark [data-testid="stSidebar"] { background: var(--side-bg) !important; }
body.adfl-dark [data-testid="stMarkdownContainer"],
body.adfl-dark [data-testid="stMarkdownContainer"] p,
body.adfl-dark [data-testid="stMarkdownContainer"] span,
body.adfl-dark [data-testid="stMarkdownContainer"] div,
body.adfl-dark [data-testid="stMarkdownContainer"] h1,
body.adfl-dark [data-testid="stMarkdownContainer"] h2,
body.adfl-dark [data-testid="stMarkdownContainer"] h3,
body.adfl-dark [data-testid="stMarkdownContainer"] strong { color: var(--tx) !important; }
body.adfl-dark [data-testid="stDataFrame"] canvas { filter: invert(1) hue-rotate(180deg) !important; }

</style>
""", unsafe_allow_html=True)

# ─── Custom favicon (AF logo SVG) ─────────────────────────────────────────────
st_components.html("""<script>
(function() {
  var doc = window.parent.document;
  var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    + '<rect width="32" height="32" rx="7" fill="#1A1A1A"/>'
    + '<path d="M4 10V5H9" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    + '<path d="M23 5H28V10" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    + '<path d="M28 22V27H23" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    + '<path d="M9 27H4V22" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    + '<text x="7.5" y="21" font-family="Arial" font-size="11" font-weight="900" fill="#FFFFFF" letter-spacing="-0.5">AF</text>'
    + '</svg>';
  var b64 = btoa(svg);
  var url = 'data:image/svg+xml;base64,' + b64;
  var link = doc.querySelector("link[rel~='icon']") || doc.createElement('link');
  link.rel = 'icon'; link.type = 'image/svg+xml'; link.href = url;
  doc.head.appendChild(link);
})();
</script>""", height=0)

# ─── Sidebar toggle button ─────────────────────────────────────────────────────
st_components.html("""
<script>
(function() {
  var doc = window.parent.document;

  function getSidebarBtn() {
    // The native Streamlit collapse button — hidden via CSS but still functional
    return doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
           doc.querySelector('button[kind="header"]');
  }

  function isSidebarCollapsed() {
    var sidebar = doc.querySelector('[data-testid="stSidebar"]');
    if (!sidebar) return false;
    return sidebar.getAttribute('aria-expanded') === 'false';
  }

  function updateBtn(outer) {
    var collapsed = isSidebarCollapsed();
    outer.style.left = collapsed ? '14px' : '230px';
  }

  function ensureBtn() {
    if (doc.getElementById('sb-custom-toggle')) return;

    var outer = doc.createElement('div');
    outer.id = 'sb-custom-toggle';
    outer.innerHTML = '&#9776;';
    outer.title = 'Toggle sidebar';
    outer.style.cssText = [
      'position:fixed',
      'top:14px',
      'left:230px',
      'z-index:999999',
      'width:34px',
      'height:34px',
      'border-radius:10px',
      'cursor:pointer',
      'display:flex',
      'align-items:center',
      'justify-content:center',
      'font-size:16px',
      'box-shadow:0 1px 4px rgba(0,0,0,0.08)',
      'transition:background 0.15s,color 0.15s,left 0.25s,border-color 0.15s,box-shadow 0.15s',
      'user-select:none'
    ].join(';');

    function isDark() { return doc.body.classList.contains('adfl-dark'); }

    function applyIdleColors() {
      if (isDark()) {
        outer.style.background = '#1E293B';
        outer.style.border = '1px solid #334155';
        outer.style.color = '#94A3B8';
      } else {
        outer.style.background = '#FFFFFF';
        outer.style.border = '1px solid #E5E7EB';
        outer.style.color = '#6B7280';
      }
    }
    applyIdleColors();

    // Re-apply whenever theme class changes
    var themeObserver = new MutationObserver(function() { applyIdleColors(); });
    themeObserver.observe(doc.body, { attributes: true, attributeFilter: ['class'] });

    outer.addEventListener('mouseover', function() {
      outer.style.background = isDark() ? 'rgba(200,240,96,0.12)' : 'rgba(200,240,96,0.18)';
      outer.style.borderColor = 'rgba(200,240,96,0.3)';
      outer.style.color = '#C8F060';
    });
    outer.addEventListener('mouseout', function() { applyIdleColors(); });
    outer.addEventListener('click', function() {
      // Click the real (hidden) Streamlit collapse button — this properly toggles sidebar state
      var nativeBtn = getSidebarBtn();
      if (nativeBtn) {
        nativeBtn.click();
        // Update position after Streamlit processes the toggle (slight delay)
        setTimeout(function() { updateBtn(outer); }, 150);
        setTimeout(function() { updateBtn(outer); }, 400);
      }
    });

    doc.body.appendChild(outer);

    // Watch for sidebar state changes (e.g. on page load / rerun)
    var observer = new MutationObserver(function() { updateBtn(outer); });
    var sidebar = doc.querySelector('[data-testid="stSidebar"]');
    if (sidebar) observer.observe(sidebar, { attributes: true, attributeFilter: ['aria-expanded'] });
  }

  // Wait for DOM to be ready then inject button
  function tryInit() {
    var sidebar = doc.querySelector('[data-testid="stSidebar"]');
    if (sidebar) { ensureBtn(); }
    else { setTimeout(tryInit, 200); }
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', tryInit);
  } else {
    tryInit();
  }
})();
</script>
""", height=0)

# ─── Checkbox style injector ──────────────────────────────────────────────────
st_components.html("""<script>
(function() {
  var doc = window.parent.document;
  var STYLE_ID = 'adfl-checkbox-style';
  function injectCheckboxCSS() {
    if (doc.getElementById(STYLE_ID)) return;
    var s = doc.createElement('style');
    s.id = STYLE_ID;
    s.textContent = [
      /* unchecked box */
      '[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div,',
      '[data-testid="stCheckbox"] label > div:first-child > div:first-child {',
      '  background-color: #FFFFFF !important;',
      '  border: 2px solid #9CA3AF !important;',
      '  border-radius: 4px !important;',
      '}',
      /* svg checkmark color */
      '[data-testid="stCheckbox"] svg { color: #111827 !important; fill: #111827 !important; }',
      /* dark mode */
      'body.adfl-dark [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div,',
      'body.adfl-dark [data-testid="stCheckbox"] label > div:first-child > div:first-child {',
      '  background-color: #1E293B !important;',
      '  border-color: #475569 !important;',
      '}',
      'body.adfl-dark [data-testid="stCheckbox"] svg { color: #F1F5F9 !important; fill: #F1F5F9 !important; }'
    ].join('\n');
    doc.head.appendChild(s);
  }
  function start() { injectCheckboxCSS(); }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start);
  else start();
})();
</script>""", height=0)

# ─── Dark mode class toggle ────────────────────────────────────────────────────
_dm_active = st.session_state.get("dark_mode", False)
st_components.html(f"""<script>
(function(){{
  var body = window.parent.document.body;
  if ({str(_dm_active).lower()}) {{
    body.classList.add('adfl-dark');
  }} else {{
    body.classList.remove('adfl-dark');
  }}
}})();
</script>""", height=0)


# ─── Database ─────────────────────────────────────────────────────────────────

@st.cache_resource
def get_sb():
    url = st.secrets.get("SUPABASE_URL", "https://rregsjhewznaiapkonmp.supabase.co")
    key = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZWdzamhld3puYWlhcGtvbm1wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwNTgxNzQsImV4cCI6MjA4ODYzNDE3NH0.d06xTShGMljQWSfBt-BLyY6sCk4XxwtxDQJT0EEPMdQ")
    return create_client(url, key)

# ─── Auth helpers ─────────────────────────────────────────────────────────────

def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def auth_check_login(email: str, password: str):
    """Return user dict if credentials valid, else None."""
    try:
        sb  = get_sb()
        res = sb.table("users").select("*").eq("email", email.lower().strip()).execute()
        rows = res.data or []
        if not rows:
            return None
        u = rows[0]
        if u.get("password_hash") == _hash_pw(password):
            return u
        return None
    except Exception:
        return None

def auth_get_users():
    try:
        return get_sb().table("users").select("*").order("created_at").execute().data or []
    except Exception:
        return []

def auth_create_user(name: str, email: str, password: str, role: str = "user") -> bool:
    try:
        get_sb().table("users").insert({
            "name":          name.strip(),
            "email":         email.lower().strip(),
            "password_hash": _hash_pw(password),
            "role":          role,
        }).execute()
        return True
    except Exception:
        return False

def auth_delete_user(user_id) -> bool:
    try:
        get_sb().table("users").delete().eq("id", user_id).execute()
        return True
    except Exception:
        return False

if "generating"          not in st.session_state: st.session_state.generating          = False
if "pending_ugc_id"      not in st.session_state: st.session_state.pending_ugc_id      = None
if "pending_comp_ugc_id" not in st.session_state: st.session_state.pending_comp_ugc_id = None
if "pending_dd_meta"     not in st.session_state: st.session_state.pending_dd_meta     = {}
if "pending_comp_meta"   not in st.session_state: st.session_state.pending_comp_meta   = {}
if "job_submitted"       not in st.session_state: st.session_state.job_submitted       = False
if "comp_job_submitted"  not in st.session_state: st.session_state.comp_job_submitted  = False
if "poll_count"          not in st.session_state: st.session_state.poll_count          = 0
if "comp_poll_count"     not in st.session_state: st.session_state.comp_poll_count     = 0
if "loc_job_submitted"   not in st.session_state: st.session_state.loc_job_submitted   = False
if "pending_loc_ugc_id"  not in st.session_state: st.session_state.pending_loc_ugc_id  = None
if "loc_poll_count"      not in st.session_state: st.session_state.loc_poll_count      = 0
if "pending_loc_meta"    not in st.session_state: st.session_state.pending_loc_meta    = {}
if "ugc_video_generating" not in st.session_state: st.session_state.ugc_video_generating = False
if "ugc_video_result"     not in st.session_state: st.session_state.ugc_video_result     = None
if "ugc_video_task_id"    not in st.session_state: st.session_state.ugc_video_task_id    = None
if "ugc_video_poll_start" not in st.session_state: st.session_state.ugc_video_poll_start = None
if "ugc_video_error"      not in st.session_state: st.session_state.ugc_video_error      = None
# Auth
if "auth_user"  not in st.session_state: st.session_state.auth_user  = None
if "auth_role"  not in st.session_state: st.session_state.auth_role  = None
if "auth_name"  not in st.session_state: st.session_state.auth_name  = None
if "auth_email" not in st.session_state: st.session_state.auth_email = None
# Active page (replaces st.radio)
if "page"       not in st.session_state: st.session_state.page       = "home"
if "dark_mode"   not in st.session_state: st.session_state.dark_mode   = False

# ─── Constants ────────────────────────────────────────────────────────────────
TONE_OPTIONS = [
    "Professional", "Bold & Energetic", "Friendly & Casual",
    "Luxury & Exclusive", "Playful & Fun", "Urgent & Direct",
]
WEBHOOK_URL              = "https://lorenzotalia.app.n8n.cloud/webhook/d0037d38-4ab7-474f-826c-1a2d96248b98"
COMPETITOR_WEBHOOK_URL   = "https://lorenzotalia.app.n8n.cloud/webhook/competitor-reverse-v1"
MANUAL_WEBHOOK_URL       = "https://lorenzotalia.app.n8n.cloud/webhook/manual-prompt-v1"
RESULTS_POLL_URL         = "https://lorenzotalia.app.n8n.cloud/webhook/results-dd"
MANUAL_RESULTS_URL       = "https://lorenzotalia.app.n8n.cloud/webhook/results-manual"
LOCALIZE_WEBHOOK_URL     = "https://lorenzotalia.app.n8n.cloud/webhook/ads-localize"
UGC_VIDEO_WEBHOOK_URL   = "https://lorenzotalia.app.n8n.cloud/webhook/ugc-video-create"
UGC_VIDEO_STATUS_URL    = "https://lorenzotalia.app.n8n.cloud/webhook/ugc-video-status"

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

LOCALIZE_COUNTRIES = [
    {"code": "AT", "flag": "🇦🇹", "name": "Austria",         "language": "de"},
    {"code": "CH", "flag": "🇨🇭", "name": "Switzerland",     "language": "de"},
    {"code": "CZ", "flag": "🇨🇿", "name": "Czech Republic",  "language": "cs"},
    {"code": "DE", "flag": "🇩🇪", "name": "Germany",         "language": "de"},
    {"code": "DK", "flag": "🇩🇰", "name": "Denmark",         "language": "da"},
    {"code": "ES", "flag": "🇪🇸", "name": "Spain",           "language": "es"},
    {"code": "FI", "flag": "🇫🇮", "name": "Finland",         "language": "fi"},
    {"code": "FR", "flag": "🇫🇷", "name": "France",          "language": "fr"},
    {"code": "IT", "flag": "🇮🇹", "name": "Italy",           "language": "it"},
    {"code": "PT", "flag": "🇵🇹", "name": "Portugal",        "language": "pt"},
    {"code": "RO", "flag": "🇷🇴", "name": "Romania",         "language": "ro"},
    {"code": "SE", "flag": "🇸🇪", "name": "Sweden",          "language": "sv"},
    {"code": "SK", "flag": "🇸🇰", "name": "Slovakia",        "language": "sk"},
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
        0%   { background-position: -600px 0; }
        100% { background-position:  600px 0; }
    }
    .shimmer-box {
        background: linear-gradient(90deg,
            #F8F8F6 25%,
            rgba(124,58,237,0.06) 50%,
            #F8F8F6 75%);
        background-size: 600px 100%;
        animation: shimmer 1.8s infinite;
        border-radius: 14px;
        border: 1px solid #E8E8E6;
    }
    @keyframes pulse-dot {
        0%,80%,100% { opacity:.2; transform:scale(.8); }
        40%          { opacity:1;  transform:scale(1);  }
    }
    .dot {
        display:inline-block; width:6px; height:6px;
        background:var(--p,#C8F060); border-radius:50%; margin:0 2px;
        animation: pulse-dot 1.4s infinite ease-in-out;
        box-shadow: 0 0 6px rgba(200,240,96,0.5);
    }
    .dot:nth-child(2) { animation-delay:.2s; }
    .dot:nth-child(3) { animation-delay:.4s; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
        <div><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
        <span style="font-size:13px;color:#6B6B6B;font-weight:500">Generating your ads… refreshing every 5s</span>
        <span style="font-size:10px;color:#9A9A9A;font-family:'DM Mono',monospace;margin-left:auto">{ugc_id}</span>
    </div>
    """, unsafe_allow_html=True)
    for i, name in enumerate(slot_names):
        st.markdown(f"""
        <div style="margin-bottom:12px">
            <div style="font-size:10px;color:#9A9A9A;font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">
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
        f'<div style="margin-bottom:32px;padding-bottom:22px;border-bottom:1px solid #E8E8E6;'
        f'position:relative">'
        f'<h1 style="font-family:Fraunces,serif;font-size:28px;font-weight:800;'
        f'color:#1A1A1A;margin:0 0 6px;letter-spacing:-0.02em">{title}</h1>'
        + (f'<p style="font-size:14px;color:#6B6B6B;margin:0;font-family:Inter,sans-serif">{subtitle}</p>' if subtitle else "")
        + '<div style="position:absolute;bottom:-1px;left:0;width:40px;height:3px;'
        + 'background:#C8F060;border-radius:2px"></div>'
        + '</div>',
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
        f'<div style="width:{size}px;height:{size}px;background:#F2F2F0;'
        f'border:1px solid #EFEFED;'
        f'border-radius:10px;display:flex;align-items:center;justify-content:center;'
        f'font-size:{size//3}px;flex-shrink:0">📦</div>'
    )
    if not image_url or not image_url.strip():
        return placeholder
    encoded   = urllib.parse.quote(image_url.strip(), safe="")
    proxy_url = f"https://images.weserv.nl/?url={encoded}&w={size*2}&h={size*2}&fit=cover&output=jpg"
    return (
        f'<img src="{proxy_url}" width="{size}" height="{size}" '
        f'style="border-radius:8px;object-fit:cover;background:#F8F8F6;flex-shrink:0" '
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
             border:1px solid #E8E8E6;transition:opacity .15s;}}
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
        f'<img src="{proxy}" style="width:56px;height:56px;border-radius:8px;object-fit:cover;background:#EFEFED;flex-shrink:0" onerror="this.style.display=\'none\'">'
        if proxy else
        '<div style="width:56px;height:56px;border-radius:10px;background:#F2F2F0;border:1px solid #EFEFED;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">📦</div>'
    )
    benefits = parse_benefits(product.get("key_benefits", ""), max_items=3, max_chars=25)
    pills = "".join([
        f'<span style="display:inline-block;background:#EFEFED;border:1px solid #E8E8E6;color:#9A9A9A;font-size:10px;padding:1px 8px;border-radius:20px;margin:1px 2px">{b}</span>'
        for b in benefits
    ])
    offer = product.get("offer_promotion", "")
    show_offer = bool(offer and offer.strip().lower() not in ("", "none", "n/a", "no promo for now"))
    offer_html = f'<span style="font-size:10px;color:#3fb950;margin-left:8px">🎁 {offer[:40]}</span>' if show_offer else ""
    desc = product.get("description", "") or ""
    desc_short = desc[:80] + "…" if len(desc) > 80 else desc
    return (
        f'<div style="display:flex;align-items:flex-start;gap:14px;padding:14px 16px;'
        f'background:#F8F8F6;border:1px solid #E8E8E6;'
        f'border-radius:14px;margin:4px 0">'
        f'{img_html}'
        f'<div style="flex:1;min-width:0">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">'
        f'<span style="font-size:14px;font-weight:600;color:#1A1A1A;font-family:Fraunces,serif;'
        f'letter-spacing:-0.02em">{product["name"]}</span>'
        f'<span style="font-size:10px;color:#6B6B6B;background:#F2F2F0;padding:2px 8px;'
        f'border-radius:20px;border:1px solid #EFEFED">{brand_name}</span>'
        f'{offer_html}</div>'
        f'<div style="font-size:11px;color:#9A9A9A;margin-bottom:6px;line-height:1.4;white-space:nowrap;'
        f'overflow:hidden;text-overflow:ellipsis">{desc_short}</div>'
        f'<div>{pills}</div>'
        f'</div></div>'
    )

def render_brand_card(brand: dict) -> str:
    logo_url = brand.get("logo_url", "").strip()
    encoded = urllib.parse.quote(logo_url, safe="") if logo_url else ""
    proxy = f"https://images.weserv.nl/?url={encoded}&w=100&h=100&fit=cover&output=jpg" if logo_url else ""
    img_html = (
        f'<img src="{proxy}" style="width:48px;height:48px;border-radius:8px;object-fit:cover;background:#EFEFED;flex-shrink:0" onerror="this.style.display=\'none\'">'
        if proxy else
        '<div style="width:48px;height:48px;border-radius:10px;background:#F2F2F0;border:1px solid #EFEFED;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">🏷️</div>'
    )
    tone = brand.get("tone_of_voice", "") or brand.get("tone", "")
    tagline = brand.get("tagline", "") or ""
    tone_html = (
        f'<span style="font-size:10px;color:#6B6B6B;background:rgba(200,240,96,0.08);padding:2px 9px;'
        f'border-radius:20px;border:1px solid rgba(200,240,96,0.12);margin-top:5px;display:inline-block;'
        f'font-weight:500">{tone}</span>'
        if tone else ""
    )
    return (
        f'<div style="display:flex;align-items:center;gap:14px;padding:14px 16px;'
        f'background:#F8F8F6;border:1px solid #E8E8E6;'
        f'border-radius:14px;margin:4px 0">'
        f'{img_html}'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:14px;font-weight:700;color:#1A1A1A;margin-bottom:3px;'
        f'font-family:Fraunces,serif;letter-spacing:-0.02em">{brand["name"]}</div>'
        f'<div style="font-size:11px;color:#6B6B6B;white-space:nowrap;overflow:hidden;'
        f'text-overflow:ellipsis">{tagline[:60]}</div>'
        f'{tone_html}</div></div>'
    )

# ─── Ad info card HTML helper ─────────────────────────────────────────────────
def _ad_info_html(
    filename: str = "",
    platform: str = "META",
    date: str = "",
    impressions: int = None,
    clicks: int = None,
    conversions: int = None,
) -> str:
    """Returns the HTML block shown below every ad image (outside the image)."""
    date_row = (
        f'<div style="font-size:11px;color:#6B6B6B;font-weight:500;margin-bottom:12px">'
        f'📅 {date}</div>'
    ) if date else ""

    if impressions is not None:
        metrics_row = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;'
            f'margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #E8E8E6">'
            f'<div>'
            f'<div style="font-size:9px;font-weight:700;color:#9A9A9A;text-transform:uppercase;'
            f'letter-spacing:0.9px;margin-bottom:3px">Impressions</div>'
            f'<div style="font-size:15px;font-weight:700;color:#1A1A1A;'
            f'font-family:\'Fraunces\',sans-serif;letter-spacing:-0.03em">{impressions:,}</div>'
            f'</div>'
            f'<div>'
            f'<div style="font-size:9px;font-weight:700;color:#9A9A9A;text-transform:uppercase;'
            f'letter-spacing:0.9px;margin-bottom:3px">Clicks</div>'
            f'<div style="font-size:15px;font-weight:700;color:#1A1A1A;'
            f'font-family:\'Fraunces\',sans-serif;letter-spacing:-0.03em">{clicks:,}</div>'
            f'</div>'
            f'<div>'
            f'<div style="font-size:9px;font-weight:700;color:#9A9A9A;text-transform:uppercase;'
            f'letter-spacing:0.9px;margin-bottom:3px">Conversions</div>'
            f'<div style="font-size:15px;font-weight:700;color:#1A1A1A;'
            f'font-family:\'Fraunces\',sans-serif;letter-spacing:-0.03em">{conversions:,}</div>'
            f'</div>'
            f'</div>'
        )
    else:
        metrics_row = ""

    tag_row = (
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<span style="display:inline-block;background:rgba(200,240,96,0.1);color:#C8F060;'
        f'font-size:9px;font-weight:700;padding:2px 10px;border-radius:20px;'
        f'border:1px solid #E8E8E6;letter-spacing:0.6px;'
        f'white-space:nowrap;flex-shrink:0">{platform}</span>'
        f'<span style="font-family:\'DM Mono\',monospace;font-size:9px;color:#6B6B6B;'
        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1">{filename}</span>'
        f'</div>'
    )

    return (
        f'<div style="background:#F8F8F6;border:1px solid #E8E8E6;'
        f'border-radius:12px;padding:14px 16px;margin-top:8px;margin-bottom:4px">'
        f'{date_row}'
        f'{metrics_row}'
        f'{tag_row}'
        f'</div>'
    )

# ─── Image grid renderer ──────────────────────────────────────────────────────
IMAGE_GRID_CSS = """<style>
[data-testid="stImage"] img { border-radius: 8px; object-fit: cover; }
[data-testid="stImage"] { border: 1px solid #E8E8E6; border-radius: 12px; padding: 6px; background: #F8F8F6; margin-bottom: 4px; }
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
            st.markdown(_ad_info_html(filename=filename), unsafe_allow_html=True)
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

    ugc_id = st.session_state.pending_ugc_id or ""
    is_manual_job = ugc_id.startswith("manual_")
    panel_matches = (key_prefix == "manual") == is_manual_job

    if st.session_state.job_submitted and ugc_id and panel_matches:
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
        poll_url = MANUAL_RESULTS_URL if ugc_id.startswith("manual_") else RESULTS_POLL_URL
        try:
            poll_resp = requests.get(poll_url, params={"ugc_id": ugc_id}, timeout=10)
            poll_data = poll_resp.json()
        except Exception:
            poll_data = {"status": "processing"}

        MAX_POLLS = 40  # ~3 min 20 sec timeout
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
            st.session_state["last_results_mode"]     = key_prefix
            st.session_state.pending_ugc_id           = None
            st.session_state.pending_dd_meta          = {}
            st.session_state.generating               = False
            st.session_state.job_submitted            = False
            st.session_state.poll_count               = 0
            inject_generation_guard(False)
            st.rerun()
        elif st.session_state.poll_count >= MAX_POLLS:
            st.error("⏱️ Timeout — la generazione sta impiegando troppo. Controlla la History quando le immagini sono pronte.")
            if st.button("🔄 Reset", key="dd_reset_timeout"):
                st.session_state.generating     = False
                st.session_state.job_submitted  = False
                st.session_state.poll_count     = 0
                st.session_state.pending_ugc_id = None
                inject_generation_guard(False)
                st.rerun()
        else:
            if st.button("✕ Cancel", key="dd_cancel_btn", type="secondary"):
                st.session_state.generating     = False
                st.session_state.job_submitted  = False
                st.session_state.poll_count     = 0
                st.session_state.pending_ugc_id = None
                inject_generation_guard(False)
                st.rerun()
            st.session_state.poll_count += 1
            time.sleep(5)
            st.rerun()

    elif st.session_state.get("last_results") and (st.session_state.get("last_results_mode", "dd") == key_prefix):
        images   = st.session_state["last_results"]
        brand_id = st.session_state.get("last_results_brand_id")
        product  = st.session_state.get("last_results_product", "")
        st.markdown(
            f'<p style="font-size:12px;color:#22c55e;font-weight:700;margin-bottom:10px;'
            f'letter-spacing:-0.01em">'
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
                _today = datetime.now().strftime("%Y-%m-%d")
                st.markdown(
                    _ad_info_html(filename=filename, date=_today),
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
        return {"score": 0, "label": "Empty", "color": "#9A9A9A", "tips": []}
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
        <div style="flex:1;height:4px;background:#E8E8E6;border-radius:2px">
            <div style="width:{score}%;height:100%;background:{color};
                        border-radius:2px;transition:width 0.3s"></div>
        </div>
        <div style="font-size:11px;color:#9A9A9A;min-width:32px;text-align:right">
            {score}/100
        </div>
    </div>
    """, unsafe_allow_html=True)
    for tip in tips[:2]:
        st.markdown(
            f'<div style="font-size:10px;color:#6B6B6B;margin:2px 0 0 4px">{tip}</div>',
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
            '<div style="font-size:11px;color:#6B6B6B;margin-bottom:12px;line-height:1.5">'
            'Write one prompt per variant. Describe scene, lighting, headline, CTA, and visual style.'
            '</div>',
            unsafe_allow_html=True,
        )

        prompts    = []
        all_scores = []
        for i in range(num_variants):
            st.markdown(
                f'<div style="font-size:10px;font-weight:700;color:#9A9A9A;'
                f'text-transform:uppercase;letter-spacing:1.2px;'
                f'margin:{"18px" if i > 0 else "0"} 0 5px">Variant {i+1}</div>',
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
                f'<div style="font-size:11px;color:#6B6B6B;margin-bottom:8px;font-weight:500">'
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


# ─── Remember me: auto-restore session from query param ───────────────────────
if not st.session_state.auth_user:
    _saved_s = st.query_params.get("_s", "")
    if _saved_s:
        try:
            _res = get_sb().table("users").select("*").eq("id", _saved_s).execute()
            if _res.data:
                _su = _res.data[0]
                st.session_state.auth_user  = _su["id"]
                st.session_state.auth_role  = _su.get("role", "user")
                st.session_state.auth_name  = _su.get("name", "")
                st.session_state.auth_email = _su.get("email", "")
                st.session_state.page       = "home"
                st.rerun()
        except Exception:
            st.query_params.pop("_s", None)

# ─── Nav query param: sidebar link clicks ────────────────────────────────────
_nav_qp = st.query_params.get("nav", "")
if _nav_qp and st.session_state.get("auth_user"):
    if _nav_qp != st.session_state.get("page", "home"):
        st.session_state.page = _nav_qp

# ─── Login gate ───────────────────────────────────────────────────────────────
if not st.session_state.auth_user:
    _, login_col, _ = st.columns([1, 1.4, 1])
    with login_col:
        st.markdown("""
        <div style="margin-top:60px;text-align:center">
            <div style="width:48px;height:48px;background:#1A1A1A;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;
                        margin:0 auto 20px">
                <svg width="26" height="26" viewBox="0 0 18 18" fill="none">
                  <path d="M1 5V2H5" stroke="#C8F060" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M13 2H16V5" stroke="#C8F060" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16 13V16H13" stroke="#C8F060" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M5 16H2V13" stroke="#C8F060" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <text x="4.5" y="12" font-family="Arial" font-size="6.5" font-weight="900" fill="#FFFFFF" letter-spacing="-0.3">AF</text>
                </svg>
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:22px;font-weight:700;
                        color:#1A1A1A;letter-spacing:-0.03em;margin-bottom:4px">AdFrame<em style="font-weight:400;font-style:italic">Lab</em></div>
            <div style="font-size:13px;color:#9A9A9A;margin-bottom:36px;font-family:'Inter',sans-serif">Sign in to your workspace</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            login_email   = st.text_input("Email", placeholder="you@example.com")
            login_pass    = st.text_input("Password", type="password", placeholder="••••••••")
            remember_me   = st.checkbox("Keep me signed in", value=True)
            login_btn     = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if login_btn:
            if not login_email or not login_pass:
                st.error("Please enter your email and password.")
            else:
                user = auth_check_login(login_email, login_pass)
                if user:
                    st.session_state.auth_user  = user["id"]
                    st.session_state.auth_role  = user.get("role", "user")
                    st.session_state.auth_name  = user.get("name", login_email)
                    st.session_state.auth_email = user.get("email", login_email)
                    st.session_state.page       = "home"
                    if remember_me:
                        st.query_params["_s"] = str(user["id"])
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
    st.stop()


# ─── Image preview dialog ─────────────────────────────────────────────────────
@st.dialog("Image Preview", width="large")
def _image_preview_dialog():
    item = st.session_state.get("_preview_item", {})
    if not item:
        st.warning("No image selected.")
        return
    url      = item.get("url", "")
    title    = item.get("title", "Ad Creative")
    platform = item.get("platform", "")
    date_str = item.get("date", "")
    filename = item.get("filename", title)

    if url:
        st.image(url, use_container_width=True)
        st.markdown(f"### {title}")
        meta_parts = []
        if platform:
            meta_parts.append(f"**Platform:** {platform}")
        if date_str:
            meta_parts.append(f"**Date:** {date_str}")
        if meta_parts:
            st.caption("  ·  ".join(meta_parts))
        st.markdown("---")
        get_download_button(url, filename, label="⬇️ Download Image", key_suffix="dlg")
    else:
        st.info("⚠️ Image unavailable — the URL may have expired or the file was removed.")

# ─── Sidebar navigation ───────────────────────────────────────────────────────
def _nav(label: str, key: str, indent: bool = False):
    """Render a sidebar nav item as a plain HTML link — full left-align control."""
    active = st.session_state.page == key
    _s = st.query_params.get("_s", "")
    url = f"?nav={key}" + (f"&_s={_s}" if _s else "")
    active_style = (
        "background:var(--side-active-bg);color:var(--side-active-tx)!important;font-weight:600;"
        if active else
        "background:transparent;color:var(--side-text)!important;font-weight:400;"
    )
    st.sidebar.markdown(f"""
<a class="sb-nav-link{'  sb-nav-active' if active else ''}" href="{url}" target="_self"
   style="display:flex;align-items:center;width:100%;box-sizing:border-box;
          padding:0 12px;height:34px;border-radius:6px;border:none;
          font-size:12.5px;font-family:'Inter',sans-serif;letter-spacing:0;
          text-decoration:none;line-height:1;{active_style}">{label}</a>
""", unsafe_allow_html=True)

with st.sidebar:
    _name_display = st.session_state.get("auth_name", "User")
    _role_display = st.session_state.get("auth_role", "user")

    # ── Logo ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sb-logo-wrap" style="padding:12px 12px 10px;border-bottom:1px solid var(--side-border);margin-bottom:0">
        <div style="display:flex;align-items:center;gap:9px">
            <div style="width:30px;height:30px;background:#1A1A1A;border-radius:7px;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M2 7V3H7" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M17 3H22V7" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M22 17V22H17" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M7 22H2V17" stroke="#C8F060" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                  <text x="5.5" y="16" font-family="Arial" font-size="9" font-weight="900" fill="#FFFFFF" letter-spacing="-0.5">AF</text>
                </svg>
            </div>
            <div>
                <div class="sb-logo-brand" style="font-size:13px;font-weight:700;
                            letter-spacing:-0.03em;line-height:1.1">AdFrame<em style="font-weight:400;font-style:italic">Lab</em></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.markdown('<span class="nav-cat">Overview</span>', unsafe_allow_html=True)
    _nav("🏠  Home",       "home")
    _nav("📊  Analytics",  "analytics")

    st.markdown('<span class="nav-cat">Create</span>', unsafe_allow_html=True)
    _nav("🖼️  Image Ads",  "image-ads")
    _nav("🌍  Localize",   "localize")
    st.sidebar.markdown(
        f'<div style="display:flex;align-items:center;gap:0px;padding:0 2px;margin:1px 0">' +
        ('<style>[data-testid="stSidebar"] .ugc-wrap button{display:none!important}</style>' if False else '') +
        f'</div>',
        unsafe_allow_html=True
    )
    _nav("🎬  UGC Video", "ugc-video")
    st.sidebar.markdown(
        '<div style="margin-top:-30px;margin-left:auto;padding-right:10px;display:flex;justify-content:flex-end;pointer-events:none">' +
        '<span style="background:#3B82F6;color:#fff;font-size:9px;font-weight:700;padding:1px 7px;' +
        'border-radius:20px;font-family:Inter,sans-serif;letter-spacing:0.3px">New</span></div>',
        unsafe_allow_html=True
    )

    st.markdown('<span class="nav-cat">Library</span>', unsafe_allow_html=True)
    _nav("🗂️  Ad Library", "library")
    _nav("📋  History",    "history")

    st.markdown('<span class="nav-cat">Configuration</span>', unsafe_allow_html=True)
    _nav("🏷️  Brands",    "brands")
    _nav("📦  Products",  "products")
    if _role_display == "admin":
        _nav("⚙️  Settings",  "settings")
        _nav("👥  Users", "users")

    # ── User footer ───────────────────────────────────────────────────────────
    st.markdown('<div class="sb-flex-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<hr class="nav-divider" style="margin:20px 0 4px">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:9px;padding:6px 12px 10px">
        <div style="width:28px;height:28px;border-radius:50%;background:#3B82F6;
                    display:flex;align-items:center;justify-content:center;
                    font-size:11px;font-weight:700;color:#FFFFFF;flex-shrink:0;
                    font-family:'Inter',sans-serif;line-height:1">
            {_name_display[0].upper() if _name_display else "U"}
        </div>
        <div style="min-width:0;flex:1;display:flex;flex-direction:column;gap:1px;justify-content:center">
            <div style="font-size:12.5px;font-weight:600;color:var(--side-text-h);font-family:'Inter',sans-serif;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.3">{_name_display}</div>
            <div style="font-size:10px;color:var(--tx3);font-family:'Inter',sans-serif;
                        text-transform:capitalize;line-height:1.2">{_role_display}</div>
        </div>
        <div style="font-size:13px;color:var(--tx3);flex-shrink:0;letter-spacing:2px;line-height:1;padding-bottom:2px">···</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    # ── Dark mode toggle ──────────────────────────────────────────────────────
    _dm_label = "☀️  Light Mode" if st.session_state.get("dark_mode") else "🌙  Dark Mode"
    if st.sidebar.button(_dm_label, key="_nb_darkmode", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.get("dark_mode", False)
        st.rerun()
    if st.sidebar.button("Sign Out", key="_nb_logout", use_container_width=True):
        for _k in ["auth_user", "auth_role", "auth_name", "auth_email"]:
            st.session_state[_k] = None
        st.session_state.page = "home"
        st.query_params.pop("_s", None)
        st.rerun()

    # ── Keep brand/product data for pages ─────────────────────────────────────
    brands      = get_brands()
    brand_names = [b["name"] for b in brands]
    brand_ids   = [b["id"]   for b in brands]
    try:
        _all_prods = get_products()
        n_products = len(_all_prods)
    except Exception:
        n_products = 0

# ─── Route from session state ─────────────────────────────────────────────────
page = st.session_state.get("page", "home")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — HOME
# ═══════════════════════════════════════════════════════════════════════════════
if page == "home":
    _u_name = st.session_state.get("auth_name", "there")

    # ── Fetch stats ─────────────────────────────────────────────────────────────
    try:
        sb         = get_sb()
        _n_ads     = len((sb.table("saved_ads").select("id").execute().data or []))
        _n_brands  = len((sb.table("brands").select("id").execute().data or []))
        _n_prods   = len((sb.table("products").select("id").execute().data or []))
        _hist_raw  = sb.table("generation_history").select("id,created_at").order("created_at", desc=True).execute().data or []
        _n_hist    = len(_hist_raw)
        _all_brands = brands
        _all_ads_raw = sb.table("saved_ads").select("brand_id").execute().data or []
        _brand_counts = {}
        for _a in _all_ads_raw:
            _bid = str(_a.get("brand_id", ""))
            _brand_counts[_bid] = _brand_counts.get(_bid, 0) + 1
    except Exception:
        _n_ads = _n_brands = _n_prods = _n_hist = 0
        _hist_raw = []
        _all_brands = []
        _brand_counts = {}

    # ── Inline sparkline SVG ─────────────────────────────────────────────────────
    def _sparkline(color="#3B82F6"):
        pts = "4,28 12,22 20,24 28,16 36,20 44,10 52,14 60,6"
        uid = color.replace("#","")
        return (
            f'<svg width="64" height="36" viewBox="0 0 64 36" fill="none">' +
            f'<defs><linearGradient id="sg{uid}" x1="0" y1="0" x2="0" y2="1">' +
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>' +
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>' +
            f'<polygon points="{pts} 60,36 4,36" fill="url(#sg{uid})"/>' +
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' +
            f'</svg>'
        )

    # ── KPI row ─────────────────────────────────────────────────────────────────
    kc1, kc2, kc3, kc4 = st.columns(4, gap="small")
    for _col, _val, _lbl, _clr in [
        (kc1, _n_ads,    "Saved Ads",    "#3B82F6"),
        (kc2, _n_brands, "Brands",       "#10B981"),
        (kc3, _n_prods,  "Products",     "#F59E0B"),
        (kc4, _n_hist,   "Generations",  "#8B5CF6"),
    ]:
        with _col:
            st.markdown(
                f'<div class="kpi-card">' +
                f'  <div>' +
                f'    <div class="kpi-label">{_lbl}</div>' +
                f'    <div class="kpi-value">{_val}</div>' +
                f'    <div class="kpi-delta kpi-delta-up">&#8593; Active</div>' +
                f'  </div>' +
                _sparkline(_clr) +
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Quick Actions (compact) ────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;' +
        'color:var(--tx);letter-spacing:-0.01em;margin-bottom:12px">Quick Actions</div>',
        unsafe_allow_html=True,
    )
    qa1, qa2, qa3 = st.columns(3, gap="small")
    _quick = [
        ("qa1", "\U0001f5bc\ufe0f", "Generate Image Ads",  "Data-driven, competitor reverse, or manual prompt.", "image-ads"),
        ("qa2", "\U0001f30d", "Localize Ads",         "Translate creatives for 13 European markets.",        "localize"),
        ("qa3", "\U0001f3ac", "Create UGC Video",     "AI-generated UGC product videos via Kie.ai Sora.",   "ugc-video"),
    ]
    for _col, (_key, _icon, _title, _sub, _dest) in zip([qa1, qa2, qa3], _quick):
        with _col:
            st.markdown(
                f'<div style="background:var(--card-bg);border:1px solid var(--card-bd);border-radius:12px;' +
                f'padding:16px 18px;box-shadow:var(--card-sh);margin-bottom:4px">' +
                f'<div style="font-size:20px;margin-bottom:8px">{_icon}</div>' +
                f'<div style="font-family:Inter,sans-serif;font-size:13px;font-weight:600;' +
                f'color:var(--tx);margin-bottom:4px">{_title}</div>' +
                f'<div style="font-size:12px;color:var(--tx2);line-height:1.5;font-family:Inter,sans-serif">{_sub}</div>' +
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Open \u2192", key=f"_hqa_{_key}", use_container_width=True):
                st.session_state.page = _dest
                st.rerun()

    # ── Main 2-col: Activity chart + Top Brands ──────────────────────────────────
    _chart_col, _brands_col = st.columns([13, 7], gap="small")

    with _chart_col:
        _today = datetime.now().date()
        _dates = [(str(_today - timedelta(days=i))) for i in range(29, -1, -1)]
        _dcounts = {d: 0 for d in _dates}
        for _h in _hist_raw:
            _d = str(_h.get("created_at", ""))[:10]
            if _d in _dcounts:
                _dcounts[_d] += 1
        _df_chart = pd.DataFrame({"date": list(_dcounts.keys()), "Generations": list(_dcounts.values())})
        _df_chart["date"] = pd.to_datetime(_df_chart["date"])
        _period_key = st.session_state.get("dash_period", "30d")
        _period_days = {"7d": 7, "30d": 30, "90d": 90}.get(_period_key, 30)
        _df_filt = _df_chart.tail(_period_days)
        _total_gens = int(_df_filt["Generations"].sum())
        _avg_gens   = round(_df_filt["Generations"].mean(), 1)
        _peak_gens  = int(_df_filt["Generations"].max())

        _p_col, _s_col = st.columns([3, 1])
        with _p_col:
            st.markdown(
                '<div class="analytics-card-title">Generation Activity</div>' +
                f'<div class="analytics-card-sub">Ad creations — last {_period_days} days</div>',
                unsafe_allow_html=True,
            )
        with _s_col:
            _period_new = st.selectbox(
                "Period", ["7d", "30d", "90d"],
                index=["7d", "30d", "90d"].index(_period_key),
                key="_dash_period_sel", label_visibility="collapsed",
            )
            if _period_new != _period_key:
                st.session_state.dash_period = _period_new
                st.rerun()

        _area_chart = (
            alt.Chart(_df_filt)
            .mark_area(
                line={"color": "#3B82F6", "strokeWidth": 2},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="rgba(59,130,246,0.2)", offset=0),
                        alt.GradientStop(color="rgba(59,130,246,0.0)",  offset=1),
                    ],
                    x1=0, x2=0, y1=1, y2=0,
                ),
                interpolate="monotone",
            )
            .encode(
                x=alt.X("date:T", axis=alt.Axis(
                    format="%b %d", labelAngle=-30, labelColor="#9CA3AF",
                    gridColor="#F3F4F6", tickColor="#F3F4F6", domainColor="#E5E7EB",
                    labelFontSize=10, title=None,
                )),
                y=alt.Y("Generations:Q", axis=alt.Axis(
                    labelColor="#9CA3AF", gridColor="#F3F4F6",
                    tickColor="#F3F4F6", domainColor="#E5E7EB",
                    labelFontSize=10, title=None, tickMinStep=1,
                )),
            )
            .properties(height=160, background="transparent")
            .configure_view(strokeWidth=0)
        )

        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
        st.altair_chart(_area_chart, use_container_width=True)
        st.markdown(
            f'<div class="chart-stat-row">' +
            f'  <div class="chart-stat-item"><div class="chart-stat-label">Total Generations</div>' +
            f'  <div class="chart-stat-value">{_total_gens:,}</div></div>' +
            f'  <div class="chart-stat-item"><div class="chart-stat-label">Daily Average</div>' +
            f'  <div class="chart-stat-value">{_avg_gens}</div></div>' +
            f'  <div class="chart-stat-item"><div class="chart-stat-label">Peak Day</div>' +
            f'  <div class="chart-stat-value">{_peak_gens}</div></div>' +
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with _brands_col:
        _BCOLORS = ["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#EC4899","#14B8A6"]
        _brands_ranked = sorted(
            [{"name": b["name"], "count": _brand_counts.get(str(b["id"]), 0),
              "color": _BCOLORS[i % len(_BCOLORS)]}
             for i, b in enumerate(_all_brands or [])],
            key=lambda x: x["count"], reverse=True,
        )[:7]
        _max_cnt = max((b["count"] for b in _brands_ranked), default=1) or 1

        _rows_html = "".join([
            f'<div class="brand-row-item">' +
            f'  <div class="brand-dot" style="background:{b["color"]}"></div>' +
            f'  <div class="brand-row-name">{b["name"]}</div>' +
            f'  <div class="brand-row-bar-wrap">' +
            f'    <div class="brand-row-bar" style="width:{max(4,int(b["count"]/_max_cnt*70))}px;background:{b["color"]}"></div>' +
            f'  </div>' +
            f'  <div class="brand-row-count">{b["count"]}</div>' +
            f'</div>'
            for b in _brands_ranked
        ]) if _brands_ranked else '<div style="color:var(--tx3);font-size:12px;padding:20px 0;text-align:center">No brands yet</div>'

        st.markdown(
            '<div class="analytics-card" style="height:100%;box-sizing:border-box">' +
            '  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">' +
            '    <div class="analytics-card-title">Top Brands</div>' +
            '    <span style="font-size:11px;color:#3B82F6;font-weight:500;font-family:Inter,sans-serif">View All</span>' +
            '  </div>' +
            _rows_html +
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Recent Creations ──────────────────────────────────────────────────────────
    _rc_head, _rc_action = st.columns([6, 1])
    with _rc_head:
        st.markdown(
            '<div style="font-family:Inter,sans-serif;font-size:16px;font-weight:700;' +
            'color:var(--tx);letter-spacing:-0.01em;margin-bottom:12px">Recent Creations</div>',
            unsafe_allow_html=True,
        )
    with _rc_action:
        st.markdown("<div style='margin-top:2px'>", unsafe_allow_html=True)
        if st.button("View Library →", key="_home_lib_btn"):
            st.session_state.page = "library"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    try:
        _recent_ads = get_saved_ads()[:10]
    except Exception:
        _recent_ads = []

    _gradients = [
        "linear-gradient(135deg,#0a1a8a,#1a6bca,#0d9fca)",
        "linear-gradient(155deg,#2d0a6b,#6b1faa,#8b1a6b)",
        "linear-gradient(140deg,#0a1a0d,#1a5a1d,#2a8a2d)",
        "linear-gradient(135deg,#8a4a00,#ca7a00,#e5a800)",
        "linear-gradient(155deg,#6b0a0a,#aa1f1f,#ca2a2a)",
        "linear-gradient(140deg,#0a2a4a,#1a4a8a,#0a6bca)",
        "linear-gradient(135deg,#1a0a3a,#3a1a7a,#6b2aaa)",
        "linear-gradient(150deg,#0a3a2a,#1a6a4a,#2aaa7a)",
        "linear-gradient(135deg,#3a1a00,#7a3a00,#aa5a00)",
        "linear-gradient(155deg,#0a0a3a,#1a1a6a,#2a2aaa)",
    ]

    if _recent_ads:
        _rc_cols = st.columns(5, gap="small")
        for _ri, _rad in enumerate(_recent_ads[:10]):
            with _rc_cols[_ri % 5]:
                _img_url = _rad.get("image_url", "")
                _plat    = (_rad.get("platform") or "Meta").upper()
                _title   = (_rad.get("headline") or f"Ad Creative {_ri+1}")
                _title_s = _title[:22]
                _date_s  = str(_rad.get("created_at", ""))[:10]
                _grad    = _gradients[_ri % len(_gradients)]
                _proxy   = f'https://images.weserv.nl/?url={urllib.parse.quote(_img_url, safe="")}' if _img_url else ""
                _img_tag = (
                    f'<img src="{_proxy}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"'
                    f' onerror="this.style.display:none" />' if _img_url else ""
                )
                st.markdown(
                    f'<div style="border-radius:10px;overflow:hidden;border:1px solid var(--card-bd);'
                    f'box-shadow:var(--card-sh);margin-bottom:2px">'
                    f'  <div style="position:relative;aspect-ratio:3/4;background:{_grad};overflow:hidden">'
                    f'    {_img_tag}'
                    f'    <div style="position:absolute;bottom:4px;right:5px">'
                    f'      <span style="background:rgba(0,0,0,0.45);color:#fff;font-size:8px;'
                    f'padding:2px 5px;border-radius:3px;font-family:DM Mono,monospace">{_plat}</span>'
                    f'    </div>'
                    f'  </div>'
                    f'  <div class="card-info-wrap" style="padding:6px 8px 4px;background:var(--card-bg)">'
                    f'    <div class="card-info-title" style="font-size:10.5px;font-weight:600;color:var(--tx);font-family:Inter,sans-serif;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{_title_s}</div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if _img_url:
                    _rbv, _rbd = st.columns(2, gap="small")
                    with _rbv:
                        if st.button("🔍", key=f"_rc_view_{_ri}", use_container_width=True, type="secondary", help="View full size"):
                            st.session_state._preview_item = {
                                "url":      _img_url,
                                "title":    _title,
                                "platform": _plat,
                                "date":     _date_s,
                                "filename": _rad.get("headline") or f"ad_{_rad['id']}",
                            }
                            _image_preview_dialog()
                    with _rbd:
                        get_download_button(_img_url, _rad.get("headline") or f"ad_{_rad['id']}", label="⬇️", key_suffix=f"rc_{_ri}")
                else:
                    st.markdown(
                        '<div style="text-align:center;font-size:10px;color:#9CA3AF;padding:2px 0">'
                        'Unavailable</div>', unsafe_allow_html=True
                    )
    else:
        _rc_cols2 = st.columns(5, gap="small")
        for _pi in range(5):
            with _rc_cols2[_pi]:
                st.markdown(
                    f'<div style="border-radius:10px;overflow:hidden;border:1px solid var(--card-bd)">'
                    f'  <div style="aspect-ratio:3/4;background:{_gradients[_pi]};opacity:0.65"></div>'
                    f'  <div style="padding:8px;background:var(--card-bg);text-align:center;color:var(--tx3);font-size:10px">No ads yet</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — IMAGE ADS (was "Generate Ads")
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "image-ads":

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
                ) or '<span style="color:#9A9A9A;font-size:10px">—</span>'
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;background:#F8F8F6;'
                    f'border:1px solid #E8E8E6;border-radius:8px;padding:10px 14px;margin:8px 0">'
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
                    f'border-radius:8px;background:#F8F8F6;display:block" /></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="kie-img-placeholder" style="border-color:#EFEFED;background:#F8F8F6;margin-bottom:10px">'
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
                elif st.session_state.comp_poll_count >= 40:
                    st.error("⏱️ Timeout — controlla la History quando le immagini sono pronte.")
                    if st.button("🔄 Reset", key="comp_reset_timeout"):
                        st.session_state.generating          = False
                        st.session_state.comp_job_submitted  = False
                        st.session_state.comp_poll_count     = 0
                        st.session_state.pending_comp_ugc_id = None
                        inject_generation_guard(False)
                        st.rerun()
                else:
                    if st.button("✕ Cancel", key="comp_cancel_btn", type="secondary"):
                        st.session_state.generating          = False
                        st.session_state.comp_job_submitted  = False
                        st.session_state.comp_poll_count     = 0
                        st.session_state.pending_comp_ugc_id = None
                        inject_generation_guard(False)
                        st.rerun()
                    st.session_state.comp_poll_count += 1
                    time.sleep(5)
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
                            f'<p style="font-family:\'DM Mono\',monospace;font-size:9px;'
                            f'color:#9A9A9A;margin:2px 0 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{filename}</p>',
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
            st.markdown('<span class="sec-label" style="color:#9A9A9A">🎯 Your product</span>', unsafe_allow_html=True)
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
                        f'<div style="display:flex;align-items:center;gap:10px;background:#F8F8F6;'
                        f'border:1px solid #E8E8E6;border-radius:8px;padding:8px 12px;margin:6px 0 10px">'
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
            st.markdown('<span class="sec-label" style="color:#9A9A9A">🕵️ Competitor creative</span>', unsafe_allow_html=True)
            competitor_url = st.text_input(
                "Competitor ad URL",
                placeholder="Paste URL of competitor ad screenshot...",
                key="comp_img_url",
                label_visibility="collapsed",
            )
            st.markdown(
                '<div style="font-size:10px;color:#9A9A9A;margin-top:4px">'
                '💡 Use <strong>Imgur</strong> or <strong>Google Drive</strong> public links. '
                'Facebook/Instagram CDN links are not supported.</div>',
                unsafe_allow_html=True,
            )
            if competitor_url:
                is_private, platform = is_private_cdn_url(competitor_url)
                if is_private:
                    st.markdown(f"""
                    <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;
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
elif page == "analytics":
    page_header("Campaign Analytics", "Performance overview of your Meta ad campaigns.")

    df = analytics_dataframe()

    if df.empty:
        # ── Demo mode — synthetic data ──────────────────────────────────────────
        import numpy as _np
        _rng = _np.random.default_rng(42)
        _demo_days  = pd.date_range(end=pd.Timestamp.today(), periods=30, freq="D")
        _demo_brands = ["Nike", "Glossier", "Oatly"]
        _rows = []
        for _b in _demo_brands:
            for _d in _demo_days:
                _imp  = int(_rng.integers(4000, 18000))
                _clk  = int(_rng.integers(80, int(_imp * 0.07)))
                _conv = int(_rng.integers(2, max(3, _clk // 8)))
                _spend = round(float(_rng.uniform(40, 280)), 2)
                _rows.append({"brand": _b, "date": _d.date(), "impressions": _imp,
                               "clicks": _clk, "conversions": _conv, "spend": _spend})
        df = pd.DataFrame(_rows)
        df["ctr"]  = (df["clicks"] / df["impressions"].replace(0, 1) * 100).round(2)
        df["cpc"]  = (df["spend"]  / df["clicks"].replace(0, 1)).round(2)
        df["roas"] = (df["conversions"] * 50 / df["spend"].replace(0, 1)).round(2)
        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:8px;'
            'background:rgba(200,240,96,0.08);border:1px solid rgba(200,240,96,0.3);'
            'border-radius:20px;padding:4px 14px;margin-bottom:20px;font-size:11px;color:#6B6B6B;font-weight:600">'
            '✦ Demo data — connect your ad account to see real metrics'
            '</div>',
            unsafe_allow_html=True,
        )
    if not df.empty:
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
                    stops=[alt.GradientStop(color="#C8F060", offset=0),
                           alt.GradientStop(color="rgba(200,240,96,0.05)", offset=1)],
                    x1=1, x2=1, y1=1, y2=0,
                ),
                line={"color": "#1A1A1A"}, opacity=0.7,
            ).encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("impressions:Q", title="Impressions"),
                tooltip=["date:T", "impressions:Q", "clicks:Q"],
            ).properties(height=250, background="#FFFFFF").configure_axis(
                grid=False, labelColor="#6B6B6B", titleColor="#6B6B6B",
            ).configure_view(strokeWidth=0, fill="#FFFFFF")
            st.altair_chart(chart, use_container_width=True)

        with c2:
            st.markdown("**CTR by Brand**")
            ctr_brand = df.groupby("brand")["ctr"].mean().reset_index()
            bar = alt.Chart(ctr_brand).mark_bar(
                cornerRadiusTopLeft=6, cornerRadiusTopRight=6,
            ).encode(
                x=alt.X("brand:N", sort="-y", title="Brand"),
                y=alt.Y("ctr:Q", title="Avg CTR (%)"),
                color=alt.Color("brand:N", scale=alt.Scale(
                    range=["#1A1A1A", "#C8F060", "#EF4444", "#22C55E", "#F59E0B"]
                ), legend=None),
                tooltip=["brand:N", alt.Tooltip("ctr:Q", format=".2f")],
            ).properties(height=250, background="#FFFFFF").configure_axis(
                grid=False, labelColor="#6B6B6B", titleColor="#6B6B6B",
            ).configure_view(strokeWidth=0, fill="#FFFFFF")
            st.altair_chart(bar, use_container_width=True)

        st.markdown("---")
        st.markdown("**Top Performing Ads**")
        tbl = df[["brand", "impressions", "clicks", "conversions", "spend", "ctr", "roas"]].copy()
        tbl.columns = ["Brand", "Impressions", "Clicks", "Conversions", "Spend ($)", "CTR (%)", "ROAS (x)"]
        st.dataframe(
            tbl.sort_values("ROAS (x)", ascending=False).head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Brand": st.column_config.TextColumn("Brand"),
                "Impressions": st.column_config.NumberColumn("Impressions", format="%d"),
                "Clicks": st.column_config.NumberColumn("Clicks", format="%d"),
                "Conversions": st.column_config.NumberColumn("Conversions", format="%d"),
                "Spend ($)": st.column_config.NumberColumn("Spend ($)", format="$%.2f"),
                "CTR (%)": st.column_config.NumberColumn("CTR (%)", format="%.2f%%"),
                "ROAS (x)": st.column_config.NumberColumn("ROAS (x)", format="%.1fx"),
            }
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — SAVED ADS LIBRARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "library":
    page_header("Saved Ads Library", "Browse all ad creatives you've saved locally.")

    lib_f1, lib_f2, lib_f3, lib_f4 = st.columns(4)
    with lib_f1:
        lib_brand_filter = st.selectbox("Brand", ["All Brands"] + brand_names, key="lib_brand")
    with lib_f2:
        lib_mode_filter = st.selectbox("Mode", ["All Modes", "ugc-generated", "data-driven", "competitor-reverse"], key="lib_mode")

    filter_id = None
    if lib_brand_filter != "All Brands":
        filter_id = brand_ids[brand_names.index(lib_brand_filter)]

    # Product filter — build product list for selected brand
    _lib_products = get_products(filter_id) if filter_id else get_products()
    _lib_prod_names = ["All Products"] + [p["name"] for p in _lib_products]
    with lib_f3:
        lib_product_filter = st.selectbox("Product", _lib_prod_names, key="lib_product")

    import datetime as _dt

    ads = get_saved_ads(brand_id=filter_id)

    # Mode filter
    if lib_mode_filter != "All Modes":
        ads = [a for a in ads if (a.get("mode") or "") == lib_mode_filter]

    # Product filter: the filename (headline) is "static_{brand_slug}_{product_slug}_..."
    # search the product slug as a plain substring — do NOT slugify the whole filename
    if lib_product_filter != "All Products":
        _prod_slug = _slugify(lib_product_filter)   # e.g. "nikerunpro"
        ads = [a for a in ads if _prod_slug in (a.get("headline") or "")]

    # Date range filter — compute bounds from the already-filtered list
    _all_dates = [a["created_at"][:10] for a in ads if a.get("created_at")]
    _min_d = min(_all_dates) if _all_dates else None
    _max_d = max(_all_dates) if _all_dates else None

    with lib_f4:
        if _min_d and _max_d:
            _d0 = _dt.date.fromisoformat(_min_d)
            _d1 = _dt.date.fromisoformat(_max_d)
            lib_date_filter = st.date_input("Date range", value=(_d0, _d1), key="lib_date")
        else:
            lib_date_filter = st.date_input("Date range", key="lib_date", disabled=True)
            lib_date_filter = None

    if lib_date_filter and isinstance(lib_date_filter, (list, tuple)) and len(lib_date_filter) == 2:
        _df0, _df1 = lib_date_filter
        ads = [a for a in ads
               if a.get("created_at")
               and _df0 <= _dt.date.fromisoformat(a["created_at"][:10]) <= _df1]

    if not ads:
        st.info("No saved ads match the selected filters.")
    else:
        st.caption(f"{len(ads)} ad(s) found")
        # Inject lightbox overlay into parent document
        st_components.html("""<script>
(function(){
  // Inject into both parent window and grandparent (handles nested iframes)
  var targets = [window.parent];
  try { if(window.parent.parent !== window.parent) targets.push(window.parent.parent); } catch(e){}
  targets.forEach(function(w){
    try {
      var doc = w.document;
      if(doc.getElementById('__adfl_lb__')) { w.__adflOpenLb && (w.__adflOpenLb = w.__adflOpenLb); return; }
      var ov = doc.createElement('div');
      ov.id = '__adfl_lb__';
      ov.style.cssText = 'display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.92);z-index:2147483647;align-items:center;justify-content:center;cursor:zoom-out;flex-direction:column;gap:12px';
      var img = doc.createElement('img');
      img.style.cssText = 'max-width:90vw;max-height:85vh;border-radius:12px;box-shadow:0 0 80px rgba(0,0,0,0.9)';
      ov.appendChild(img);
      ov.onclick = function(){ ov.style.display='none'; doc.body.style.overflow=''; };
      doc.body.appendChild(ov);
      w.__adflOpenLb = function(url){ img.src=url; ov.style.display='flex'; doc.body.style.overflow='hidden'; };
    } catch(e){}
  });
})();
</script>""", height=0)
        _lib_grads = [
            "linear-gradient(135deg,#1a1a2e 0%,#16213e 100%)",
            "linear-gradient(135deg,#0f3460 0%,#533483 100%)",
            "linear-gradient(135deg,#1b4332 0%,#2d6a4f 100%)",
            "linear-gradient(135deg,#3d1a00 0%,#7c3a0a 100%)",
            "linear-gradient(135deg,#2d0b3a 0%,#5a1a6b 100%)",
            "linear-gradient(135deg,#003049 0%,#0a4f6b 100%)",
            "linear-gradient(135deg,#1a0a00 0%,#4a1500 100%)",
            "linear-gradient(135deg,#0a0a0a 0%,#2a2a3a 100%)",
            "linear-gradient(135deg,#012a1a 0%,#024d35 100%)",
            "linear-gradient(135deg,#1a0020 0%,#3d0050 100%)",
        ]
        _lib_cols = st.columns(5, gap="small")
        for _li, _lad in enumerate(ads):
            with _lib_cols[_li % 5]:
                _limg     = _lad.get("image_url") or ""
                _ltitle   = _lad.get("headline") or f"Ad {_lad['id']}"
                _ltitle_s = _ltitle[:22]
                _lplat    = (_lad.get("platform") or "META").upper()
                _lcreated = _lad.get("created_at", "")[:10]
                _lgrad    = _lib_grads[_li % len(_lib_grads)]
                _lproxy   = f'https://images.weserv.nl/?url={urllib.parse.quote(_limg, safe="")}' if _limg else ""
                _limg_tag = (
                    f'<img src="{_lproxy}"'
                    f' style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"'
                    f' onerror="this.style.display=\'none\'"' if _limg else ""
                )
                st.markdown(
                    f'<div style="border-radius:10px;overflow:hidden;border:1px solid #E8EAED;'
                    f'box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:2px">'
                    f'  <div style="position:relative;aspect-ratio:3/4;background:{_lgrad};overflow:hidden">'
                    f'    {_limg_tag}'
                    f'    <div style="position:absolute;bottom:4px;right:5px">'
                    f'      <span style="background:rgba(0,0,0,0.45);color:#fff;font-size:8px;'
                    f'padding:2px 5px;border-radius:3px;font-family:DM Mono,monospace">{_lplat}</span>'
                    f'    </div>'
                    f'  </div>'
                    f'  <div class="card-info-wrap" style="padding:6px 8px 4px;background:var(--card-bg)">'
                    f'    <div class="card-info-title" style="font-size:10.5px;font-weight:600;color:var(--tx);font-family:Inter,sans-serif;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{_ltitle_s}</div>'
                    f'    <div class="card-info-date" style="font-size:9px;color:var(--tx2);font-family:DM Mono,monospace;margin-top:1px">{_lcreated}</div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if _limg:
                    _lbv, _lbd = st.columns(2, gap="small")
                    with _lbv:
                        if st.button("🔍", key=f"_lib_view_{_li}", use_container_width=True, type="secondary", help="View full size"):
                            st.session_state._preview_item = {
                                "url":      _limg,
                                "title":    _ltitle,
                                "platform": _lplat,
                                "date":     _lcreated,
                                "filename": _lad.get("headline") or f"ad_{_lad['id']}",
                            }
                            _image_preview_dialog()
                    with _lbd:
                        get_download_button(_limg, _lad.get("headline") or f"ad_{_lad['id']}", label="⬇️", key_suffix=f"lib_{_li}")
                else:
                    st.markdown(
                        '<div style="text-align:center;font-size:10px;color:#9CA3AF;padding:2px 0">'
                        'Unavailable</div>', unsafe_allow_html=True
                    )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "history":
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
                badge = '<span style="background:#FEE2E2;color:#EF4444;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px">🕵️ Competitor Reverse</span>'
            else:
                badge = '<span style="background:#F2F2F0;color:#1A1A1A;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px">🎯 Data-Driven</span>'

            with st.container():
                thumbs_html = ""
                if images:
                    thumb_imgs = "".join([
                        f'<img src="https://images.weserv.nl/?url={urllib.parse.quote(img.get("image_url",""),safe="")}&w=80&h=80&fit=cover&output=jpg"'
                        f' style="width:52px;height:52px;border-radius:6px;object-fit:cover;background:#EFEFED"'
                        f' onerror="this.style.display=\'none\'">'
                        for img in images[:4]
                    ])
                    extra = f'<div style="width:52px;height:52px;border-radius:6px;background:#EFEFED;display:flex;align-items:center;justify-content:center;font-size:11px;color:#9A9A9A">+{len(images)-4}</div>' if len(images) > 4 else ""
                    thumbs_html = (
                        f'<div style="display:flex;gap:6px;margin-top:8px;padding-top:8px;border-top:1px solid #E8E8E6">'
                        f'{thumb_imgs}{extra}</div>'
                    )
                st.markdown(
                    f"""<div class="history-card">
                        <div style="font-size:15px;font-weight:700;color:#e6edf3">{entry["product_name"]}{badge}</div>
                        <div class="history-meta">
                            Brand: {entry["brand_name"] or "—"} &nbsp;·&nbsp;
                            {entry["variants_qty"]} image(s) &nbsp;·&nbsp;
                            {ts} &nbsp;·&nbsp;
                            <span style="font-family:monospace;color:#1A1A1A">{entry["ugc_id"]}</span>
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
                                    st.markdown(f'<div style="margin:6px 0 10px;padding:6px 8px;background:#F8F8F6;border:1px solid #E8E8E6;border-radius:6px;font-family:\'DM Mono\',monospace;font-size:10px;color:#6B6B6B;word-break:break-all;line-height:1.4">{filename}</div>', unsafe_allow_html=True)
                                    get_download_button(url, filename, key_suffix=f"hist_{entry['id']}_{i}")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — BRANDS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "brands":
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
elif page == "products":
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
            st.markdown(f'<p style="font-size:11px;font-weight:700;color:#9A9A9A;text-transform:uppercase;letter-spacing:0.8px;margin:16px 0 6px">{bname}</p>', unsafe_allow_html=True)
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
elif page == "settings":
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

        loc_webhook = st.text_input(
            "Localize Webhook URL",
            value=st.session_state.get("localize_webhook_url", LOCALIZE_WEBHOOK_URL),
            placeholder="https://….app.n8n.cloud/webhook/localize-v1",
        )
        if st.button("Save Localize URL"):
            st.session_state["localize_webhook_url"] = loc_webhook
            st.success("Localize webhook URL updated.")

        ugc_video_webhook = st.text_input(
            "UGC Video Webhook URL",
            value=st.session_state.get("ugc_video_webhook_url", UGC_VIDEO_WEBHOOK_URL),
            placeholder="https://….app.n8n.cloud/webhook/ugc-video-create",
        )
        if st.button("Save UGC Video URL"):
            st.session_state["ugc_video_webhook_url"] = ugc_video_webhook
            st.success("UGC Video webhook URL updated.")

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
        st.markdown('<p style="font-size:11px;color:#9A9A9A;margin:0 0 10px;font-family:monospace">Supabase (cloud)</p>', unsafe_allow_html=True)
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
                f'<div style="background:#F8F8F6;border:1px solid #E8E8E6;border-radius:8px;padding:12px 14px;text-align:center">'
                f'<div style="font-size:20px;font-weight:700;color:#e6edf3">{v}</div>'
                f'<div style="font-size:10px;color:#9A9A9A;text-transform:uppercase;letter-spacing:0.5px;margin-top:2px">{k}</div>'
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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — LOCALIZE ADS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "localize":
    page_header("Localize Ads", "Translate your ad creatives for specific European markets.")

    loc_left, loc_right = st.columns([1, 1], gap="large")

    # ── RIGHT COL — results ────────────────────────────────────────────────
    with loc_right:
        st.markdown('<span class="sec-label">Output</span>', unsafe_allow_html=True)

        if st.session_state.get("last_loc_results"):
            loc_images = st.session_state["last_loc_results"]
            brand_id   = st.session_state.get("last_loc_brand_id")
            loc_ad_id  = st.session_state.get("last_loc_ad_id", "loc")

            st.markdown(
                f'<p style="font-size:12px;color:#22c55e;font-weight:700;margin-bottom:12px">'
                f'✅ {len(loc_images)} localized version{"s" if len(loc_images)!=1 else ""}</p>',
                unsafe_allow_html=True,
            )

            # 2-col grid
            res_cols = st.columns(2, gap="small")
            for i, img in enumerate(loc_images):
                url          = img.get("image_url", "")
                country      = img.get("country", "unknown")
                language     = img.get("language", "")
                flag         = img.get("flag", "🌍")
                preview_text = img.get("texts_preview", "") or ""
                filename     = f"{_slugify(country)}_{loc_ad_id}"

                with res_cols[i % 2]:
                    # image via st.image — no iframe gap
                    if url:
                        try:
                            st.image(url, use_container_width=True)
                        except Exception:
                            st.markdown('<div class="img-placeholder" style="height:120px">No image</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="img-placeholder" style="height:120px">No image</div>', unsafe_allow_html=True)

                    # flag + language + country — immediately below image
                    st.markdown(
                        f'**{flag} {language}** — {country.title()}',
                    )

                    # texts_preview — only if non-empty and not "No translation"
                    _preview_clean = preview_text.strip()
                    if _preview_clean and _preview_clean.lower() not in ("no translation", "no translation.", ""):
                        short = (_preview_clean[:100] + "…") if len(_preview_clean) > 100 else _preview_clean
                        st.caption(f'*"{short}"*')

                    # Save + Download — small, side by side, space filler on right
                    b1, b2, _ = st.columns([1, 1, 2])
                    with b1:
                        if st.button("💾 Save", key=f"loc_save_{i}", use_container_width=True):
                            save_ad_image(brand_id, url, filename, mode="localized")
                            st.success("Saved!")
                    with b2:
                        if url:
                            get_download_button(url, filename, label="⬇️", key_suffix=f"loc_{i}")
        else:
            st.markdown(
                '<div class="kie-img-placeholder">🌍 Localized ads will appear here</div>',
                unsafe_allow_html=True,
            )

    # ── LEFT COL — inputs ──────────────────────────────────────────────────
    with loc_left:

        # initialise selection lists before the tabs so they're always in scope
        selected_ad_urls: list[dict] = []
        uploaded_images:  list[dict] = []

        # ── Source: Saved Ads or Upload ──────────────────────────────────
        src_tab1, src_tab2 = st.tabs(["📚 Saved Ads", "📤 Upload"])

        with src_tab1:
            tf1, tf2 = st.columns([3, 2], gap="small")
            with tf1:
                loc_brand_filter = st.selectbox(
                    "Brand", ["All Brands"] + brand_names,
                    key="loc_brand_filter", label_visibility="collapsed",
                )
            loc_filter_id = None
            if loc_brand_filter != "All Brands" and loc_brand_filter in brand_names:
                loc_filter_id = brand_ids[brand_names.index(loc_brand_filter)]

            loc_ads = get_saved_ads(brand_id=loc_filter_id)

            if not loc_ads:
                st.info("No saved ads yet — generate & save some, or use the Upload tab.")
            else:
                with tf2:
                    st.markdown(
                        f'<div style="font-size:11px;color:#6B6B6B;padding-top:8px">'
                        f'{len(loc_ads)} ad{"s" if len(loc_ads)!=1 else ""}</div>',
                        unsafe_allow_html=True,
                    )
                MAX_SHOW = 12
                g_cols = st.columns(4)
                for i, ad in enumerate(loc_ads[:MAX_SHOW]):
                    url      = ad.get("image_url", "")
                    filename = ad.get("headline") or f"ad_{ad['id']}"
                    is_checked = st.session_state.get(f"loc_sel_{ad['id']}", False)
                    border = "2px solid rgba(124,58,237,0.7)" if is_checked else "1px solid #E8E8E6"
                    with g_cols[i % 4]:
                        if url:
                            encoded = urllib.parse.quote(url.strip(), safe="")
                            proxy   = f"https://images.weserv.nl/?url={encoded}&w=160&h=160&fit=cover&output=jpg"
                            st.markdown(
                                f'<img src="{proxy}" style="width:100%;border-radius:6px;display:block;'
                                f'border:{border};margin-bottom:2px">',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown('<div style="height:60px;background:#F8F8F6;border-radius:6px;margin-bottom:2px"></div>', unsafe_allow_html=True)
                        if st.checkbox("✓", key=f"loc_sel_{ad['id']}", label_visibility="collapsed"):
                            selected_ad_urls.append({
                                "image_url":  url,
                                "filename":   filename,
                                "brand_id":   ad.get("brand_id"),
                                "brand_name": ad.get("brand_name", ""),
                            })
                        short = filename[-16:] if len(filename) > 16 else filename
                        st.markdown(
                            f'<div style="font-size:8px;color:#9A9A9A;font-family:monospace;'
                            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:6px"'
                            f' title="{filename}">{short}</div>',
                            unsafe_allow_html=True,
                        )
                if len(loc_ads) > MAX_SHOW:
                    st.caption(f"Showing first {MAX_SHOW}. Filter by brand to narrow down.")

        with src_tab2:
            up_files = st.file_uploader(
                "Drag & drop or browse",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="loc_upload",
                label_visibility="collapsed",
            )
            if up_files:
                up_cols = st.columns(4)
                for i, uf in enumerate(up_files):
                    raw = uf.read()
                    b64 = base64.b64encode(raw).decode()
                    uploaded_images.append({"name": uf.name, "data": b64, "type": uf.type})
                    with up_cols[i % 4]:
                        st.image(raw, use_container_width=True)
                        st.markdown(
                            f'<div style="font-size:8px;color:#9A9A9A;font-family:monospace;'
                            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:6px">'
                            f'{uf.name[:16]}</div>',
                            unsafe_allow_html=True,
                        )

        # ── Target markets — always visible, outside tabs ─────────────────
        st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)
        mh1, mh2, mh3 = st.columns([3, 1, 1])
        with mh1:
            st.markdown('<span class="sec-label">Target Markets</span>', unsafe_allow_html=True)
        with mh2:
            if st.button("All", key="loc_sel_all", use_container_width=True):
                for c in LOCALIZE_COUNTRIES:
                    st.session_state[f"loc_country_{c['code']}"] = True
                st.rerun()
        with mh3:
            if st.button("None", key="loc_clear_all", use_container_width=True):
                for c in LOCALIZE_COUNTRIES:
                    st.session_state[f"loc_country_{c['code']}"] = False
                st.rerun()

        selected_countries: list[dict] = []
        cc_cols = st.columns(4)
        for i, country in enumerate(LOCALIZE_COUNTRIES):
            with cc_cols[i % 4]:
                if st.checkbox(f"{country['flag']} {country['name']}", key=f"loc_country_{country['code']}"):
                    selected_countries.append(country)

        # ── Summary + submit — always visible, outside tabs ───────────────
        st.markdown('<hr class="kie-divider">', unsafe_allow_html=True)

        n_ads_sel = len(selected_ad_urls) + len(uploaded_images)
        n_mkt_sel = len(selected_countries)
        n_total   = n_ads_sel * n_mkt_sel
        ready     = n_ads_sel > 0 and n_mkt_sel > 0

        if ready:
            st.markdown(
                f'<div style="font-size:12px;color:#6B6B6B;margin-bottom:8px">'
                f'<b style="color:#1A1A1A">{n_ads_sel}</b> ad{"s" if n_ads_sel!=1 else ""} × '
                f'<b style="color:#1A1A1A">{n_mkt_sel}</b> market{"s" if n_mkt_sel!=1 else ""} '
                f'= <b style="color:#C8F060">{n_total} output{"s" if n_total!=1 else ""}</b></div>',
                unsafe_allow_html=True,
            )
        elif n_ads_sel == 0:
            st.markdown('<div style="font-size:11px;color:#9A9A9A;margin-bottom:8px">Select or upload at least one ad</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:11px;color:#9A9A9A;margin-bottom:8px">Select at least one market</div>', unsafe_allow_html=True)

        loc_btn = st.button(
            f"🌍  Localize  ·  {n_total} output{'s' if n_total!=1 else ''}" if ready else "🌍  Localize",
            disabled=not ready,
            use_container_width=True,
            type="primary",
            key="loc_submit_btn",
        )

        if loc_btn and ready:
            ugc_id       = f"loc_{int(time.time())}"
            first_ad     = selected_ad_urls[0] if selected_ad_urls else {}
            brand_id_loc = first_ad.get("brand_id")

            payload = {
                "ugc_id":          ugc_id,
                "image_urls":      [a["image_url"] for a in selected_ad_urls if a["image_url"]],
                "uploaded_images": uploaded_images,
                "countries":       [{"code": c["code"], "language": c["language"], "name": c["name"]} for c in selected_countries],
                "brand_id":        str(brand_id_loc) if brand_id_loc else "",
                "brand_name":      first_ad.get("brand_name", ""),
            }

            with st.spinner("🌍 Localizing your ads… this may take 2–4 minutes"):
                try:
                    resp = requests.post(
                        st.session_state.get("localize_webhook_url", LOCALIZE_WEBHOOK_URL),
                        json=payload,
                        timeout=300,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "completed":
                            st.session_state["last_loc_results"]  = data.get("localized_ads", [])
                            st.session_state["last_loc_brand_id"] = brand_id_loc
                            st.session_state["last_loc_ad_id"]    = data.get("ad_id", ugc_id)
                            st.rerun()
                        else:
                            st.error(f"Unexpected status: {data.get('status')}")
                            st.code(resp.text[:1000])
                    else:
                        st.error(f"Webhook error: HTTP {resp.status_code}")
                        st.code(resp.text[:1000])
                except requests.exceptions.Timeout:
                    st.error("⏱️ Timed out after 5 minutes. Check your n8n workflow.")
                except requests.exceptions.ConnectionError:
                    st.error("Connection failed — check the Localize webhook URL in Settings.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — UGC VIDEO
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "ugc-video":
    page_header("UGC Video", "Generate UGC-style product videos powered by Kie.ai Sora.")

    ugc_webhook_url  = st.session_state.get("ugc_video_webhook_url", UGC_VIDEO_WEBHOOK_URL)
    ugc_status_url   = UGC_VIDEO_STATUS_URL
    UGC_POLL_TIMEOUT = 600  # 10 minutes

    vid_left, vid_right = st.columns([1, 1], gap="large")

    # ── LEFT COL — inputs ─────────────────────────────────────────────────────
    with vid_left:
        st.markdown('<span class="sec-label">Input</span>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Product Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload the product image to feature in the video.",
        )

        product_description = st.text_area(
            "Product Description",
            placeholder="Describe your product, key benefits, target audience...",
            height=120,
        )

        orientation = st.selectbox("Orientation", ["portrait", "landscape"], index=0)

        col_len, col_shot = st.columns(2)
        with col_len:
            total_length = st.selectbox(
                "Total Length",
                [10, 15, 25],
                index=1,
                format_func=lambda x: f"{x}s",
            )
        with col_shot:
            shot_duration = st.selectbox(
                "Shot Duration",
                [3, 5],
                index=1,
                format_func=lambda x: f"{x}s",
            )

        scenes_count = total_length // shot_duration
        st.info(f"📊 This will generate **{scenes_count} scene{'s' if scenes_count != 1 else ''}**")

        is_polling = bool(st.session_state.get("ugc_video_task_id"))
        generate_btn = st.button(
            "🎬 Generate UGC Video",
            disabled=(uploaded_file is None or not product_description.strip() or is_polling),
            use_container_width=True,
            type="primary",
        )

        if generate_btn:
            image_bytes = uploaded_file.read()
            image_b64   = base64.b64encode(image_bytes).decode("utf-8")
            ugc_id      = f"ugc_{int(time.time())}"

            payload = {
                "ugc_id":               ugc_id,
                "product_image_b64":    image_b64,
                "product_image_name":   uploaded_file.name,
                "product_description":  product_description,
                "orientation":          orientation,
                "total_length":         total_length,
                "shot_duration":        shot_duration,
                "brand_name":           st.session_state.get("selected_brand_name", ""),
            }

            # Reset state
            st.session_state["ugc_video_result"]     = None
            st.session_state["ugc_video_error"]      = None
            st.session_state["ugc_video_task_id"]    = None
            st.session_state["ugc_video_poll_start"] = None

            try:
                resp = requests.post(ugc_webhook_url, json=payload, timeout=30)
                if resp.status_code == 200:
                    data    = resp.json()
                    task_id = data.get("task_id")
                    if task_id:
                        st.session_state["ugc_video_task_id"]    = task_id
                        st.session_state["ugc_video_poll_start"] = time.time()
                        st.rerun()
                    else:
                        # Workflow responded synchronously with result already
                        st.session_state["ugc_video_result"] = data
                        st.rerun()
                else:
                    st.session_state["ugc_video_error"] = f"Webhook error: HTTP {resp.status_code} — {resp.text[:500]}"
                    st.rerun()
            except requests.exceptions.Timeout:
                st.session_state["ugc_video_error"] = "Connection timed out — check the UGC Video webhook URL in Settings."
                st.rerun()
            except requests.exceptions.ConnectionError:
                st.session_state["ugc_video_error"] = "Connection failed — check the UGC Video webhook URL in Settings."
                st.rerun()
            except Exception as e:
                st.session_state["ugc_video_error"] = f"Error: {e}"
                st.rerun()

    # ── RIGHT COL — output ────────────────────────────────────────────────────
    with vid_right:
        st.markdown('<span class="sec-label">Output</span>', unsafe_allow_html=True)

        _task_id    = st.session_state.get("ugc_video_task_id")
        _result     = st.session_state.get("ugc_video_result")
        _error      = st.session_state.get("ugc_video_error")
        _poll_start = st.session_state.get("ugc_video_poll_start")

        if _error:
            st.error(_error)

        elif _task_id:
            # ── Polling loop ──────────────────────────────────────────────
            elapsed = time.time() - (_poll_start or time.time())

            if elapsed >= UGC_POLL_TIMEOUT:
                st.session_state["ugc_video_task_id"]    = None
                st.session_state["ugc_video_poll_start"] = None
                st.error("⏱ Timeout — il video non è stato completato in 10 minuti. Riprova più tardi.")
            else:
                mins_left = int((UGC_POLL_TIMEOUT - elapsed) // 60)
                secs_left = int((UGC_POLL_TIMEOUT - elapsed) % 60)
                st.info(f"🎬 Video in elaborazione… ({int(elapsed)}s trascorsi — timeout tra {mins_left}m {secs_left:02d}s)")

                try:
                    poll_resp = requests.get(
                        ugc_status_url,
                        params={"task_id": _task_id},
                        timeout=10,
                    )
                    if poll_resp.status_code == 200:
                        poll_data  = poll_resp.json()
                        vid_status = poll_data.get("status", "pending")

                        if vid_status == "success":
                            st.session_state["ugc_video_result"]     = poll_data
                            st.session_state["ugc_video_task_id"]    = None
                            st.session_state["ugc_video_poll_start"] = None
                            st.rerun()
                        elif vid_status == "failed":
                            st.session_state["ugc_video_task_id"]    = None
                            st.session_state["ugc_video_poll_start"] = None
                            st.session_state["ugc_video_error"]      = f"Generazione fallita: {poll_data.get('message', 'unknown error')}"
                            st.rerun()
                        else:
                            # still pending — wait 15s then rerun
                            time.sleep(15)
                            st.rerun()
                    else:
                        st.warning(f"Status check error: HTTP {poll_resp.status_code}")
                        time.sleep(15)
                        st.rerun()
                except Exception as _pe:
                    st.warning(f"Polling error: {_pe}")
                    time.sleep(15)
                    st.rerun()

        elif _result:
            video_url = _result.get("video_url", "")

            st.success("✅ UGC Video pronto!")

            if video_url:
                st.video(video_url)

                dl_col, link_col, _ = st.columns([1, 1, 2])
                with dl_col:
                    st.link_button("⬇ Download", video_url, use_container_width=True)
                with link_col:
                    with st.expander("🔗 Link"):
                        st.code(video_url, language=None)
            else:
                st.warning("Video URL non trovato nella risposta.")
                st.json(_result)

        else:
            st.markdown(
                '<div class="kie-img-placeholder">🎬 Il video generato apparirà qui</div>',
                unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 10 — ADMIN: USERS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "users":
    if st.session_state.get("auth_role") != "admin":
        st.error("⛔ Access denied — admin only.")
        st.stop()

    page_header("Users", "Manage workspace members and their access roles.")

    ul, ur = st.columns([1.4, 1], gap="large")

    # ── Left: user list ───────────────────────────────────────────────────────
    with ul:
        st.markdown('<span class="sec-label">Members</span>', unsafe_allow_html=True)
        all_users = auth_get_users()
        if not all_users:
            st.info("No users found. Add one using the form.")
        for u in all_users:
            _uname  = u.get("name", "—")
            _uemail = u.get("email", "—")
            _urole  = u.get("role", "user")
            _uid    = u.get("id")
            _badge  = f'<span class="user-role-badge role-{_urole}">{_urole}</span>'
            _init   = _uname[0].upper() if _uname and _uname != "—" else "?"
            _ts     = u.get("created_at", "")[:10] if u.get("created_at") else "—"

            _c1, _c2 = st.columns([5, 1])
            with _c1:
                st.markdown(
                    f'<div class="user-row">'
                    f'<div class="user-avatar">{_init}</div>'
                    f'<div style="flex:1;min-width:0">'
                    f'<div style="font-size:13px;font-weight:600;color:#1A1A1A">{_uname}</div>'
                    f'<div style="font-size:11px;color:#6B6B6B">{_uemail}</div>'
                    f'</div>'
                    f'{_badge}'
                    f'<div style="font-size:10px;color:#9A9A9A;white-space:nowrap">{_ts}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with _c2:
                _is_self = str(_uid) == str(st.session_state.get("auth_user"))
                if not _is_self:
                    if st.button("🗑", key=f"_del_usr_{_uid}", help="Delete user"):
                        if auth_delete_user(_uid):
                            st.success(f"Deleted {_uname}.")
                            st.rerun()
                        else:
                            st.error("Failed to delete user.")

    # ── Right: add user form ──────────────────────────────────────────────────
    with ur:
        st.markdown('<span class="sec-label">Add Member</span>', unsafe_allow_html=True)
        with st.form("add_user_form", clear_on_submit=True):
            new_name  = st.text_input("Full Name", placeholder="Jane Smith")
            new_email = st.text_input("Email", placeholder="jane@example.com")
            new_pass  = st.text_input("Password", type="password", placeholder="••••••••")
            new_role  = st.selectbox("Role", ["user", "admin"])
            add_btn   = st.form_submit_button("Add Member", use_container_width=True, type="primary")

        if add_btn:
            if not new_name or not new_email or not new_pass:
                st.error("Please fill in all fields.")
            elif auth_create_user(new_name, new_email, new_pass, new_role):
                st.success(f"✅ {new_name} added as {new_role}.")
                st.rerun()
            else:
                st.error("Failed to create user — email may already exist.")

        st.markdown(
            '<div style="margin-top:20px;padding:14px 16px;background:rgba(124,58,237,0.07);'
            'border:1px solid rgba(200,240,96,0.1);border-radius:10px;font-size:12px;color:#6B6B6B;line-height:1.6">'
            '<strong style="color:#C8F060">Note:</strong> This requires a <code>users</code> table in Supabase with columns: '
            '<code>id</code>, <code>name</code>, <code>email</code>, <code>password_hash</code>, '
            '<code>role</code>, <code>created_at</code>.'
            '</div>',
            unsafe_allow_html=True,
        )

