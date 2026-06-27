# 🌿 NutriScan AI — Pembaca Label Gizi & Klasifikasi Nutri-Level

Aplikasi web **Streamlit** yang membaca panel **Informasi Nilai Gizi** dari foto
kemasan minuman, lalu mengklasifikasikan **Nutri-Level (A–D)** berdasarkan
kandungan **Gula**, **Lemak Jenuh**, dan **Garam (Natrium)** sesuai
**Kepmenkes No. HK.01.07/MENKES/301/2026**.

Mesin pembaca memakai model **Donut** (`VisionEncoderDecoder`) hasil fine-tuning,
dengan tahap pra-lokalisasi panel memakai **EasyOCR** agar konsisten dengan
distribusi data latih. Model di-host di Hugging Face dan diunduh otomatis saat
aplikasi dijalankan.

---

## ✨ Fitur Utama

- **Dua cara input** — unggah berkas gambar, atau **ambil foto langsung dari
  kamera**. Di smartphone, tombol *Buka Kamera* langsung membuka aplikasi kamera
  belakang secara fullscreen (resolusi penuh, bukan kamera mini di halaman).
- **Koreksi orientasi otomatis** — foto dari kamera HP yang menyimpan rotasi di
  metadata EXIF otomatis ditegakkan, sehingga tidak tampil miring.
- **Pangkas + Putar** — pada tahap pangkas, pengguna dapat **memutar gambar**
  (±90° / reset) bila foto miring, lalu memangkas tepat pada tabel gizi. Hasil
  diambil pada resolusi penuh untuk menjaga akurasi pembacaan.
- **Pratinjau langsung** — pratinjau hasil crop diperbarui real-time, lengkap
  dengan info ukuran, rasio aspek, dan indikator kualitas resolusi.
- **Sidebar stepper** — navigasi langkah **Capture → Crop → Analyze** dengan
  status model dan tombol buka/tutup sidebar (drawer di layar kecil).
- **Klasifikasi Nutri-Level** — level per komponen (Gula, Lemak Jenuh, Garam)
  dan level keseluruhan (komponen terburuk), plus lapis-2 edukasi: persentase
  batas konsumsi harian per kemasan (Permenkes 30/2013).
- **Mode demo otomatis** — bila model/dependensi tidak tersedia, aplikasi tetap
  berjalan dengan contoh deterministik agar seluruh alur & desain dapat dinilai.

---

## 🔄 Alur Aplikasi

```
Capture ─────────► Crop ──────────► Analyze ─────────► Hasil
(unggah/kamera)   (putar+pangkas)   (baca model)      (Nutri-Level)
```

1. **Foto Label** — unggah berkas atau jepret lewat kamera perangkat.
2. **Pangkas** — putar bila miring, lalu pangkas area panel **Informasi Nilai
   Gizi**. Semakin tepat pangkasan, semakin akurat hasilnya.
3. **Memproses** — memuat model → melokalisasi panel (EasyOCR) → membaca nilai
   (Donut) → koreksi garam/natrium → menghitung Nutri-Level.
4. **Hasil** — seluruh field ditampilkan (Takaran Saji, Sajian per Kemasan,
   Jumlah per Kemasan, Lemak Total, Lemak Jenuh, Gula Total, Sukrosa, Laktosa,
   Garam), beserta badge Nutri-Level per komponen dan keseluruhan.

---

## 📁 Struktur Proyek

```
nutriscan_app/
├── app.py                  # Wizard utama (state machine antar-layar)
├── config.py               # Sumber konfigurasi: MODEL_DIR, field, tema, warna
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml         # Tema & batas unggah
├── asset/
│   ├── logo.png
│   └── animasi_ilustrasi_beranda.png
├── core/                   # Logika inti (tanpa UI)
│   ├── inference.py        #   Pipeline: muat model → crop panel → baca → koreksi
│   ├── nutrilevel.py       #   Klasifikasi Nutri-Level (port persis dari notebook)
│   └── schema.py           #   Parse output decoder Donut → field
└── ui/                     # Lapisan tampilan
    ├── sidebar.py          #   Sidebar stepper (Capture → Crop → Analyze)
    ├── components.py       #   Komponen UI (hero, kartu hasil, badge, dll.)
    └── styles.py           #   CSS kustom (tema, layout, responsif)
```

Setiap folder punya tanggung jawab jelas: `core/` = logika & model, `ui/` =
tampilan. `app.py` mengorkestrasi alur antar-layar.

---

## 🚀 Menjalankan Secara Lokal

### 1. Prasyarat

- Python 3.10+
- (Opsional) GPU CUDA untuk inferensi lebih cepat — CPU juga didukung.

### 2. Pasang dependensi

```bash
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. (Opsional) Token Hugging Face untuk repo privat

Bila repo model bersifat privat, sediakan token lewat **Streamlit secrets**.
Buat berkas `.streamlit/secrets.toml`:

```toml
HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
```

### 4. Jalankan

```bash
streamlit run app.py
```

Buka `http://localhost:8501`. Saat pertama kali dijalankan, model (~770 MB)
diunduh dari Hugging Face lalu di-cache; pemuatan berikutnya jauh lebih cepat.

---

## ☁️ Deploy ke Streamlit Community Cloud

1. Push repositori ke GitHub **tanpa** menyertakan berkas model besar (lihat
   `.gitignore`). Model diunduh otomatis dari Hugging Face saat aplikasi jalan.
2. Di [share.streamlit.io](https://share.streamlit.io), arahkan ke repo Anda dan
   tetapkan `app.py` sebagai entry point.
3. Bila repo model privat, tambahkan `HF_TOKEN` pada **Settings → Secrets**.
4. Deploy. Cold start pertama lebih lama karena mengunduh model.

> Catatan: GitHub menolak berkas > 100 MB. Pastikan `model.safetensors` dan
> arsip ekspor tidak ikut ter-commit — itulah mengapa model di-host di Hugging
> Face dan diunduh runtime.

---

## ⚙️ Konfigurasi

Diatur di `config.py` (atau lewat environment variable):

| Pengaturan              | Default               | Keterangan                                   |
| ----------------------- | --------------------- | -------------------------------------------- |
| `MODEL_DIR`             | `Jejetrs/nusca-donut` | Repo Hugging Face atau path folder lokal     |
| `MODEL_REVISION`        | `master`              | Revisi/branch repo HF                        |
| `BACKBONE`              | `donut`               | `donut` atau `trocr`                         |
| `USE_PANEL_CROP`        | `True`                | Lokalisasi panel via EasyOCR sebelum dibaca  |
| `SODIUM_OVERRIDE_MODE`  | `conservative`        | Strategi koreksi garam vs kalium dari OCR    |

Override lewat environment variable, mis. `NUTRISCAN_MODEL_DIR`.

---

## 🧮 Tentang Nutri-Level

Level A–D ditentukan dari kandungan **gula (dikurangi laktosa)**, **garam
(natrium, mg)**, dan **lemak jenuh** per **100 ml**. Nilai per-100-ml dibulatkan
1 desimal lalu dipetakan ke level; level akhir produk = komponen **terburuk**.

| Zat gizi (per 100 ml) | A      | B           | C            | D       |
| --------------------- | ------ | ----------- | ------------ | ------- |
| Gula (g)              | <= 1.0 | > 1 – 5     | > 5 – 10     | > 10    |
| Garam/Natrium (mg)    | <= 5   | > 5 – 120   | > 120 – 500  | > 500   |
| Lemak jenuh (g)       | <= 0.7 | > 0.7 – 1.2 | > 1.2 – 2.8  | > 2.8   |

Untuk produk **serbuk** (takaran dalam gram), per-100-ml diestimasi dari asumsi
volume seduhan (default 200 ml/saji) dan ditandai sebagai estimasi.

---

## 🩺 Mengatasi Masalah

- **"Mode demo aktif"** padahal ingin model asli → cek panel "Kenapa mode demo?"
  di sidebar. Penyebab umum: `torch`/`transformers`/`easyocr` belum terpasang,
  repo HF privat tanpa `HF_TOKEN`, atau berkas model di repo tidak lengkap.
- **Foto hasil kamera miring** → gunakan tombol **Putar Kiri/Kanan** di tahap
  pangkas. Orientasi EXIF sudah dikoreksi otomatis; tombol untuk koreksi sisanya.
- **Kamera tidak terbuka langsung di HP** → pastikan situs diakses lewat
  **HTTPS** (wajib untuk akses kamera) dan izin kamera diberikan.

---

## 📜 Lisensi & Atribusi

Model Donut: arsitektur `VisionEncoderDecoder` (Naver Clova IX) hasil
fine-tuning. EasyOCR untuk lokalisasi panel. Klasifikasi Nutri-Level mengacu
pada Kepmenkes No. HK.01.07/MENKES/301/2026 dan Permenkes 30/2013.
