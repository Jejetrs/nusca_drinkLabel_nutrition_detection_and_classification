"""
core/inference.py
=================
Pipeline inferensi produksi (port dari notebook):

    gambar -> crop_panel (EasyOCR melokalisasi panel) -> Donut membaca
           -> parse field -> koreksi garam/natrium (opsional)

Memuat model Donut **asli** dari `config.MODEL_DIR`. Bila model/dependensi
(torch, transformers, easyocr) tidak tersedia, otomatis jatuh ke **MODE DEMO**
agar seluruh alur UI tetap dapat dijalankan & dinilai.

Fungsi utama yang dipakai UI:
    - get_status()  -> ('model' | 'demo', pesan)
    - run_pipeline(pil_image) -> dict hasil lengkap (lihat di bawah)
"""

from __future__ import annotations
import hashlib
from pathlib import Path
import os
import gc
import ctypes
import threading

# ============================================================================ #
# GERBANG KONKURENSI — inti perbaikan OOM saat 2+ user pindai bersamaan.
# ============================================================================ #
# Di Streamlit semua sesi berbagi SATU proses & SATU model (via cache_resource).
# Bila dua inferensi berjalan bersamaan, PUNCAK memori keduanya (KV-cache Donut
# + 2x EasyOCR) saling menumpuk pada saat yang sama -> melewati batas RAM ->
# proses di-OOM-kill. Solusi paling andal: SERIALKAN inferensi berat dgn satu
# Lock global. User kedua antre beberapa detik (bukan crash). Akurasi tak
# berubah sama sekali.
_INFER_LOCK = threading.Lock()

# Penghitung antrean: berapa permintaan sedang menunggu/diproses lewat lock.
# Dipakai UI untuk menampilkan "Antrean ke-N". Dilindungi mutex ringan sendiri.
_QUEUE_LOCK = threading.Lock()
_QUEUE_WAITING = 0


def acquire_slot() -> int:
    """Daftar ke antrean inferensi. Kembalikan posisi (1 = giliran sekarang)."""
    global _QUEUE_WAITING
    with _QUEUE_LOCK:
        _QUEUE_WAITING += 1
        return _QUEUE_WAITING


def release_slot() -> None:
    """Lepas dari antrean setelah inferensi selesai."""
    global _QUEUE_WAITING
    with _QUEUE_LOCK:
        _QUEUE_WAITING = max(0, _QUEUE_WAITING - 1)


# Batasi thread BLAS/OMP agar beberapa permintaan tidak menggandakan thread CPU
# (memperparah lonjakan memori & justru memperlambat). Aman dipanggil dini.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
from PIL import Image

import streamlit as st

from config import (
    MODEL_DIR, BACKBONE, MAX_TARGET_LEN, NUM_BEAMS, MODEL_REVISION,
    USE_PANEL_CROP, CROP_PAD, CROP_MIN_CONF, SODIUM_OVERRIDE_MODE,
    TASK_START, TASK_END, OCR_MAX_SIDE,
)
from core.schema import KEYS, parse_donut, parse_flat, clean_donut_seq
import re


# ============================================================================ #
# Manajemen MEMORI — inti perbaikan "hanya bisa 1x deteksi lalu OOM"
# ============================================================================ #
# Akar masalah: setelah deteksi pertama, memori PUNCAK inferensi (terutama beam
# search Donut + dua kali jalan EasyOCR) TIDAK dikembalikan ke OS. Alokator CPU
# PyTorch meng-cache blok bebas untuk dipakai ulang, dan arena malloc glibc
# menahannya (fragmentasi), sehingga RSS proses tetap tinggi. Deteksi KEDUA
# menumpuk puncak baru di atas RSS yang sudah tinggi -> melewati batas -> proses
# dimatikan (OOM). Karena itu deteksi pertama lolos, yang kedua selalu gagal.
#
# Solusi: setelah setiap inferensi, lepaskan referensi tensor besar, jalankan
# garbage collector, kosongkan cache CUDA (bila ada), dan PALING PENTING di
# Linux -> panggil malloc_trim(0) agar glibc mengembalikan blok bebas ke OS.
try:
    _LIBC = ctypes.CDLL("libc.so.6")
except Exception:
    _LIBC = None


def _release_memory(torch_mod=None) -> None:
    """Kembalikan memori puncak inferensi ke OS setelah satu deteksi selesai."""
    try:
        gc.collect()
    except Exception:
        pass
    if torch_mod is not None:
        try:
            if torch_mod.cuda.is_available():
                torch_mod.cuda.empty_cache()
                torch_mod.cuda.ipc_collect()
        except Exception:
            pass
    if _LIBC is not None:                       # Linux/glibc saja
        try:
            _LIBC.malloc_trim(0)
        except Exception:
            pass


def _limit_size(img: Image.Image, max_side: int = OCR_MAX_SIDE) -> Image.Image:
    """Batasi sisi terpanjang gambar kerja agar puncak memori semua tahap turun.

    EasyOCR memproses pada resolusi input penuh; gambar besar = lonjakan memori.
    Donut tetap me-resize sendiri sesuai preprocessor (parity training tak
    berubah), jadi membatasi di sini aman untuk akurasi.
    """
    try:
        if max(img.size) <= max_side:
            return img
        out = img.copy()
        out.thumbnail((max_side, max_side))
        return out
    except Exception:
        return img


# ============================================================================ #
# Pemuatan model & OCR (di-cache agar hanya sekali per sesi)
# ============================================================================ #
@st.cache_resource(show_spinner=False)
def _load_model_bundle():
    """
    Load model Donut dari Hugging Face private/public repo
    atau folder lokal.
    """

    try:
        import torch
        from transformers import (
            VisionEncoderDecoderModel,
            DonutProcessor,
            TrOCRProcessor
        )
        # Satu thread per inferensi: cegah lonjakan memori/CPU saat antrean.
        try:
            torch.set_num_threads(1)
        except Exception:
            pass

    except Exception as e:
        return {
            "ok": False,
            "reason": f"transformers/torch belum terpasang ({e})"
        }


    # ============================================================
    # Hugging Face Token
    # ============================================================
    hf_token = None

    try:
        if "HF_TOKEN" in st.secrets:
            hf_token = st.secrets["HF_TOKEN"]
    except Exception:
        pass


    src = str(MODEL_DIR)

    local = Path(src)
    is_local = local.exists()


    if is_local:

        if not any(local.iterdir()):
            return {
                "ok": False,
                "reason": f"folder model kosong: {local.resolve()}"
            }

        model_ref = str(local)

    else:

        # repo Hugging Face
        model_ref = src



    try:

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )


        print("==============================")
        print("MODEL:", model_ref)
        print("DEVICE:", device)
        print(
            "HF TOKEN:",
            "ACTIVE" if hf_token else "NONE"
        )
        print("==============================")


        # ========================================================
        # Processor
        # ========================================================
        if BACKBONE == "donut":

            processor = DonutProcessor.from_pretrained(
                model_ref,
                revision=MODEL_REVISION,
                token=hf_token
            )

        else:

            processor = TrOCRProcessor.from_pretrained(
                model_ref,
                revision=MODEL_REVISION,
                token=hf_token
            )


        # ========================================================
        # Model
        # ========================================================
        model = VisionEncoderDecoderModel.from_pretrained(
            model_ref,
            revision=MODEL_REVISION,
            token=hf_token
        )


        model = (
            model
            .to(device)
            .eval()
        )


        n_params = round(
            sum(
                p.numel()
                for p in model.parameters()
            ) / 1e6,
            1
        )


        return {
            "ok": True,
            "model": model,
            "processor": processor,
            "device": device,
            "torch": torch,
            "n_params": n_params
        }



    except Exception as e:

        return {
            "ok": False,
            "reason":
            f"gagal memuat model dari '{model_ref}': {e}"
        }

@st.cache_resource(show_spinner=False)
def _load_ocr():
    """Muat EasyOCR untuk crop panel + koreksi natrium. None bila tak tersedia."""
    if not USE_PANEL_CROP:
        return None
    try:
        import easyocr
        try:
            import torch
            gpu = torch.cuda.is_available()
        except Exception:
            gpu = False
        return easyocr.Reader(["id", "en"], gpu=gpu, verbose=False)
    except Exception:
        return None


def get_status():
    """('model'|'demo', pesan) untuk ditampilkan di UI."""
    bundle = _load_model_bundle()
    if bundle.get("ok"):
        return "model", "Model AI Aktif dan Siap Menganalisis"
    return "demo", bundle.get("reason", "model tidak tersedia")


# ============================================================================ #
# Stage-1: crop panel (port persis dari notebook, parity pad/min_conf)
# ============================================================================ #
def crop_panel(img: Image.Image, ocr, pad=CROP_PAD, min_conf=CROP_MIN_CONF) -> Image.Image:
    """Lokalisasi area teks panel gizi. Bila OCR tak ada / teks minim -> kembalikan apa adanya."""
    if ocr is None:
        return img
    try:
        res = ocr.readtext(np.array(img), detail=1, paragraph=False)
    except Exception:
        return img
    pts = [pt for (bbox, t, c) in res if c >= min_conf for pt in bbox]
    if len(pts) < 4:
        return img
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    W, H = img.size
    px = int((max(xs) - min(xs)) * pad) + 8
    py = int((max(ys) - min(ys)) * pad) + 8
    x1 = max(0, int(min(xs)) - px)
    y1 = max(0, int(min(ys)) - py)
    x2 = min(W, int(max(xs)) + px)
    y2 = min(H, int(max(ys)) + py)
    return img.crop((x1, y1, x2, y2))


# ============================================================================ #
# Stage-2: baca panel dgn model (port persis)
# ============================================================================ #
def _read_panel(crop_img: Image.Image, bundle) -> tuple[str, dict]:
    torch = bundle["torch"]
    processor = bundle["processor"]
    model = bundle["model"]
    device = bundle["device"]
    pv = prompt = out = None
    try:
        pv = processor(crop_img, return_tensors="pt").pixel_values.to(device)
        with torch.no_grad():
            if BACKBONE == "donut":
                prompt = processor.tokenizer(
                    TASK_START, add_special_tokens=False, return_tensors="pt"
                ).input_ids.to(device)
                out = model.generate(pv, decoder_input_ids=prompt,
                                     max_length=MAX_TARGET_LEN, num_beams=NUM_BEAMS)
                seq = processor.tokenizer.batch_decode(out, skip_special_tokens=False)[0]
                seq = clean_donut_seq(seq, processor.tokenizer)
                return seq, parse_donut(seq)
            out = model.generate(pv, max_length=MAX_TARGET_LEN, num_beams=NUM_BEAMS)
            seq = processor.tokenizer.batch_decode(out, skip_special_tokens=True)[0]
            return seq, parse_flat(seq)
    finally:
        # Lepaskan tensor besar SEGERA agar OCR tahap koreksi natrium berikutnya
        # tidak menumpuk di atas memori puncak Donut.
        del pv, prompt, out
        _release_memory(torch)


# ============================================================================ #
# Koreksi garam <-> kalium dari OCR (port ringkas dari notebook)
# ============================================================================ #
_MG = re.compile(r"(\d+(?:[.,]\d+)?)\s*mg", re.I)
_NUM = re.compile(r"(\d+(?:[.,]\d+)?)")


def _ocr_items(crop, ocr):
    if ocr is None:
        return []
    try:
        res = ocr.readtext(np.array(crop), detail=1, paragraph=False)
    except Exception:
        return []
    items = []
    for bbox, text, conf in res:
        ys = [p[1] for p in bbox]
        xs = [p[0] for p in bbox]
        items.append(dict(text=text, yc=(min(ys) + max(ys)) / 2.0,
                          x0=min(xs), h=max(ys) - min(ys)))
    return items


def _mg_on_line(items, anchor):
    m = _MG.search(anchor["text"])
    if m:
        return m.group(1).replace(",", ".")
    tol = max(anchor["h"] * 0.8, 12)
    same = [it for it in items if it is not anchor
            and abs(it["yc"] - anchor["yc"]) <= tol and it["x0"] >= anchor["x0"]]
    same.sort(key=lambda it: it["x0"])
    for it in same:
        m = _MG.search(it["text"])
        if m:
            return m.group(1).replace(",", ".")
    for it in same:
        m = _NUM.search(it["text"])
        if m:
            return m.group(1).replace(",", ".")
    return None


def _find_value(items, keywords, anti=()):
    for it in items:
        t = it["text"].lower()
        if any(k in t for k in keywords) and not any(a in t for a in anti):
            v = _mg_on_line(items, it)
            if v:
                return v
    return None


def _num(x):
    m = _NUM.search(x or "")
    return m.group(1).replace(",", ".") if m else None


def _reconcile_garam(model_garam, crop, ocr, mode=SODIUM_OVERRIDE_MODE):
    """Kembalikan (garam_final, info). info berisi natrium_ocr/kalium_ocr/dikoreksi."""
    info = {"natrium_ocr": None, "kalium_ocr": None, "dikoreksi": False}
    if mode == "off" or ocr is None:
        return model_garam, info
    items = _ocr_items(crop, ocr)
    S = _find_value(items, ("natrium", "garam", "sodium"), anti=("kalium", "potassium"))
    K = _find_value(items, ("kalium", "potassium"))
    info["natrium_ocr"], info["kalium_ocr"] = S, K
    g = _num(model_garam)
    if mode == "always" and S is not None and _num(S) != g:
        info["dikoreksi"] = True
        return f"{S} mg", info
    if g is not None and K is not None and g == _num(K) and S is not None and _num(S) != _num(K):
        info["dikoreksi"] = True            # model mengambil Kalium -> ganti Natrium
        return f"{S} mg", info
    if g is None and S is not None:
        info["dikoreksi"] = True
        return f"{S} mg", info
    return model_garam, info


# ============================================================================ #
# MODE DEMO — agar UI bisa dilihat tanpa model. Nilai realistis & jelas ditandai.
# ============================================================================ #
_DEMO_SAMPLES = [
    {  # minuman manis (klasik) -> gula tinggi (D)
        "takaran": "250 ml", "sajian": "2", "jumlah_per_kemasan": "500 ml",
        "lemak": "0 g", "lemak_jenuh": "0 g", "gula": "27 g",
        "sukrosa": "25 g", "laktosa": "", "garam": "45 mg",
    },
    {  # susu (ada laktosa -> koreksi gula)
        "takaran": "200 ml", "sajian": "1", "jumlah_per_kemasan": "200 ml",
        "lemak": "6 g", "lemak_jenuh": "4 g", "gula": "15 g",
        "sukrosa": "", "laktosa": "9 g", "garam": "90 mg",
    },
    {  # teh kemasan ringan -> level rendah
        "takaran": "330 ml", "sajian": "1", "jumlah_per_kemasan": "330 ml",
        "lemak": "0 g", "lemak_jenuh": "0 g", "gula": "11 g",
        "sukrosa": "", "laktosa": "", "garam": "15 mg",
    },
]


def _demo_predict(pil_image: Image.Image):
    """Pilih sampel demo secara deterministik dari hash gambar (variasi antar foto)."""
    h = hashlib.md5(pil_image.tobytes()[:4096]).hexdigest()
    idx = int(h, 16) % len(_DEMO_SAMPLES)
    fields = {k: v for k, v in _DEMO_SAMPLES[idx].items() if k in KEYS and v}
    raw = "<MODE DEMO> " + " | ".join(f"{k}: {v}" for k, v in fields.items())
    return fields, raw


# ============================================================================ #
# Orkestrasi tingkat tinggi
# ============================================================================ #
def run_pipeline(pil_image: Image.Image) -> dict:
    """Jalankan pipeline penuh pada satu gambar (panel hasil crop manual user).

    return dict:
        mode            : 'model' | 'demo'
        fields          : {key: "nilai satuan"} hasil baca
        raw             : string mentah decoder
        panel_crop      : PIL.Image panel terdeteksi (untuk inspeksi)
        garam_info      : info koreksi natrium/kalium
    """
    bundle = _load_model_bundle()
    ocr = _load_ocr()

    if not bundle.get("ok"):
        fields, raw = _demo_predict(pil_image)
        return {"mode": "demo", "fields": fields, "raw": raw,
                "panel_crop": pil_image, "garam_info":
                {"natrium_ocr": None, "kalium_ocr": None, "dikoreksi": False}}

    torch_mod = bundle.get("torch")
    # SERIALKAN seluruh inferensi berat: hanya SATU permintaan diproses pada satu
    # waktu. Permintaan lain menunggu di sini (antre) alih-alih menumpuk puncak
    # memori secara bersamaan -> inilah yang mencegah OOM saat 2+ user serentak.
    with _INFER_LOCK:
        try:
            # Batasi resolusi gambar kerja -> turunkan puncak memori EasyOCR & Donut.
            work = _limit_size(pil_image)
            # Stage-1: pertajam crop manual user ke panel (parity dgn training)
            panel = crop_panel(work, ocr)
            # Stage-2: baca panel
            raw, fields = _read_panel(panel, bundle)
            # Koreksi garam/natrium
            garam_info = {"natrium_ocr": None, "kalium_ocr": None, "dikoreksi": False}
            if "garam" in KEYS:
                garam_final, garam_info = _reconcile_garam(fields.get("garam", ""), panel, ocr)
                if garam_final:
                    fields["garam"] = garam_final
            return {"mode": "model", "fields": fields, "raw": raw,
                    "panel_crop": panel, "garam_info": garam_info}
        finally:
            # Kembalikan memori puncak ke OS supaya permintaan BERIKUTNYA dalam
            # antrean mulai dari baseline lagi (mencegah penumpukan RSS).
            _release_memory(torch_mod)
