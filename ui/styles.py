"""
ui/styles.py — NutriScan AI · Redesigned
=========================================
Palet & token desain yang mencerminkan referensi UI:
  - Sidebar stepper hijau (Capture → Crop → Analyze)
  - Home hero dua kolom, kartu upload/kamera terpisah
  - Loading page dengan lingkaran animasi + langkah-langkah
  - Hasil: badge GGL per-komponen (A-D), breakdown detail, chart, tips
"""

import streamlit as st

# ─── Token desain ────────────────────────────────────────────────────────────
PRIMARY       = "#22C55E"
PRIMARY_DARK  = "#16A34A"
PRIMARY_DEEP  = "#15803D"
BLUE_ACCENT   = "#3B82F6"
INK           = "#0F172A"
INK_SOFT      = "#475569"
MUTED         = "#94A3B8"
LINE          = "#E2E8F0"
BG            = "#F8FAFC"
CARD          = "#FFFFFF"

# Nutri-Level per-komponen (A terbaik → D terburuk)
LVL = {
    "A": ("#16A34A", "#DCFCE7", "#166534"),
    "B": ("#84CC16", "#ECFCCB", "#3F6212"),
    "C": ("#F59E0B", "#FEF9C3", "#92400E"),
    "D": ("#EF4444", "#FEE2E2", "#991B1B"),
}


def inject_global_css():
    st.markdown(f"""
<style>
/* ─── Font ────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Nunito:wght@800;900&display=swap');

:root {{
  --primary:       {PRIMARY};
  --primary-dark:  {PRIMARY_DARK};
  --primary-deep:  {PRIMARY_DEEP};
  --blue:          {BLUE_ACCENT};
  --ink:           {INK};
  --ink-soft:      {INK_SOFT};
  --muted:         {MUTED};
  --line:          {LINE};
  --bg:            {BG};
  --card:          {CARD};
  --r:             16px;
  --sm: 0 1px 3px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04);
  --md: 0 4px 16px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.04);
  --lg: 0 20px 56px rgba(15,23,42,.10), 0 8px 20px rgba(15,23,42,.06);
}}

html, body, [class*="css"], .stApp {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--ink);
  background: var(--bg);
}}

/* Bersihkan SEMUA chrome bawaan Streamlit di atas layar (header jelek/strip
   gelap). Header + dekorasi disembunyikan total. Tombol buka/tutup sidebar
   tidak ditata di sini — ditangani helper JS (_ensure_sidebar_toggle):
   tombol native dibiarkan di pohon React (agar klik tetap hidup) namun
   disembunyikan, lalu tombol floating kita sendiri yang tampil di kiri-atas. */
#MainMenu, footer {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
[data-testid="stHeader"] {{
  display: none !important;
  height: 0 !important; min-height: 0 !important;
  background: transparent !important;
  box-shadow: none !important; border: none !important;
}}
header {{
  background: transparent !important;
  height: 0 !important; min-height: 0 !important;
  padding: 0 !important; margin: 0 !important;
  box-shadow: none !important; border: none !important;
  overflow: visible !important;
}}
.block-container {{ padding-top: 1.8rem; padding-bottom: 4.2rem; max-width: 1040px; }}

/* ─── Sidebar ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background: #FFFFFF;
  border-right: 1px solid var(--line);
  overflow-x: hidden !important;
}}
[data-testid="stSidebar"] * {{ box-sizing: border-box; max-width: 100%; }}
/* Konten sidebar dimulai lebih ATAS agar tidak terlalu panjang (sesuai permintaan) */
[data-testid="stSidebar"] > div {{
  padding-top: .6rem !important;
  overflow-x: hidden !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{ max-width: 100%; overflow-x: hidden; }}
/* iframe helper (components.html height=0) jangan menambah tinggi/scroll */
[data-testid="stIFrame"][height="0"],
iframe[height="0"] {{
  height: 0 !important; min-height: 0 !important; display: block !important;
  width: 0 !important; position: absolute !important; visibility: hidden !important;
}}
/* hilangkan kontainer kosong yang menyisakan ruang */
[data-testid="stElementContainer"]:has(> iframe[height="0"]) {{
  height: 0 !important; min-height: 0 !important; margin: 0 !important; padding: 0 !important;
}}
/* hilangkan elemen kosong yang kadang menambah tinggi/lebar */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
/* Status model menempel di dasar sidebar (sticky) — padding bawah secukupnya */
.ns-sidebar-status-sticky {{
  position: sticky; bottom: 0; z-index: 5;
  margin: 14px 0 0; padding: 12px 4px 16px;
  background: linear-gradient(180deg, rgba(255,255,255,0), #FFFFFF 30%);
}}
.ns-sidebar-status-sticky .ns-status-dot {{ margin: 0; }}

/* ─── Tombol utama ─────────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {{
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #fff;
  font-weight: 700;
  font-size: .95rem;
  letter-spacing: .01em;
  padding: .72rem 1.3rem;
  position: relative;
  overflow: hidden;
  transition: transform .14s cubic-bezier(.2,.9,.3,1.2), box-shadow .2s, filter .2s;
  box-shadow: 0 6px 18px rgba(22,163,74,.30), inset 0 1px 0 rgba(255,255,255,.18);
}}
.stButton > button::after {{
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,.28) 50%, transparent 70%);
  transform: translateX(-120%); transition: transform .55s ease;
}}
.stButton > button:hover {{
  transform: translateY(-2px) scale(1.012);
  box-shadow: 0 12px 28px rgba(22,163,74,.40), inset 0 1px 0 rgba(255,255,255,.22);
  filter: brightness(1.04);
  color: #fff;
}}
.stButton > button:hover::after {{ transform: translateX(120%); }}
.stButton > button:active {{ transform: translateY(0) scale(.99); }}
.stButton > button:focus:not(:active) {{ color: #fff; border: none; box-shadow: 0 0 0 4px rgba(34,197,94,.25), 0 6px 18px rgba(22,163,74,.30); }}

.stButton > button[kind="secondary"] {{
  background: #fff;
  color: var(--ink-soft);
  border: 1.5px solid var(--line);
  box-shadow: var(--sm);
}}
.stButton > button[kind="secondary"]::after {{ display: none; }}
.stButton > button[kind="secondary"]:hover {{
  background: #F8FAFC; color: var(--ink);
  border-color: #16A34A; box-shadow: 0 8px 20px rgba(15,23,42,.10);
  transform: translateY(-2px);
}}

/* ─── Tabs (gaya pil bergeser — Unggah / Ambil Foto) ──────────────── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 6px;
  background: #F1F5F9;
  border-radius: 14px;
  padding: 5px;
  margin-bottom: 4px;
  border: none;
  display: flex;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: 600;
  font-size: .9rem;
  color: var(--ink-soft);
  background: transparent;
  border: none;
  flex: 0 1 auto;
  white-space: nowrap;
  justify-content: center;
  transition: flex-grow .28s cubic-bezier(.2,.9,.3,1.2), background .18s, color .18s, box-shadow .18s;
}}
/* Tab aktif memenuhi ruang (fill section); tab non-aktif menjorok ke sisi */
.stTabs [aria-selected="true"] {{
  background: #FFFFFF !important;
  color: var(--ink) !important;
  box-shadow: 0 2px 8px rgba(15,23,42,.12);
  flex: 1 1 auto !important;
  font-weight: 700;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--ink); }}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
.stTabs [data-baseweb="tab-border"]    {{ display: none !important; }}

/* ─── Pemilih sumber gambar (st.radio horizontal bergaya segmented tab) ── */
/* Paksa lebar penuh di seluruh rantai pembungkus Streamlit agar segmented
   benar-benar selebar section di bawahnya (item 2). */
.st-key-src_mode {{ width: 100% !important; }}
.st-key-src_mode div[data-testid="stRadio"] {{ width: 100% !important; }}
.st-key-src_mode div[data-testid="stRadio"] > div {{ width: 100% !important; }}
.st-key-src_mode [role="radiogroup"] {{
  display: flex !important; flex-wrap: nowrap !important; gap: 6px;
  background: #F1F5F9; border-radius: 14px;
  padding: 5px; border: none; width: 100% !important;
}}
.st-key-src_mode [role="radiogroup"] > label {{
  flex: 0 1 auto; min-width: 0;
  display: flex; align-items: center; justify-content: center;
  margin: 0 !important; padding: 11px 22px; border-radius: 10px; cursor: pointer;
  font-weight: 600; font-size: .92rem; color: var(--ink-soft);
  background: transparent; white-space: nowrap;
  /* peralihan ukuran dibuat lebih lambat & halus (tanpa pantulan) */
  transition:
    flex-grow .55s cubic-bezier(.22,.61,.36,1),
    flex-basis .55s cubic-bezier(.22,.61,.36,1),
    background .35s ease,
    color .35s ease,
    box-shadow .35s ease;
}}
/* sembunyikan bulatan radio bawaan */
.st-key-src_mode [role="radiogroup"] > label > div:first-child {{ display: none !important; }}
/* item terpilih → MEMENUHI ruang (fill) + kartu putih; item lain menjorok ke sisi */
.st-key-src_mode [role="radiogroup"] > label:has(input:checked) {{
  flex: 1 1 0% !important;
  background: #FFFFFF; color: var(--ink); font-weight: 700;
  box-shadow: 0 2px 8px rgba(15,23,42,.12);
}}
.st-key-src_mode [role="radiogroup"] > label:hover {{ color: var(--ink); }}

/* ─── File uploader ─────────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {{
  background: #fff;
  border: 1.5px dashed #CBD5E1;
  border-radius: var(--r);
  transition: border-color .2s, background .2s;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
  border-color: var(--primary); background: #F8FFF9;
}}

/* ─── Camera input — rapikan preview & tombol "Take Photo" (item 3) ── */
/* Wrapper terluar JANGAN meng-clip apa pun, dan beri sedikit padding agar
   border tombol "Take Photo" tidak terpotong di sisi kanan/kiri/bawah. */
[data-testid="stCameraInput"] {{
  overflow: visible !important;
  padding: 2px 2px 4px !important;
  box-sizing: border-box !important;
}}
[data-testid="stCameraInput"] > div {{
  overflow: visible !important;
}}
/* Hanya komponen webcam (preview video) yang dibulatkan & di-clip. */
[data-testid="stCameraInputWebcamComponent"] {{
  margin-bottom: 4px !important;
  border-radius: 18px !important;
  overflow: hidden !important;
}}
[data-testid="stCameraInput"] video {{
  border-radius: 18px !important;
}}
/* Tombol Take Photo: beri jarak dari preview, lebar penuh tapi tak terpotong. */
[data-testid="stCameraInput"] button {{
  margin: 16px 2px 2px !important;
  width: calc(100% - 4px) !important;
  box-sizing: border-box !important;
}}

/* ─── Sidebar branding & stepper ───────────────────────────────────── */
.ns-brand {{
  display: flex; align-items: center; gap: 13px;
  padding: 0 8px 18px; border-bottom: 1px solid var(--line); margin-bottom: 18px;
}}
.ns-logo {{
  width: 52px; height: 52px; border-radius: 14px;
  background: #FFFFFF;
  display: flex; align-items: center; justify-content: center;
  box-shadow:
    0 0 0 1px rgba(22,163,74,.12),
    0 4px 14px rgba(22,163,74,.22);
  flex-shrink: 0; overflow: hidden;
  position: relative;
  transition: transform .18s ease, box-shadow .18s ease;
}}
.ns-logo::after {{
  content: ""; position: absolute; inset: 0; border-radius: 14px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.6); pointer-events: none;
}}
.ns-logo img {{
  width: 44px; height: 44px; object-fit: contain; display: block;
}}
.ns-logo svg {{
  width: 36px; height: 36px; display: block; flex-shrink: 0;
}}
.ns-brand-text {{ display: flex; flex-direction: column; gap: 2px; min-width: 0; }}
.ns-brand-name {{
  font-size: 1.32rem; font-weight: 900; letter-spacing: -.03em; line-height: 1;
  display: inline-flex; align-items: baseline; gap: 0;
}}
/* "Nus" + "ca" menyatu tanpa jarak (item 4) */
.ns-brand-name .ns-nus {{ color: #15324A; font-weight: 900; }}
.ns-brand-name .ns-ca  {{ color: var(--primary); font-weight: 900; }}
.ns-brand-sub {{
  font-size: .6rem; font-weight: 700; letter-spacing: .03em;
  color: var(--muted); text-transform: none;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.ns-progress-label {{
  font-size: .65rem; font-weight: 700; letter-spacing: .14em;
  color: var(--muted); text-transform: uppercase; margin: 0 8px 14px;
}}
.ns-status-dot {{
  display: flex; align-items: center; gap: 7px;
  font-size: .72rem; font-weight: 600; color: var(--primary-deep);
  margin: 0 8px 6px; padding: 7px 10px; background: #ECFDF5;
  border: 1px solid #A7F3D0; border-radius: 99px;
}}
.ns-status-dot span {{
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--primary); animation: ns-blink 1.8s ease-in-out infinite;
}}

/* Steps */
.ns-steps {{ padding: 0 8px; }}
.ns-step {{
  display: flex; gap: 14px; position: relative;
  padding-bottom: 28px; align-items: flex-start;
}}
.ns-step:last-child {{ padding-bottom: 0; }}
.ns-step-rail {{
  position: absolute; left: 17px; top: 36px; bottom: -4px; width: 2px;
  background: var(--line);
}}
.ns-step.done  .ns-step-rail {{ background: var(--primary-dark); }}
.ns-step.active .ns-step-rail {{ background: linear-gradient(var(--primary), var(--line)); }}
.ns-step:last-child .ns-step-rail {{ display: none; }}

.ns-dot {{
  width: 36px; height: 36px; min-width: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #F1F5F9; border: 2px solid #E2E8F0;
  color: var(--muted); z-index: 1; transition: all .3s ease;
}}
.ns-step.active .ns-dot {{
  background: var(--primary-dark); border-color: transparent; color: #fff;
  box-shadow: 0 0 0 5px rgba(34,197,94,.15), 0 6px 16px rgba(22,163,74,.28);
  animation: ns-breathe 2.2s ease-in-out infinite;
}}
.ns-step.done .ns-dot {{
  background: var(--primary-dark); border-color: transparent; color: #fff;
  box-shadow: 0 4px 12px rgba(22,163,74,.22);
}}
.ns-dot svg {{ width: 17px; height: 17px; }}

.ns-step-info {{ padding-top: 6px; }}
.ns-step-title {{
  font-size: .9rem; font-weight: 700; color: #B0B8C8; line-height: 1.2;
}}
.ns-step.active .ns-step-title,
.ns-step.done  .ns-step-title {{ color: var(--ink); }}
.ns-step-sub {{
  font-size: .74rem; font-weight: 600; margin-top: 2px; color: #C2C8D0;
}}
.ns-step.active .ns-step-sub {{ color: var(--primary-dark); }}
.ns-step.done  .ns-step-sub {{ color: var(--muted); }}

/* ─── App branding header ────────────────────────────────────────────── */
.ns-app-header {{
  text-align: center; padding: 24px 16px 16px; margin-bottom: 12px;
}}

.ns-app-branding {{
  display: flex; flex-direction: column; align-items: center; gap: 8px;
}}

.ns-app-name {{
  font-size: 2.2rem; font-weight: 900; letter-spacing: -0.02em;
  display: flex; align-items: center; gap: 0;
}}

.ns-app-name-nus {{
  color: #1E293B;
}}

.ns-app-name-ca {{
  color: var(--primary-dark);
}}

.ns-app-tagline {{
  font-size: 0.8rem; font-weight: 600; color: var(--muted);
  letter-spacing: 0.05em; text-transform: uppercase;
  position: relative; padding: 0 16px;
}}

.ns-app-tagline::before,
.ns-app-tagline::after {{
  content: "—"; margin: 0 8px; color: var(--primary-dark);
}}

@media (max-width: 900px) {{
  .ns-app-header {{ padding: 20px 16px 12px; margin-bottom: 8px; }}
  .ns-app-name {{ font-size: 1.8rem; }}
  .ns-app-tagline {{ font-size: 0.75rem; padding: 0 12px; }}
}}

@media (max-width: 720px) {{
  .ns-app-header {{ padding: 16px 12px 8px; margin-bottom: 4px; }}
  .ns-app-name {{ font-size: 1.6rem; }}
  .ns-app-tagline {{ font-size: 0.7rem; padding: 0 8px; }}
}}

/* ─── Hero home ─────────────────────────────────────────────────────── */
.ns-hero-wrap {{
  position: relative; overflow: hidden;
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: nowrap; gap: clamp(10px, 2.5vw, 20px);
  background:
    radial-gradient(120% 140% at 88% 8%, #ECFDF5 0%, rgba(236,253,245,0) 46%),
    linear-gradient(135deg, #FBFDFF 0%, #F3FAF4 52%, #FEF8EC 100%);
  border-radius: 28px; padding: clamp(24px, 4vw, 42px) clamp(20px, 4vw, 44px) clamp(96px, 9vw, 116px);
  margin-bottom: clamp(5px, 3vw, 15px);
  border: 1px solid rgba(15,23,42,.07);
  box-shadow: 0 22px 56px rgba(15,23,42,.07);
  animation: ns-fadeup .5s ease both;
}}
/* Baris tombol hero (st.columns yang memuat .st-key-hero_mulai) ditarik ke
   ATAS sehingga berada DI DALAM kartu hero, menempel rapi di bawah paragraf.
   Pull-up disetel agar tombol jelas di dalam kartu (tidak meluber ke bawah). */
[data-testid="stHorizontalBlock"]:has(.st-key-hero_mulai) {{
  margin-top: clamp(-94px, -9vw, -78px) !important;
  position: relative; z-index: 3;
  padding: 0 clamp(20px, 4vw, 44px);
  margin-bottom: clamp(20px, 3vw, 32px);
  flex-wrap: nowrap !important;
  gap: 12px !important;
}}
/* aksen lengkung tipis di sudut kanan-atas (dekoratif, halus) */
.ns-hero-wrap::before {{
  content: ""; position: absolute; top: -120px; right: -90px;
  width: 320px; height: 320px; border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, rgba(34,197,94,.10), rgba(34,197,94,0) 70%);
  pointer-events: none;
}}
.ns-hero-text {{
  position: relative; z-index: 0.5;
  flex: 1 1 auto; min-width: 0; max-width: 560px;
}}
.ns-hero-wrap h1 {{
  font-family: 'Nunito', 'Inter', sans-serif;
  font-size: clamp(1.6rem, 4.6vw, 3rem); font-weight: 900;
  letter-spacing: -.03em;
  margin: 0 0 clamp(12px, 2vw, 22px); line-height: 1.1;
  color: #2D3436;
}}
.ns-hero-wrap h1 span {{ color: #5CB85C; }}
.ns-hero-wrap p {{
  color: var(--ink-soft); font-size: clamp(.82rem, 1.5vw, 1rem); margin: 0; line-height: 1.7;
  max-width: 520px;
}}
.ns-btn-row {{ display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }}
.ns-btn-primary {{
  display: inline-flex; align-items: center; justify-content: center;
  gap: 9px; background: #111827; color: #fff;
  padding: 14px 28px; border-radius: 16px;
  font-weight: 700; font-size: .96rem; cursor: pointer;
  border: none; text-decoration: none;
  box-shadow: 0 12px 28px rgba(17,24,39,.22);
}}
.ns-btn-outline {{
  display: inline-flex; align-items: center; justify-content: center;
  gap: 9px; background: #fff; color: var(--ink);
  padding: 14px 28px; border-radius: 16px;
  font-weight: 700; font-size: .96rem; cursor: pointer;
  border: 1px solid rgba(15,23,42,.12); text-decoration: none;
  box-shadow: 0 10px 22px rgba(15,23,42,.06);
}}
.ns-hero-illustration-wrap {{
  position: relative; z-index: 1;
  flex: 0 0 auto;
  width: clamp(120px, 26vw, 360px);
  max-width: 42%; min-width: 110px;
  display: flex; align-items: center; justify-content: center;
  transition: width .25s ease, max-width .25s ease;
}}
.ns-hero-illustration-wrap::before {{
  content: ""; position: absolute; inset: 8% 6%;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 45%, #FFFFFF 0%, #F4FBF6 58%, rgba(244,251,246,0) 78%);
  box-shadow: 0 24px 60px rgba(22,163,74,.10);
  z-index: -1;
}}
.ns-hero-illustration {{
  width: 100%; height: auto; object-fit: contain;
  display: block; border-radius: 28px;
  box-shadow: none;
}}
/* Hero TIDAK pernah stacking — ilustrasi tetap di samping teks, hanya
   mengecil saat sempit (sesuai permintaan). */
@media (max-width: 820px) {{
  .ns-hero-illustration-wrap {{ width: clamp(96px, 24vw, 220px); max-width: 34%; min-width: 96px; }}
}}
@media (max-width: 560px) {{
  .ns-hero-illustration-wrap {{ width: 30%; max-width: 30%; min-width: 84px; }}
  .ns-hero-wrap {{ gap: 10px; }}
}}

/* ─── Start-analysis cards (Upload / Camera) ──────────────────────── */
.ns-start-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 32px;
}}
@media (max-width: 640px) {{ .ns-start-grid {{ grid-template-columns: 1fr; }} }}

.ns-start-card {{
  background: var(--card); border: 1.5px dashed #CBD5E1;
  border-radius: var(--r); padding: 28px 20px;
  text-align: center; transition: border-color .2s, box-shadow .2s;
}}
.ns-start-card:hover {{ border-color: var(--primary); box-shadow: var(--md); }}
.ns-start-icon {{
  width: 52px; height: 52px; border-radius: 14px;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 14px;
}}
.ns-start-icon svg {{ width: 26px; height: 26px; color: var(--ink-soft); }}
.ns-start-title {{ font-size: 1rem; font-weight: 700; margin-bottom: 4px; }}
.ns-start-sub {{ font-size: .78rem; color: var(--muted); margin-bottom: 4px; }}
.ns-start-limit {{
  font-size: .65rem; font-weight: 600; color: #A0AEC0;
  text-transform: uppercase; letter-spacing: .05em; margin-bottom: 14px;
}}

/* ─── How it works section (Layout 2 Kolom) ───────────────────────── */
.ns-how-section {{
  display: grid; grid-template-columns: 1.15fr 1fr; gap: 44px;
  align-items: stretch; margin-bottom: 48px; padding: 0 16px;
}}
@media (max-width:900px) {{ .ns-how-section {{ grid-template-columns: 1fr; gap: 20px; }} }}

.ns-how-left {{ display: flex; flex-direction: column; gap: 4px; }}
.ns-how-title {{
  font-size: 1.9rem; font-weight: 800; margin: 0 0 6px;
  color: var(--ink); line-height: 1.15; letter-spacing: -.025em;
  position: relative; padding-bottom: 12px;
}}
.ns-how-title::after {{
  content: ""; position: absolute; left: 0; bottom: 0;
  width: 44px; height: 4px; border-radius: 99px;
  background: linear-gradient(90deg, var(--primary), var(--primary-dark));
}}

.ns-how-steps {{ display: flex; flex-direction: column; gap: 14px; counter-reset: nsstep; }}
.ns-step-card {{
  position: relative; overflow: hidden;
  display: flex; align-items: flex-start; gap: 16px;
  background: #fff; border: 1px solid #EAEEF3;
  border-radius: 16px; padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(16,24,40,.04);
  counter-increment: nsstep;
}}
/* tint sangat halus + border senada per langkah (warna lembut, modern) */
.ns-step-card.blue-bg  {{ background: #F8FBFF; border-color: #E6F0FB; }}
.ns-step-card.green-bg {{ background: #F7FDF9; border-color: #E2F5E9; }}
.ns-step-card.amber-bg {{ background: #FFFDF6; border-color: #F3ECD7; }}
/* nomor langkah samar di sudut kanan-atas — aksen visual halus */
.ns-step-card::after {{
  content: counter(nsstep);
  position: absolute; top: 2px; right: 16px; z-index: 0;
  font-size: 2.6rem; font-weight: 800; line-height: 1;
  color: rgba(15,23,42,.05); pointer-events: none; user-select: none;
}}
.ns-step-card.blue-bg::after  {{ color: rgba(37,99,235,.07); }}
.ns-step-card.green-bg::after {{ color: rgba(22,163,74,.07); }}
.ns-step-card.amber-bg::after {{ color: rgba(202,138,4,.09); }}
/* aksen garis tipis di tepi kiri senada warna langkah — sentuhan modern halus */
.ns-step-card::before {{
  content: ""; position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; z-index: 1; pointer-events: none;
}}
.ns-step-card.blue-bg::before  {{ background: linear-gradient(180deg, #60A5FA, {BLUE_ACCENT}); }}
.ns-step-card.green-bg::before {{ background: linear-gradient(180deg, #4ADE80, var(--primary-dark)); }}
.ns-step-card.amber-bg::before {{ background: linear-gradient(180deg, #FBBF24, #CA8A04); }}

.ns-step-icon {{
  position: relative; z-index: 1;
  width: 46px; height: 46px; min-width: 46px;
  border-radius: 13px; display: flex; align-items: center;
  justify-content: center; flex-shrink: 0;
}}
.ns-step-icon svg {{ width: 23px; height: 23px; }}
.ns-step-icon.blue  {{ background: #E8F1FE; }}
.ns-step-icon.blue svg  {{ color: {BLUE_ACCENT}; }}
.ns-step-icon.green {{ background: #E4F7EC; }}
.ns-step-icon.green svg {{ color: var(--primary-dark); }}
.ns-step-icon.amber {{ background: #FBEFCF; }}
.ns-step-icon.amber svg {{ color: #CA8A04; }}

.ns-step-content {{ position: relative; z-index: 1; flex: 1; min-width: 0; }}
.ns-step-content h4 {{
  font-size: 1.02rem; font-weight: 700; margin: 2px 0 3px;
  color: var(--ink); letter-spacing: -.01em;
}}
.ns-step-content p {{
  font-size: .865rem; color: var(--ink-soft); margin: 0;
  line-height: 1.55;
}}

.ns-how-right {{ display: flex; flex-direction: column; }}
.ns-best-results-card {{
  background: #fff; border: 1px solid #EAEEF3;
  border-radius: 16px; padding: 22px;
  box-shadow: 0 1px 3px rgba(16,24,40,.04); height: 100%;
}}
.ns-best-results-card h4 {{
  font-size: 1.08rem; font-weight: 800; margin: 0 0 18px;
  color: var(--ink); letter-spacing: -.01em;
}}

.ns-best-result-item {{
  display: flex; align-items: flex-start; gap: 13px;
  margin-bottom: 16px;
}}
.ns-best-result-item:last-child {{ margin-bottom: 0; }}

.ns-br-check {{
  width: 22px; height: 22px; min-width: 22px;
  border-radius: 50%; background: var(--primary-dark);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 800; font-size: .72rem;
  margin-top: 1px; box-shadow: 0 1px 2px rgba(22,163,74,.25);
}}

.ns-best-result-item strong {{
  display: block; color: var(--ink); font-weight: 700;
  font-size: .94rem; margin-bottom: 2px; letter-spacing: -.01em;
}}
.ns-best-result-item p {{
  font-size: .82rem; color: var(--ink-soft);
  margin: 0; line-height: 1.55;
}}

/* ─── Loader screen (gaya referensi: gambar di lingkaran + buah melayang) ── */
.ns-loader-outer {{ text-align: center; padding: 8px 16px 0; animation: ns-fadeup .4s ease both; }}

/* Panggung untuk gambar produk + buah melayang */
.ns-scan-stage {{
  position: relative; width: 100%; max-width: 560px; height: 260px;
  margin: 0 auto 8px;
}}

/* Lingkaran gambar produk + cincin hijau berputar (animasi hijau dipertahankan) */
.ns-scan-wrap {{
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  width: 200px; height: 200px;
}}
.ns-scan-ring {{
  position: absolute; inset: 0; border-radius: 50%;
  border: 3px solid #E8EFF3;
  border-top-color: var(--primary);
  border-right-color: #86EFAC;
  animation: ns-spin 1.4s linear infinite;
}}
.ns-scan-ring.r2 {{
  inset: 11px; border: 3px solid transparent;
  border-bottom-color: #34D399; border-left-color: #BBF7D0;
  animation: ns-spin 2.1s linear infinite reverse;
}}
.ns-scan-img {{
  position: absolute; inset: 18px; border-radius: 50%; overflow: hidden;
  box-shadow: 0 12px 30px rgba(15,23,42,.16); background: #F1F5F9;
}}
.ns-scan-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.ns-scan-line {{
  position: absolute; left: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, transparent, #22C55E, transparent);
  border-radius: 99px; box-shadow: 0 0 12px rgba(34,197,94,.8);
  animation: ns-scanline 2.2s ease-in-out infinite;
}}
.ns-scan-chip {{
  position: absolute; top: 6px; right: 6px; z-index: 3;
  width: 38px; height: 38px; border-radius: 50%; background: #fff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 16px rgba(15,23,42,.14);
  animation: ns-breathe 2s ease-in-out infinite;
}}
.ns-scan-chip svg {{ width: 18px; height: 18px; color: var(--primary-dark); }}

/* Buah & minuman melayang */
.ns-fruit {{
  position: absolute; font-size: 38px; z-index: 1;
  filter: drop-shadow(0 6px 10px rgba(15,23,42,.12));
  animation: ns-float 3.4s ease-in-out infinite;
  opacity: .92;
}}
.ns-fruit.f1 {{ left: 6%;  top: 14%; animation-delay: 0s;   }}
.ns-fruit.f2 {{ left: 12%; top: 64%; animation-delay: .7s;  font-size: 32px; }}
.ns-fruit.f3 {{ right: 7%; top: 20%; animation-delay: 1.1s; }}
.ns-fruit.f4 {{ right: 11%;top: 62%; animation-delay: 1.7s; font-size: 34px; }}
.ns-fruit.f5 {{ left: 26%; top: 2%;  animation-delay: 2.1s; font-size: 28px; }}
.ns-fruit.f6 {{ right: 27%;top: 4%;  animation-delay: 1.4s; font-size: 28px; }}

.ns-loader-title {{
  font-size: 1.4rem; font-weight: 800; letter-spacing: -.02em; margin-bottom: 6px;
}}
.ns-loader-sub {{
  color: var(--ink-soft); font-size: .92rem; max-width: 420px; margin: 0 auto 22px;
  line-height: 1.6;
}}
.ns-step-list {{
  display: flex; flex-direction: column; gap: 11px;
  max-width: 360px; margin: 0 auto;
  text-align: left;
  background: #fff; border: 1px solid var(--line); border-radius: 14px;
  padding: 16px 18px; box-shadow: var(--sm);
}}
.ns-step-row {{
  display: flex; align-items: center; justify-content: space-between;
  font-size: .87rem; padding: 1px 0;
}}
.ns-step-left  {{ display: flex; align-items: center; gap: 10px; color: var(--muted); font-weight: 500; }}
.ns-step-left.done   {{ color: var(--ink); }}
.ns-step-left.active {{ color: var(--primary-deep); font-weight: 700; }}
.ns-step-ic {{
  width: 22px; height: 22px; border-radius: 50%;
  background: #EEF1F4; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}}
.ns-step-left.done   .ns-step-ic {{ background: var(--primary-dark); }}
.ns-step-left.active .ns-step-ic {{ background: var(--primary-dark); animation: ns-blink 1.2s ease-in-out infinite; }}
.ns-step-ic svg {{ width: 11px; height: 11px; color: #fff; }}
.ns-step-status {{
  font-size: .7rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
}}
.ns-step-status.done   {{ color: var(--primary-dark); }}
.ns-step-status.active {{ color: {BLUE_ACCENT}; }}
.ns-step-status.wait   {{ color: var(--muted); }}
.ns-loader-pill {{
  margin-top: 22px; display: inline-flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg,#1e293b,#0f172a); color: #fff;
  padding: 13px 38px; border-radius: 14px;
  font-weight: 700; font-size: .95rem;
  box-shadow: 0 8px 22px rgba(15,23,42,.28);
}}
.ns-loader-pill .ns-spin-sm {{
  width: 17px; height: 17px; border-radius: 50%;
  border: 2.5px solid rgba(34,197,94,.35);
  border-top-color: #22C55E;
  animation: ns-spin .8s linear infinite;
}}

/* ─── Mode banner ───────────────────────────────────────────────────── */
.ns-banner {{
  display: flex; align-items: center; gap: 9px;
  font-size: .78rem; font-weight: 600;
  border-radius: 10px; padding: 8px 13px; margin-bottom: 18px; border: 1px solid;
}}
.ns-banner.model {{ background: #ECFDF5; border-color: #A7F3D0; color: var(--primary-deep); }}
.ns-banner.demo  {{ background: #FEF9C3; border-color: #FDE68A; color: #854D0E; }}
.ns-banner .dot  {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.ns-banner.model .dot {{ background: var(--primary); }}
.ns-banner.demo  .dot {{ background: #EAB308; }}

/* ─── Result page header ─────────────────────────────────────────────── */
.ns-result-header {{
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 22px; animation: ns-fadeup .45s ease both;
}}
.ns-result-header h2 {{
  font-size: clamp(1.3rem, 3.5vw, 1.6rem); font-weight: 800; letter-spacing: -.025em; margin: 0 0 4px;
  line-height: 1.15;
}}
.ns-result-header .ns-meta {{
  font-size: .82rem; color: var(--muted); font-weight: 500;
}}
.ns-confidence {{
  display: flex; align-items: center; gap: 8px;
  font-size: .8rem; font-weight: 700;
}}
.ns-confidence-num {{
  font-size: 1.4rem; font-weight: 800; color: var(--primary-dark);
}}

/* ─── GGL Badge per-komponen ─────────────────────────────────────────── */
.ns-ggl-grid {{
  display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 22px;
}}
@media (max-width:640px) {{ .ns-ggl-grid {{ grid-template-columns: 1fr; }} }}

.ns-ggl-card {{
  background: var(--card); border: 1px solid var(--line); border-radius: 18px;
  overflow: hidden; box-shadow: var(--sm);
  animation: ns-fadeup .5s ease both;
}}
.ns-ggl-head {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 18px 12px; gap: 12px;
}}
.ns-ggl-title {{ font-weight: 800; font-size: .92rem; color: var(--ink); letter-spacing: -.01em; }}

/* Pil ringkas sesuai referensi (lingkaran solid + kartu putih persen/nama) */
.ns-ggl-pill {{ display: inline-flex; align-items: center; flex-shrink: 0; }}
.ns-ggl-pill-circle {{
  width: clamp(44px, 12vw, 52px); height: clamp(44px, 12vw, 52px); border-radius: 50%; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: clamp(1.2rem, 4vw, 1.5rem); line-height: 1; letter-spacing: -.02em;
  border: 3px solid #fff; box-shadow: 0 6px 16px rgba(0,0,0,.16);
  position: relative; z-index: 2; margin-right: -16px; flex-shrink: 0;
}}
.ns-ggl-pill-info {{
  display: flex; flex-direction: column; justify-content: center;
  background: #fff; border: 1px solid var(--line); border-radius: 14px;
  padding: 8px 16px 8px 26px; box-shadow: var(--sm); min-width: 76px;
}}
.ns-ggl-pill-pct {{ font-size: 1.18rem; font-weight: 800; color: var(--ink); line-height: 1.05; letter-spacing: -.02em; }}
.ns-ggl-pill-name {{ font-size: .74rem; font-weight: 600; color: var(--muted); text-transform: lowercase; }}
.ns-ggl-body {{ padding: 0 18px 16px; }}
.ns-ggl-val {{ font-size: 1.15rem; font-weight: 700; }}
.ns-ggl-per100 {{ font-size: .74rem; color: var(--muted); margin-top: 2px; }}
.ns-ggl-pct {{
  font-size: .78rem; font-weight: 700; margin-top: 0px;
}}

/* Skala A/B/C/D horizontal — gaya selektor pil seperti referensi */
.ns-ggl-scale {{
  display: flex; gap: 6px; margin-top: 14px;
  background: #F1F5F9; border-radius: 12px; padding: 5px;
}}
.ns-ggl-scale-item {{
  flex: 1; height: 46px; border-radius: 9px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px;
  font-size: .92rem; font-weight: 800; letter-spacing: .01em;
  background: transparent; color: #B6BEC8; transition: all .28s cubic-bezier(.2,.9,.3,1.2);
}}
.ns-ggl-scale-item small {{ font-size: .54rem; font-weight: 700; opacity: .85; letter-spacing: 0; line-height: 1; }}
.ns-ggl-scale-item.active-a {{ background: #16A34A; color: #fff; transform: scale(1.06); box-shadow: 0 6px 14px rgba(22,163,74,.40); }}
.ns-ggl-scale-item.active-b {{ background: #84CC16; color: #fff; transform: scale(1.06); box-shadow: 0 6px 14px rgba(132,204,22,.40); }}
.ns-ggl-scale-item.active-c {{ background: #F59E0B; color: #fff; transform: scale(1.06); box-shadow: 0 6px 14px rgba(245,158,11,.40); }}
.ns-ggl-scale-item.active-d {{ background: #EF4444; color: #fff; transform: scale(1.06); box-shadow: 0 6px 14px rgba(239,68,68,.40); }}

/* ─── Kartu Grade utama (gaya referensi "Good Quality") ────────────── */
.ns-grade-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 20px; padding: clamp(18px, 3vw, 28px); margin-bottom: 18px;
  box-shadow: var(--md); display: flex; gap: clamp(18px, 3vw, 28px); align-items: stretch;
  animation: ns-fadeup .45s ease both;
}}
@media (max-width: 760px) {{ .ns-grade-card {{ flex-direction: column; gap: 20px; }} }}
.ns-grade-left {{ flex: 1; min-width: 0; }}
.ns-grade-eyebrow {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }}
.ns-grade-pill {{
  font-size: .68rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
  background: #DCFCE7; color: #166534; padding: 5px 12px; border-radius: 99px;
}}
.ns-grade-conf {{ font-size: .72rem; font-weight: 700; color: var(--ink-soft); }}
.ns-grade-conf b {{ font-size: 1.05rem; color: var(--primary-dark); }}
.ns-grade-title {{ font-size: clamp(1.5rem, 4.5vw, 2rem); font-weight: 900; letter-spacing: -.03em; margin: 2px 0 12px; line-height: 1.08; }}
.ns-grade-desc {{ font-size: clamp(.86rem, 1.6vw, .95rem); color: var(--ink-soft); line-height: 1.65; max-width: 460px; }}
.ns-grade-right {{ width: 320px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; }}
@media (max-width: 760px) {{ .ns-grade-right {{ width: 100%; }} }}

/* Selektor pil besar A-B-C-D di kartu grade */
.ns-grade-pills {{ display: flex; gap: clamp(6px, 1.2vw, 8px); margin-bottom: 18px; }}
.ns-grade-pill-item {{
  flex: 1; aspect-ratio: 1; border-radius: clamp(10px, 1.6vw, 14px);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.05rem, 3.4vw, 1.5rem); font-weight: 800;
  background: #F1F5F9; color: #C2C8D0; transition: all .3s cubic-bezier(.2,.9,.3,1.2);
}}
/* Saat layar mengecil, pil ikut mengecil */
@media (max-width: 520px) {{
  .ns-grade-pill-item {{ max-width: 56px; max-height: 56px; font-size: .95rem; }}
  .ns-grade-pills {{ gap: 5px; }}
}}
.ns-grade-pill-item.on-a {{ background: #16A34A; color: #fff; transform: scale(1.1); box-shadow: 0 10px 22px rgba(22,163,74,.40); }}
.ns-grade-pill-item.on-b {{ background: #84CC16; color: #fff; transform: scale(1.1); box-shadow: 0 10px 22px rgba(132,204,22,.40); }}
.ns-grade-pill-item.on-c {{ background: #F59E0B; color: #fff; transform: scale(1.1); box-shadow: 0 10px 22px rgba(245,158,11,.40); }}
.ns-grade-pill-item.on-d {{ background: #EF4444; color: #fff; transform: scale(1.1); box-shadow: 0 10px 22px rgba(239,68,68,.40); }}

.ns-grade-score-row {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }}
.ns-grade-score-lbl {{ font-size: .82rem; font-weight: 600; color: var(--ink-soft); }}
.ns-grade-score-val {{ font-size: .82rem; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }}
.ns-grade-score-bar {{ height: 9px; border-radius: 99px; background: #EEF1F4; overflow: hidden; }}
.ns-grade-score-fill {{ height: 100%; border-radius: 99px; transition: width 1s cubic-bezier(.2,.8,.2,1); }}

/* ─── Analyzed label + Alert/Breakdown (dua kolom) ─────────────────── */
.ns-row2 {{
  display: grid; grid-template-columns: 1.1fr 1.5fr; gap: 16px; margin-bottom: 22px;
  align-items: stretch;
}}
.ns-row2 > * {{
  min-height: 0;
}}

.ns-breakdown-wrap {{
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100%;
  justify-content: stretch;
}}
.ns-breakdown-wrap > .ns-alert,
.ns-breakdown-wrap > .ns-note,
.ns-breakdown-wrap > .ns-breakdown-card {{
  flex-shrink: 0;
}}
.ns-breakdown-wrap > .ns-breakdown-card {{
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
}}

@media (max-width:720px) {{ .ns-row2 {{ grid-template-columns: 1fr; }} }}

/* Analyzed Label Card (preview gambar dideteksi) */
.ns-analyzed-label-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 18px; overflow: hidden; box-shadow: var(--sm);
  animation: ns-fadeup .5s ease .05s both;
  display: flex; flex-direction: column; height: fit-content;
}}
.ns-analyzed-label-head {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px 12px;
}}
.ns-analyzed-label-title {{ 
  font-size: .75rem; font-weight: 700; color: var(--muted); 
  text-transform: uppercase; letter-spacing: .08em; 
}}
.ns-view-full-link {{
  font-size: .75rem; font-weight: 600; color: #3B82F6; 
  text-decoration: none; cursor: pointer; transition: color .2s;
}}
.ns-view-full-link:hover {{ color: #1E40AF; }}
.ns-analyzed-label-content {{
  display: flex; flex-direction: column; padding: 12px; gap: 12px;
}}
.ns-analyzed-label-img {{
  width: 100%; height: auto; object-fit: contain;
  display: block; border-radius: 14px; max-height: 420px;
  background: #F1F5F9;
}}
.ns-detect-badges-area {{
  display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; 
  padding: 0; margin-top: auto;
}}
.ns-detect-badge-new {{
  font-size: .7rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  padding: 8px 16px; border-radius: 6px; background: #475569; color: #fff;
  display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}}
.ns-serving-info-row {{
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0;
  border-top: 1px solid var(--line);
}}
.ns-serving-info-col {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 12px; text-align: center;
}}
.ns-serving-info-col:not(:last-child) {{ border-right: 1px solid var(--line); }}
.ns-si-label {{
  font-size: .65rem; font-weight: 600; color: var(--muted); 
  text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px;
}}
.ns-si-val {{ font-size: .9rem; font-weight: 700; color: var(--ink); }}

.ns-label-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 18px; overflow: hidden; box-shadow: var(--sm);
  animation: ns-fadeup .5s ease .05s both;
  display: flex; flex-direction: column; min-height: 400px;
}}
.ns-label-head {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px 12px;
}}
.ns-label-head-title {{ font-size: .82rem; font-weight: 700; color: var(--ink-soft); text-transform: uppercase; letter-spacing: .06em; }}
.ns-label-img-container {{
  flex: 1; overflow: hidden; display: flex; align-items: center; justify-content: center;
  background: #F8FAFC; border-radius: 14px; margin: 0 14px; min-height: 280px;
}}
.ns-label-img {{
  width: 100%; height: 100%; object-fit: contain; display: block;
}}
.ns-label-img-wrapper {{
  position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
  background: #F8FAFC; border-radius: 14px; margin: 0 14px; min-height: 280px; flex: 1;
}}
.ns-label-img {{
  width: 100%; height: 100%; object-fit: contain; display: block;
}}
.ns-detect-overlay {{
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;
  width: calc(100% - 28px); padding: 0 14px;
}}
.ns-detect-badge {{
  font-size: .7rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  padding: 8px 14px; border-radius: 6px; background: rgba(71, 85, 105, 0.85); color: #fff;
  backdrop-filter: blur(4px); display: inline-block;
}}
.ns-label-meta {{ display: flex; gap: 6px; flex-wrap: wrap; padding: 0 16px 14px; }}
.ns-tag {{
  font-size: .65rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  padding: 4px 9px; border-radius: 6px; background: #1e293b; color: #fff;
}}
.ns-label-serving {{
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0;
  border-top: 1px solid var(--line); padding: 14px 16px;
}}
.ns-serving-item {{ text-align: center; }}
.ns-serving-item:not(:last-child) {{ border-right: 1px solid var(--line); }}
.ns-serving-label {{ font-size: .65rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 3px; }}
.ns-serving-val {{ font-size: .9rem; font-weight: 700; color: var(--ink); }}

/* Alert */
.ns-alert {{
  background: #FFF1F2; border: 1px solid #FECDD3; border-radius: 14px;
  padding: 14px 16px; margin-bottom: 12px;
  animation: ns-fadeup .5s ease .1s both;
}}
.ns-alert-head {{
  display: flex; align-items: center; gap: 8px;
  font-size: .9rem; font-weight: 700; color: #BE123C; margin-bottom: 6px;
}}
.ns-alert svg {{ width: 17px; height: 17px; }}
.ns-alert-body {{ font-size: .82rem; color: #9F1239; line-height: 1.5; }}
.ns-alert-body strong {{ color: #BE123C; }}

/* Breakdown (detail) */
.ns-breakdown-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 14px 16px;
  box-shadow: var(--sm); animation: ns-fadeup .5s ease .15s both;
  display: flex; flex-direction: column; min-height: 500px;
}}
.ns-breakdown-title {{ font-size: .9rem; font-weight: 700; margin-bottom: 14px; }}
.ns-bd-item {{ margin-bottom: 16px; }}
.ns-bd-item:last-child {{ margin-bottom: 0; }}
.ns-serving-summary {{
  background: #F8FAFC; border-radius: 8px; padding: 12px 14px; margin-bottom: 14px;
  font-size: .8rem;
}}
.ns-ss-row {{
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
}}
.ns-ss-row:last-child {{ margin-bottom: 0; }}
.ns-ss-label {{ font-weight: 600; color: #475569; font-size: .75rem; text-transform: uppercase; }}
.ns-ss-val {{ font-weight: 700; color: #0F172A; }}
.ns-bd-divider {{
  border: none; border-top: 1px solid #E2E8F0; margin: 12px 0; opacity: .5;
}}
.ns-bd-row1 {{
  display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3px;
}}
.ns-bd-name {{ font-size: .85rem; font-weight: 700; }}
.ns-bd-right {{ display: flex; align-items: baseline; gap: 6px; }}
.ns-bd-pct {{ font-size: .82rem; font-weight: 700; color: var(--ink-soft); }}
.ns-bd-daily {{ font-size: .65rem; color: var(--muted); text-transform: uppercase; }}
.ns-bd-val {{ font-size: .78rem; font-weight: 600; margin-bottom: 4px; }}
.ns-bd-bar {{ height: 6px; border-radius: 99px; background: #EEF1F4; overflow: hidden; }}
.ns-bd-fill {{ height: 100%; border-radius: 99px; transition: width .9s cubic-bezier(.2,.8,.2,1); }}
.ns-other-gizi-row {{
  display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: .78rem;
}}
.ns-og-label {{ font-weight: 600; color: #475569; }}
.ns-og-val {{ font-weight: 700; color: #0F172A; }}

/* ─── New Results Layout (2-column design) ────────────────────────── */
.ns-results-container {{
  display: grid; grid-template-columns: 1.1fr 1.5fr; gap: 16px; margin-bottom: 22px;
  align-items: stretch;
}}

.ns-results-left {{
  display: flex; flex-direction: column; gap: 16px; min-height: 100%;
}}

.ns-results-right {{
  display: flex; flex-direction: column; gap: 16px; min-height: 100%;
}}

.ns-detailed-breakdown {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 20px 16px;
  box-shadow: var(--sm); animation: ns-fadeup .5s ease .15s both;
}}

.ns-breakdown-title {{
  font-size: 1rem; font-weight: 700; color: var(--ink);
  margin-bottom: 16px;
}}

.ns-breakdown-item {{
  display: flex; align-items: stretch; gap: 12px;
  margin-bottom: 16px; padding: 12px; border-radius: 8px;
  background: #F8FAFC;
}}

.ns-breakdown-item:last-child {{
  margin-bottom: 0;
}}

.ns-breakdown-left-bar {{
  width: 4px; border-radius: 2px; flex-shrink: 0;
}}

.ns-breakdown-content {{
  flex: 1; display: flex; flex-direction: column; justify-content: space-between;
}}

.ns-breakdown-head {{
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 4px;
}}

.ns-breakdown-name {{
  font-size: .9rem; font-weight: 700; color: var(--ink);
}}

.ns-breakdown-pct {{
  font-size: .9rem; font-weight: 700; color: var(--ink);
}}

.ns-breakdown-level {{
  font-size: .75rem; font-weight: 600; color: var(--ink-soft);
  margin-bottom: 6px;
}}

.ns-breakdown-progress-bar {{
  height: 6px; background: #E2E8F0; border-radius: 3px;
  overflow: hidden; margin-bottom: 4px;
}}

.ns-breakdown-progress-fill {{
  height: 100%; border-radius: 3px;
  transition: width .6s cubic-bezier(.2,.8,.2,1);
}}

.ns-breakdown-footer {{
  display: flex; justify-content: space-between; align-items: center;
}}

.ns-breakdown-daily {{
  font-size: .7rem; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: .04em;
}}

@media (max-width:720px) {{
  .ns-results-container {{ grid-template-columns: 1fr; }}
}}

/* ─── Intake chart bars ─────────────────────────────────────────────── */
.ns-chart-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 18px; padding: 20px 22px;
  box-shadow: var(--sm); margin-bottom: 22px;
  animation: ns-fadeup .5s ease .2s both;
}}
.ns-chart-head {{
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
}}
.ns-chart-title {{ font-size: 1rem; font-weight: 700; }}
.ns-chart-sub {{ font-size: .78rem; color: var(--muted); margin-bottom: 20px; }}
.ns-chart-legend {{ display: flex; gap: 14px; }}
.ns-legend-item {{ display: flex; align-items: center; gap: 5px; font-size: .72rem; font-weight: 600; color: var(--ink-soft); }}
.ns-legend-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
.ns-bars-area {{
  display: flex; align-items: flex-end; gap: clamp(16px, 4vw, 48px); height: 150px;
  border-bottom: 1px solid #E2E8F0; padding-bottom: 0; position: relative;
  flex: 1 1 auto; min-width: 0;            /* ISI penuh lebar kartu (fill) */
}}
.ns-guide-100 {{
  position: absolute; top: 0; left: 0; right: 0;
  border-top: 1.5px dashed #CBD5E1;
  font-size: .6rem; color: var(--muted); font-weight: 600; padding-left: 4px;
}}
.ns-bar-col {{ flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; }}
.ns-bar-outer {{ width: 100%; max-width: 96px; margin: 0 auto; border-radius: 8px 8px 0 0; background: #F1F5F9; flex: 1; display: flex; align-items: flex-end; }}
.ns-bar-fill {{ width: 100%; border-radius: 8px 8px 0 0; transition: height .9s cubic-bezier(.2,.8,.2,1); }}
.ns-bar-label {{ font-size: .65rem; font-weight: 600; color: var(--ink-soft); text-align: center; margin-top: 7px; }}
.ns-bar-pct {{ font-size: .7rem; font-weight: 700; color: var(--ink); }}
/* Sumbu-Y grafik asupan: judul (rotasi 90°) + tick 0%/100% sejajar skala */
.ns-chart-plot {{ display: flex; align-items: stretch; gap: 6px; }}
.ns-yaxis-title {{
  writing-mode: vertical-rl; transform: rotate(180deg);
  font-size: .62rem; font-weight: 700; letter-spacing: .03em;
  color: var(--muted); text-transform: uppercase; white-space: nowrap;
  display: flex; align-items: center; justify-content: center; flex: 0 0 auto;
}}
.ns-yaxis-ticks {{ position: relative; width: 30px; flex: 0 0 auto; }}
.ns-yaxis-ticks span {{
  position: absolute; right: 2px; line-height: 1;
  font-size: .6rem; font-weight: 600; color: var(--muted);
}}

/* ─── Field hasil baca ──────────────────────────────────────────────── */
.ns-field-grid {{
  display: grid; grid-template-columns: repeat(3,1fr); gap: 10px;
}}
@media (max-width:640px) {{ .ns-field-grid {{ grid-template-columns: repeat(2,1fr); }} }}
.ns-field {{
  background: #fff; border: 1px solid var(--line); border-radius: 12px;
  padding: 12px 14px; animation: ns-fadeup .4s ease both;
  transition: transform .15s, box-shadow .2s;
}}
.ns-field-label {{
  font-size: .67rem; font-weight: 700; color: var(--muted);
  text-transform: uppercase; letter-spacing: .05em; margin-bottom: 5px;
}}
.ns-field-val {{ font-size: 1.05rem; font-weight: 700; color: var(--ink); }}
.ns-field-val.empty {{ color: #CBD5E1; font-weight: 600; }}

/* ─── Consumption tips ──────────────────────────────────────────────── */
.ns-tips-card {{
  position: relative; overflow: hidden;
  display: grid; grid-template-columns: 0.9fr 2.6fr; gap: 18px; align-items: center;
  background: linear-gradient(135deg, #3B3A9E 0%, #353394 55%, #2E2C82 100%);
  border-radius: 22px; padding: 26px 30px;
  color: #fff; margin-bottom: 22px;
  animation: ns-fadeup .5s ease .25s both;
  box-shadow: 0 14px 32px rgba(46, 44, 130, .30);
}}
@media (max-width: 860px) {{ .ns-tips-card {{ grid-template-columns: 1fr; gap: 18px; }} }}
/* lengkungan dekoratif kanan-atas (seperti referensi) */
.ns-tips-deco {{
  position: absolute; top: -70px; right: -70px; width: 190px; height: 190px;
  border-radius: 50%;
  border: 30px solid rgba(255,255,255,.06);
  pointer-events: none;
}}
.ns-tips-head {{ position: relative; z-index: 1; }}
.ns-tips-head h3 {{ font-size: 1.45rem; font-weight: 800; margin: 0 0 8px; letter-spacing: -.01em; }}
.ns-tips-sub {{ font-size: .82rem; color: #C7C5F0; line-height: 1.55; }}
.ns-tips-items {{
  position: relative; z-index: 1;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px;
}}
@media (max-width: 720px) {{ .ns-tips-items {{ grid-template-columns: 1fr; gap: 16px; }} }}
.ns-tip-col {{ display: flex; flex-direction: column; }}
.ns-tip-col-icon {{
  width: 38px; height: 38px; border-radius: 11px;
  background: rgba(255,255,255,.12);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 11px;
}}
.ns-tip-col-icon svg {{ width: 18px; height: 18px; color: #C7C5F0; }}
.ns-tip-col-title {{ font-size: .92rem; font-weight: 700; margin-bottom: 6px; color: #FFFFFF; }}
.ns-tip-col-body {{ font-size: .78rem; color: #B9B7E8; line-height: 1.55; }}

/* ─── Bottom action bar ─────────────────────────────────────────────── */
.ns-action-bar {{
  display: flex; justify-content: center; gap: 12px; padding-top: 8px;
}}
.ns-action-btn {{
  display: inline-flex; align-items: center; gap: 7px;
  padding: 10px 24px; border-radius: 12px;
  font-weight: 700; font-size: .88rem; cursor: pointer; border: none;
}}
.ns-action-btn.outline {{
  background: transparent; color: var(--ink-soft);
  border: 1.5px solid var(--line);
}}
.ns-action-btn.primary {{
  background: var(--primary-dark); color: #fff;
  box-shadow: 0 4px 14px rgba(22,163,74,.28);
}}

/* ─── Crop page ─────────────────────────────────────────────────────── */
.ns-crop-header {{
  margin-bottom: 16px; animation: ns-fadeup .4s ease both;
}}
.ns-crop-header h2 {{
  font-size: 1.4rem; font-weight: 800; letter-spacing: -.02em; margin: 0 0 4px;
}}
.ns-crop-header p {{ font-size: .9rem; color: var(--ink-soft); margin: 0; }}

.ns-crop-tip {{
  display: flex; align-items: flex-start; gap: 10px;
  background: #FFFBEB; border: 1px solid #FDE68A;
  border-radius: 12px; padding: 12px 15px; margin-bottom: 18px;
  font-size: .85rem; color: #92400E; line-height: 1.5;
}}
.ns-crop-tip svg {{ width: 17px; height: 17px; flex-shrink: 0; margin-top: 1px; color: #D97706; }}

.ns-preview-tag {{
  display: inline-flex; align-items: center; gap: 6px;
  font-size: .68rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: var(--primary-deep); background: #ECFDF5;
  border: 1px solid #A7F3D0; border-radius: 99px; padding: 4px 11px; margin-bottom: 10px;
}}

/* ─── Catatan / note ───────────────────────────────────────────────── */
.ns-note {{
  display: flex; gap: 10px; background: #FFFBEB; border: 1px solid #FDE68A;
  border-radius: 12px; padding: 12px 14px; font-size: .82rem; color: #92400E;
  line-height: 1.5; margin-bottom: 8px;
}}
.ns-note.info {{ background: #EFF6FF; border-color: #BFDBFE; color: #1E40AF; }}
.ns-note svg {{ width: 15px; height: 15px; flex-shrink: 0; margin-top: 2px; }}

.ns-divider {{ height: 1px; background: var(--line); margin: 20px 0; border: 0; }}

/* ─── Animações ────────────────────────────────────────────────────── */
@keyframes ns-fadeup {{
  from {{ opacity: 0; transform: translateY(9px); }}
  to   {{ opacity: 1; transform: none; }}
}}
@keyframes ns-pop {{
  0%   {{ opacity: 0; transform: scale(.93); }}
  100% {{ opacity: 1; transform: none; }}
}}
@keyframes ns-spin  {{ to {{ transform: rotate(360deg); }} }}
@keyframes ns-blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.35; }} }}
@keyframes ns-breathe {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.07); }} }}
@keyframes ns-scanline {{ 0%,100% {{ top: 12%; }} 50% {{ top: 84%; }} }}
@keyframes ns-float {{ 0%,100% {{ transform: translateY(0) rotate(-3deg); }} 50% {{ transform: translateY(-14px) rotate(3deg); }} }}

/* ─── Cropper: pastikan gambar asli tampil utuh & MUAT di dalam box ── */
[data-testid="stImageContainer"] img,
.stImage img {{ border-radius: 14px; }}

/* Section pembungkus kolom crop & pratinjau (margin + radius seragam) */
.ns-crop-section {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 20px; padding: 16px; margin: 4px 4px 8px;
  box-shadow: var(--sm);
}}

/* Box yang membungkus kanvas cropper — gambar HARUS mengikuti lebar box.
   overflow:hidden + max-width:100% pada kanvas mencegah gambar meluap. */
.ns-cropper-box {{
  width: 100%; border-radius: 16px; overflow: hidden;
  background: #F1F5F9; display: flex; justify-content: center;
}}
.ns-cropper-box > div {{ max-width: 100% !important; }}
.ns-cropper-box [data-testid="stImageContainer"],
.ns-cropper-box .stImage {{ max-width: 100% !important; }}
.ns-cropper-box canvas {{
  max-width: 100% !important; height: auto !important;
  border-radius: 14px; display: block;
}}
/* streamlit-cropper kadang membungkus kanvas di div ber-style inline width */
div[class*="cropper"] {{ max-width: 100% !important; }}
div[class*="cropper"] canvas,
.streamlit-cropper canvas {{ max-width: 100% !important; height: auto !important; }}
/* Cropper dirender sebagai KOMPONEN di dalam IFRAME. CSS dari halaman induk
   tak bisa mengecilkan <canvas> di dalam iframe (itu ditangani skrip responsif
   di app.py yang masuk ke dokumen iframe). Aturan di bawah HANYA lapis pengaman:
   bila skrip itu gagal (mis. iframe beda-origin), kontainer komponen tetap
   dibatasi selebar kolom dan luapan kanvas DI-CLIP, sehingga tidak pernah
   menimpa kartu atau keluar layar. Catatan: komponen pihak-ketiga memakai
   data-testid "stCustomComponentV1" (bukan "stIFrame"), jadi keduanya disasar. */
[data-testid="stCustomComponentV1"],
[data-testid="stCustomComponent"],
[data-testid="stIFrame"] {{ max-width: 100% !important; }}
[data-testid="stCustomComponentV1"]:has(iframe[title*="cropper" i]),
[data-testid="stCustomComponent"]:has(iframe[title*="cropper" i]) {{
  overflow: hidden !important; border-radius: 14px;
}}
iframe[title*="cropper" i] {{ max-width: 100% !important; display: block; }}

/* Pratinjau langsung: gambar dalam box rounded yang fit */
.ns-preview-section {{ display: flex; flex-direction: column; gap: 10px; }}
.ns-preview-imgbox {{
  width: 100%; height: 300px; overflow: hidden; border-radius: 16px;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;
}}
.ns-preview-img {{ width: 100%; height: 100%; object-fit: contain; display: block; border-radius: 16px; }}
.ns-preview-meta {{
  background: #F8FAFC; border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
}}
.ns-pm-row {{ display: flex; justify-content: space-between; align-items: center; font-size: .8rem; padding: 5px 0; }}
.ns-pm-row.ns-pm-last {{ border-top: 1px solid #E9EEF4; margin-top: 4px; padding-top: 9px; }}
.ns-pm-key {{ color: var(--muted); font-weight: 600; }}
.ns-pm-val {{ font-weight: 700; color: var(--ink); }}

/* Pratinjau unggah di beranda — badge sejajar vertikal dgn gambar (item 4) */
.ns-uppreview {{ display: flex; flex-direction: column; gap: 10px; }}
.ns-uppreview .ns-preview-tag {{ margin-bottom: 0; align-self: flex-start; }}
.ns-uppreview-imgbox {{
  width: 100%; height: clamp(260px, 38vw, 380px); overflow: hidden; border-radius: 18px;
  background: #F1F5F9; display: block; border: 1px solid var(--line);
}}
/* Gambar MENGISI penuh kotak (tanpa celah) — item 5 */
.ns-uppreview-img {{ width: 100%; height: 100%; object-fit: cover; display: block; border-radius: 18px; }}

/* Kartu Pratinjau Langsung tunggal (badge + gambar + metadata) — gaya gambar 6 */
.ns-live-card {{
  background: var(--card); border: 1px solid var(--line);
  border-radius: 20px; padding: 16px; box-shadow: var(--sm);
  display: flex; flex-direction: column; gap: 12px;
}}
.ns-live-card .ns-preview-tag {{ margin-bottom: 0; align-self: flex-start; }}
.ns-live-imgbox {{
  width: 100%; min-height: 300px; border-radius: 14px; overflow: hidden;
  background: #F1F5F9; display: flex; align-items: center; justify-content: center;
}}
.ns-live-img {{ width: 100%; height: auto; max-height: 460px; object-fit: contain; display: block; }}
.ns-live-meta {{
  background: #F8FAFC; border: 1px solid var(--line); border-radius: 14px; padding: 6px 14px;
}}
</style>
""", unsafe_allow_html=True)

    # ── CSS tambahan untuk komponen baru ───────────────────────────────────
    # (string biasa, bukan f-string — gunakan var(--…) yang sudah didefinisikan)
    st.markdown("""
<style>
/* Hero: badge + statistik */
.ns-hero-badge {
  display:inline-flex; align-items:center; gap:6px; font-size:.72rem; font-weight:700;
  color:var(--primary-deep); background:rgba(255,255,255,.72); border:1px solid #BBF7D0;
  padding:6px 13px; border-radius:99px; margin-bottom:16px;
}
.ns-hero-stats { display:flex; align-items:center; gap:18px; margin-top:26px; }
.ns-hero-stat { display:flex; flex-direction:column; }
.ns-hero-stat b { font-size:1.4rem; font-weight:900; color:var(--ink); letter-spacing:-.02em; line-height:1; }
.ns-hero-stat span { font-size:.72rem; color:var(--ink-soft); margin-top:4px; }
.ns-hero-stat-div { width:1px; height:34px; background:var(--line); }
@media (max-width:640px){ .ns-hero-stats { flex-wrap:wrap; gap:14px; } }

/* Infografik Nutri-Level (logo simplifikasi A/B/C/D + %) */
.ns-info-wrap { margin:2px 0 20px; }
.ns-info-caption {
  font-size:.72rem; font-weight:700; color:var(--muted);
  text-transform:uppercase; letter-spacing:.06em; margin-bottom:11px;
}
.ns-info-row { display:flex; flex-wrap:wrap; gap:16px; }
.ns-info-badge { display:inline-flex; align-items:center; animation:ns-pop .5s ease both; }
.ns-info-circle {
  width:56px; height:56px; border-radius:50%; color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-size:1.75rem; font-weight:900; line-height:1; border:3px solid #fff;
  box-shadow:0 6px 16px rgba(0,0,0,.18); position:relative; z-index:2; margin-right:-18px;
}
.ns-info-pill {
  display:flex; flex-direction:column; justify-content:center;
  background:#fff; border:1px solid var(--line); border-radius:13px;
  padding:7px 16px 7px 27px; box-shadow:var(--sm); min-width:64px;
}
.ns-info-pill b { font-size:1.1rem; font-weight:800; color:var(--ink); line-height:1.05; }
.ns-info-pill span { font-size:.72rem; font-weight:600; color:var(--muted); }

/* Strip ringkasan dasar perhitungan */
.ns-sum-strip { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:2px; }
@media (max-width:720px){ .ns-sum-strip { grid-template-columns:repeat(2,1fr); } }
.ns-sum-tile {
  display:flex; gap:11px; align-items:flex-start; background:var(--card);
  border:1px solid var(--line); border-radius:14px; padding:14px 15px;
  box-shadow:var(--sm); animation:ns-fadeup .45s ease both;
}
.ns-sum-ic { font-size:1.2rem; line-height:1; }
.ns-sum-body { min-width:0; }
.ns-sum-lbl { font-size:.68rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
.ns-sum-val { font-size:1.02rem; font-weight:800; color:var(--ink); margin:3px 0 1px; }
.ns-sum-sub { font-size:.72rem; color:var(--ink-soft); line-height:1.35; }

/* Acuan batas Kepmenkes */
.ns-thr-card {
  background:var(--card); border:1px solid var(--line); border-radius:18px;
  padding:18px 20px; box-shadow:var(--sm); margin-bottom:2px; animation:ns-fadeup .5s ease both;
}
.ns-thr-head { display:flex; gap:11px; align-items:flex-start; margin-bottom:8px; }
.ns-thr-head svg { width:20px; height:20px; color:var(--primary-dark); flex-shrink:0; margin-top:1px; }
.ns-thr-title { font-weight:800; font-size:.98rem; }
.ns-thr-sub { font-size:.76rem; color:var(--muted); line-height:1.45; margin-top:2px; }
.ns-thr-row {
  display:grid; grid-template-columns:140px 1fr 132px; gap:12px; align-items:center;
  padding:11px 0; border-top:1px solid #F1F5F9;
}
@media (max-width:720px){ .ns-thr-row { grid-template-columns:1fr; gap:8px; } }
.ns-thr-name { font-weight:700; font-size:.86rem; }
.ns-thr-scale { display:flex; gap:6px; flex-wrap:wrap; }
.ns-thr-chip { font-size:.68rem; font-weight:700; padding:3px 9px; border-radius:7px; white-space:nowrap; }
.ns-thr-chip.a { background:#DCFCE7; color:#166534; }
.ns-thr-chip.b { background:#ECFCCB; color:#3F6212; }
.ns-thr-chip.c { background:#FEF3C7; color:#92400E; }
.ns-thr-chip.d { background:#FEE2E2; color:#991B1B; }
.ns-thr-val { display:flex; align-items:center; gap:8px; justify-content:flex-end; }
.ns-thr-val > span { font-size:.86rem; font-weight:800; color:var(--ink); white-space:nowrap; }
.ns-thr-val small { font-size:.66rem; font-weight:600; color:var(--muted); }
.ns-thr-now {
  width:26px; height:26px; border-radius:8px; color:#fff; font-weight:800; font-size:.82rem;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
@media (max-width:720px){ .ns-thr-val { justify-content:flex-start; } }

/* Tambahan kartu komponen GGL: rincian per sajian/kemasan + chip gula */
.ns-ggl-detail { display:flex; gap:14px; flex-wrap:wrap; margin-top:7px; }
.ns-ggl-detail span { font-size:.74rem; color:var(--muted); }
.ns-ggl-detail b { color:var(--ink); font-weight:700; }
.ns-ggl-chips { display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; }
.ns-ggl-chips span {
  font-size:.68rem; font-weight:600; color:var(--ink-soft);
  background:#F1F5F9; border-radius:7px; padding:3px 9px;
}

/* Ikon aksi pada header hasil (bagikan / unduh) */
.ns-header-actions { display:flex; gap:9px; flex-shrink:0; }
.ns-header-btn {
  width:38px; height:38px; border-radius:11px; background:var(--card);
  border:1px solid var(--line); display:flex; align-items:center; justify-content:center;
  color:var(--ink-soft); box-shadow:var(--sm); transition:all .15s; cursor:default;
}
.ns-header-btn:hover { color:var(--primary-dark); border-color:#BBF7D0; transform:translateY(-1px); }

/* Tombol Cetak / PDF (tombol Streamlit asli, memicu window.print()) */
.st-key-print_pdf_btn button {
  background:#fff !important; color:var(--ink-soft) !important;
  border:1.5px solid var(--line) !important; border-radius:12px !important;
  font-weight:700 !important; font-size:.82rem !important;
  box-shadow:var(--sm) !important;
}
.st-key-print_pdf_btn button::after { display:none !important; }
.st-key-print_pdf_btn button:hover {
  border-color:#16A34A !important; color:var(--primary-dark) !important;
  background:#F8FFF9 !important; transform:translateY(-1px) !important;
}

/* Tombol "Tentang Nutri-Level" di header — samakan gaya dengan Cetak/PDF */
.st-key-open_nl_info_result button {
  background:#fff !important; color:var(--ink-soft) !important;
  border:1.5px solid var(--line) !important; border-radius:12px !important;
  font-weight:700 !important; font-size:.82rem !important;
  box-shadow:var(--sm) !important;
}
.st-key-open_nl_info_result button:hover {
  border-color:#16A34A !important; color:var(--primary-dark) !important;
  background:#F8FFF9 !important; transform:translateY(-1px) !important;
}

/* Baris tombol navigasi bawah — di tengah, lebar seragam (item 8) */
.ns-nav-btns { max-width:680px; margin:0 auto; }
.ns-nav-btns + div [data-testid="column"] { display:flex; align-items:stretch; }

/* Insight per komponen GGL berdasarkan aturan Kepmenkes (item 2) */
.ns-ggl-insight {
  margin-top:12px; padding:10px 12px; border-radius:11px;
  border:1px solid var(--line); background:#F8FAFC;
}
.ns-ggl-insight.ins-a { background:#F0FDF4; border-color:#BBF7D0; }
.ns-ggl-insight.ins-b { background:#F7FEE7; border-color:#D9F99D; }
.ns-ggl-insight.ins-c { background:#FFFBEB; border-color:#FDE68A; }
.ns-ggl-insight.ins-d { background:#FEF2F2; border-color:#FECACA; }
.ns-ggl-insight-rule {
  font-size:.66rem; font-weight:800; letter-spacing:.02em;
  text-transform:uppercase; color:var(--ink-soft); margin-bottom:3px;
}
.ns-ggl-insight-text { font-size:.76rem; color:var(--ink-soft); line-height:1.5; }

/* Strip label resmi Nutri-Level A-B-C-D (gaya Kepmenkes) */
.ns-nlstrip { display:flex; gap:clamp(7px,2vw,10px); justify-content:center; margin:6px 0 18px; }
.ns-nlstrip-cell { position:relative; flex:0 0 auto; }
.ns-nlstrip-letter {
  position:relative; width:clamp(42px,13vw,54px); height:clamp(42px,13vw,54px); border-radius:clamp(10px,2.6vw,13px);
  display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:clamp(1.15rem,4vw,1.5rem); line-height:1;
  box-shadow:0 2px 6px rgba(15,23,42,.10);
}
.ns-nlstrip-cell.on .ns-nlstrip-letter {
  transform:scale(1.08); box-shadow:0 8px 18px rgba(15,23,42,.20);
}
.ns-nlstrip-arrow {
  position:absolute; left:50%; transform:translateX(-50%);
  bottom:-12px; width:0; height:0;
  border-left:7px solid transparent; border-right:7px solid transparent;
  border-top:8px solid currentColor;
}

/* Dialog penjelasan Nutri-Level (item 6) */
.ns-nlinfo-lead { font-size:.86rem; color:var(--ink-soft); line-height:1.7; margin:0 0 14px; text-align:justify; }
.ns-nlinfo-rows { display:flex; flex-direction:column; gap:9px; margin-top:6px; }
.ns-nlinfo-row { display:flex; align-items:flex-start; gap:11px; }
.ns-nlinfo-badge {
  width:30px; height:30px; min-width:30px; border-radius:9px; color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:.95rem; flex-shrink:0;
}
.ns-nlinfo-text { font-size:.8rem; color:var(--ink-soft); line-height:1.5; padding-top:3px; text-align:justify; }
.ns-nlinfo-note {
  margin-top:14px; padding:11px 13px; border-radius:11px;
  background:#F1F5F9; border:1px solid var(--line);
  font-size:.74rem; color:var(--ink-soft); line-height:1.6; text-align:justify;
}

/* Saat mencetak: sembunyikan elemen UI non-konten agar PDF rapi */
@media print {
  [data-testid="stSidebar"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarHeader"],
  #ns-custom-sidebar-toggle,
  .stButton,
  iframe,
  .ns-hidden-trigger { display:none !important; }
  .block-container { max-width:100% !important; padding:0 !important; }
  .stApp { background:#fff !important; }
}

/* Judul bagian (mis. "Mulai Analisis") */
.ns-section-title {
  font-size: clamp(1.05rem, 2.4vw, 1.25rem); font-weight: 800; color: var(--ink);
  letter-spacing: -.015em; display: flex; align-items: center; gap: 10px;
}
.ns-section-title::before {
  content: ""; width: 4px; height: 1.1em; border-radius: 99px; flex-shrink: 0;
  background: linear-gradient(180deg, var(--primary), var(--primary-deep));
}
/* Sub-judul ringan untuk hierarki yang harmonis (item 7) */
.ns-section-sub {
  font-size: .85rem; color: var(--muted); font-weight: 500; line-height: 1.6;
  margin: 4px 0 0;
}

/* Tombol pemicu modal "View Full Image" — disembunyikan dari layout
   (pengganti label_visibility yang tidak didukung st.button).
   Streamlit menambahkan kelas .st-key-<key> pada kontainer widget. */
.st-key-view_full_image { position:absolute !important; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); margin:-1px; padding:0; border:0; }
.ns-hidden-trigger { display:none; }
.ns-btn-outline { cursor:pointer; }

/* Tombol hero ASLI (Streamlit) — ditata seperti tombol di desain hero.
   "Mulai Pindai" gelap; "Pelajari Cara Kerja" putih ber-outline. */
.st-key-hero_mulai button {
  background: #111827 !important;
  color: #fff !important;
  border: none !important;
  border-radius: clamp(11px, 2vw, 16px) !important;
  font-weight: 700 !important;
  font-size: clamp(.72rem, 2.7vw, .95rem) !important;
  padding: clamp(.5rem, 1.7vw, .8rem) clamp(.5rem, 2vw, 1.4rem) !important;
  box-shadow: 0 12px 28px rgba(17,24,39,.22) !important;
}
.st-key-hero_mulai button:hover {
  filter: brightness(1.1) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 16px 32px rgba(17,24,39,.30) !important;
}
.st-key-hero_mulai button::after { display:none !important; }
.st-key-hero_pelajari button {
  background: #fff !important;
  color: #0F172A !important;
  border: 1.5px solid rgba(15,23,42,.12) !important;
  border-radius: clamp(11px, 2vw, 16px) !important;
  font-weight: 700 !important;
  font-size: clamp(.72rem, 2.7vw, .95rem) !important;
  padding: clamp(.5rem, 1.7vw, .8rem) clamp(.5rem, 2vw, 1.4rem) !important;
  box-shadow: 0 10px 22px rgba(15,23,42,.06) !important;
}
.st-key-hero_pelajari button:hover {
  border-color: #16A34A !important;
  color: var(--primary-dark) !important;
  background: #F8FFF9 !important;
  transform: translateY(-2px) !important;
}
/* Posisi vertikal baris tombol hero diatur via aturan stHorizontalBlock
   (lihat blok pertama). Di sini cukup tata gaya tombolnya saja. */

/* Pertahankan kedua tombol hero SELALU bersisian (tidak menumpuk) bahkan saat
   layar sempit / sidebar terbuka. Streamlit kerap memaksa kolom jadi full-width
   di mobile; kita timpa agar tetap horizontal. */
[data-testid="stHorizontalBlock"]:has(.st-key-hero_mulai) {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: stretch !important;
}
[data-testid="stHorizontalBlock"]:has(.st-key-hero_mulai) > [data-testid="stColumn"] {
  width: auto !important;
  flex: 0 1 auto !important;
  min-width: 0 !important;
}
/* kolom spacer (ketiga) boleh menyusut habis saat sempit */
[data-testid="stHorizontalBlock"]:has(.st-key-hero_mulai) > [data-testid="stColumn"]:last-child {
  flex: 1 1 0% !important;
}
.st-key-hero_mulai button,
.st-key-hero_pelajari button {
  white-space: nowrap !important;
  width: 100% !important;
  min-width: 0 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
/* Label teks di dalam tombol (Streamlit membungkusnya dalam <p>) HARUS
   mewarisi font-size responsif tombol, bukan ukuran default-nya, agar ikut
   mengecil di layar kecil dan tidak terpotong. */
.st-key-hero_mulai button p,
.st-key-hero_pelajari button p {
  font-size: inherit !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  margin: 0 !important;
  max-width: 100% !important;
}
/* HP layar sangat kecil: rapatkan padding, gap, & font agar kedua tombol
   muat sebaris tanpa terpotong. */
@media (max-width: 400px) {
  [data-testid="stHorizontalBlock"]:has(.st-key-hero_mulai) {
    padding-left: 14px !important;
    padding-right: 14px !important;
    gap: 6px !important;
  }
  .st-key-hero_mulai button,
  .st-key-hero_pelajari button {
    padding: .5rem .4rem !important;
    font-size: clamp(.62rem, 3.3vw, .8rem) !important;
  }
}

/* Tombol "lanjut/next" proses deteksi — biru agak tua (item 7) */
.st-key-to_crop button,
.st-key-to_loading button,
.st-key-restart button {
  background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
  box-shadow: 0 6px 18px rgba(30,64,175,.32), inset 0 1px 0 rgba(255,255,255,.18) !important;
  color: #fff !important;
}
.st-key-to_crop button:hover,
.st-key-to_loading button:hover,
.st-key-restart button:hover {
  filter: brightness(1.06) !important;
  box-shadow: 0 12px 28px rgba(30,64,175,.42), inset 0 1px 0 rgba(255,255,255,.22) !important;
}
.st-key-to_crop button:focus:not(:active),
.st-key-to_loading button:focus:not(:active),
.st-key-restart button:focus:not(:active) {
  box-shadow: 0 0 0 4px rgba(37,99,235,.25), 0 6px 18px rgba(30,64,175,.32) !important;
}

/* ── Kartu petunjuk "Ambil foto dengan kamera" ── */
.ns-cam-hint {
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 12px;
}
.ns-cam-hint-title {
  font-weight: 700;
  font-size: .92rem;
  color: #1E40AF;
  margin-bottom: 4px;
}
.ns-cam-hint-sub {
  font-size: .83rem;
  color: #1e3a8a;
  line-height: 1.6;
}

/* ── Tombol "Buka Kamera" (disuntik via JS menggantikan dropzone) ── */
.ns-cam-open-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: clamp(.8rem, 2vw, 1rem) 1.4rem;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563EB, #1E40AF);
  color: #fff;
  font-family: inherit;
  font-weight: 700;
  font-size: clamp(.9rem, 2.4vw, 1rem);
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(30,64,175,.30);
  transition: transform .15s, box-shadow .2s, filter .2s;
}
.ns-cam-open-btn:hover {
  filter: brightness(1.06);
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(30,64,175,.40);
}
.ns-cam-open-btn:active {
  transform: translateY(0) scale(.99);
}
.ns-cam-open-btn svg {
  flex: 0 0 auto;
}

/* ── Kamera RESPONSIF: desktop (camera_input tertanam) vs mobile (tombol) ──
   Strategi: SEMBUNYIKAN kamera tertanam pada layar HP; tampilkan HANYA pada
   layar lebar (≥ 901px). Dengan begitu di HP `st.camera_input` tidak pernah
   tampil (display:none juga menghentikan stream webcam), dan yang muncul hanya
   tombol "Buka Kamera". Toggle murni CSS → responsif instan saat resize.

   Kita menyembunyikan via dua jalur agar tidak bergantung waktu eksekusi JS:
   (a) langsung ke widget Streamlit [data-testid="stCameraInput"], dan
   (b) ke kelas .ns-cam-desktop-w yang disuntik JS pada pembungkusnya. */
@media (max-width: 900px) {
  [data-testid="stCameraInput"],
  .ns-cam-desktop-w {
    display: none !important;
  }
  .ns-cam-mobile {
    display: block !important;
  }
}

@media (min-width: 901px) {
  /* Desktop: tampilkan kamera tertanam, sembunyikan tombol native mobile. */
  .ns-cam-mobile {
    display: none !important;
  }
}

/* Penanda kosong (div pengait) tidak perlu memakan ruang. */
#ns-cam-desktop, #ns-cam-marker, #ns-cam-marker-end { display: none; }


/* ════════════════════════════════════════════════════════════════════════
   PERBAIKAN SIDEBAR (navbar) & TOMBOL HEADER  (override final)
   - Sidebar mengisi penuh tinggi layar, tanpa scrollbar.
   - Logo/brand naik mendekati pojok kiri-atas; glow tidak terpotong.
   - Status (Mode Demo / Model siap) menempel di DASAR sidebar.
   - Tombol "Cetak / PDF" & "Tentang Nutri-Level" hug ke lebar teks (1 baris).
   ════════════════════════════════════════════════════════════════════════ */

/* Sidebar: tanpa scrollbar, isi penuh tinggi viewport */
section[data-testid="stSidebar"] { overflow: hidden !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  height: 100vh !important;
  height: 100dvh !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  padding-top: 4px !important;
  padding-bottom: 16px !important;
  padding-left: 4px !important;
  padding-right: 4px !important;
}
/* Header bawaan (tombol collapse) dikecilkan → brand naik ke atas.
   Toggle tetap tersedia lewat tombol mengambang kustom (kiri-atas). */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
  height: 0 !important; min-height: 0 !important;
  padding: 0 !important; margin: 0 !important;
}
/* Konten mengisi sisa tinggi → status dapat didorong ke dasar.
   padding-top memberi ruang agar GLOW logo tidak terpotong; padding-left
   dirapatkan agar konten dekat ke pojok kiri. */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
  flex: 1 1 auto !important; min-height: 0 !important;
  display: flex !important; flex-direction: column !important;
  padding: 24px 10px 0 12px !important;
}
/* Pembungkus emotion antara userContent dan blok vertikal harus ikut flex. */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {
  flex: 1 1 auto !important; min-height: 0 !important;
  display: flex !important; flex-direction: column !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  flex: 1 1 auto !important; min-height: 0 !important;
  display: flex !important; flex-direction: column !important;
  gap: 0 !important;
}
/* Jangan biarkan flexbox MENGECILKAN kontainer (membuat pill status terpotong).
   Tiap elemen tetap pada tinggi alaminya. */
section[data-testid="stSidebar"] [data-testid="stElementContainer"] {
  flex: 0 0 auto !important;
}
/* Dorong kontainer status ke DASAR sidebar. */
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.ns-sidebar-status-sticky) {
  margin-top: auto !important;
}
.ns-sidebar-status-sticky {
  position: static !important;
  margin: 0 !important;
  padding: 12px 6px 72px !important;
  background: transparent !important;
}
/* Brand & langkah dirapatkan ke kiri (mendekati pojok) — padding atas/kiri cukup agar logo tidak terpotong. */
.ns-brand { padding: 6px 6px 16px 10px !important; margin-bottom: 16px !important; }
.ns-progress-label { margin: 0 6px 14px !important; }
.ns-steps { padding: 0 6px !important; }
.ns-status-dot { margin: 0 6px !important; }

/* Tombol header: sejajar dengan meta text, satu baris. */
[data-testid="stHorizontalBlock"]:has(.st-key-print_pdf_btn) {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: flex-end !important;
  gap: 8px !important;
}
[data-testid="stHorizontalBlock"]:has(.st-key-print_pdf_btn) > [data-testid="stColumn"] {
  flex: 0 1 auto !important;
  min-width: 0 !important;
}
/* Kolom header (pertama) — mengisi sisa ruang */
[data-testid="stHorizontalBlock"]:has(.st-key-print_pdf_btn) > [data-testid="stColumn"]:first-child {
  flex: 1 1 auto !important;
}
.st-key-print_pdf_btn button, .st-key-open_nl_info_result button {
  white-space: nowrap !important;
  font-size: .8rem !important;
  padding: .5rem .85rem !important;
}
/* Hilangkan margin bawah header agar sejajar dengan tombol */
.ns-result-header { margin-bottom: 4px !important; }

/* Tombol lihat gambar penuh (tanpa outline, gaya text link) */
.ns-view-full-btn {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: .72rem; font-weight: 600; color: #3B82F6;
  background: none; border: none; cursor: pointer;
  padding: 4px 8px; border-radius: 6px;
  transition: background .15s, color .15s;
}
.ns-view-full-btn:hover {
  background: #EFF6FF; color: #1D4ED8;
}

/* Modal popup full image — CSS-only checkbox hack */
.ns-fullimg-checkbox {
  position: absolute; opacity: 0; pointer-events: none;
  width: 0; height: 0;
}
.ns-fullimg-modal {
  display: none; position: fixed; inset: 0; z-index: 999999;
  align-items: center; justify-content: center;
  padding: 24px;
}
.ns-fullimg-checkbox:checked ~ .ns-fullimg-modal {
  display: flex;
}
.ns-fullimg-overlay {
  position: fixed; inset: 0; cursor: pointer;
  background: rgba(0,0,0,.7); backdrop-filter: blur(6px);
}
.ns-fullimg-inner {
  position: relative; max-width: 90vw; max-height: 90vh;
  background: #fff; border-radius: 16px; padding: 12px;
  box-shadow: 0 24px 64px rgba(0,0,0,.3);
  overflow: auto; z-index: 1;
}
.ns-fullimg-inner img {
  display: block; max-width: 100%; max-height: 82vh;
  object-fit: contain; border-radius: 10px;
}
.ns-fullimg-close {
  position: absolute; top: 8px; right: 8px;
  width: 32px; height: 32px; border: none; border-radius: 50%;
  background: rgba(0,0,0,.5); color: #fff;
  font-size: 1.3rem; line-height: 1; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s; z-index: 2;
}
.ns-fullimg-close:hover { background: rgba(0,0,0,.75); }

/* ─── Status antrean (layar memproses) ───────────────────────────────── */
.ns-queue {
  display: flex; align-items: center; gap: 10px;
  max-width: 460px; margin: 4px auto 14px; padding: 11px 16px;
  border-radius: 12px; font-size: .86rem; font-weight: 600;
  line-height: 1.45; animation: ns-fadeup .35s ease both;
}
.ns-queue.wait { background: #1E293B; color: #E2E8F0; border: 1px solid #334155; }
.ns-queue.go   { background: #16A34A; color: #fff; border: 1px solid #15803D; }
.ns-queue b { font-weight: 800; }
.ns-queue-ic { display: inline-flex; flex: 0 0 auto; }
.ns-queue.wait .ns-queue-ic { animation: ns-qspin 1.4s linear infinite; }
@keyframes ns-qspin { to { transform: rotate(360deg); } }

/* ─── Mobile: tombol header (Cetak/PDF & Tentang Nutri-Level) → ikon saja ─
   Di layar sempit teks tombol memakan tempat & bisa terpotong. Sembunyikan
   label teks (<p>) dan rapatkan tombol jadi kotak ikon. Emoji di awal label
   tetap tampil sebagai ikon (lewat ::first-letter). */
@media (max-width: 640px) {
  .st-key-print_pdf_btn button p,
  .st-key-open_nl_info_result button p {
    font-size: 0 !important;
    line-height: 0 !important;
  }
  .st-key-print_pdf_btn button p::first-letter,
  .st-key-open_nl_info_result button p::first-letter {
    font-size: 1.15rem !important;
  }
  .st-key-print_pdf_btn button,
  .st-key-open_nl_info_result button {
    padding: 0 !important; min-width: 44px !important; width: 44px !important;
    height: 44px !important; aspect-ratio: 1 / 1; margin-left: auto;
  }
}

/* ════════════════════════════════════════════════════════════════════════
   1) Rapatkan ruang kosong di ATAS konten.
   Default Streamlit memberi padding-atas besar (≈6rem) pada kontainer utama
   yang menimpa setelan kita -> muncul celah kosong besar. Paksa kecil di SEMUA
   selektor kontainer yang mungkin dipakai lintas-versi.
   ════════════════════════════════════════════════════════════════════════ */
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"] .block-container,
section.main > div.block-container,
.appview-container .main .block-container,
.block-container {
  padding-top: 0.6rem !important;
}

/* ════════════════════════════════════════════════════════════════════════
   CELAH ATAS BESAR — penyebab utamanya: iframe penyuntik dari
   components.html(height=0) (auto-scroll, toggle sidebar, dll). Di sebagian
   versi Streamlit iframe ini TIDAK ikut diciutkan oleh aturan atribut height=0
   bawaan, sehingga menyisakan tinggi default ~150px -> ruang kosong di atas.
   Semua iframe components.html membawa atribut srcdoc; komponen cropper memakai
   atribut src (BUKAN srcdoc) sehingga TIDAK PERNAH cocok dengan selektor ini —
   cropper aman. Pakai position:absolute + visibility:hidden (BUKAN display:none)
   agar script di dalam iframe tetap dieksekusi browser. */
[data-testid="stElementContainer"]:has(iframe[srcdoc]) {
  position: absolute !important;
  width: 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  visibility: hidden !important;
  pointer-events: none !important;
}
iframe[srcdoc] {
  position: absolute !important;
  width: 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  visibility: hidden !important;
}
/* AKAR celah kosong besar di atas konten: iframe-injektor dari components.html
   (auto-scroll, toggle sidebar, dll) TIDAK terkolaps di sebagian versi Streamlit
   sehingga memakai tinggi iframe default (~150px). Semua iframe components.html
   punya atribut `srcdoc`; komponen sungguhan seperti cropper memakai `src`.
   Jadi kita keluarkan TOTAL dari flow HANYA kontainer ber-srcdoc -> celah hilang,
   dan cropper/kamera AMAN (tak pernah tersentuh). Pakai position:absolute (bukan
   display:none) agar script di dalam iframe dijamin tetap dieksekusi. */
[data-testid="stElementContainer"]:has(iframe[srcdoc]) {
  position: absolute !important;
  width: 0 !important; height: 0 !important;
  margin: 0 !important; padding: 0 !important;
  overflow: hidden !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

/* Hilangkan ikon anchor/tautan (🔗) yang Streamlit suntikkan & muncul saat hover
   di setiap heading — tidak ada gunanya bagi pengguna. Cakup semua varian
   struktur/versi Streamlit agar benar-benar hilang. */
[data-testid="stHeaderActionElements"],
[data-testid="StyledLinkIconContainer"],
[data-testid="stHeaderLink"],
.stMarkdown a.anchor-link,
.stMarkdown a.headerLink,
.stHeading [data-testid="stHeaderActionElements"],
.stHeading a[href^="#"],
.stMarkdown :is(h1,h2,h3,h4,h5,h6) a[href^="#"],
:is(h1,h2,h3,h4,h5,h6) > a[href^="#"]:first-child,
:is(h1,h2,h3,h4,h5,h6) [data-testid="stHeaderActionElements"],
.stMarkdown a[href^="#"]:has(svg) {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  pointer-events: none !important;
}

/* ════════════════════════════════════════════════════════════════════════
   1) Tombol Putar Kiri / Kanan / Reset: LEBAR MENGIKUTI TEKS (hug content) dan
   teks TIDAK PERNAH membungkus ke bawah — selalu sebaris & bersisian, di semua
   ukuran layar. Kolom-tombol dibuat seukuran konten; kolom spacer menyerap sisa
   ruang sehingga tombol rapat di kiri (desktop maupun mobile). */
[data-testid="stHorizontalBlock"]:has(.st-key-rot_left) {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: stretch !important;
  gap: 10px !important;
}
/* kolom yang berisi tombol -> seukuran konten (tidak meregang) */
[data-testid="stHorizontalBlock"]:has(.st-key-rot_left) > [data-testid="stColumn"]:has(button) {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
}
/* kolom spacer (tanpa tombol) -> serap sisa ruang, dorong tombol ke kiri */
[data-testid="stHorizontalBlock"]:has(.st-key-rot_left) > [data-testid="stColumn"]:not(:has(button)) {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}
/* tombol seukuran teksnya, satu baris (nowrap) */
.st-key-rot_left button, .st-key-rot_right button, .st-key-rot_reset button {
  width: auto !important;
  min-width: 0 !important;
  white-space: nowrap !important;
  padding: .55rem .95rem !important;
}
/* paksa NOWRAP pada SEMUA elemen di dalam tombol (p / div / span / dll) agar
   teks tak pernah turun ke baris berikutnya, apa pun struktur DOM Streamlit. */
.st-key-rot_left button *, .st-key-rot_right button *, .st-key-rot_reset button * {
  white-space: nowrap !important;
  word-break: keep-all !important;
  overflow-wrap: normal !important;
}
.st-key-rot_left button p, .st-key-rot_right button p, .st-key-rot_reset button p {
  font-size: clamp(.74rem, 2.6vw, .9rem) !important;  /* mengecil di HP agar tetap muat sebaris */
  margin: 0 !important;
}

/* ════════════════════════════════════════════════════════════════════════
   3) Baris Foto Ulang / Konfirmasi & Analisis: tetap bersisian di mobile
   (desktop sudah bersisian). Hanya perlu override di layar sempit.
   ════════════════════════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  [data-testid="stHorizontalBlock"]:has(.st-key-back_cap) {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 8px !important;
  }
  [data-testid="stHorizontalBlock"]:has(.st-key-back_cap) > [data-testid="stColumn"] {
    flex: 1 1 0 !important;
    width: auto !important;
    min-width: 0 !important;
  }
  /* Label panjang ("Konfirmasi & Analisis") boleh membungkus 2 baris agar utuh;
     tinggi kedua tombol disamakan oleh align-items:stretch. */
  .st-key-back_cap button, .st-key-to_loading button {
    white-space: normal !important;
    width: 100% !important; min-width: 0 !important;
    padding: .6rem .5rem !important;
    line-height: 1.2 !important;
  }
  .st-key-back_cap button p, .st-key-to_loading button p {
    font-size: clamp(.74rem, 3.2vw, .92rem) !important;
    white-space: normal !important;
    margin: 0 !important; max-width: 100% !important;
  }
}
</style>
""", unsafe_allow_html=True)
