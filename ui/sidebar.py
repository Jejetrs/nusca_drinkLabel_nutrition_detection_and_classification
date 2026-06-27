"""
ui/sidebar.py — NutriScan AI
Sidebar stepper yang menampilkan logo, progress, dan status.
"""

import base64
from pathlib import Path

import streamlit as st

ASSET_ROOT = Path(__file__).resolve().parent.parent / "asset"

# ── Ikon SVG ──────────────────────────────────────────────────────────────────
IC_LEAF = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>'
    '<path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>'
)
IC_CAMERA = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z"/>'
    '<circle cx="12" cy="13" r="3"/></svg>'
)
IC_CROP = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/></svg>'
)
IC_ANALYZE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/></svg>'
)
IC_CHECK = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
)

# ── Konfigurasi langkah ───────────────────────────────────────────────────────
_STEPS = [
    ("mulai",    "1. Foto Label",    IC_CAMERA),
    ("pangkas",  "2. Pangkas",       IC_CROP),
    ("analisis", "3. Analisis",      IC_ANALYZE),
]
_STEP_INDEX = {"mulai": 0, "pangkas": 1, "memproses": 2, "hasil": 2}

_SUBS = {
    "mulai":     {0: "Kamera Aktif",    1: "Langkah Berikutnya", 2: "Memproses"},
    "pangkas":   {0: "Selesai",         1: "Sedang dipangkas",   2: "Memproses"},
    "memproses": {0: "Selesai",         1: "Selesai",            2: "Memproses…"},
    "hasil":     {0: "Selesai",         1: "Selesai",            2: "Selesai"},
}


def _asset_uri(filename: str) -> str:
    path = ASSET_ROOT / filename
    if not path.exists():
        return ""
    data = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def render_sidebar(current_step: str, mode: str = "demo", status_msg: str = ""):
    active = _STEP_INDEX.get(current_step, 0)
    subs   = _SUBS.get(current_step, _SUBS["mulai"])

    if mode == "model":
        status_dot = (
            f'<div class="ns-status-dot"><span></span>{status_msg}</div>'
        )
    else:
        status_dot = (
            '<div class="ns-status-dot" style="background:#FEF9C3;border-color:#FDE68A;'
            'color:#854D0E"><span style="background:#EAB308"></span>'
            'Mode Demo aktif</div>'
        )

    logo_uri = _asset_uri("logo.png")
    brand = (
        '<div class="ns-brand">'
        f'<div class="ns-logo"><img src="{logo_uri}" alt="Nusca"/></div>'
        '<div class="ns-brand-text">'
        '<div class="ns-brand-name"><span class="ns-nus">Nus</span><span class="ns-ca">ca</span></div>'
        '<div class="ns-brand-sub">Nutrition Scanner &amp; Classifier</div>'
        '</div>'
        '</div>'
        '<div class="ns-progress-label">Progres Saat Ini</div>'
    )

    steps_html = ['<div class="ns-steps">']
    for i, (_key, title, icon) in enumerate(_STEPS):
        if current_step == "hasil":
            state = "done"
        elif i < active:
            state = "done"
        elif i == active:
            state = "active"
        else:
            state = ""
        dot_icon = IC_CHECK if state == "done" else icon
        steps_html.append(
            f'<div class="ns-step {state}">'
            f'<div class="ns-step-rail"></div>'
            f'<div class="ns-dot">{dot_icon}</div>'
            f'<div class="ns-step-info">'
            f'<div class="ns-step-title">{title}</div>'
            f'<div class="ns-step-sub">{subs.get(i, "")}</div>'
            f'</div></div>'
        )
    steps_html.append('</div>')

    with st.sidebar:
        st.markdown(f"{brand}{''.join(steps_html)}", unsafe_allow_html=True)
        st.markdown(
            f'<div class="ns-sidebar-status-sticky">{status_dot}</div>',
            unsafe_allow_html=True,
        )
