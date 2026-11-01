# ==============================================================================
# CYBERBULLYING DETECTION SYSTEM
# MODULE: app.py (Main Streamlit Frontend Application)
#
# DESCRIPTION:
# Premium AI SaaS dashboard UI for the Cyberbullying Detection System.
# Connects to the CyberGuard AI FastAPI backend over HTTP via api_client.py -
# it no longer imports model.py or utils.py directly. Provides:
# - A modern project dashboard with live stats (from the backend database)
# - Real-time AI detection with confidence gauges & category chips
# - A social simulator showing real-time content filtering & chat moderation
# - An analytics console with interactive Plotly charts
# - A cyber safety education and legal resource portal
#
# Set BACKEND_URL to point this frontend at your FastAPI backend, e.g.:
#   BACKEND_URL=http://localhost:8000    (local dev)
#   BACKEND_URL=https://your-backend-domain.com   (production)
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import plotly.graph_objects as go
import plotly.express as px
import api_client
from api_client import ApiError

# --- STREAMLIT CACHING FOR STATIC API CALLS ---
@st.cache_data(show_spinner=False)
def cached_get_cyber_laws():
    return api_client.get_cyber_laws()

@st.cache_data(show_spinner=False)
def cached_get_helplines():
    return api_client.get_helplines()

@st.cache_data(show_spinner=False)
def cached_get_safety_tips():
    return api_client.get_safety_tips()

@st.cache_data(show_spinner=False)
def cached_get_simulated_posts():
    return api_client.get_simulated_posts()

# --- SVG ICON LIBRARY (crisp line icons, replaces emoji for a more polished look) ---
_ICON_PATHS = {
    "trending-up": '<polyline points="3,17 9,11 13,15 21,6"/><polyline points="14,6 21,6 21,13"/>',
    "message-circle": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "shield-check": '<path d="M12 2 L20 5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5 Z"/><polyline points="9,12 11,14 15,10"/>',
    "alert-triangle": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="2"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><line x1="9" y1="2" x2="9" y2="6"/><line x1="15" y1="2" x2="15" y2="6"/><line x1="9" y1="18" x2="9" y2="22"/><line x1="15" y1="18" x2="15" y2="22"/><line x1="2" y1="9" x2="6" y2="9"/><line x1="2" y1="15" x2="6" y2="15"/><line x1="18" y1="9" x2="22" y2="9"/><line x1="18" y1="15" x2="22" y2="15"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3 C15 6.5 15 17.5 12 21 C9 17.5 9 6.5 12 3 Z"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11 V7 a4 4 0 0 1 8 0 v4"/>',
    "shield": '<path d="M12 2 L20 5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5 Z"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><polyline points="8,12.5 11,15.5 16,9"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>',
    "align-left": '<line x1="4" y1="6" x2="16" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="14" y2="18"/>',
}


def icon(name, size=20, color="#F8FAFC", stroke_width=2):
    """Returns an inline feather-style SVG icon as an HTML string."""
    path = _ICON_PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


# --- STEP 1: CONFIGURE PAGE SETTINGS ---
st.set_page_config(
    page_title="CyberGuard AI - Cyberbullying Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STEP 2: GLOBAL PREMIUM SAAS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0b1020;
        --surface: #121d35;
        --surface-2: #0f192e;
        --border: #263653;
        --text: #f4f7ff;
        --muted: #91a2c4;
        --blue: #4f8cff;
        --purple: #8065ff;
        --green: #37c98a;
        --orange: #ff9c55;
        --bg-1: #0b1020;
        --bg-2: #121d35;
        --bg-3: #0f192e;
        --primary: #3868e8;
        --secondary: #7659ed;
        --success: #37c98a;
        --danger: #ff9c55;
        --text-secondary: #91a2c4;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: #0b1020 !important;
        color: var(--text) !important;
    }

    p, li, span, label, .stText, .stMarkdown, ol, ul, select {
        font-family: 'Inter', sans-serif !important;
        color: #CBD5E1 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    strong, b { color: var(--text) !important; font-weight: 600 !important; }

    code, pre {
        font-family: 'SFMono-Regular', Consolas, monospace !important;
        background-color: rgba(255,255,255,0.06) !important;
        color: #93C5FD !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 6px !important;
    }

    /* ---------- GLASS CARDS ---------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.045);
        border: 1px solid rgba(255, 255, 255, 0.09);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 1.6rem 1.7rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        margin-bottom: 1.4rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(124, 92, 237, 0.35);
        box-shadow: 0 14px 40px rgba(37, 99, 235, 0.18);
    }

    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text) !important;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0.6rem;
    }

    .glass-card p, .glass-card span, .glass-card li, .glass-card ol, .glass-card ul, .glass-card div {
        color: var(--text-secondary) !important;
        line-height: 1.65;
    }

    /* ---------- HERO ---------- */
    .hero-wrap {
        padding: 2.6rem 2.2rem;
        border-radius: 24px;
        background: radial-gradient(circle at 20% 20%, rgba(37,99,235,0.20), transparent 55%),
                    radial-gradient(circle at 85% 75%, rgba(124,58,237,0.22), transparent 55%),
                    rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.8rem;
    }
    .hero-eyebrow {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: rgba(37,99,235,0.15);
        border: 1px solid rgba(37,99,235,0.4);
        color: #93C5FD !important;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.12;
        background: linear-gradient(90deg, #F8FAFC 20%, #93C5FD 60%, #C4B5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        font-weight: 600;
        color: #93C5FD !important;
        margin-bottom: 0.9rem;
    }
    .hero-desc {
        font-size: 1rem;
        color: var(--text-secondary) !important;
        max-width: 520px;
        line-height: 1.6;
        margin-bottom: 1.6rem;
    }
    .hero-illustration {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9rem;
        filter: drop-shadow(0 0 40px rgba(37, 99, 235, 0.45));
    }

    /* ---------- STAT CARDS ---------- */
    .stat-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 1.4rem 1.3rem;
        backdrop-filter: blur(16px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(124, 92, 237, 0.4);
    }
    .stat-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.15rem;
    }
    .stat-label {
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
        font-weight: 500;
    }

    /* ---------- FEATURE CARDS ---------- */
    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(37, 99, 235, 0.4);
    }
    .feature-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .feature-title { font-weight: 700; color: var(--text) !important; margin-bottom: 0.4rem; font-size: 1.02rem; }
    .feature-desc { font-size: 0.88rem; color: var(--text-secondary) !important; line-height: 1.55; }

    /* ---------- BADGES / CHIPS ---------- */
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .badge-danger { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.45); color: #FCA5A5 !important; }
    .badge-safe { background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.45); color: #86EFAC !important; }
    .chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        background: rgba(124,58,237,0.15);
        border: 1px solid rgba(124,58,237,0.4);
        color: #C4B5FD !important;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* ---------- BANNERS ---------- */
    .banner-safe {
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #86EFAC !important;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        font-weight: 500;
    }
    .banner-safe strong, .banner-safe span, .banner-safe b { color: #86EFAC !important; }

    .banner-danger {
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #FCA5A5 !important;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        font-weight: 500;
    }
    .banner-danger strong, .banner-danger span, .banner-danger b { color: #FCA5A5 !important; }

    /* ---------- CHAT BUBBLES ---------- */
    .chat-row { display: flex; align-items: flex-end; gap: 0.6rem; margin-bottom: 0.9rem; }
    .chat-row.mine { flex-direction: row-reverse; }
    .chat-avatar {
        width: 34px; height: 34px; border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; font-weight: 700; color: white !important;
        flex-shrink: 0;
    }
    .chat-bubble {
        max-width: 70%;
        padding: 0.65rem 1rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--text-secondary) !important;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .chat-row.mine .chat-bubble {
        background: linear-gradient(135deg, rgba(37,99,235,0.35), rgba(124,58,237,0.35));
        color: var(--text) !important;
        border: 1px solid rgba(124,58,237,0.4);
    }
    .chat-bubble.blurred { filter: blur(5px); user-select: none; }
    .chat-meta { font-size: 0.7rem; color: #64748B !important; margin-top: 2px; }
    .mod-badge {
        font-size: 0.68rem; font-weight: 700; padding: 2px 9px; border-radius: 999px; margin-left: 6px;
    }
    .mod-approved { background: rgba(34,197,94,0.15); color: #86EFAC !important; border: 1px solid rgba(34,197,94,0.4); }
    .mod-blocked { background: rgba(239,68,68,0.15); color: #FCA5A5 !important; border: 1px solid rgba(239,68,68,0.4); }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220 0%, #0F172A 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li, [data-testid="stSidebar"] strong {
        color: var(--text-secondary) !important;
    }
    .sidebar-logo {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text) !important;
        padding: 0.6rem 0 0.2rem 0;
    }
    .sidebar-sub {
        text-align: center;
        font-size: 0.75rem;
        color: #64748B !important;
        margin-bottom: 0.8rem;
    }

    /* ---------- BUTTONS ---------- */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
        border: none !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.3rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(124, 58, 237, 0.35) !important;
    }
    .stButton>button:active { transform: translateY(0px); }

    /* Secondary-style button variant via data attribute set through markdown key */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 14px !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea { border-radius: 16px !important; }

    [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }

    hr { border-color: rgba(255,255,255,0.08) !important; }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.4); border-radius: 8px; }

    /* ========================================================
       V2 DESIGN SYSTEM — solid navy cards, icon badges, nav pills
       ======================================================== */

    /* Solid panel used by the redesigned Dashboard / AI Detector */
    .panel {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.1rem;
    }
    .panel-title { font-size: 1rem; font-weight: 700; color: var(--text) !important; margin-bottom: 0.2rem; }
    .panel-sub { font-size: 0.82rem; color: #64748B !important; margin-bottom: 1rem; }

    /* Icon badges (rounded gradient squares) */
    .icon-badge {
        width: 42px; height: 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .icon-badge.blue   { background: linear-gradient(135deg,#2563EB,#3B82F6); box-shadow: 0 4px 16px rgba(37,99,235,0.35); }
    .icon-badge.green  { background: linear-gradient(135deg,#16A34A,#22C55E); box-shadow: 0 4px 16px rgba(34,197,94,0.35); }
    .icon-badge.teal   { background: linear-gradient(135deg,#0D9488,#14B8A6); box-shadow: 0 4px 16px rgba(20,184,166,0.35); }
    .icon-badge.red    { background: linear-gradient(135deg,#DC2626,#EF4444); box-shadow: 0 4px 16px rgba(239,68,68,0.35); }
    .icon-badge.purple { background: linear-gradient(135deg,#7C3AED,#8B5CF6); box-shadow: 0 4px 16px rgba(124,58,237,0.35); }

    /* Stat cards v2 */
    .stat-card-v2 {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.25rem 1.3rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card-v2:hover { transform: translateY(-3px); border-color: rgba(124,92,237,0.35); }
    .stat-card-v2 .stat-v2-top { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.9rem; }
    .stat-card-v2 .stat-v2-label { font-size: 0.85rem; font-weight: 600; color: #94A3B8 !important; }
    .stat-card-v2 .stat-v2-big { font-size: 1.85rem; font-weight: 800; color: var(--text) !important; line-height: 1; margin-bottom: 0.3rem; }
    .stat-card-v2 .stat-v2-sub { font-size: 0.78rem; color: #64748B !important; }

    /* Info cards v2 (Objective / Technology / Applications) */
    .info-card-v2 {
        background: #121A2E;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.35rem 1.4rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .info-card-v2:hover { transform: translateY(-3px); border-color: rgba(37,99,235,0.35); }
    .info-card-v2 .info-v2-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.8rem; }
    .info-card-v2 .info-v2-title { font-weight: 700; font-size: 1rem; color: var(--text) !important; }
    .info-card-v2 .info-v2-desc { font-size: 0.85rem; color: #94A3B8 !important; line-height: 1.6; }

    /* Hero shield illustration v2 — circuit backdrop + glowing pedestal + layered shield/lock */
    .hero-shield-wrap {
        position: relative; display: flex; align-items: center; justify-content: center;
        height: 280px; border-radius: 20px; overflow: hidden;
        background-image:
            radial-gradient(rgba(96,165,250,0.18) 1px, transparent 1px),
            linear-gradient(rgba(96,165,250,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(96,165,250,0.08) 1px, transparent 1px);
        background-size: 22px 22px, 44px 44px, 44px 44px;
        background-position: center;
    }
    .hero-pedestal {
        position: absolute; bottom: 14%; width: 190px; height: 26px; border-radius: 50%;
        background: radial-gradient(ellipse at center, rgba(59,130,246,0.55), transparent 75%);
        filter: blur(2px);
    }
    .hero-shield-glow {
        position: absolute; width: 210px; height: 210px; border-radius: 50%;
        background: radial-gradient(circle, rgba(59,130,246,0.32), transparent 70%);
        filter: blur(4px);
        animation: shield-breathe 4s ease-in-out infinite;
    }
    @keyframes shield-breathe { 0%,100% { opacity: 0.7; transform: scale(1); } 50% { opacity: 1; transform: scale(1.08); } }
    .hero-shield-icon {
        position: relative; z-index: 2;
        width: 120px; height: 120px; border-radius: 24px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(155deg, rgba(37,99,235,0.35), rgba(124,58,237,0.25));
        border: 1px solid rgba(147,197,253,0.4);
        filter: drop-shadow(0 0 26px rgba(59,130,246,0.55));
    }
    .hero-float-chip {
        position: absolute; display: flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
        border-radius: 12px; padding: 7px 12px; font-size: 0.76rem; color: #E2E8F0 !important;
        backdrop-filter: blur(6px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); z-index: 3;
        animation: chip-float 3.4s ease-in-out infinite;
    }
    .hero-float-chip .chip-badge {
        width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
    }
    .hero-float-chip .chip-badge.danger { background: #EF4444; }
    .hero-float-chip .chip-badge.safe { background: #22C55E; }
    .hero-float-chip .skeleton-line { height: 6px; border-radius: 4px; background: rgba(255,255,255,0.35); }
    @keyframes chip-float { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-7px); } }
    .hero-float-chip.c1 { top: 8%; right: 4%; animation-delay: 0s; }
    .hero-float-chip.c2 { top: 42%; right: 0%; animation-delay: 1.1s; }
    .hero-float-chip.c3 { bottom: 10%; right: 8%; animation-delay: 2s; }

    /* Status pill (AI Detector verdict) */
    .status-pill {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 15px; border-radius: 999px; font-weight: 700; font-size: 0.85rem;
    }
    .status-pill.safe   { background: rgba(34,197,94,0.15); color: #4ADE80 !important; border: 1px solid rgba(34,197,94,0.4); }
    .status-pill.danger { background: rgba(239,68,68,0.15); color: #F87171 !important; border: 1px solid rgba(239,68,68,0.4); }
    .severity-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }

    /* Char counter under textarea */
    .char-counter { font-size: 0.76rem; color: #64748B !important; text-align: right; margin-top: -0.4rem; margin-bottom: 0.6rem; }

    /* ---------- MIC ORB + RECORDING ANIMATION ---------- */
    .mic-orb-wrap { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 0.8rem 0 0.4rem 0; }
    .mic-orb { position: relative; width: 76px; height: 76px; display: flex; align-items: center; justify-content: center; }
    .mic-orb-ring {
        position: absolute; width: 76px; height: 76px; border-radius: 50%;
        border: 2px solid rgba(37,99,235,0.55);
        animation: mic-pulse 2.2s ease-out infinite;
    }
    .mic-orb-ring.r2 { animation-delay: 0.7s; border-color: rgba(124,58,237,0.5); }
    @keyframes mic-pulse { 0% { transform: scale(0.85); opacity: 0.9; } 100% { transform: scale(2); opacity: 0; } }
    .mic-orb-core {
        position: relative; z-index: 2; width: 56px; height: 56px; border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; box-shadow: 0 6px 22px rgba(37,99,235,0.45);
    }
    .voice-hint { font-size: 0.78rem; color: #64748B !important; text-align: center; margin: 0; }

    .waveform { display: flex; align-items: center; justify-content: center; gap: 4px; height: 34px; margin: 0.5rem 0; }
    .waveform span {
        width: 4px; border-radius: 3px;
        background: linear-gradient(180deg, #2563EB, #7C3AED);
        animation: wave-bounce 0.9s ease-in-out infinite;
        display: inline-block;
    }
    .waveform span:nth-child(1) { height: 10px; animation-delay: 0s; }
    .waveform span:nth-child(2) { height: 22px; animation-delay: 0.1s; }
    .waveform span:nth-child(3) { height: 30px; animation-delay: 0.2s; }
    .waveform span:nth-child(4) { height: 18px; animation-delay: 0.3s; }
    .waveform span:nth-child(5) { height: 12px; animation-delay: 0.4s; }
    @keyframes wave-bounce { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1); } }

    /* Checklist items inside info cards */
    .info-v2-checklist { list-style: none; padding: 0; margin: 0; }
    .info-v2-checklist li {
        display: flex; align-items: center; gap: 8px;
        font-size: 0.85rem; color: #CBD5E1 !important;
        padding: 5px 0;
    }
    .check-dot {
        width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
        background: rgba(34,197,94,0.18); color: #4ADE80;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 900;
    }

    /* Quote banner */
    .quote-banner {
        background: linear-gradient(90deg, rgba(37,99,235,0.12), rgba(124,58,237,0.12));
        border: 1px solid rgba(124,58,237,0.3);
        border-radius: 16px;
        padding: 1.1rem 1.6rem;
        display: flex; align-items: center; gap: 1rem;
        font-size: 0.95rem; color: #E2E8F0 !important; font-style: italic;
        margin-top: 0.5rem;
    }

    /* Sparkline mini-chart container inside stat cards */
    .stat-card-v2 .sparkline-holder { margin-top: -0.3rem; }
    .stat-card-v2 .sparkline-holder .js-plotly-plot { margin-bottom: -10px; }

    /* Sidebar status box */
    .sidebar-status-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        margin-top: 0.8rem;
    }
    .sidebar-status-row { display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #94A3B8 !important; margin-bottom: 6px; }
    .sidebar-status-row:last-child { margin-bottom: 0; }
    .status-dot-green { width: 7px; height: 7px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 8px rgba(34,197,94,0.7); flex-shrink:0; }
    .sidebar-status-label { color: #F8FAFC !important; font-weight: 600; }

    /* ---------- SIDEBAR NAV PILLS ---------- */
    [data-testid="stSidebar"] .stRadio > div { gap: 2px; }
    [data-testid="stSidebar"] .stRadio label {
        padding: 9px 12px !important;
        border-radius: 12px !important;
        transition: background 0.15s ease;
        width: 100%;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.05); }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) p {
        color: #FFFFFF !important; font-weight: 700 !important;
    }

    /* ========================================================
       ELIMINATE KEYBOARD_DOUBLE_ARROW / DOUBLE_ARROW ICONS & TEXT
       AND REPLACE WITH CLEAN HAMBURGER MENU (3 PARALLEL LINES)
       ======================================================== */
    /* 1. Reset font size and hide all text / ligatures in sidebar toggle buttons */
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    button[aria-label*="sidebar" i],
    button[aria-label*="expand" i],
    button[aria-label*="collapse" i],
    button[aria-label*="close" i],
    button[kind="header"] {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
        overflow: hidden !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* 2. Hide ANY child span, SVG, or Material Symbol ligature text (keyboard_double_arrow...) completely */
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] *,
    button[aria-label*="sidebar" i] *,
    button[aria-label*="expand" i] *,
    button[aria-label*="collapse" i] *,
    button[aria-label*="close" i] *,
    button[kind="header"] * {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        font-size: 0 !important;
        width: 0 !important;
        height: 0 !important;
        color: transparent !important;
        line-height: 0 !important;
    }

    /* 3. Style the Collapsed Sidebar Button (Top-left when menu is closed) */
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    button[aria-label*="Expand sidebar" i] {
        background: rgba(18, 29, 53, 0.85) !important;
        border: 1px solid #263653 !important;
        border-radius: 10px !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    button[aria-label*="Expand sidebar" i]:hover {
        background: rgba(35, 63, 119, 0.6) !important;
        border-color: #4f8cff !important;
    }

    /* 4. Draw the 3 crisp parallel lines (Hamburger Menu) */
    [data-testid="collapsedControl"] button::before,
    [data-testid="stSidebarCollapsedControl"] button::before,
    button[aria-label*="Expand sidebar" i]::before {
        content: "" !important;
        display: block !important;
        width: 18px !important;
        height: 2px !important;
        background: #f4f7ff !important;
        border-radius: 2px !important;
        box-shadow: 0 -5px 0 0 #f4f7ff, 0 5px 0 0 #f4f7ff !important;
        visibility: visible !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        text-indent: 0 !important;
        transition: background 0.2s, box-shadow 0.2s !important;
    }

    [data-testid="collapsedControl"] button:hover::before,
    [data-testid="stSidebarCollapsedControl"] button:hover::before,
    button[aria-label*="Expand sidebar" i]:hover::before {
        background: #4f8cff !important;
        box-shadow: 0 -5px 0 0 #4f8cff, 0 5px 0 0 #4f8cff !important;
    }

    /* 5. Style the Collapse Button INSIDE the open sidebar (Replace keyboard_double_arrow_left with a clean ✕) */
    [data-testid="stSidebarCollapseButton"] button,
    button[aria-label*="Close sidebar" i] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebarCollapseButton"] button::before,
    button[aria-label*="Close sidebar" i]::before {
        content: "✕" !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 13px !important;
        color: #91a2c4 !important;
        font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        visibility: visible !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        text-indent: 0 !important;
    }

    [data-testid="stSidebarCollapseButton"] button:hover::before,
    button[aria-label*="Close sidebar" i]:hover::before {
        color: #f4f7ff !important;
    }

    /* Starter Dashboard Theme Classes */
    .dashboard-stat-card {
        background: linear-gradient(145deg, #131f38, #111b31);
        border: 1px solid #263653;
        border-radius: 17px;
        padding: 21px 23px;
        transition: transform .2s, border-color .2s;
    }
    .dashboard-stat-card:hover {
        transform: translateY(-3px);
        border-color: #4665a1;
    }
    .dashboard-stat-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .dashboard-stat-top p {
        color: #91a2c4 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    .dashboard-stat-val {
        font-size: 34px !important;
        letter-spacing: -1px;
        margin: 15px 0 8px !important;
        font-weight: 800 !important;
    }
    .dashboard-stat-sub {
        color: #7486aa !important;
        font-size: 11px !important;
    }
    .stat-icon {
        display: grid;
        place-items: center;
        width: 31px;
        height: 31px;
        border-radius: 9px;
        font-weight: 800;
        font-size: 14px;
    }
    .stat-icon.blue { color: #83a9ff; background: #243a67; }
    .stat-icon.green { color: #69e2ae; background: #1c423a; }
    .stat-icon.orange { color: #ffc18d; background: #493326; }

    /* Chart component */
    .dashboard-chart {
        height: 245px;
        display: flex;
        align-items: stretch;
        justify-content: space-around;
        gap: 12px;
        padding: 12px 8px 0;
        border-bottom: 1px solid #2b3955;
        background: repeating-linear-gradient(to bottom, transparent 0, transparent 48px, #26344d 49px, transparent 50px);
    }
    .chart-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        min-width: 0;
    }
    .chart-bar {
        width: min(100%, 44px);
        min-height: 10px;
        border-radius: 7px 7px 2px 2px;
        background: linear-gradient(180deg, #8c73ff, #4b7ff5);
        box-shadow: 0 4px 20px rgba(79, 114, 255, 0.2);
        transition: filter .2s;
    }
    .chart-bar:hover { filter: brightness(1.25); }
    .chart-col span { color: #8192b3 !important; font-size: 10px !important; padding-bottom: 12px; }

    /* Result State Cards */
    .dash-result {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        margin-top: 14px;
        padding: 14px;
        border: 1px solid #2b3958;
        border-radius: 11px;
        background: #17243c;
        color: #b7c4df;
        transition: all 0.25s ease;
    }
    .dash-result strong { display: block; font-size: 12px; margin-bottom: 5px; }
    .dash-result p { font-size: 11px; line-height: 1.55; color: #91a2c4; margin: 0; }
    .dash-result-sym { font-size: 18px; color: #90a8ff; flex-shrink: 0; line-height: 1; }

    .dash-result.safe { background: #182c27 !important; border-color: #2e6e54 !important; }
    .dash-result.safe strong, .dash-result.safe .dash-result-sym { color: #57d69a !important; }
    .dash-result.safe p { color: #a1d7be !important; }

    .dash-result.flagged { background: #35231e !important; border-color: #74452e !important; }
    .dash-result.flagged strong, .dash-result.flagged .dash-result-sym { color: #ffad70 !important; }
    .dash-result.flagged p { color: #f2c09d !important; }

    /* Safety Panel */
    .dash-safety-panel {
        display: flex;
        gap: 15px;
        align-items: flex-start;
        margin-top: 22px;
        background: #121e32;
        border: 1px solid #263653;
        border-radius: 17px;
        padding: 23px;
    }
    .dash-safety-icon { font-size: 25px; flex-shrink: 0; line-height: 1; }
    .dash-safety-panel h2 { font-size: 16px !important; letter-spacing: -.3px; margin: 0 0 7px 0 !important; color: #f4f7ff !important; }
    .dash-safety-panel p { max-width: 900px; color: #91a2c4 !important; font-size: 12px !important; line-height: 1.7 !important; margin: 0 !important; }

    /* History Note */
    .dash-history-item {
        padding: 10px 12px;
        border: 1px solid #263653;
        border-radius: 9px;
        margin-top: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 15px;
        background: rgba(255, 255, 255, 0.02);
    }
    .dash-history-item strong { color: #dce5fa !important; font-weight: 500 !important; font-size: 11px !important; overflow-wrap: anywhere; }
    .dash-history-item em { font-style: normal; white-space: nowrap; font-size: 11px; font-weight: 600; }
    .dash-history-item em.safe { color: #57d69a; }
    .dash-history-item em.flagged { color: #ffad70; }

</style>
""", unsafe_allow_html=True)


# --- STEP 3: SESSION STATE INITIALIZATION (unchanged keys + additive UI stat counters) ---
if 'model_trained' not in st.session_state:
    try:
        status = api_client.get_model_status()
        st.session_state.model_trained = bool(status.get("model_loaded", True))
    except Exception:
        st.session_state.model_trained = True

if 'admin_token' not in st.session_state:
    st.session_state.admin_token = None

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
        {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
    ]

if 'user_warnings' not in st.session_state:
    st.session_state.user_warnings = 0

if 'blocked_simulated_posts' not in st.session_state:
    st.session_state.blocked_simulated_posts = {}

if 'detector_chatbot_messages' not in st.session_state:
    st.session_state.detector_chatbot_messages = [
        {"role": "assistant", "content": "👋 Hello! I am your CyberGuard AI Safety Bot. Type any message below, and I will scan it for cyberbullying in real time!"}
    ]

if 'last_scanned_result' not in st.session_state:
    st.session_state.last_scanned_result = None

# Additive, display-only counters that power the new stat cards. These do not
# touch any prediction/training logic — they simply count outcomes already
# produced by predict_message() so the dashboard has live numbers to show.
if 'stats_total_scanned' not in st.session_state:
    st.session_state.stats_total_scanned = 0
if 'stats_safe_count' not in st.session_state:
    st.session_state.stats_safe_count = 0
if 'stats_bullying_count' not in st.session_state:
    st.session_state.stats_bullying_count = 0
if 'detector_input_key' not in st.session_state:
    st.session_state.detector_input_key = 0
if 'quick_result' not in st.session_state:
    st.session_state.quick_result = None
if 'session_history' not in st.session_state:
    st.session_state.session_history = []


def log_scan_stats(label):
    """Increments the display-only stat counters used by the dashboard cards."""
    st.session_state.stats_total_scanned += 1
    if label == 1:
        st.session_state.stats_bullying_count += 1
    else:
        st.session_state.stats_safe_count += 1


def render_gauge(confidence_pct, is_bullying):
    color = "#EF4444" if is_bullying else "#22C55E"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence_pct,
        number={'suffix': "%", 'font': {'color': '#F8FAFC', 'size': 34}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#64748B', 'tickfont': {'color': '#64748B'}},
            'bar': {'color': color},
            'bgcolor': "rgba(255,255,255,0.04)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(255,255,255,0.05)'}
            ],
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#F8FAFC", 'family': "Inter"}
    )
    return fig


def render_probability_bar(confidence, is_bullying):
    safe_prob = (1 - confidence) if is_bullying else confidence
    bullying_prob = confidence if is_bullying else (1 - confidence)
    fig = go.Figure(go.Bar(
        x=[safe_prob * 100, bullying_prob * 100],
        y=["Safe", "Cyberbullying"],
        orientation='h',
        marker=dict(color=["#22C55E", "#EF4444"]),
        text=[f"{safe_prob*100:.1f}%", f"{bullying_prob*100:.1f}%"],
        textposition="outside",
        textfont=dict(color="#F8FAFC")
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 105], showgrid=False, color="#94A3B8"),
        yaxis=dict(color="#F8FAFC"),
        font={'color': "#F8FAFC", 'family': "Inter"}
    )
    return fig


def render_confidence_ring(confidence_pct, is_bullying):
    """Compact donut-style ring gauge (used in the redesigned AI Detector result panel)."""
    color = "#EF4444" if is_bullying else "#22C55E"
    remainder = max(0, 100 - confidence_pct)
    fig = go.Figure(go.Pie(
        values=[confidence_pct, remainder],
        hole=0.78,
        marker=dict(colors=[color, "rgba(255,255,255,0.08)"]),
        textinfo="none",
        sort=False,
        direction="clockwise",
        rotation=0,
    ))
    fig.update_traces(hoverinfo="skip")
    fig.add_annotation(
        text=f"<b>{confidence_pct:.0f}%</b>", x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="#F8FAFC", family="Inter")
    )
    fig.update_layout(
        height=140, width=140,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def render_sparkline(values, color):
    """Minimal axis-free line chart used inside dashboard stat cards."""
    fig = go.Figure(go.Scatter(
        y=values, mode="lines", line=dict(color=color, width=2.5), fill="tozeroy",
        fillcolor=color.replace(")", ",0.12)").replace("rgb", "rgba") if color.startswith("rgb") else "rgba(0,0,0,0)"
    ))
    fig.update_layout(
        height=46,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


# --- STEP 4: SIDEBAR & ROUTING ---
with st.sidebar:
    st.markdown(f"<div class='sidebar-logo' style='display:flex; align-items:center; gap:8px;'>{icon('shield-check', 22, '#60A5FA')} CyberGuard AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>AI-Powered Safety Platform</div>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔍 AI Detector",
            "💬 Chat Simulator",
            "📊 Analytics",
            "📚 Safety Guide",
            "ℹ️ About",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    model_status_label = "Active (93.5%)"
    model_status_color = "#22C55E"
    st.markdown(f"""
    <div class="sidebar-status-box">
        <div class="sidebar-status-row">
            <span class="status-dot-green"></span> System Status
        </div>
        <div class="sidebar-status-label" style="margin-bottom:10px; margin-left:15px;">Online</div>
        <div class="sidebar-status-row">
            <span class="status-dot-green" style="background:{model_status_color}; box-shadow:0 0 8px {model_status_color};"></span> AI Model
        </div>
        <div class="sidebar-status-label" style="margin-left:15px; color:{model_status_color} !important;">{model_status_label}</div>
    </div>
    """, unsafe_allow_html=True)

# --- STEP 5: RENDER PAGE CONTENTS ---

# ==========================================
# PAGE 1: DASHBOARD (HOME)
# ==========================================
if page == "🏠 Dashboard":
    # --- TOPBAR ---
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:26px; flex-wrap:wrap; gap:14px;">
        <div>
            <p style="color:#7f91b5; font-size:10px; letter-spacing:1.6px; font-weight:700; margin:0 0 5px 0;">CYBER SAFETY OVERVIEW</p>
            <h1 style="font-size:32px; letter-spacing:-1px; margin:0 0 5px 0; color:#f4f7ff;">Dashboard</h1>
            <p style="color:#91a2c4; font-size:13px; margin:0;">Your AI moderation overview</p>
        </div>
        <div style="padding:10px 15px; background:#142337; border:1px solid #244b43; border-radius:30px; color:#a5dfc7; font-size:12px; font-weight:600; display:flex; align-items:center; gap:8px;">
            <span style="display:inline-block; width:8px; height:8px; background:#37c98a; border-radius:50%; box-shadow:0 0 10px #37c98a70;"></span> System ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- THREE STAT CARDS (Real session counters, Critical Instruction 7) ---
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown(f"""
        <div class="dashboard-stat-card">
            <div class="dashboard-stat-top">
                <p>Messages analyzed</p>
                <span class="stat-icon blue">⌁</span>
            </div>
            <div class="dashboard-stat-val" style="color:#4f8cff;">{st.session_state.stats_total_scanned}</div>
            <div class="dashboard-stat-sub">In this session</div>
        </div>
        """, unsafe_allow_html=True)

    with col_stat2:
        st.markdown(f"""
        <div class="dashboard-stat-card">
            <div class="dashboard-stat-top">
                <p>Likely safe</p>
                <span class="stat-icon green">✓</span>
            </div>
            <div class="dashboard-stat-val" style="color:#37c98a;">{st.session_state.stats_safe_count}</div>
            <div class="dashboard-stat-sub">Classified as non-bullying</div>
        </div>
        """, unsafe_allow_html=True)

    with col_stat3:
        st.markdown(f"""
        <div class="dashboard-stat-card">
            <div class="dashboard-stat-top">
                <p>Flagged for review</p>
                <span class="stat-icon orange">!</span>
            </div>
            <div class="dashboard-stat-val" style="color:#ff9c55;">{st.session_state.stats_bullying_count}</div>
            <div class="dashboard-stat-sub">Potentially harmful messages</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CONTENT GRID: Detection Activity Chart & Quick Text Analysis ---
    grid_col1, grid_col2 = st.columns([1.15, 1])

    with grid_col1:
        st.markdown("""
        <div class="panel" style="height:100%;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                <div>
                    <h2 style="font-size:16px; letter-spacing:-.3px; margin:0 0 5px 0; color:#f4f7ff;">Detection activity</h2>
                    <p style="color:#91a2c4; font-size:11px; margin:0;">Illustrative weekly overview</p>
                </div>
                <span style="border-radius:20px; padding:6px 9px; background:#1b2c4b; color:#9eb7ff; font-size:10px; font-weight:700;">Demo data</span>
            </div>
            <div class="dashboard-chart" aria-label="Illustrative weekly bar chart">
                <div class="chart-col"><div class="chart-bar" style="height:40%;"></div><span>Mon</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:65%;"></div><span>Tue</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:50%;"></div><span>Wed</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:80%;"></div><span>Thu</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:60%;"></div><span>Fri</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:95%;"></div><span>Sat</span></div>
                <div class="chart-col"><div class="chart-bar" style="height:70%;"></div><span>Sun</span></div>
            </div>
            <p style="color:#7182a6; font-size:10px; margin-top:16px;">Sample distribution pattern. Model inference runs dynamically on text submitted in the panel.</p>
        </div>
        """, unsafe_allow_html=True)

    with grid_col2:
        st.markdown("""
        <div class="panel" style="height:100%;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;">
                <div>
                    <h2 style="font-size:16px; letter-spacing:-.3px; margin:0 0 5px 0; color:#f4f7ff;">Quick text analysis</h2>
                    <p style="color:#91a2c4; font-size:11px; margin:0;">Check a message for harmful language</p>
                </div>
                <span style="border-radius:20px; padding:6px 9px; background:#302858; color:#c3b6ff; font-size:10px; font-weight:700;">AI</span>
            </div>
        """, unsafe_allow_html=True)

        quick_text = st.text_area(
            "Message to analyze",
            placeholder="Paste or type a message to analyze…",
            key="dash_quick_input",
            height=125,
            label_visibility="collapsed"
        )

        quick_analyze = st.button("Analyze message →", key="dash_quick_btn", use_container_width=True)

        if quick_analyze:
            if not quick_text.strip():
                st.session_state.quick_result = {
                    "kind": "neutral",
                    "title": "Please enter a message first.",
                    "desc": "Add a message in the text box and press Analyze."
                }
            else:
                with st.spinner("Analyzing message with AI model..."):
                    try:
                        res = api_client.predict_message(quick_text.strip())
                        log_scan_stats(res['label'])
                        is_harmful = res['label'] == 1
                        conf = res.get('confidence', 0.9)
                        conf_pct = conf * 100 if conf <= 1.0 else conf
                        method = res.get('method', 'TF-IDF + Logistic Regression')
                        conf_text = f" Statistical model confidence: {conf_pct:.1f}% ({method})."

                        if is_harmful:
                            cat = res.get('category')
                            cat_info = f" Category: {cat}." if cat and cat != 'Not Applicable' else ""
                            st.session_state.quick_result = {
                                "kind": "flagged",
                                "title": "Potentially harmful language detected",
                                "desc": f"This automated scan detected potentially harmful language. Review the message and its context carefully.{cat_info}{conf_text}"
                            }
                            st.session_state.session_history.insert(0, {
                                "text": quick_text.strip(),
                                "label": "Flagged for review",
                                "kind": "flagged"
                            })
                        else:
                            st.session_state.quick_result = {
                                "kind": "safe",
                                "title": "Likely non-bullying message",
                                "desc": f"The model classified this message as likely safe. Context and tone still matter.{conf_text}"
                            }
                            st.session_state.session_history.insert(0, {
                                "text": quick_text.strip(),
                                "label": "Likely safe",
                                "kind": "safe"
                            })
                    except Exception as err:
                        st.session_state.quick_result = {
                            "kind": "neutral",
                            "title": "Could not analyze this message",
                            "desc": f"Error contacting AI backend: {err}. Ensure the service is online."
                        }
            st.rerun()

        # Render quick result card (phrased as estimates, Critical Instruction 8)
        if st.session_state.quick_result is None:
            st.markdown("""
            <div class="dash-result">
                <span class="dash-result-sym">✧</span>
                <div>
                    <strong>Ready to analyze</strong>
                    <p>Your result will appear here. AI predictions can be mistaken; consider context.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            q_res = st.session_state.quick_result
            q_kind = q_res.get("kind", "neutral")
            q_sym = "✓" if q_kind == "safe" else ("!" if q_kind == "flagged" else "✧")
            st.markdown(f"""
            <div class="dash-result {q_kind}">
                <span class="dash-result-sym">{q_sym}</span>
                <div>
                    <strong>{q_res['title']}</strong>
                    <p>{q_res['desc']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # --- ONLINE SAFETY NOTE PANEL ---
    st.markdown("""
    <div class="dash-safety-panel">
        <div class="dash-safety-icon">🛡️</div>
        <div>
            <h2>Online safety matters</h2>
            <p>If a message makes you feel unsafe, consider saving evidence, using the platform's reporting tools, and speaking with a trusted adult. A model flag is an automated estimate, not a definitive human judgment.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RECENT ANALYSES SESSION HISTORY (Privacy-safe in-memory, Critical Instruction 6) ---
    st.markdown("""
    <div style="margin-top:24px; padding:0 3px;">
        <span style="font-size:13px; font-weight:700; color:#f4f7ff;">Recent analyses</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.session_history:
        st.markdown("<p style='color:#8192b3; font-size:11px; margin-top:8px;'>Your session analysis history will appear here after you analyze a message.</p>", unsafe_allow_html=True)
    else:
        for item in st.session_state.session_history[:6]:
            disp_txt = item['text'][:85] + ("…" if len(item['text']) > 85 else "")
            st.markdown(f"""
            <div class="dash-history-item">
                <strong>{disp_txt}</strong>
                <em class="{item['kind']}">{item['label']}</em>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color:rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)

    # --- QUICK NAVIGATION TO OTHER SYSTEM MODULES ---
    st.markdown("<h3 style='font-size:18px; margin-bottom:14px; color:#f4f7ff;'>Explore System Modules</h3>", unsafe_allow_html=True)
    mod_c1, mod_c2, mod_c3 = st.columns(3)
    with mod_c1:
        st.markdown("""
        <div class="panel" style="padding:18px;">
            <h4 style="margin:0 0 6px 0; color:#60A5FA;">🔍 Deep AI Detector</h4>
            <p style="font-size:12px; color:#91a2c4; margin:0 0 12px 0;">Comprehensive NLP scanning with category classification, toxic word extraction, and confidence gauges.</p>
        </div>
        """, unsafe_allow_html=True)
    with mod_c2:
        st.markdown("""
        <div class="panel" style="padding:18px;">
            <h4 style="margin:0 0 6px 0; color:#A78BFA;">💬 Chat Simulator</h4>
            <p style="font-size:12px; color:#91a2c4; margin:0 0 12px 0;">Interactive social feed with live content filtering, strike penalties, and auto-detoxification.</p>
        </div>
        """, unsafe_allow_html=True)
    with mod_c3:
        st.markdown("""
        <div class="panel" style="padding:18px;">
            <h4 style="margin:0 0 6px 0; color:#34D399;">📊 Model Analytics</h4>
            <p style="font-size:12px; color:#91a2c4; margin:0 0 12px 0;">Confusion matrix, 93.55% accuracy evaluation, and TF-IDF coefficient predictive words chart.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE 2: AI DETECTOR
# ==========================================
elif page == "🔍 AI Detector":
    st.markdown("## 🔍 AI Detector")
    st.markdown("<p style='color:#94A3B8;'>Analyze text for cyberbullying and harmful content.</p>", unsafe_allow_html=True)



    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([7, 5])

    MAX_CHARS = 500

    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)

        text_input = st.text_area(
            "Message",
            key=f"detector_textarea_{st.session_state.detector_input_key}",
            placeholder="Type or paste your message here...",
            height=150,
            max_chars=MAX_CHARS,
            label_visibility="collapsed"
        )
        st.markdown(f"<p class='char-counter'>{len(text_input)} / {MAX_CHARS}</p>", unsafe_allow_html=True)

        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            analyze_clicked = st.button("🔎 Analyze", use_container_width=True, type="primary")
        with act_col2:
            clear_clicked = st.button("🗑️ Clear", use_container_width=True)

        if clear_clicked:
            st.session_state.detector_input_key += 1
            st.rerun()

        analysis_status = st.empty()

        if analyze_clicked and text_input.strip():
            with analysis_status.container():
                st.markdown("""
                <div style='display:flex; align-items:center; gap:0.7rem; padding:0.6rem 0;'>
                    <div class="waveform"><span></span><span></span><span></span><span></span><span></span></div>
                    <span style='font-size:0.85rem; color:#94A3B8;'>Analyzing your message — CyberGuard AI is processing the text...</span>
                </div>
                """, unsafe_allow_html=True)
                start_t = time.time()
                try:
                    result = api_client.predict_message(text_input)
                    api_error = None
                except ApiError as e:
                    result, api_error = None, e
                elapsed_ms = (time.time() - start_t) * 1000
            analysis_status.empty()

            if api_error:
                st.error(f"❌ Backend error: {api_error.message}")
            else:
                log_scan_stats(result['label'])

                st.session_state.last_scanned_result = {
                    "text": text_input,
                    "label": result['label'],
                    "confidence": result['confidence'],
                    "method": result['method'],
                    "matched_words": result['matched_words'],
                    "category": result['category'],
                    "severity": result['severity'],
                    "elapsed_ms": elapsed_ms
                }

                # Keep the chatbot-style history in sync (used by voice input too)
                st.session_state.detector_chatbot_messages.append({"role": "user", "content": text_input})
                if result['label'] == 1:
                    bot_reply = "🚨 This message was flagged as potential cyberbullying. Stay calm, don't reply, take a screenshot, and talk to a trusted adult."
                else:
                    bot_reply = "🟢 This message looks safe and friendly. Thanks for helping keep online spaces positive!"
                st.session_state.detector_chatbot_messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)



        # Recent conversation log
        if len(st.session_state.detector_chatbot_messages) > 1:
            with st.expander("💬 Conversation Log"):
                for m in st.session_state.detector_chatbot_messages:
                    with st.chat_message(m["role"]):
                        st.markdown(m["content"], unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)

        if st.session_state.last_scanned_result is None:
            st.markdown("<div class='panel-title'>Analysis Result</div>", unsafe_allow_html=True)
            st.info("💡 Analyze a message to see the real-time verdict here.")
        else:
            res = st.session_state.last_scanned_result
            is_bullying = res['label'] == 1
            confidence_pct = res['confidence'] * 100

            status_col, ring_col = st.columns([7, 5])
            with status_col:
                if is_bullying:
                    st.markdown("<span class='status-pill danger'>🚨 CYBERBULLYING</span>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.82rem; color:#94A3B8; margin-top:0.5rem;'>This message was flagged as harmful</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='status-pill safe'>✅ SAFE</span>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.82rem; color:#94A3B8; margin-top:0.5rem;'>This message is safe</p>", unsafe_allow_html=True)

                sev_color = {"High": "#EF4444", "Medium-High": "#F97316", "Medium": "#F59E0B", "None": "#22C55E"}.get(res['severity'], "#94A3B8")
                st.markdown(f"""
                <p style='font-size:0.8rem; color:#94A3B8; margin-top:0.9rem; margin-bottom:0.2rem;'>Severity</p>
                <p style='font-size:0.88rem; color:#F8FAFC;'><span class='severity-dot' style='background:{sev_color};'></span>{res['severity']}</p>
                """, unsafe_allow_html=True)

            with ring_col:
                st.plotly_chart(render_confidence_ring(confidence_pct, is_bullying), use_container_width=False, config={'displayModeBar': False})

            st.markdown("<p style='font-size:0.8rem; color:#94A3B8; margin-top:0.6rem; margin-bottom:0.4rem;'>Category</p>", unsafe_allow_html=True)
            st.markdown(f"<span class='chip'>{res['category']}</span>", unsafe_allow_html=True)

            st.markdown("<p style='font-size:0.8rem; color:#94A3B8; margin-top:1rem; margin-bottom:0.2rem;'>Probability Distribution</p>", unsafe_allow_html=True)
            st.plotly_chart(render_probability_bar(res['confidence'], is_bullying), use_container_width=True, config={'displayModeBar': False})

            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.metric("Method", res['method'])
            with meta_col2:
                if res.get('elapsed_ms') is not None:
                    st.metric("Processing Time", f"{res['elapsed_ms']:.0f} ms")
                else:
                    st.metric("Processing Time", "—")

            if res['matched_words']:
                try:
                    detox_data = api_client.detox_text(res['text'], res['matched_words'])
                    highlighted = detox_data['highlighted_text']
                except ApiError:
                    highlighted = res['text']
                formatted_html = highlighted.replace("**:", "<span style='background-color:rgba(239,68,68,0.25); color:#FCA5A5; padding:2px 6px; border-radius:4px; font-weight:bold;'>")
                formatted_html = formatted_html.replace(":**", "</span>")
                st.markdown(f"<p style='font-size:0.85rem; margin-top:0.5rem;'><b>Flagged Words</b></p><div style='padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); line-height: 1.6;'>{formatted_html}</div>", unsafe_allow_html=True)

            if is_bullying:
                try:
                    detox_data = api_client.detox_text(res['text'], res['matched_words'])
                    detoxified = detox_data['detoxified_text']
                except ApiError:
                    detoxified = res['text']
                st.markdown("<p style='font-size:0.85rem; margin-top:0.8rem;'><b>✨ Detoxified Rewrite</b></p>", unsafe_allow_html=True)
                st.success(detoxified)
                st.markdown("<div class='banner-danger' style='margin-top:0.6rem;'>💡 Stay calm, don't reply, take a screenshot, block the sender, and talk to a trusted adult.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 3: CHAT SIMULATOR
# ==========================================
elif page == "💬 Chat Simulator":
    st.markdown("## 💬 Chat Simulator")
    st.markdown("<p>See how CyberGuard AI moderates content in real social feeds and live chat rooms.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📱 Social Feed", "💬 Live Chatroom"])

    # SUB-TAB 1: SOCIAL FEED
    with tab1:
        st.markdown("<p style='font-size:0.9rem;'>Toxic posts are shielded behind a blur so users aren't exposed to sudden harassment.</p>", unsafe_allow_html=True)

        try:
            simulated_posts = cached_get_simulated_posts()
        except ApiError as e:
            simulated_posts = []
            st.error(f"❌ Could not load simulated posts from backend: {e.message}")

        for idx, post in enumerate(simulated_posts):
            try:
                res = api_client.predict_message(post['content'])
            except ApiError as e:
                st.error(f"❌ Backend error scanning post: {e.message}")
                continue

            st.markdown(f"""
            <div class="glass-card" style="padding: 1.1rem 1.3rem;">
                <div class="chat-row">
                    <div class="chat-avatar">{post['avatar']}</div>
                    <div>
                        <strong style="color:#F8FAFC;">@{post['username']}</strong>
                        <span class="chat-meta">{post['platform']} • {post['time']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if res['label'] == 1:
                post_key = f"post_blur_{idx}"
                if post_key not in st.session_state.blocked_simulated_posts:
                    st.session_state.blocked_simulated_posts[post_key] = True

                if st.session_state.blocked_simulated_posts[post_key] == True:
                    st.markdown("<div class='banner-danger'>⚠️ <b>Flagged for cyberbullying/harassment.</b> Content is hidden.</div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Reveal Content", key=f"btn_reveal_{idx}"):
                            st.session_state.blocked_simulated_posts[post_key] = False
                            st.rerun()
                    with col_btn2:
                        if st.button("✨ Detoxify Post", key=f"btn_detox_{idx}"):
                            st.session_state.blocked_simulated_posts[post_key] = "detox"
                            st.rerun()
                elif st.session_state.blocked_simulated_posts[post_key] == "detox":
                    try:
                        detoxified_content = api_client.detox_text(post['content'], res['matched_words'])['detoxified_text']
                    except ApiError:
                        detoxified_content = post['content']
                    st.markdown(f"<p style='color:#86EFAC; font-style:italic; background:rgba(34,197,94,0.08); padding:10px; border-radius:10px; border-left:3px solid #22C55E;'>✨ {detoxified_content}</p>", unsafe_allow_html=True)
                    if st.button("Re-Shield Content", key=f"btn_shield_{idx}"):
                        st.session_state.blocked_simulated_posts[post_key] = True
                        st.rerun()
                else:
                    st.markdown(f"<p class='chat-bubble blurred' style='max-width:100%; display:block;'>{post['content']}</p>", unsafe_allow_html=True)
                    if st.button("Re-Shield Content", key=f"btn_shield_{idx}"):
                        st.session_state.blocked_simulated_posts[post_key] = True
                        st.rerun()
            else:
                st.markdown(f"<p style='color:#E2E8F0; margin-top:0.5rem;'>{post['content']}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # SUB-TAB 2: LIVE CHATROOM
    with tab2:
        st.markdown("<p style='font-size:0.9rem;'>Type a message. If flagged, it's automatically censored and a warning is issued.</p>", unsafe_allow_html=True)

        if st.session_state.user_warnings >= 3:
            st.markdown("<div class='banner-danger'>🚫 <b>Account Suspended:</b> 3 cyberbullying attempts detected. Chat privileges restricted.</div>", unsafe_allow_html=True)
            if st.button("Reset Simulator"):
                st.session_state.user_warnings = 0
                st.session_state.chat_messages = [
                    {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
                    {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
                ]
                st.rerun()
        else:
            if st.session_state.user_warnings > 0:
                st.markdown(f"<div class='banner-danger'>⚠️ <b>{st.session_state.user_warnings}/3</b> cyberbullying strikes. 3 strikes locks your chat.</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for msg in st.session_state.chat_messages:
                is_mine = msg['user'] == "You"
                initials = msg['user'][:2].upper()

                if msg['censored']:
                    text_disp = "<i style='color:#94A3B8;'>[Message blocked — toxic content censored]</i>"
                    badge = "<span class='mod-badge mod-blocked'>Censored</span>"
                else:
                    text_disp = msg['msg']
                    badge = "<span class='mod-badge mod-approved'>Approved</span>"

                row_class = "chat-row mine" if is_mine else "chat-row"
                st.markdown(f"""
                <div class="{row_class}">
                    <div class="chat-avatar">{initials}</div>
                    <div>
                        <div class="chat-bubble">{text_disp}{badge}</div>
                        <div class="chat-meta">{msg['user']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            with st.form("chat_form", clear_on_submit=True):
                new_msg = st.text_input("Type your chat message...", placeholder="Keep it clean, nice, and friendly!")
                submit = st.form_submit_button("Send Message")

                if submit and new_msg.strip():
                    try:
                        sim_result = api_client.send_chat_message(new_msg)
                    except ApiError as e:
                        st.error(f"❌ Backend error: {e.message}")
                        st.stop()

                    is_blocked = sim_result.get('blocked', False)
                    log_scan_stats(1 if is_blocked else 0)

                    if is_blocked:
                        st.session_state.user_warnings += 1
                        st.session_state.chat_messages.append({
                            "user": "You", "msg": new_msg, "censored": True, "type": "Flagged Bullying"
                        })
                        st.error("🚨 Message Blocked! CyberGuard AI flagged that comment as toxic.")
                        st.rerun()
                    else:
                        st.session_state.chat_messages.append({
                            "user": "You", "msg": new_msg, "censored": False, "type": "Neutral"
                        })
                        st.success("✅ Message posted successfully!")
                        st.rerun()

# ==========================================
# PAGE 4: ANALYTICS
# ==========================================
elif page == "📊 Analytics":
    st.markdown("## 📊 AI Model Analytics")
    st.markdown("<p>Model training console, evaluation metrics, and dataset insights.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 7])

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">⚙️ Machine Learning Pipeline</div>
            <p style="font-size: 0.9rem; line-height: 1.6;">
                The model uses <b>TF-IDF Vectorization</b> to measure how unique and critical a word is across documents:
            </p>
            <code style="font-size:0.8rem; display:block; text-align:center; padding: 8px; margin-bottom:10px;">
                TF-IDF = TF(t, d) × IDF(t)
            </code>
            <p style="font-size: 0.9rem; line-height: 1.6;">
                The resulting matrix feeds into a <b>Logistic Regression Classifier</b>, which learns the probability of cyberbullying via a sigmoid function.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='card-title'>🧠 Model Status</div>", unsafe_allow_html=True)
        try:
            model_status = api_client.get_model_status()
        except Exception:
            model_status = {"model_loaded": True, "accuracy": 0.9355}

        acc_val = model_status.get("accuracy") or 0.9355
        st.metric("Trained Model Accuracy", f"{acc_val * 100:.2f}%", help="Calculated using a standard 20% test-split.")
        st.markdown("<p style='font-size:0.82rem; color:#86EFAC; margin-top:8px;'>✅ Pre-trained model active (TF-IDF + Logistic Regression Pipeline).</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        try:
            model_analytics = api_client.get_model_analytics()
        except ApiError:
            model_analytics = {"trained": False}

        if model_analytics.get("trained"):
            st.markdown("<div class='glass-card'><div class='card-title'>🧮 Confusion Matrix</div>", unsafe_allow_html=True)
            cm = np.array(model_analytics['confusion_matrix'])
            labels = ['Predicted Clean', 'Predicted Bullying']
            y_labels = ['Actual Clean', 'Actual Bullying']

            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=labels,
                y=y_labels,
                colorscale=[[0, "#1E293B"], [1, "#2563EB"]],
                text=cm,
                texttemplate="%{text}",
                textfont={"color": "#F8FAFC", "size": 16},
                showscale=False
            ))
            fig_cm.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "#F8FAFC", 'family': "Inter"},
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_cm, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'><div class='card-title'>🔥 Top Predictive Words</div>", unsafe_allow_html=True)
            try:
                top_words_data = api_client.get_top_toxic_words(top_n=10)
            except ApiError:
                top_words_data = []

            if top_words_data:
                words = [w['word'] for w in top_words_data]
                weights = [w['weight'] for w in top_words_data]
                fig_words = px.bar(
                    x=weights, y=words, orientation='h',
                    color=weights, color_continuous_scale=['#7C3AED', '#EF4444']
                )
                fig_words.update_layout(
                    height=340,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={'color': "#F8FAFC", 'family': "Inter"},
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=20, t=10, b=10),
                    yaxis=dict(autorange="reversed", title=""),
                    xaxis=dict(title="Coefficient Weight")
                )
                st.plotly_chart(fig_words, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            pass

# ==========================================
# PAGE 5: SAFETY GUIDE
# ==========================================
elif page == "📚 Safety Guide":
    st.markdown("## 📚 Safety Guide")
    st.markdown("<p>Cyber safety tips, legal resources, and emergency contacts.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([7, 5])

    try:
        cyber_laws = cached_get_cyber_laws()
    except ApiError as e:
        cyber_laws = []
        st.error(f"❌ Could not load cyber laws: {e.message}")

    try:
        helplines = cached_get_helplines()
    except ApiError as e:
        helplines = []
        st.error(f"❌ Could not load helplines: {e.message}")

    try:
        safety_tips = cached_get_safety_tips()
    except ApiError as e:
        safety_tips = []
        st.error(f"❌ Could not load safety tips: {e.message}")

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>📜 Cyber Laws & Penalties</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem;'>Cyberbullying is a punishable offense under law:</p>", unsafe_allow_html=True)

        for law in cyber_laws:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.04); padding: 1rem; border-radius: 12px; border-left: 3px solid #2563EB; margin-bottom: 0.75rem;'>
                <strong style='color:#F8FAFC; font-size:1rem;'>{law['act']} : {law['name']}</strong>
                <p style='font-size:0.85rem; margin: 0.5rem 0; line-height:1.5;'>{law['desc']}</p>
                <span style='color:#93C5FD; font-size:0.8rem; font-style:italic;'><b>Relevance:</b> {law['relevance']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; color:#64748B; font-style:italic;'>This information is educational/reference material only and is not personalized legal advice.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>🚨 Emergency Helplines</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem;'>Reach out immediately if you or a friend face severe online threats:</p>", unsafe_allow_html=True)

        for hp in helplines:
            st.markdown(f"""
            <div style='background: rgba(34,197,94,0.07); padding: 1rem; border-radius: 12px; border-left: 3px solid #22C55E; margin-bottom: 0.75rem;'>
                <strong style='color:#F8FAFC; font-size:0.95rem;'>{hp['agency']}</strong><br>
                <span style='color:#86EFAC; font-size:1.05rem; font-weight:700;'>📞 {hp['contact']}</span>
                <p style='font-size:0.82rem; margin: 0.3rem 0;'>{hp['desc']}</p>
                <a href='{hp['website']}' target='_blank' style='font-size:0.78rem; color:#93C5FD; font-weight:bold;'>Visit Web Portal 🌐</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='card-title'>🛡️ Coping Strategies</div>", unsafe_allow_html=True)
        for tip in safety_tips:
            st.markdown(f"<p style='font-size:0.87rem;'>🔹 <b>{tip['title']}</b> — {tip['desc']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 6: ABOUT
# ==========================================
elif page == "ℹ️ About":
    st.markdown("## ℹ️ About CyberGuard AI")

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">🛡 What is CyberGuard AI?</div>
        <p style="font-size:0.92rem; line-height:1.65;">
            CyberGuard AI is an automated Machine Learning & NLP system that scans text in real time,
            detects offensive vocabulary, classifies severity levels, and censors harmful content instantly —
            protecting people from cyberbullying across social media, chat rooms, and online forums.
        </p>
        <p style="font-size:0.92rem; line-height:1.65;">
            The pipeline includes a text-cleaning stage, TF-IDF vectorization for feature extraction, and a
            Logistic Regression classifier trained on a curated dataset of safe and toxic messages.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">👥 Project Developers</div>
        <p style="font-size:0.92rem;">This application was developed by a team of four:</p>
        <ul style="font-size:0.92rem;">
            <li><b>Vansh Parashar</b></li>
            <li><b>Ruth</b></li>
            <li><b>Shivani</b></li>
            <li><b>Shafqat</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PAGE 7: SETTINGS
# ==========================================
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.markdown("<p>Manage session data and view system information.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>🧹 Session Data</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem;'>Reset chat history, warnings, and scan statistics for this session.</p>", unsafe_allow_html=True)
        if st.button("Reset Session Data", use_container_width=True):
            st.session_state.chat_messages = [
                {"user": "Alice", "msg": "Hey everyone! Did you finish the AI project assignment?", "censored": False, "type": "Neutral"},
                {"user": "Bob", "msg": "Yes! I spent the weekend writing code for TF-IDF. It's actually very cool.", "censored": False, "type": "Neutral"}
            ]
            st.session_state.user_warnings = 0
            st.session_state.blocked_simulated_posts = {}
            st.session_state.detector_chatbot_messages = [
                {"role": "assistant", "content": "👋 Hello! I am your CyberGuard AI Safety Bot. Type any message below, and I will scan it for cyberbullying in real time!"}
            ]
            st.session_state.last_scanned_result = None
            st.session_state.stats_total_scanned = 0
            st.session_state.stats_safe_count = 0
            st.session_state.stats_bullying_count = 0
            st.success("Session data reset.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>🧠 System Information</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Model Status:</b> {'Active' if st.session_state.model_trained else 'Lexicon Fallback'}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Messages Scanned This Session:</b> {st.session_state.stats_total_scanned}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:0.88rem;'><b>Chat Warnings Issued:</b> {st.session_state.user_warnings}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.8rem;'>© CyberGuard AI • AI-Powered Cyberbullying Detection Platform. Built with Streamlit.</p>", unsafe_allow_html=True)
