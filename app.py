"""
app.py — NutriScan AI (Minuman Kemasan)
=========================================
Aplikasi Streamlit untuk membaca label "Informasi Nilai Gizi" minuman kemasan
dan menghitung Nutri-Level GGL (Kepmenkes HK.01.07/MENKES/301/2026).

State: mulai → pangkas → memproses → hasil
Jalankan: streamlit run app.py
"""

import time
import io

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

from config import APP_NAME, APP_TAGLINE
from ui.styles import inject_global_css
from ui.sidebar import render_sidebar
from ui import components as C
from core.inference import run_pipeline, get_status
from core import inference
from core.nutrilevel import nutri_level, nutri_level_sensitivitas


# ─── Halaman & tema ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="asset/logo.png",
    layout="wide",
)
inject_global_css()


def _ensure_sidebar_toggle():
    """Tampilkan tombol buka/tutup sidebar di kiri-ATAS layar yang BENAR-BENAR
    bisa diklik.

    Pelajaran penting: MEMINDAHKAN tombol native ke <body> merusak event React
    (klik jadi mati). Maka pendekatannya kini:
      • Tombol native dibiarkan DI TEMPAT (tetap di pohon React) tapi disembunyikan
        secara visual (tetap ada & bisa di-`click()` lewat program).
      • Kita buat tombol kita sendiri (floating, kiri-atas) sebagai kontrol yang
        terlihat; saat diklik, ia memanggil `.click()` pada tombol native yang
        masih di pohon React → React men-toggle sidebar seperti biasa.
    Dipantau via MutationObserver karena Streamlit kerap membuat ulang elemennya.
    """
    components.html(
        """
        <script>
        const doc = window.parent.document;
        const TIDS = [
          'stSidebarCollapsedControl',
          'collapsedControl',
          'stSidebarCollapseButton',
          'stExpandSidebarButton'
        ];
        // Cari semua kemungkinan tombol toggle native (TANPA memindahkannya).
        function nativeButtons() {
          const out = [];
          TIDS.forEach(t => {
            doc.querySelectorAll('[data-testid="' + t + '"]').forEach(e => out.push(e));
          });
          // Saat sidebar terbuka, tombol collapse biasanya di header sidebar.
          const sbHeader = doc.querySelector('[data-testid="stSidebarHeader"]');
          if (sbHeader) sbHeader.querySelectorAll('button').forEach(b => out.push(b));
          // Cadangan lebar: elemen dengan aria-label terkait sidebar.
          doc.querySelectorAll('[aria-label*="sidebar" i]').forEach(e => out.push(e));
          return out;
        }
        // Klik tombol native yang relevan (yang sedang terlihat di layar).
        function clickNative() {
          const btns = nativeButtons().filter(b => b.id !== 'ns-custom-sidebar-toggle');
          // Utamakan yang benar-benar tampil (offsetParent != null), lalu fallback
          // ke mana pun yang ada.
          let target = btns.find(b => b.offsetParent !== null) || btns[0];
          if (!target) return;
          const real = (target.tagName === 'BUTTON') ? target : (target.querySelector('button') || target);
          real.click();
        }
        // Sembunyikan tombol native secara visual TAPI tetap di pohon React.
        function hideNative() {
          nativeButtons().forEach(el => {
            if (el.id === 'ns-custom-sidebar-toggle') return;
            el.style.setProperty('opacity', '0', 'important');
            el.style.setProperty('width', '1px', 'important');
            el.style.setProperty('height', '1px', 'important');
            el.style.setProperty('min-width', '0', 'important');
            el.style.setProperty('min-height', '0', 'important');
            el.style.setProperty('overflow', 'hidden', 'important');
            el.style.setProperty('position', 'fixed', 'important');
            el.style.setProperty('left', '0', 'important');
            el.style.setProperty('top', '0', 'important');
            el.style.setProperty('pointer-events', 'none', 'important');
            el.style.setProperty('z-index', '-1', 'important');
          });
        }
        // Buat / pastikan tombol floating kita ada di kiri-atas.
        function ensureCustom() {
          let fb = doc.getElementById('ns-custom-sidebar-toggle');
          if (!fb) {
            fb = doc.createElement('button');
            fb.id = 'ns-custom-sidebar-toggle';
            fb.type = 'button';
            fb.setAttribute('aria-label', 'Buka atau tutup panel samping');
            fb.innerHTML = '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
            // Tombol DI BAWAH layar (fixed) — selalu terlihat penuh, tidak
            // tertutup. left/bottom diberi jarak cukup dari tepi.
            fb.style.cssText = 'position:fixed;left:16px;bottom:22px;top:auto;width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:#16A34A;border:none;border-radius:14px;box-shadow:0 8px 22px rgba(22,163,74,.45);cursor:pointer;z-index:2147483647;transition:transform .15s ease,box-shadow .2s ease;padding:0;';
            fb.addEventListener('mouseenter', () => {
              fb.style.transform = 'translateY(-2px)';
              fb.style.boxShadow = '0 12px 28px rgba(22,163,74,.55)';
            });
            fb.addEventListener('mouseleave', () => {
              fb.style.transform = 'none';
              fb.style.boxShadow = '0 8px 22px rgba(22,163,74,.45)';
            });
            fb.addEventListener('click', (ev) => {
              ev.preventDefault();
              ev.stopPropagation();
              clickNative();
            });
            doc.body.appendChild(fb);
          }
          fb.style.setProperty('display', 'flex', 'important');
        }
        function tick() {
          ensureCustom();
          hideNative();
        }
        tick();
        const obs = new MutationObserver(tick);
        obs.observe(doc.body, {childList: true, subtree: true});
        setInterval(tick, 500);
        </script>
        """,
        height=0,
    )


# ─── Manajemen state ─────────────────────────────────────────────────────────
def _init():
    ss = st.session_state
    ss.setdefault("step",     "mulai")
    ss.setdefault("original", None)
    ss.setdefault("cropped",  None)
    ss.setdefault("result",   None)
    ss.setdefault("calc",     None)
    ss.setdefault("sens",     None)
    ss.setdefault("show_nl_dialog", False)
    ss.setdefault("_do_print", False)
    ss.setdefault("_scroll_to_analisis", False)


def _reset():
    for k in ("original", "cropped", "result", "calc", "sens"):
        st.session_state[k] = None
    st.session_state.step = "mulai"


def _goto(step):
    st.session_state.step = step
    st.rerun()


# Sisi terpanjang maksimum untuk gambar yang diproses. Kamera HP modern bisa
# 48–200 MP; bila di-decode penuh ke RGB (PIL membuat 2–3 salinan) lalu
# dijalankan EasyOCR, memori server bisa habis -> proses di-OOM-kill ->
# halaman "Oh no. Error running app". 2000 px lebih dari cukup untuk OCR/Donut.
MAX_IMAGE_SIDE = 2000


def _to_pil(uploaded):
    """Konversi unggahan -> PIL RGB tegak, AMAN-memori untuk foto kamera HP.

    Mengembalikan None bila gambar tidak bisa dibaca (caller sudah menjaga
    dengan `if img is not None`).

    Kenapa perlu hati-hati: foto dari kamera NATIVE ponsel diambil pada
    resolusi sensor penuh (puluhan MP). Bila di-decode utuh ke array RGB, satu
    foto 48 MP = ~144 MB per salinan, dan `Image.open + exif_transpose +
    convert` membuat beberapa salinan — lalu EasyOCR dijalankan dua kali di
    atasnya. Di server (Streamlit Cloud, memori efektif terbatas setelah model
    Donut + EasyOCR dimuat) lonjakan ini melewati batas dan prosesnya
    dimatikan, memunculkan halaman "Oh no". Kamera WEB (gambar kecil ~VGA/720p)
    dan unggah file (umumnya sudah kecil) tidak memicunya — makanya hanya
    kamera native yang error.

    Kuncinya `Image.draft()`: untuk JPEG (format kamera HP) ini menyuruh
    libjpeg men-decode LANGSUNG pada skala kecil saat dekompresi, jadi array
    resolusi penuh tidak pernah dibuat. Untuk PNG/WebP draft() tidak berefek,
    sehingga `thumbnail()` di akhir bertindak sebagai jaring pengaman.
    """
    try:
        img = Image.open(io.BytesIO(uploaded.getvalue()))

        # Minta decoder JPEG bekerja pada skala kecil sejak awal (hemat memori
        # besar). No-op untuk format non-JPEG; karena itu ada thumbnail di bawah.
        try:
            img.draft("RGB", (MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
        except Exception:
            pass

        # Koreksi orientasi EXIF (foto HP sering menyimpan rotasi di metadata,
        # bukan pada piksel). Dibungkus try agar EXIF rusak tidak meng-crash.
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        img = img.convert("RGB")

        # Jaring pengaman: pastikan sisi terpanjang <= MAX_IMAGE_SIDE
        # (untuk PNG/WebP, atau bila draft hanya memperkecil sebagian).
        if max(img.size) > MAX_IMAGE_SIDE:
            img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))

        return img

    except Exception as e:
        st.error(
            "Foto tidak dapat dibaca. Coba ambil ulang fotonya, atau gunakan "
            f"format JPG/PNG. (Detail teknis: {e})"
        )
        return None


# ─── Layar 1 — Mulai (pilih foto) ────────────────────────────────────────────
def screen_capture():
    mode, msg = get_status()
    render_sidebar("mulai", mode, msg)

    # Hero (status model TIDAK lagi diulang di sini — sudah sticky di sidebar)
    C.hero(mode, msg)

    # ── Tombol hero ASLI (Streamlit), ditarik MASUK ke dalam kartu hero ──
    # (Streamlit tak bisa menaruh tombol di dalam blok HTML; jadi kartu hero
    #  diberi ruang bawah lalu baris tombol ini ditarik ke atas via CSS.)
    #  Rasio kolom + CSS menjaga kedua tombol tetap bersisian di semua lebar.
    #  Spacer kanan dibuat kecil agar tombol mendapat lebih banyak ruang
    #  (penting di layar HP supaya teks tombol tidak terpotong).
    hb1, hb2, hb_sp = st.columns([1.3, 1.3, 0.4], gap="small")
    with hb1:
        if st.button("⚡  Pindai Sekarang", key="hero_mulai", use_container_width=True):
            st.session_state.src_mode = "📷  Ambil Foto"
            st.session_state._scroll_to_analisis = True
            st.rerun()
    with hb2:
        if st.button("Pelajari Lebih Lanjut", key="hero_pelajari",
                     use_container_width=True, type="secondary"):
            st.session_state.show_nl_dialog = True
            st.rerun()

    # ── Pemilih sumber: Unggah / Ambil Foto (radio bergaya tab agar bisa
    #    dikontrol dari Python — "Mulai Pindai" mengaktifkan tab Ambil Foto) ──
    st.markdown('<div id="mulai-analisis-anchor"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ns-section-title" style="margin-bottom:14px">Mulai Pindai</div>',
        unsafe_allow_html=True,
    )

    _SRC_UP = "📤  Unggah Foto"
    _SRC_CAM = "📷  Ambil Foto"
    st.session_state.setdefault("src_mode", _SRC_UP)

    sumber = st.radio(
        "Sumber gambar",
        [_SRC_UP, _SRC_CAM],
        key="src_mode",
        horizontal=True,
        label_visibility="collapsed",
    )

    img = None
    if sumber == _SRC_UP:
        up = st.file_uploader(
            "Pilih file gambar",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            label_visibility="collapsed",
            key="file_up",
        )
        if up is not None:
            with st.spinner("Memproses gambar, mohon tunggu…"):
                img = _to_pil(up)
    else:
        # ── Ambil Foto — RESPONSIF berdasarkan ukuran layar ──
        # Layar LEBAR (desktop): tampilkan st.camera_input (kamera tertanam
        #   langsung di halaman, seperti versi sebelumnya).
        # Layar HP: tampilkan tombol "Buka Kamera" yang memicu kamera NATIVE
        #   perangkat (fullscreen) via st.file_uploader + capture="environment".
        #
        # Kedua mekanisme DIRENDER, lalu CSS media-query menampilkan yang sesuai
        # (lihat .ns-cam-desktop / .ns-cam-mobile di styles.py). Pemilihan murni
        # CSS sehingga responsif instan saat layar diubah ukurannya, tanpa
        # round-trip ke server.
        st.markdown(
            '<div class="ns-cam-hint">'
            '<div class="ns-cam-hint-title">📷 Ambil foto dengan kamera</div>'
            '<div class="ns-cam-hint-sub">Di komputer, kamera tampil langsung '
            'di bawah. Di ponsel, tekan tombol untuk membuka kamera perangkat. '
            'Arahkan ke tabel <b>Informasi Nilai Gizi</b>, lalu lanjut '
            'memangkas.</div></div>',
            unsafe_allow_html=True,
        )

        img_cam = None

        # (A) DESKTOP — kamera tertanam (st.camera_input). Dibungkus penanda agar
        #     CSS menyembunyikannya di layar kecil.
        st.markdown('<div class="ns-cam-desktop" id="ns-cam-desktop"></div>',
                    unsafe_allow_html=True)
        shot = st.camera_input(
            "Ambil foto label gizi (desktop)",
            label_visibility="collapsed",
            key="cam_shot_desktop",
        )
        if shot is not None:
            with st.spinner("Memproses gambar, mohon tunggu…"):
                img_cam = _to_pil(shot)

        # (B) MOBILE — tombol "Buka Kamera" yang memicu kamera native. Dropzone
        #     file_uploader disembunyikan; tombol disuntik via JS.
        st.markdown('<div id="ns-cam-marker"></div>', unsafe_allow_html=True)
        cam = st.file_uploader(
            "Ambil foto label gizi (mobile)",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            label_visibility="collapsed",
            key="cam_capture",
        )
        st.markdown('<div id="ns-cam-marker-end"></div>', unsafe_allow_html=True)
        if cam is not None:
            with st.spinner("Memproses gambar, mohon tunggu…"):
                img_cam = _to_pil(cam)

        img = img_cam

        # JS: pasang capture="environment", sembunyikan dropzone mobile, sisipkan
        # tombol "Buka Kamera", DAN tandai blok desktop/mobile agar CSS bisa
        # menampilkan yang sesuai ukuran layar.
        components.html(
            """
            <script>
            const doc = window.parent.document;

            function camInput() {
              const marker = doc.getElementById('ns-cam-marker');
              if (!marker) return null;
              // Cari input file SETELAH penanda mobile (widget file_uploader B).
              let probe = marker.closest('[data-testid="stMarkdownContainer"]');
              probe = probe ? probe.parentElement : marker.parentElement;
              for (let i = 0; i < 8 && probe; i++) {
                const found = probe.querySelector &&
                              probe.querySelector('input[type="file"]');
                if (found) return found;
                probe = probe.nextElementSibling || probe.parentElement;
              }
              const all = doc.querySelectorAll('input[type="file"]');
              return all.length ? all[all.length - 1] : null;
            }

            function setup() {
              const input = camInput();
              if (!input) return;

              // 1) Atribut kamera belakang.
              if (input.getAttribute('capture') !== 'environment') {
                input.setAttribute('accept', 'image/*');
                input.setAttribute('capture', 'environment');
              }

              // 2) Bungkus dropzone mobile dengan kelas .ns-cam-mobile agar CSS
              //    bisa menampilkannya HANYA di layar kecil.
              const dropzone = input.closest('section');
              const wrap = dropzone ? dropzone.parentElement : null;
              if (wrap && !wrap.classList.contains('ns-cam-mobile')) {
                wrap.classList.add('ns-cam-mobile');
              }

              // 3) Sisipkan tombol "Buka Kamera" (sekali) menggantikan dropzone.
              const host = wrap || input.parentElement;
              if (dropzone) dropzone.style.display = 'none';
              if (host && !host.querySelector('.ns-cam-open-btn')) {
                const btn = doc.createElement('button');
                btn.type = 'button';
                btn.className = 'ns-cam-open-btn';
                btn.innerHTML =
                  '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" ' +
                  'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" ' +
                  'stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 ' +
                  '2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z"/>' +
                  '<circle cx="12" cy="13" r="3"/></svg><span>Buka Kamera</span>';
                btn.addEventListener('click', () => input.click());
                host.appendChild(btn);
              }

              // 4) Tandai blok desktop (st.camera_input) dengan kelas pada
              //    pembungkus terdekatnya agar CSS bisa menyembunyikannya di HP.
              const dMark = doc.getElementById('ns-cam-desktop');
              if (dMark) {
                // Cari widget camera_input (punya tombol "Take Photo"/video).
                let p = dMark.closest('[data-testid="stMarkdownContainer"]');
                p = p ? p.parentElement : null;
                for (let i = 0; i < 8 && p; i++) {
                  const cam = p.querySelector &&
                    p.querySelector('[data-testid="stCameraInput"]');
                  if (cam) {
                    const cw = cam.closest('[data-testid="stElementContainer"]') || cam;
                    if (cw && !cw.classList.contains('ns-cam-desktop-w')) {
                      cw.classList.add('ns-cam-desktop-w');
                    }
                    break;
                  }
                  p = p.nextElementSibling || p.parentElement;
                }
              }
            }

            setup();
            const obs = new MutationObserver(() => setup());
            obs.observe(doc.body, {childList: true, subtree: true});
            setTimeout(() => obs.disconnect(), 8000);
            </script>
            """,
            height=0,
        )

    # Auto-scroll ke bagian analisis bila dipicu tombol "Mulai Pindai"
    if st.session_state.get("_scroll_to_analisis"):
        st.session_state._scroll_to_analisis = False
        components.html(
            """
            <script>
            const doc = window.parent.document;
            const el = doc.getElementById('mulai-analisis-anchor');
            if (el) { el.scrollIntoView({behavior:'smooth', block:'center'}); }
            </script>
            """,
            height=0,
        )

    # ── Pratinjau foto & tombol lanjut ──
    if img is not None:
        st.markdown('<hr class="ns-divider"/>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            # Badge + gambar dalam satu section sejajar vertikal (item 4)
            try:
                img_uri = C._img_uri(img, max_px=1200)
            except Exception:
                img_uri = None
            if img_uri:
                st.markdown(
                    '<div class="ns-uppreview">'
                    '<div class="ns-preview-tag">📸 Foto yang dipilih</div>'
                    '<div class="ns-uppreview-imgbox">'
                    f'<img src="{img_uri}" class="ns-uppreview-img"/>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="ns-preview-tag">📸 Foto yang dipilih</div>',
                    unsafe_allow_html=True,
                )
                st.image(img, use_container_width=True)
        with c2:
            st.markdown("""
<div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:16px;
  padding:22px 24px">
  <div style="font-weight:700;font-size:.98rem;margin-bottom:8px;color:#166534">
    ✅ Foto siap diproses
  </div>
  <div style="font-size:.86rem;color:#1a6630;line-height:1.65">
    Selanjutnya, pangkas foto agar hanya menyisakan
    tabel <b>Informasi Nilai Gizi</b> pada kemasan.
    Semakin tepat pangkasannya, semakin akurat hasilnya.
  </div>
</div>
""", unsafe_allow_html=True)
            st.write("")
            if st.button(
                "Lanjut: Pangkas Foto  →",
                use_container_width=True,
                key="to_crop",
            ):
                st.session_state.original = img
                st.session_state.crop_rot = 0      # mulai dari rotasi 0 untuk foto baru
                _goto("pangkas")

    # ── Cara kerja (layout 2 kolom) ──
    st.markdown('<hr class="ns-divider"/>', unsafe_allow_html=True)
    
    how_html = '''<div class="ns-how-section">
<div class="ns-how-left">
<div class="ns-how-title">Cara Kerja</div>
<div class="ns-how-steps">
<div class="ns-step-card blue-bg">
<div class="ns-step-icon blue">
<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z"/>
<circle cx="12" cy="13" r="3"/>
</svg>
</div>
<div class="ns-step-content">
<h4>Foto Label Kemasan</h4>
<p>Arahkan kamera ke bagian Informasi Nilai Gizi pada kemasan minuman dan pastikan teks terlihat jelas.</p>
</div>
</div>
<div class="ns-step-card green-bg">
<div class="ns-step-icon green">
<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
</svg>
</div>
<div class="ns-step-content">
<h4>Baca Otomatis</h4>
<p>AI membaca seluruh angka gizi dari label — gula, garam, lemak jenuh, dan lainnya.</p>
</div>
</div>
<div class="ns-step-card amber-bg">
<div class="ns-step-icon amber">
<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
<line x1="6" y1="20" x2="6" y2="14"/>
</svg>
</div>
<div class="ns-step-content">
<h4>Lihat Skor Kesehatan</h4>
<p>Lihat kandungan nutrisi dan dapatkan skor Nutri-Level</p>
</div>
</div>
</div>
</div>
<div class="ns-how-right">
<div class="ns-best-results-card">
<h4>Tips Foto Terbaik</h4>
<div class="ns-best-result-item">
<div class="ns-br-check">✓</div>
<div>
<strong>Cahaya Merata</strong>
<p>Hindari pantulan dan bayangan agar teks label terlihat jelas oleh kamera.</p>
</div>
</div>
<div class="ns-best-result-item">
<div class="ns-br-check">✓</div>
<div>
<strong>Posisi Lurus</strong>
<p>Pegang kemasan tegak lurus di depan kamera — jangan miring atau bersudut.</p>
</div>
</div>
<div class="ns-best-result-item">
<div class="ns-br-check">✓</div>
<div>
<strong>Label Utuh</strong>
<p>Pastikan tabel Informasi Nilai Gizi tidak terlipat, basah, atau tertutup.</p>
</div>
</div>
<div class="ns-best-result-item">
<div class="ns-br-check">✓</div>
<div>
<strong>Tangan Stabil</strong>
<p>Tahan kamera sebentar agar hasil foto tajam dan tidak buram.</p>
</div>
</div>
</div>
</div>
</div>'''
    
    st.markdown(how_html, unsafe_allow_html=True)

    # Dialog Nutri-Level dibuka dari tombol "Pelajari Cara Kerja" di hero.
    if st.session_state.get("show_nl_dialog"):
        C.render_nutrilevel_dialog(active=None)


# ─── Layar 2 — Pangkas ───────────────────────────────────────────────────────
def _slider_crop(img: Image.Image) -> Image.Image:
    W, H = img.size
    cx = st.slider("Area horizontal (%)", 0, 100, (5, 95), key="cx")
    cy = st.slider("Area vertikal (%)", 0, 100, (5, 95), key="cy")
    x1, x2 = int(W * cx[0] / 100), int(W * cx[1] / 100)
    y1, y2 = int(H * cy[0] / 100), int(H * cy[1] / 100)
    return img.crop((x1, y1, x2, y2)) if x2 - x1 > 10 and y2 - y1 > 10 else img


def screen_crop():
    img = st.session_state.original
    if img is None:
        _goto("mulai")

    mode, msg = get_status()
    render_sidebar("pangkas", mode, msg)
    C.scroll_to_top()

    st.markdown("""
<div class="ns-crop-header">
  <h2>Pangkas Area Label</h2>
  <p>Geser kotak hingga hanya menyisakan tabel <b>Informasi Nilai Gizi</b>
     pada kemasan minuman.</p>
</div>
<div class="ns-crop-tip">
  <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor"
       stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  Semakin tepat pangkasan pada tabel gizi, semakin akurat hasil pembacaannya.
</div>
""", unsafe_allow_html=True)

    # ── Rotasi gambar (untuk foto kamera yang miring) ──
    # Sudut rotasi disimpan di session_state agar bertahan antar-rerun. Tombol
    # memutar ±90°; gambar diputar SEBELUM masuk cropper sehingga koordinat
    # pangkasan tetap akurat terhadap gambar yang sudah tegak.
    st.session_state.setdefault("crop_rot", 0)

    rcol1, rcol2, rcol3, rspace = st.columns([1, 1, 1, 3], gap="small")
    with rcol1:
        if st.button("↺ Putar Kiri", key="rot_left", use_container_width=False):
            st.session_state.crop_rot = (st.session_state.crop_rot - 90) % 360
            st.rerun()
    with rcol2:
        if st.button("↻ Putar Kanan", key="rot_right", use_container_width=False):
            st.session_state.crop_rot = (st.session_state.crop_rot + 90) % 360
            st.rerun()
    with rcol3:
        if st.button("⟲ Reset", key="rot_reset", type="secondary", use_container_width=False):
            st.session_state.crop_rot = 0
            st.rerun()

    # Terapkan rotasi (expand=True agar seluruh gambar tetap terlihat).
    rot = st.session_state.crop_rot % 360
    work_img = img.rotate(-rot, expand=True) if rot else img

    cropped = None

    try:
        from streamlit_cropper import st_cropper

        # RESOLUSI kanvas cropper (piksel). Ini menentukan KETAJAMAN saja, BUKAN
        # lebar tampil: kanvas dibuat RESPONSIF lewat skrip di bawah sehingga
        # selalu menyusut mengikuti lebar kolom/kartu — termasuk di layar HP yang
        # sempit. Hasil pangkasan tetap diambil dari gambar resolusi penuh lewat
        # pemetaan koordinat kotak (sx/sy), jadi akurasi pembacaan tidak berkurang.
        CROP_DISP_W = 480          # resolusi piksel kanvas (bukan lebar tampil)
        CROP_DISP_H = 620
        disp = work_img.copy()
        disp.thumbnail((CROP_DISP_W, CROP_DISP_H))   # perkecil proporsional
        sx = work_img.width  / max(disp.width, 1)    # faktor skala balik ke gambar kerja
        sy = work_img.height / max(disp.height, 1)

        col1, col2 = st.columns([1.6, 1], gap="medium")
        with col1:
            st.markdown(
                '<div class="ns-preview-tag">✂️ Geser kotak untuk memangkas</div>',
                unsafe_allow_html=True,
            )
            _box = st_cropper(
                disp,
                realtime_update=True,
                box_color="#16A34A",
                aspect_ratio=None,
                return_type="box",           # ambil KOORDINAT, bukan gambar tampil
                should_resize_image=False,   # kanvas = ukuran 'disp'
            )

            # ── Buat kanvas cropper RESPONSIF (perbaikan luapan di HP) ──
            # streamlit-cropper menggambar <canvas> dengan lebar = piksel gambar
            # (di sini ≤480 px) DI DALAM iframe komponen. Di HP kolomnya lebih
            # sempit dari itu, sehingga kanvas meluap melewati kartu. CSS dari
            # halaman induk TIDAK bisa mengecilkan kanvas di dalam iframe, jadi
            # kita masuk ke dokumen iframe (komponen ini same-origin) lalu memaksa
            # kanvas mengikuti lebar kontainer dengan rasio aspek tetap, dan
            # menyamakan tinggi iframe agar tak ada ruang kosong.
            #
            # Koordinat tetap akurat: kotak dikembalikan dalam ruang piksel 'disp'
            # (fabric.js memetakan pointer via getBoundingClientRect, sehingga
            # kanvas yang diperkecil CSS tetap terbaca benar), lalu sx/sy memetakan
            # ke gambar resolusi penuh.
            components.html(
                f"""
                <script>
                (function() {{
                  const pdoc = window.parent.document;
                  const AR = "{disp.width} / {disp.height}";
                  const CSS =
                    ".canvas-container{{width:100%!important;max-width:100%!important;" +
                    "height:auto!important;aspect-ratio:" + AR + "!important;}}" +
                    ".canvas-container>canvas.lower-canvas,.canvas-container>canvas.upper-canvas{{" +
                    "width:100%!important;height:100%!important;left:0!important;top:0!important;}}" +
                    "body{{margin:0!important;overflow:hidden!important;}}";

                  function fit() {{
                    const frames = [];
                    pdoc.querySelectorAll("iframe").forEach(function(fr) {{
                      const t = (fr.title || "").toLowerCase();
                      const s = (fr.getAttribute("src") || "").toLowerCase();
                      if (t.indexOf("cropper") >= 0 || s.indexOf("cropper") >= 0) {{
                        frames.push(fr);
                      }}
                    }});
                    frames.forEach(function(fr) {{
                      fr.style.maxWidth = "100%";
                      fr.style.display = "block";
                      fr.style.margin = "0 auto";
                      let idoc;
                      try {{ idoc = fr.contentDocument || fr.contentWindow.document; }}
                      catch (e) {{ return; }}            // beda origin -> lewati
                      if (!idoc || !idoc.body) return;
                      if (!idoc.getElementById("ns-cropper-fit")) {{
                        const s = idoc.createElement("style");
                        s.id = "ns-cropper-fit"; s.textContent = CSS;
                        (idoc.head || idoc.body).appendChild(s);
                      }}
                      // Samakan tinggi iframe dgn tinggi kanvas yang sudah diskalakan.
                      const cc = idoc.querySelector(".canvas-container");
                      if (cc) {{
                        const h = Math.round(cc.getBoundingClientRect().height);
                        if (h > 0) fr.style.height = h + "px";
                      }}
                    }});
                  }}

                  fit();
                  const obs = new MutationObserver(fit);
                  obs.observe(pdoc.body, {{childList: true, subtree: true}});
                  window.parent.addEventListener("resize", fit);
                  // Kanvas dibuat fabric.js secara asinkron; poll sebentar lalu stop.
                  let n = 0;
                  const iv = setInterval(function() {{
                    fit(); if (++n > 40) clearInterval(iv);
                  }}, 150);
                  setTimeout(function() {{ obs.disconnect(); }}, 9000);
                }})();
                </script>
                """,
                height=0,
            )

            # Petakan kotak (ruang gambar tampil) → gambar KERJA (sudah dirotasi),
            # lalu pangkas pada resolusi penuh.
            if _box:
                _l = max(0, int(_box["left"] * sx))
                _t = max(0, int(_box["top"]  * sy))
                _w = min(work_img.width  - _l, int(_box["width"]  * sx))
                _h = min(work_img.height - _t, int(_box["height"] * sy))
                cropped = work_img.crop((_l, _t, _l + _w, _t + _h)) if (_w > 10 and _h > 10) else work_img
            else:
                cropped = work_img
        with col2:
            # SATU kartu: badge + gambar + metadata (gaya referensi gambar 6)
            if cropped is not None:
                img_uri = C._img_uri(cropped, max_px=1200)
                W, H = cropped.size
                from math import gcd
                g = gcd(W, H) or 1
                rasio = f"{W//g}:{H//g}"
                if min(W, H) >= 700:
                    kual, kual_col = "Resolusi Tinggi", "#16A34A"
                elif min(W, H) >= 400:
                    kual, kual_col = "Resolusi Cukup", "#F59E0B"
                else:
                    kual, kual_col = "Resolusi Rendah", "#EF4444"
                img_html = (
                    f'<div class="ns-live-imgbox"><img src="{img_uri}" class="ns-live-img"/></div>'
                    if img_uri else ""
                )
                st.markdown(f"""
<div class="ns-live-card">
<div class="ns-preview-tag">👁 Pratinjau langsung</div>
{img_html}
<div class="ns-live-meta">
  <div class="ns-pm-row">
    <span class="ns-pm-key">Ukuran</span>
    <span class="ns-pm-val">{W} × {H} px</span>
  </div>
  <div class="ns-pm-row">
    <span class="ns-pm-key">Rasio Aspek</span>
    <span class="ns-pm-val">{rasio}</span>
  </div>
  <div class="ns-pm-row">
    <span class="ns-pm-key">Kualitas Gambar</span>
    <span class="ns-pm-val" style="color:{kual_col}">{kual}</span>
  </div>
  <div class="ns-pm-row ns-pm-last">
    <span class="ns-pm-key">Status</span>
    <span class="ns-pm-val" style="color:#16A34A">✓ Siap dianalisis</span>
  </div>
</div>
</div>
""", unsafe_allow_html=True)
                if not img_uri:
                    st.image(cropped, use_container_width=True)
            else:
                st.markdown(
                    '<div class="ns-live-card">'
                    '<div class="ns-preview-tag">👁 Pratinjau langsung</div>'
                    '<div class="ns-live-imgbox" style="color:#94A3B8;font-size:.8rem">'
                    'Menunggu area pangkasan…</div></div>',
                    unsafe_allow_html=True,
                )

    except Exception:
        col1, col2 = st.columns([1.35, 1], gap="medium")
        with col1:
            st.markdown(
                '<div class="ns-preview-tag">🔧 Pangkas dengan Slider</div>',
                unsafe_allow_html=True,
            )
            st.image(work_img, use_container_width=True)
            cropped = _slider_crop(work_img)
        with col2:
            st.markdown(
                '<div class="ns-preview-tag">👁 Pratinjau</div>',
                unsafe_allow_html=True,
            )
            if cropped is not None:
                img_uri = C._img_uri(cropped, max_px=1200)
                if img_uri:
                    st.markdown(
                        f'<div class="ns-preview-imgbox">'
                        f'<img src="{img_uri}" class="ns-preview-img"/>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.image(cropped, use_container_width=True)

    st.write("")
    st.markdown('<div class="ns-nav-btns">', unsafe_allow_html=True)
    b1, b2 = st.columns([1, 1], gap="medium")
    with b1:
        if st.button(
            "← Foto Ulang",
            type="secondary",
            use_container_width=True,
            key="back_cap",
        ):
            st.session_state.crop_rot = 0      # reset rotasi saat foto ulang
            _goto("mulai")
    with b2:
        if st.button(
            "Konfirmasi & Analisis →",
            use_container_width=True,
            key="to_loading",
        ):
            st.session_state.cropped = cropped if cropped is not None else work_img
            _goto("memproses")
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Layar 3 — Memproses ─────────────────────────────────────────────────────
def screen_loading():
    img = st.session_state.cropped
    if img is None:
        _goto("mulai")

    mode, msg = get_status()
    render_sidebar("memproses", mode, msg)
    C.scroll_to_top()

    # Gambar disematkan sebagai base64 di dalam HTML (tidak pakai st.image agar
    # tidak ada "bug gambar menempel" — st.image keluar dari div berbentuk lingkaran)
    img_uri = C._img_uri(img, max_px=420)

    # Bagian atas statis (gambar lingkaran + cincin hijau + buah melayang)
    st.markdown(C.loader_stage_html(img_uri), unsafe_allow_html=True)

    # Placeholder untuk daftar langkah (di-update tiap tahap)
    ph = st.empty()
    # Placeholder status antrean (di atas langkah) — beri tahu user bila sedang
    # menunggu permintaan lain selesai (inferensi diserialkan oleh lock).
    qph = st.empty()

    ph.markdown(C.loader_steps_html(0), unsafe_allow_html=True)
    get_status()
    time.sleep(0.7)

    ph.markdown(C.loader_steps_html(1), unsafe_allow_html=True)
    pos = inference.acquire_slot()
    with qph.container():
        C.queue_notice(pos)
    try:
        result = run_pipeline(img)
    finally:
        inference.release_slot()
    qph.empty()
    time.sleep(0.5)

    ph.markdown(C.loader_steps_html(2), unsafe_allow_html=True)
    fields = result["fields"]
    sens   = nutri_level_sensitivitas(fields)
    calc   = sens["utama"] if sens["serbuk_asumsi"] else nutri_level(fields)
    time.sleep(0.6)

    st.session_state.result = result
    st.session_state.calc   = calc
    st.session_state.sens   = sens
    _goto("hasil")


# ─── Layar 4 — Hasil ─────────────────────────────────────────────────────────
def screen_result():
    result = st.session_state.result
    calc   = st.session_state.calc
    sens   = st.session_state.sens
    if result is None or calc is None:
        _goto("mulai")

    fields  = result["fields"]
    mode    = result["mode"]
    est     = bool(sens and sens.get("serbuk_asumsi"))
    rentang = sens.get("level_rentang") if sens else None

    mode_txt, mode_msg = get_status()
    render_sidebar("hasil", mode_txt, mode_msg)
    C.scroll_to_top()

    # Status model TIDAK diulang di area utama (sudah sticky di sidebar, item 7).
    # Banner hanya muncul pada mode demo sebagai peringatan nilai ilustratif.
    if mode != "model":
        C.mode_banner(
            mode,
            "model tidak tersedia — nilai di bawah hanya contoh ilustrasi",
        )

    # Header hasil dengan tombol Share & Download
    C.result_header_with_actions(mode, calc, fields, result)

    # Kartu grade utama (gaya "Good Quality" referensi)
    C.grade_card(calc, fields, mode)

    # Dialog penjelasan Nutri-Level (tombol pemicunya kini ada di header, sejajar Cetak/PDF)
    if st.session_state.get("show_nl_dialog"):
        C.render_nutrilevel_dialog(active=calc.get("level_akhir"))

    # GGL per komponen (selektor pil A-D, label Nutri-Level GGL)
    st.markdown(
        '<div style="font-size:.75rem;font-weight:700;color:#94A3B8;'
        'text-transform:uppercase;letter-spacing:.08em;margin:6px 0 12px">'
        'Detail Nutri-Level per Kandungan · per 100 ml</div>',
        unsafe_allow_html=True,
    )
    C.components_section(calc, fields)
    st.write("")

    # Label kemasan + Alert + Rincian detail
    C.label_and_breakdown(
        calc, fields,
        cropped_img=st.session_state.cropped,
        panel_img=result.get("panel_crop"),
    )
    st.write("")

    # Grafik Asupan vs Batas Harian
    C.intake_chart_section(calc, fields)
    st.write("")

    # Saran konsumsi
    C.consumption_tips_section(calc)

    # Catatan now shown within the right-hand breakdown column

    st.write("")

    # Tombol aksi bawah
    col_c1, col_c2, col_c3 = st.columns([1, 1.5, 1])
    with col_c2:
        if st.button(
            "↩ Pindai Minuman Lain",
            use_container_width=True,
            key="restart",
        ):
            _reset()
            st.rerun()


# ─── Router ───────────────────────────────────────────────────────────────────
_STEP_MAP = {
    "mulai":      screen_capture,
    "pangkas":    screen_crop,
    "memproses":  screen_loading,
    "hasil":      screen_result,
}


def main():
    _init()
    _ensure_sidebar_toggle()
    fn = _STEP_MAP.get(st.session_state.step)
    if fn:
        fn()
    else:
        _reset()
        st.rerun()


if __name__ == "__main__":
    main()
