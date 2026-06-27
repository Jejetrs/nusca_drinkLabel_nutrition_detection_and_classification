"""
ui/components.py — NutriScan AI (Minuman Kemasan)
==================================================
Komponen visual tingkat tinggi. Tampilan hasil meniru desain referensi:
kartu grade utama, kartu GGL per komponen dengan selektor pil A-D, label
kemasan + alert + rincian, grafik asupan, dan saran konsumsi.

PENTING: semua HTML disuntik lewat _md() yang menghapus indentasi awal baris.
Tanpa ini, baris HTML yang menjorok 4+ spasi akan dianggap "code block" oleh
parser markdown Streamlit dan tampil sebagai teks mentah (bukan ter-render).
"""

import base64
import io
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from core.nutrilevel import NL_BATAS

ASSET_ROOT = Path(__file__).resolve().parent.parent / "asset"


# ─── Helper anti code-block markdown ─────────────────────────────────────────
def _md(html: str):
    """Render HTML via st.markdown TANPA terkena aturan indented-code-block."""
    cleaned = "\n".join(line.lstrip() for line in html.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def scroll_to_top():
    """Paksa jendela induk scroll ke paling atas.

    Streamlit mempertahankan posisi scroll antar-rerun (efek 'layar beku' yang
    masih menampilkan konten halaman sebelumnya). Dipanggil di awal tiap layar
    agar setiap halaman selalu mulai dari atas.
    """
    components.html(
        "<script>window.parent.scrollTo({top:0,left:0,behavior:'instant'});</script>",
        height=0,
    )


def queue_notice(position: int):
    """Banner status antrean. position: 1 = giliran sekarang, >1 = menunggu."""
    if position and position > 1:
        ahead = position - 1
        txt = (f"Anda berada di <b>antrean ke-{position}</b> — menunggu "
               f"{ahead} permintaan lain selesai. Mohon tunggu sebentar…")
        cls, ic = "wait", _IC_CLOCK
    else:
        txt = "Giliran Anda — memproses gambar sekarang…"
        cls, ic = "go", _IC_SPARK
    _md(f'<div class="ns-queue {cls}"><span class="ns-queue-ic">{ic}</span>'
        f'<span>{txt}</span></div>')


def _asset_uri(filename: str) -> str:
    path = ASSET_ROOT / filename
    if not path.exists():
        return ""
    data = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def _img_uri(pil, max_px=620, fmt="JPEG"):
    """PIL.Image -> data URI (untuk disematkan dalam kartu HTML)."""
    if pil is None:
        return None
    try:
        im = pil.copy()
        im.thumbnail((max_px, max_px))
        buf = io.BytesIO()
        im.convert("RGB").save(buf, format=fmt, quality=85)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _img_uri_full(pil, fmt="JPEG"):
    """PIL.Image -> data URI (full resolution untuk modal)."""
    if pil is None:
        return None
    try:
        buf = io.BytesIO()
        pil.convert("RGB").save(buf, format=fmt, quality=90)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _ic(path: str, w: int = 24, sw: float = 2, extra: str = "") -> str:
    """Bangun ikon SVG inline (stroke-based, mirip Lucide)."""
    return (f'<svg viewBox="0 0 24 24" width="{w}" height="{w}" fill="none" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" {extra}>{path}</svg>')


_IC_CHECK = _ic('<path d="M20 6 9 17l-5-5"/>', sw=3)
_IC_WARN  = _ic('<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><path d="M12 9v4M12 17h.01"/>')
_IC_INFO  = _ic('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>')
_IC_CHART = _ic('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>', extra='color="#CA8A04"')
_IC_CLOCK = _ic('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>', w=18, extra='color="#C7D2FE"')
_IC_SCALE = _ic('<path d="M16 16 3 3"/><path d="M21 21H3"/><path d="M3.58 12.42 8 8l4 4 4-4.5"/>', w=18, extra='color="#C7D2FE"')
_IC_LEAF  = _ic('<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/>', w=18, extra='color="#C7D2FE"')
_IC_SPARK = _ic('<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>', w=22, extra='color="#fff"')
_IC_CPU   = _ic('<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>')


# ─── Peta level ──────────────────────────────────────────────────────────────
_GRADE_COLOR = {"A": "#16A34A", "B": "#84CC16", "C": "#F59E0B", "D": "#EF4444"}
_GRADE_BG    = {"A": "#DCFCE7", "B": "#ECFCCB", "C": "#FEF3C7", "D": "#FEE2E2"}
_GRADE_LABEL = {"A": "Sangat Rendah", "B": "Rendah", "C": "Sedang", "D": "Tinggi"}
_QUALITY     = {"A": "Sangat Baik", "B": "Kualitas Baik", "C": "Kualitas Sedang", "D": "Perlu Diperhatikan"}

# Warna RESMI Nutri-Level sesuai Kepmenkes HK.01.07/MENKES/301/2026
# (Lampiran B.4.b — konversi CMYK → RGB, disesuaikan agar akurat secara visual):
#   A Hijau tua  CMYK 100/25/100/0 ; B Hijau muda CMYK 55/0/100/0
#   C Kuning     CMYK 0/30/90/0    ; D Merah      CMYK 20/100/100/10
_NL_OFFICIAL = {"A": "#1A7A3D", "B": "#7AB829", "C": "#F4A81D", "D": "#C0241B"}
_NL_DESC = {
    "A": "Pilihan paling baik — kandungan gula, garam, dan lemak jenuh paling rendah.",
    "B": "Pilihan baik — kandungan GGL tergolong rendah.",
    "C": "Konsumsi secukupnya — kandungan GGL tergolong sedang.",
    "D": "Batasi konsumsi — kandungan GGL tergolong tinggi.",
}

def nutrilevel_strip_html(active: str = None) -> str:
    """Strip label A-B-C-D resmi (gaya Kepmenkes), level aktif disorot + panah."""
    cells = []
    for g in ["A", "B", "C", "D"]:
        on = (g == active)
        col = _NL_OFFICIAL[g]
        style = (f"background:{col};color:#fff;" if on
                 else f"background:#fff;color:{col};border:2px solid {col};")
        arrow = ('<div class="ns-nlstrip-arrow" '
                 f'style="border-top-color:{col}"></div>' if on else "")
        cells.append(
            f'<div class="ns-nlstrip-cell{" on" if on else ""}">'
            f'<div class="ns-nlstrip-letter" style="{style}">{g}{arrow}</div>'
            f'</div>'
        )
    return f'<div class="ns-nlstrip">{"".join(cells)}</div>'


def _gc(g):  return _GRADE_COLOR.get(g, "#94A3B8")
def _gbg(g): return _GRADE_BG.get(g, "#F1F5F9")

def _pct_color(p):
    if p is None: return "#94A3B8"
    if p <= 25:   return "#16A34A"
    if p <= 50:   return "#F59E0B"
    return "#EF4444"


# ─── Mode banner ─────────────────────────────────────────────────────────────
def mode_banner(mode: str, msg: str):
    if mode == "model":
        _md(f'<div class="ns-banner model"><span class="dot"></span>{msg}</div>')
    else:
        _md(f'<div class="ns-banner demo"><span class="dot"></span>'
            f'Mode demo aktif — {msg}. Nilai yang ditampilkan hanya contoh ilustrasi.</div>')
# ─── Hero (layar Mulai) ──────────────────────────────────────────────────────
def hero(mode: str, mode_msg: str):
    illustration_uri = _asset_uri("animasi_ilustrasi_beranda.png")
    illustration_html = (
        f'<img src="{illustration_uri}" alt="Ilustrasi Beranda" class="ns-hero-illustration"/>'
        if illustration_uri else ""
    )
    _md(f"""
<div class="ns-hero-wrap">
  <div class="ns-hero-text">
    <div class="ns-hero-badge">🍃 Didukung AI untuk Analisis Nutrisi Otomatis</div>
    <h1>Kenali isi<br><span>minumanmu.</span></h1>
    <p>Foto label Informasi Nilai Gizi pada kemasan minuman untuk mendapatkan hasil 
    analisis nutrisi dan skor Nutri-Level secara otomatis.</p>
  </div>
  <div class="ns-hero-illustration-wrap">{illustration_html}</div>
</div>
""")


# ─── Loader (langkah-langkah) ────────────────────────────────────────────────
_STAGES = [
    "Memindai label kemasan",
    "Menghitung Nutri-Level GGL",
    "Mengidentifikasi kandungan gizi",
]

def loader_steps_html(active: int) -> str:
    """HANYA daftar langkah (di-update lewat placeholder)."""
    rows = []
    for i, label in enumerate(_STAGES):
        if i < active:
            cls, status, sc = "done", "SELESAI", "done"
            ic = _IC_CHECK
        elif i == active:
            cls, status, sc = "active", "MEMPROSES", "active"
            ic = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/></svg>'
        else:
            cls, status, sc = "", "MENUNGGU", "wait"
            ic = '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/></svg>'
        rows.append(
            f'<div class="ns-step-row"><div class="ns-step-left {cls}">'
            f'<div class="ns-step-ic">{ic}</div>{label}</div>'
            f'<span class="ns-step-status {sc}">{status}</span></div>'
        )
    return ('<div class="ns-step-list">' + "".join(rows) + '</div>'
            '<div style="text-align:center"><div class="ns-loader-pill">'
            '<div class="ns-spin-sm"></div>Sedang Memproses Label…</div></div>')


def loader_stage_html(img_uri: str) -> str:
    """Bagian atas statis: gambar di lingkaran + cincin hijau + buah melayang."""
    img_html = (f'<img src="{img_uri}"/>' if img_uri else
                '<div style="width:100%;height:100%;display:flex;align-items:center;'
                'justify-content:center;color:#94A3B8;font-size:.8rem">tanpa gambar</div>')
    return f"""
<div class="ns-loader-outer">
<div class="ns-scan-stage">
<span class="ns-fruit f1">🍎</span>
<span class="ns-fruit f2">🫐</span>
<span class="ns-fruit f3">🍊</span>
<span class="ns-fruit f4">🥤</span>
<span class="ns-fruit f5">🧃</span>
<span class="ns-fruit f6">🍋</span>
<div class="ns-scan-wrap">
<div class="ns-scan-ring"></div>
<div class="ns-scan-ring r2"></div>
<div class="ns-scan-chip">{_IC_CPU}</div>
<div class="ns-scan-img">{img_html}<div class="ns-scan-line"></div></div>
</div>
</div>
<div class="ns-loader-title">Sedang menganalisis label minuman…</div>
<div class="ns-loader-sub">Membaca kandungan gula, garam, dan lemak jenuh
untuk menghitung skor kesehatan minuman.</div>
</div>
"""
def result_header_with_actions(mode: str, calc: dict, fields: dict, result: dict, verified_time: str = "baru saja"):
    """Result header dengan tombol Cetak/PDF sejajar meta text."""
    verified = "Dianalisis model Donut" if mode == "model" else "Mode Demo · contoh ilustrasi"

    # Satu baris: header kiri, dua tombol kanan — sejajar dengan meta text.
    col_h, col_b1, col_b2 = st.columns([1, 0.26, 0.36], gap="small")

    with col_h:
        _md(f"""
<div class="ns-result-header">
<div>
<h2>Hasil Analisis</h2>
<div class="ns-meta">{verified} &bull; Dipindai {verified_time}</div>
</div>
</div>
""")

    with col_b1:
        if st.button("🖨  Cetak / PDF", key="print_pdf_btn", use_container_width=True):
            st.session_state._do_print = True

    with col_b2:
        if st.button("ℹ️  Tentang Nutri-Level", key="open_nl_info_result",
                     use_container_width=True, type="secondary"):
            st.session_state.show_nl_dialog = True

    if st.session_state.get("_do_print"):
        st.session_state._do_print = False
        components.html(
            """
            <script>
            setTimeout(function(){ window.parent.print(); }, 150);
            </script>
            """,
            height=0,
        )


# ─── Hasil: kartu grade utama ────────────────────────────────────────────────
def grade_card(calc: dict, fields: dict, mode: str):
    level = calc.get("level_akhir")
    # keyakinan AI ~ kelengkapan field inti
    core = ["takaran", "gula", "lemak_jenuh", "garam"]
    present = sum(1 for k in core if fields.get(k))
    conf = int(72 + 28 * present / len(core))

    penentu = calc.get("penentu")
    _PEN = {"gula": "gula", "garam": "garam (natrium)", "lemak_jenuh": "lemak jenuh"}
    pen_lbl = _PEN.get(penentu, "salah satu komponen")

    if level is None:
        title = "Belum Dapat Dinilai"
        desc = ("Label belum terbaca lengkap. Pastikan foto mencakup seluruh "
                "tabel Informasi Nilai Gizi termasuk takaran saji dalam ml.")
        score_pct, score_lbl, score_col = 0, "TIDAK TERSEDIA", "#94A3B8"
        pills = ["A", "B", "C", "D"]
        active = None
    else:
        title = _QUALITY[level]
        if level in ("A", "B"):
            desc = ("Minuman ini tergolong sehat. Kandungan gula, garam, dan lemak jenuh "
                    "berada dalam batas yang baik untuk dikonsumsi sehari-hari.")
        elif level == "C":
            desc = (f"Minuman ini cukup sehat, namun kandungan {pen_lbl} tergolong sedang. "
                    "Sebaiknya dikonsumsi secukupnya dan tidak berlebihan.")
        else:
            desc = (f"Kandungan {pen_lbl} pada minuman ini cukup tinggi. "
                    "Sebaiknya dibatasi dan diimbangi dengan pola makan sehat.")
        score_map = {"A": (100, "SANGAT BAIK"), "B": (82, "BAIK"),
                     "C": (55, "SEDANG"), "D": (30, "TINGGI")}
        score_pct, score_lbl = score_map[level]
        score_col = _gc(level)
        active = level

    pill_html = ""
    for g in ["A", "B", "C", "D"]:
        on = f"on-{g.lower()}" if g == active else ""
        pill_html += f'<div class="ns-grade-pill-item {on}">{g}</div>'

    _md(f"""
<div class="ns-grade-card">
<div class="ns-grade-left">
<div class="ns-grade-eyebrow">
<span class="ns-grade-pill">Nutri-Level GGL</span>
<span class="ns-grade-conf"><b>{conf}%</b> Keyakinan AI</span>
</div>
<div class="ns-grade-title">{title}</div>
<div class="ns-grade-desc">{desc}</div>
</div>
<div class="ns-grade-right">
<div class="ns-grade-pills">{pill_html}</div>
<div class="ns-grade-score-row">
<span class="ns-grade-score-lbl">Skor Nutri-Level</span>
<span class="ns-grade-score-val" style="color:{score_col}">{score_lbl}</span>
</div>
<div class="ns-grade-score-bar"><div class="ns-grade-score-fill" style="width:{score_pct}%;background:{score_col}"></div></div>
</div>
</div>
""")


# ─── Hasil: GGL per komponen (selektor pil A-D, gaya referensi) ──────────────
def components_section(calc: dict, fields: dict):
    per100  = calc.get("per100", {})
    levels  = calc.get("level", {})
    pct_kem = calc.get("pct_harian_kemasan", {})
    per_kem = calc.get("per_kemasan", {})

    _COMP = [
        ("gula",        "Gula",            "g",  "gula",    "gula_g"),
        ("lemak_jenuh", "Lemak Jenuh",     "g",  "lemak",   None),
        ("garam",       "Garam (Natrium)", "mg", "natrium", "natrium_mg"),
    ]

    cards = []
    for fkey, name, unit, pctkey, kemkey in _COMP:
        lv   = levels.get(fkey)
        p    = per100.get(fkey)
        raw  = fields.get(fkey, "—")
        col  = _gc(lv)

        per100_txt = (f"{p:.1f}".replace(".", ",") + f" {unit} / 100 ml"
                      if p is not None else "per 100 ml tidak tersedia")

        # rincian per sajian & per kemasan
        kem_val = per_kem.get(kemkey) if kemkey else None
        kem_txt = (f"{kem_val:g} {unit}".replace(".", ",")
                   if kem_val is not None else None)
        detail = f'<span>per sajian <b>{raw}</b></span>'
        if kem_txt:
            detail += f'<span>per kemasan <b>{kem_txt}</b></span>'
        rincian = f'<div class="ns-ggl-detail">{detail}</div>'

        # catatan khusus gula (sukrosa/laktosa)
        note = ""
        if fkey == "gula":
            chips = []
            if fields.get("sukrosa"):
                chips.append(f'sukrosa {fields["sukrosa"]}')
            if fields.get("laktosa"):
                chips.append(f'laktosa {fields["laktosa"]} (dikurangi)')
            if chips:
                note = ('<div class="ns-ggl-chips">'
                        + "".join(f'<span>{c}</span>' for c in chips)
                        + '</div>')

        pv = pct_kem.get(pctkey)
        if pv is not None:
            pct_str, pct_col = f"{pv:.0f}%", _pct_color(pv)
        else:
            pct_str, pct_col = "—", "#94A3B8"

        # skala A-D dengan nilai ambang
        a, b, c = NL_BATAS[fkey]
        def fx(x):
            return f"{x:g}".replace(".", ",")
        bounds = {"A": f"≤{fx(a)}", "B": f"≤{fx(b)}", "C": f"≤{fx(c)}", "D": f">{fx(c)}"}
        scale = ""
        for g in ["A", "B", "C", "D"]:
            act = f"active-{g.lower()}" if g == lv else ""
            scale += (f'<div class="ns-ggl-scale-item {act}">{g}'
                      f'<small>{bounds[g]}</small></div>')

        grade_txt = lv if lv else "?"
        # ── Insight per komponen berdasarkan aturan Kepmenkes (item 2) ──
        # Menyebut ambang Kepmenkes yang terpicu + wawasan kesehatan singkat.
        insight = ""
        if lv and p is not None:
            band_txt = {
                "A": f"≤ {fx(a)} {unit}/100 ml",
                "B": f"{fx(a)}–{fx(b)} {unit}/100 ml",
                "C": f"{fx(b)}–{fx(c)} {unit}/100 ml",
                "D": f"> {fx(c)} {unit}/100 ml",
            }[lv]
            _INS = {
                "gula": {
                    "A": "kandungan gula sangat rendah — aman untuk konsumsi rutin.",
                    "B": "gula tergolong rendah — masih relatif aman, tetap perhatikan porsi.",
                    "C": "gula tergolong sedang — batasi agar total gula harian tetap terjaga.",
                    "D": "gula tinggi — konsumsi berlebih berisiko bagi berat badan & gula darah.",
                },
                "lemak_jenuh": {
                    "A": "lemak jenuh sangat rendah — baik bagi kesehatan jantung.",
                    "B": "lemak jenuh rendah — masih dalam batas wajar.",
                    "C": "lemak jenuh sedang — batasi untuk menjaga kolesterol.",
                    "D": "lemak jenuh tinggi — berlebih dapat meningkatkan kolesterol jahat.",
                },
                "garam": {
                    "A": "natrium sangat rendah — ramah untuk tekanan darah.",
                    "B": "natrium rendah — relatif aman untuk konsumsi harian.",
                    "C": "natrium sedang — perhatikan total garam dari sumber lain.",
                    "D": "natrium tinggi — berlebih berisiko menaikkan tekanan darah.",
                },
            }[fkey][lv]
            insight = (
                f'<div class="ns-ggl-insight ins-{lv.lower()}">'
                f'<div class="ns-ggl-insight-rule">Kepmenkes · Level {lv}: {band_txt}</div>'
                f'<div class="ns-ggl-insight-text">{_INS}</div>'
                f'</div>'
            )
        # Pil ringkas sesuai referensi: lingkaran solid berisi huruf grade +
        # kartu putih (persentase tebal di atas, nama field huruf kecil di bawah).
        name_lower = name.lower()
        if lv and pv is not None:
            badge = (f'<div class="ns-ggl-pill">'
                     f'<div class="ns-ggl-pill-circle" style="background:{col}">{lv}</div>'
                     f'<div class="ns-ggl-pill-info">'
                     f'<span class="ns-ggl-pill-pct">{pct_str}</span>'
                     f'<span class="ns-ggl-pill-name">{name_lower}</span>'
                     f'</div>'
                     f'</div>')
        elif lv:
            badge = (f'<div class="ns-ggl-pill">'
                     f'<div class="ns-ggl-pill-circle" style="background:{col}">{lv}</div>'
                     f'<div class="ns-ggl-pill-info">'
                     f'<span class="ns-ggl-pill-pct">{lv}</span>'
                     f'<span class="ns-ggl-pill-name">{name_lower}</span>'
                     f'</div>'
                     f'</div>')
        else:
            badge = (f'<div class="ns-ggl-pill">'
                     f'<div class="ns-ggl-pill-circle" style="background:#94A3B8">?</div>'
                     f'<div class="ns-ggl-pill-info">'
                     f'<span class="ns-ggl-pill-pct">—</span>'
                     f'<span class="ns-ggl-pill-name">{name_lower}</span>'
                     f'</div>'
                     f'</div>')

        cards.append(f"""
<div class="ns-ggl-card">
<div class="ns-ggl-head">
<span class="ns-ggl-title">{name}</span>
{badge}
</div>
<div class="ns-ggl-body">
<div class="ns-ggl-val" style="color:{col}">{per100_txt}</div>
{rincian}
{note}
<div class="ns-ggl-scale">{scale}</div>
{insight}
</div>
</div>""")

    _md('<div class="ns-ggl-grid">' + "".join(cards) + '</div>')


# ─── Hasil: label kemasan + alert + rincian ─────────────────────────────────
def _alert_html(calc, fields):
    levels  = calc.get("level", {})
    per100  = calc.get("per100", {})
    pct_kem = calc.get("pct_harian_kemasan", {})
    _LABEL = {"gula": "gula", "garam": "garam (natrium)", "lemak_jenuh": "lemak jenuh"}
    _PCT   = {"gula": "gula", "garam": "natrium", "lemak_jenuh": "lemak"}
    _UNIT  = {"gula": "g", "garam": "mg", "lemak_jenuh": "g"}

    alerts = []
    for key in ["gula", "garam", "lemak_jenuh"]:
        if levels.get(key) in ("C", "D"):
            raw  = fields.get(key, "?")
            pct  = pct_kem.get(_PCT[key])
            p100 = per100.get(key)
            p100s = f"{p100:.1f} {_UNIT[key]}/100 ml" if p100 is not None else ""
            if pct is not None:
                alerts.append(
                    f"Minuman ini mengandung <strong>{raw}</strong> {_LABEL[key]} per sajian "
                    f"(≈ {p100s}). Setara <strong>{pct:.0f}%</strong> dari batas konsumsi harian.")
            else:
                tinggi = "tinggi" if levels.get(key) == "D" else "sedang"
                alerts.append(
                    f"Minuman ini mengandung <strong>{raw}</strong> {_LABEL[key]} per sajian "
                    f"({p100s}). Kandungan ini tergolong <strong>{tinggi}</strong>.")
    if not alerts:
        return ""
    items = "".join(f"<div>• {a}</div>" for a in alerts)
    return (f'<div class="ns-alert"><div class="ns-alert-head">{_IC_WARN} Perhatian!</div>'
            f'<div class="ns-alert-body">{items}</div></div>')
def label_and_breakdown(calc, fields, cropped_img=None, panel_img=None):
    per100 = calc.get("per100", {})
    levels = calc.get("level", {})
    pct    = calc.get("pct_harian_kemasan", {})

    # Alert box (untuk left block)
    alert_msg = _alert_html(calc, fields)

    # KIRI — Alert + kartu label kemasan analyzed
    img_uri = _img_uri(panel_img if panel_img is not None else cropped_img)
    
    # Tampilkan badges untuk semua nutrient yang terdeteksi
    tags = []
    if fields.get("energi"):           tags.append("ENERGI TERDETEKSI")
    if fields.get("lemak"):            tags.append("LEMAK TOTAL TERDETEKSI")
    if fields.get("lemak_jenuh"):      tags.append("LEMAK JENUH TERDETEKSI")
    if fields.get("gula"):             tags.append("GULA TERDETEKSI")
    if fields.get("garam"):            tags.append("GARAM TERDETEKSI")
    
    tags_html = "".join(f'<span class="ns-detect-badge-new">{t}</span>' for t in tags)
    
    img_block = (f'<div class="ns-analyzed-label-content">'
                 f'<img src="{img_uri}" class="ns-analyzed-label-img"/>'
                 f'<div class="ns-detect-badges-area">{tags_html}</div>'
                 f'</div>' if img_uri else
                 '<div style="flex:1;background:#F1F5F9;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:.82rem;border-radius:12px;margin:12px;min-height:300px">Gambar tidak tersedia</div>')

    # Ikon mata untuk tombol lihat gambar penuh
    _IC_EYE = (
        '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
        '<circle cx="12" cy="12" r="3"/></svg>'
    )

    # Modal popup full image — CSS-only (checkbox hack, tanpa JS)
    full_img_uri = _img_uri_full(panel_img if panel_img is not None else cropped_img)
    modal_html = ""
    view_btn_html = ""
    if full_img_uri:
        view_btn_html = (
            f'<label for="ns-fullimg-toggle" class="ns-view-full-btn" '
            f'title="Lihat gambar penuh">{_IC_EYE} Lihat Penuh</label>'
        )
        modal_html = f"""
<input type="checkbox" id="ns-fullimg-toggle" class="ns-fullimg-checkbox"/>
<div class="ns-fullimg-modal">
<label for="ns-fullimg-toggle" class="ns-fullimg-overlay"></label>
<div class="ns-fullimg-inner">
<label for="ns-fullimg-toggle" class="ns-fullimg-close">&times;</label>
<img src="{full_img_uri}" alt="Label penuh"/>
</div>
</div>
"""

    left_card = f"""
<div class="ns-analyzed-label-card">
<div class="ns-analyzed-label-head">
<span class="ns-analyzed-label-title">ANALYZED LABEL</span>
{view_btn_html}
</div>
{img_block}
</div>
"""

    left_block = f'''<div class="ns-results-left">
{alert_msg}
{left_card}
</div>
{modal_html}'''

    # KANAN — Kandungan Gizi Lengkap
    nutrition_section = nutrition_complete_with_scores(calc, fields)
    
    breakdown_section = f'''
<div class="ns-detailed-breakdown">
{nutrition_section}
</div>
'''
    
    right_block = f'''<div class="ns-results-right">
{breakdown_section}
</div>'''

    _md(f'<div class="ns-results-container">{left_block}{right_block}</div>')


# ─── Hasil: grafik asupan vs batas harian ────────────────────────────────────
def intake_chart_section(calc: dict, fields: dict):
    pct = calc.get("pct_harian_kemasan", {})
    bars = [("Gula", pct.get("gula"), "#F59E0B"),
            ("Natrium", pct.get("natrium"), "#EF4444"),
            ("Lemak", pct.get("lemak"), "#3B82F6")]
    bars = [(n, v, c) for n, v, c in bars if v is not None]
    if not bars:
        return

    MAXH = 200
    cols = ""
    for name, val, color in bars:
        capped = min(val, 120)
        h = max(4, int(capped / 120 * MAXH))
        cols += (f'<div class="ns-bar-col"><div class="ns-bar-pct">{val:.0f}%</div>'
                 f'<div class="ns-bar-outer" style="height:{MAXH}px">'
                 f'<div class="ns-bar-fill" style="height:{h}px;background:{color}"></div></div>'
                 f'<div class="ns-bar-label">{name}</div></div>')
    guide = int(100 / 120 * MAXH)
    plot_h = MAXH + 20
    _md(f"""
<div class="ns-chart-card">
<div class="ns-chart-head">
<div class="ns-chart-title">Asupan vs Batas Harian</div>
<div class="ns-chart-legend">
<div class="ns-legend-item"><span class="ns-legend-dot" style="background:#16A34A"></span>Optimal</div>
<div class="ns-legend-item"><span class="ns-legend-dot" style="background:#F59E0B"></span>Sedang</div>
<div class="ns-legend-item"><span class="ns-legend-dot" style="background:#EF4444"></span>Berlebih</div>
</div>
</div>
<div class="ns-chart-sub">% terhadap batas konsumsi harian (Permenkes 30/2013) · per kemasan utuh</div>
<div class="ns-chart-plot">
<div class="ns-yaxis-title">% Batas Harian</div>
<div class="ns-yaxis-ticks" style="height:{plot_h}px">
<span style="bottom:{guide}px">100%</span>
<span style="bottom:14px">0%</span>
</div>
<div class="ns-bars-area" style="height:{plot_h}px">
<div class="ns-guide-100" style="bottom:{guide}px;top:auto;position:absolute"></div>
{cols}
</div>
</div>
</div>
""")


# ─── Helper: kandungan gizi lengkap (DETAILED BREAKDOWN) ─────────────────────
def nutrition_complete_with_scores(calc: dict, fields: dict) -> str:
    """Return HTML untuk SEMUA data hasil baca label: penyajian + kandungan gizi (raw data) + perhitungan nutri-level."""
    levels = calc.get("level", {})
    per100 = calc.get("per100", {})
    pct    = calc.get("pct_harian_kemasan", {})
    
    # ─── Helper untuk menampilkan nilai (0 ditampilkan sebagai "0" bukan "-") ───
    def format_value(val, suffix=""):
        if val is None:
            return "—"
        return f"{val}{suffix}"
    
    # ─── BAGIAN 1: Informasi Penyajian Per Kemasan ───
    takaran = format_value(fields.get("takaran"))
    sajian = format_value(fields.get("sajian"))
    jumlah_per_kemasan = format_value(fields.get("jumlah_per_kemasan"))
    
    penyajian_html = f'''
<div style="padding:10px 0;border-bottom:1px solid #E0F2FE">
<div style="font-size:.75rem;font-weight:700;color:#0369A1;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Informasi Penyajian Per Kemasan</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
<div style="background:#fff;padding:10px;border-radius:8px;border:1px solid #E0F2FE;text-align:center">
<div style="font-size:.7rem;color:#0369A1;font-weight:600">Takaran Saji</div>
<div style="font-size:.9rem;color:#0F172A;font-weight:700;margin-top:6px">{takaran}</div>
</div>
<div style="background:#fff;padding:10px;border-radius:8px;border:1px solid #E0F2FE;text-align:center">
<div style="font-size:.7rem;color:#0369A1;font-weight:600">Sajian/Kemasan</div>
<div style="font-size:.9rem;color:#0F172A;font-weight:700;margin-top:6px">{sajian}</div>
</div>
<div style="background:#fff;padding:10px;border-radius:8px;border:1px solid #E0F2FE;text-align:center">
<div style="font-size:.7rem;color:#0369A1;font-weight:600">Jumlah/Kemasan</div>
<div style="font-size:.9rem;color:#0F172A;font-weight:700;margin-top:6px">{jumlah_per_kemasan}</div>
</div>
</div>
</div>
'''
    
    # ─── BAGIAN 2: Kandungan Gizi (Per 100 ml) - DATA ASLI DETEKSI LABEL ───
    # Mapping langsung dari fields ke label tampilan dengan unit
    nutrients_raw = [
        ("Lemak Total", "lemak", "g"),
        ("Lemak Jenuh", "lemak_jenuh", "g"),
        ("Gula Total", "gula", "g"),
        ("Sukrosa", "sukrosa", "g"),
        ("Laktosa", "laktosa", "g"),
        ("Garam (Natrium)", "garam", "mg"),
    ]
    
    nutrient_items = []
    for label, key, unit in nutrients_raw:
        raw_val = fields.get(key)  # Ambil langsung dari fields (data asli deteksi)
        # Extract hanya angka dari value (misal "0 g" -> "0", "45 mg" -> "45")
        if raw_val is not None:
            # Ambil bagian numerik saja
            numeric_str = str(raw_val).split()[0] if raw_val else None
            try:
                val_num = float(numeric_str)
                # Tampilkan nilai APA ADANYA hasil deteksi (JANGAN dibulatkan):
                #   3.5 -> "3,5"   |   16.0 -> "16"   |   45 -> "45"
                num_txt = f"{val_num:g}".replace(".", ",")
                display = f"{num_txt} {unit}"
            except (ValueError, IndexError, AttributeError):
                display = "—"
        else:
            display = "—"
        nutrient_items.append(f'''
<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #E0F2FE">
<span style="font-size:.85rem;color:#0F172A;font-weight:500">{label}</span>
<span style="font-size:.85rem;color:#0369A1;font-weight:700">{display}</span>
</div>
''')
    
    gizi_html = f'''
<div style="padding:10px 0;border-bottom:1px solid #E0F2FE">
<div style="font-size:.75rem;font-weight:700;color:#0369A1;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Kandungan Gizi</div>
{"".join(nutrient_items)}
</div>
'''
    
    # ─── BAGIAN 3: Hasil Perhitungan Nutri-Level ───
    _BD = [
        ("Total Gula",       "gula",         "gula",        pct.get("gula"),    "#F59E0B"),
        ("Total Lemak",      "lemak",        "lemak_jenuh", pct.get("lemak"),   "#3B82F6"),
        ("Garam (Natrium)",  "garam",        "garam",       pct.get("natrium"), "#EF4444"),
    ]
    
    score_items = []
    for name, fkey, lvkey, pv, color in _BD:
        per100_val = per100.get(fkey)
        if fkey == "garam":
            display_val = f"{per100_val:.1f}mg" if per100_val is not None else "—"
        else:
            display_val = f"{per100_val:.1f}g" if per100_val is not None else "—"
        lv = levels.get(lvkey)
        lv_lbl = _GRADE_LABEL.get(lv, "")
        pct_str = f"{pv:.0f}%" if pv is not None else "—"
        fill = min(pv, 100) if pv is not None else 0
        
        score_items.append(f'''
<div style="padding:10px 0;border-bottom:1px solid #E0F2FE">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
<span style="font-size:.85rem;color:#0F172A;font-weight:600">{name}</span>
<span style="font-size:.85rem;color:#0369A1;font-weight:700">{display_val}</span>
</div>
<div style="font-size:.75rem;color:#6B7280;margin-bottom:6px">{lv_lbl}</div>
<div style="background:#E0F2FE;height:6px;border-radius:3px;overflow:hidden">
<div style="width:{fill:.0f}%;height:100%;background:{color};transition:width .3s ease"></div>
</div>
<div style="font-size:.7rem;color:#6B7280;text-align:right;margin-top:4px">{pct_str} NILAI HARIAN</div>
</div>
''')
    
    perhitungan_html = f'''
<div style="padding:10px 0">
<div style="font-size:.75rem;font-weight:700;color:#0369A1;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Hasil Perhitungan Nutri-Level (Per 100 ml)</div>
{"".join(score_items)}
</div>
'''
    
    return f'''
<div style="background:#F0F9FF;border-radius:12px;padding:14px">
{penyajian_html}
{gizi_html}
{perhitungan_html}
</div>
'''


# ─── Dialog info: penjelasan Nutri-Level + desain label resmi Kemenkes ──────
def _nutrilevel_dialog_body(active: str = None):
    """Isi dialog penjelasan Nutri-Level (dipakai di dalam @st.dialog)."""
    rows = ""
    for g in ["A", "B", "C", "D"]:
        col = _NL_OFFICIAL[g]
        rows += (
            f'<div class="ns-nlinfo-row">'
            f'<div class="ns-nlinfo-badge" style="background:{col}">{g}</div>'
            f'<div class="ns-nlinfo-text"><b>Level {g}</b> — {_NL_DESC[g]}</div>'
            f'</div>'
        )
    _md(f"""
<div class="ns-nlinfo">
<p class="ns-nlinfo-lead">
<b>Nutri-Level</b> adalah label peringkat gizi (A–D) untuk minuman/pangan olahan
sesuai <b>Kepmenkes No. HK.01.07/MENKES/301/2026</b>. Level dihitung dari kandungan
<b>Gula, Garam (natrium), dan Lemak Jenuh (GGL)</b> per 100 ml; level akhir mengikuti
komponen yang <b>paling tinggi (terburuk)</b>.
</p>
{nutrilevel_strip_html(active)}
<div class="ns-nlinfo-rows">{rows}</div>
<div class="ns-nlinfo-note">
Warna mengikuti ketentuan resmi: A hijau tua, B hijau muda, C kuning, D merah.
Level A juga mensyaratkan <b>tanpa pemanis</b> dan level B <b>hanya pemanis alami</b> —
syarat ini diperiksa dari daftar komposisi, bukan dari tabel nilai gizi.
</div>
</div>
""")


def render_nutrilevel_dialog(active: str = None):
    """Buka dialog penjelasan Nutri-Level. Aman bila st.dialog tak tersedia."""
    dlg = getattr(st, "dialog", None)
    if dlg is None:
        # fallback: tampilkan sebagai expander
        with st.expander("Tentang Nutri-Level", expanded=True):
            _nutrilevel_dialog_body(active)
        return

    @st.dialog("Tentang Nutri-Level")
    def _d():
        _nutrilevel_dialog_body(active)
        # Tombol "Mengerti" dihapus — sudah ada tombol X bawaan dialog (item 1).
        # Reset state agar dialog tidak terus terbuka pada rerun berikutnya.
        st.session_state.show_nl_dialog = False

    _d()


# ─── Hasil: saran konsumsi ───────────────────────────────────────────────────
def consumption_tips_section(calc: dict):
    levels = calc.get("level", {})
    vol_ml = calc.get("vol_ml", "—")

    tip_time  = "Waktu terbaik menikmati minuman ini adalah siang hari, saat metabolisme sedang aktif."
    tip_limit = (f"Cukup 1 sajian ({vol_ml} ml) per hari agar asupan gula, garam, "
                 "dan lemak jenuh tetap terjaga.")
    tip_alt   = ("Untuk konsumsi rutin, pilih minuman dengan gula di bawah 5 g dan "
                 "natrium di bawah 120 mg per 100 ml.")

    if levels.get("gula") in ("C", "D"):
        tip_time  = ("Hindari minum ini menjelang tidur — kandungan gula tinggi bisa "
                     "mengganggu metabolisme malam hari.")
        tip_limit = ("Perbanyak air putih dan batasi minuman ini agar total asupan "
                     "gula harian tetap aman.")
    if levels.get("garam") in ("C", "D"):
        tip_alt   = ("Jika sudah minum ini, kurangi makanan dan minuman tinggi garam "
                     "lainnya di hari yang sama.")
    if levels.get("lemak_jenuh") in ("C", "D"):
        tip_alt   = ("Untuk sehari-hari, pilih minuman dengan lemak jenuh di bawah "
                     "0,7 g per 100 ml sebagai alternatif.")

    _md(f"""
<div class="ns-tips-card">
<div class="ns-tips-deco"></div>
<div class="ns-tips-head">
<h3>Saran Konsumsi</h3>
<div class="ns-tips-sub">Rekomendasi agar konsumsi minuman ini tetap sehat.</div>
</div>
<div class="ns-tips-items">
<div class="ns-tip-col"><div class="ns-tip-col-icon">{_IC_CLOCK}</div>
<div class="ns-tip-col-title">Waktu Terbaik</div><div class="ns-tip-col-body">{tip_time}</div></div>
<div class="ns-tip-col"><div class="ns-tip-col-icon">{_IC_SCALE}</div>
<div class="ns-tip-col-title">Batas Konsumsi</div><div class="ns-tip-col-body">{tip_limit}</div></div>
<div class="ns-tip-col"><div class="ns-tip-col-icon">{_IC_LEAF}</div>
<div class="ns-tip-col-title">Alternatif Lebih Sehat</div><div class="ns-tip-col-body">{tip_alt}</div></div>
</div>
</div>
""")
