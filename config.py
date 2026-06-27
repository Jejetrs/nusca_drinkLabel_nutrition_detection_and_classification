"""
config.py
=========
Satu sumber konfigurasi untuk aplikasi NutriScan AI.

Yang paling sering Anda ubah hanya **MODEL_DIR** -> arahkan ke folder hasil
ekspor Donut dari notebook (mis. folder `donut_export` yang berisi
`model.safetensors`, `config.json`, `preprocessor_config.json`, dst).

Bila MODEL_DIR belum diisi / belum ada, aplikasi tetap berjalan dalam
**MODE DEMO** sehingga seluruh alur & desain bisa dilihat tanpa model.
"""

from __future__ import annotations
import os
from pathlib import Path

# ----------------------------------------------------------------------------- #
# 1. Model
# ----------------------------------------------------------------------------- #
# Sumber model Donut. Bisa berupa:
#   (a) Repo ID Hugging Face Hub, mis. "Jejetrs/nusca-donut"  <-- default
#   (b) Path folder lokal hasil ekspor (mis. "models/donut")
# Dapat dioverride lewat environment variable NUTRISCAN_MODEL_DIR.
#
# Untuk deployment (Streamlit Cloud) kita TIDAK menyertakan file model di repo
# Git (ukurannya >100 MB). Sebagai gantinya transformers akan mengunduh otomatis
# dari Hugging Face Hub saat pertama dijalankan, lalu meng-cache-nya.
MODEL_DIR = "Jejetrs/nusca-donut"
MODEL_REVISION = "master"

BACKBONE = "donut"               # "donut" (default notebook) atau "trocr"
MAX_TARGET_LEN = int(os.getenv("NUTRISCAN_MAX_LEN", "160"))   # samakan dengan training (ini batas atas, bukan paksaan)

# --------------------------------------------------------------------------- #
# Pengendali MEMORI inferensi (penyebab "hanya bisa 1x deteksi lalu OOM").
# --------------------------------------------------------------------------- #
# NUM_BEAMS adalah tuas memori TERBESAR. Beam search menyimpan `num_beams`
# salinan KV-cache + logits decoder; num_beams=4 memakai ~4x memori puncak
# decoder dibanding greedy (num_beams=1). Untuk Donut (ekstraksi field
# terstruktur), greedy biasanya hampir sama akuratnya namun jauh lebih hemat.
#
#   - RAM kecil (mis. Streamlit Cloud ~1 GB efektif) -> biarkan 1 (default).
#   - Punya RAM lega & ingin akurasi maksimal        -> set env NUTRISCAN_NUM_BEAMS=4
NUM_BEAMS = int(os.getenv("NUTRISCAN_NUM_BEAMS", "1"))

# Batas sisi-terpanjang gambar kerja sebelum inferensi. Membatasi puncak memori
# EasyOCR (yang memproses pada resolusi input penuh) DAN encoder Donut. Donut
# tetap me-resize sendiri secara internal sesuai preprocessor_config (parity
# training tidak berubah), jadi nilai >= ukuran input Donut (umumnya ~1280) aman.
OCR_MAX_SIDE = int(os.getenv("NUTRISCAN_OCR_MAX_SIDE", "1600"))

# Stage-1: lokalisasi panel "Informasi Nilai Gizi" via EasyOCR sebelum dibaca.
# Model dilatih pada crop panel, jadi inferensi sebaiknya juga meng-crop dahulu.
USE_PANEL_CROP = True
CROP_PAD = 0.04                  # HARUS sama dgn training (parity)
CROP_MIN_CONF = 0.2              # HARUS sama dgn training (parity)

# Koreksi garam vs kalium dari OCR: "conservative" | "always" | "off"
SODIUM_OVERRIDE_MODE = "conservative"

# Token tugas Donut (sama dgn notebook)
TASK_START, TASK_END = "<s_gizi>", "</s_gizi>"

# ----------------------------------------------------------------------------- #
# 2. Skema field (urutan baca pada label) — samakan dengan TARGET_FIELDS notebook
# ----------------------------------------------------------------------------- #
TARGET_FIELDS = [
    "takaran",              # Takaran Saji (ml/g)
    "sajian",               # Sajian per Kemasan
    "jumlah_per_kemasan",   # Jumlah per Kemasan
    "lemak",                # Lemak total
    "lemak_jenuh",          # Lemak jenuh (komponen Nutri-Level)
    "gula",                 # Gula total
    "sukrosa",              # Sukrosa (informasi tambahan)
    "laktosa",              # Laktosa (koreksi gula Nutri-Level)
    "garam",                # Garam = Natrium (mg)
]

# Label tampilan yang ramah pengguna untuk tiap field.
FIELD_LABELS = {
    "takaran": "Takaran Saji",
    "sajian": "Sajian per Kemasan",
    "jumlah_per_kemasan": "Jumlah per Kemasan",
    "lemak": "Lemak Total",
    "lemak_jenuh": "Lemak Jenuh",
    "gula": "Gula Total",
    "sukrosa": "Sukrosa",
    "laktosa": "Laktosa",
    "garam": "Garam (Natrium)",
}

# Kelompok tampilan
PORSI_FIELDS = ["takaran", "sajian", "jumlah_per_kemasan"]
GIZI_FIELDS = ["lemak", "lemak_jenuh", "gula", "sukrosa", "laktosa", "garam"]

# ----------------------------------------------------------------------------- #
# 3. Tema / warna
# ----------------------------------------------------------------------------- #
APP_NAME = "Nusca"
APP_TAGLINE = "Cek Nutrisi Minuman Kemasan"

# Warna level Nutri-Level (A terbaik -> D terburuk)
LEVEL_COLORS = {
    "A": {"bg": "#16A34A", "soft": "#DCFCE7", "text": "#166534", "label": "Sangat Baik"},
    "B": {"bg": "#84CC16", "soft": "#ECFCCB", "text": "#3F6212", "label": "Baik"},
    "C": {"bg": "#F59E0B", "soft": "#FEF3C7", "text": "#92400E", "label": "Sedang"},
    "D": {"bg": "#EF4444", "soft": "#FEE2E2", "text": "#991B1B", "label": "Tinggi"},
}
LEVEL_NA = {"bg": "#94A3B8", "soft": "#F1F5F9", "text": "#475569", "label": "Tidak dapat dihitung"}

# Komponen yang ditampilkan sebagai badge Nutri-Level (urutan tampil)
NUTRI_COMPONENTS = [
    ("gula", "Gula", "g"),
    ("lemak_jenuh", "Lemak Jenuh", "g"),
    ("garam", "Garam (Natrium)", "mg"),
]
