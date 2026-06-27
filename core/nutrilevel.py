"""
core/nutrilevel.py
==================
Klasifikasi **Nutri-Level** sesuai Kepmenkes No. HK.01.07/MENKES/301/2026
(Lampiran A & B). Modul ini adalah PORT PERSIS dari notebook pelatihan/inferensi
(`nutriscore-reader-nutrilevel-kepmenkes-fix-1.ipynb`) agar hasil aplikasi
identik dengan hasil pada notebook (sudah diverifikasi round-trip).

Inti aturan
-----------
Level A-D ditentukan dari kandungan **gula (dikurangi laktosa)**, **garam
(natrium, mg)**, dan **lemak jenuh** per 100 ml. Nilai per-100-ml dibulatkan
1 desimal lebih dulu, baru dipetakan ke level; level akhir produk = komponen
**terburuk** (paling tinggi). Lapis ke-2 (edukasi): % batas konsumsi harian
(Permenkes 30/2013) per kemasan utuh.

Catatan:
- field ``garam`` di seluruh pipeline berarti **NATRIUM (mg)**.
- field ``lemak`` adalah **lemak total** (hanya dipakai utk lapis-2 % AKG),
  sedangkan komponen Nutri-Level memakai **lemak_jenuh**.
"""

from __future__ import annotations
import re

# ===================================================================================
# Ambang batas Nutri-Level (batas atas band A, B, C; di atas C -> D), per 100 ml.
#   Zat gizi            A          B               C                 D
#   Gula (g)          <= 1.0    >1 - 5         >5 - 10           > 10
#   Garam/natrium(mg) <= 5      >5 - 120       >120 - 500        > 500
#   Lemak jenuh (g)   <= 0.7    >0.7 - 1.2     >1.2 - 2.8        > 2.8
# ===================================================================================
NL_BATAS = {
    "gula":        (1.0, 5.0, 10.0),     # g
    "garam":       (5.0, 120.0, 500.0),  # mg natrium
    "lemak_jenuh": (0.7, 1.2, 2.8),      # g
}
NL_URUT = {"A": 0, "B": 1, "C": 2, "D": 3}

# Angka Kecukupan Gizi harian (Permenkes 30/2013) untuk lapis-2.
AKG_HARIAN = {"gula": 50.0, "natrium": 2000.0, "lemak": 67.0}   # gula/lemak g ; natrium mg
MG_NATRIUM_PER_G_GARAM = 400.0                                  # 2000 mg Na = 5 g garam NaCl


def natrium_mg_to_garam_g(mg):
    return None if mg is None else mg / MG_NATRIUM_PER_G_GARAM


# --- Kebijakan produk serbuk (takaran saji dalam GRAM) ---------------------------
# "seduh"        -> hitung per 100 ml minuman jadi memakai volume seduhan
#                   (kolom `volume_seduh` bila ada; jika tidak, ASUMSI
#                   VOLUME_SEDUH_DEFAULT ml/saji). Hasil = ESTIMASI + catatan.
# "skip"         -> level tidak dihitung (per 100 ml tak dapat diturunkan dari label).
# "per100g_proxy"-> per 100 g serbuk sebagai PROKSI KASAR (cenderung melebih-lebihkan).
SERBUK_POLICY = "seduh"
VOLUME_SEDUH_DEFAULT = 200                      # ml/saji (1 gelas, contoh Lampiran I PerBPOM 26/2021)
VOLUME_SEDUH_SENSITIVITAS = (150, 200, 250)     # ml: skenario uji ketahanan level


_NUM = re.compile(r"(-?\d+(?:[.,]\d+)?)")
_UNIT = re.compile(r"[a-zA-Z%]+")


def to_number(v):
    m = _NUM.search("" if v is None else str(v))
    return float(m.group(1).replace(",", ".")) if m else None


def unit_of(v):
    m = _UNIT.search("" if v is None else str(v))
    return m.group(0).lower() if m else ""


def _basis_volume(row):
    """Hierarki fallback untuk mendapatkan basis volume (ml) + jumlah saji/kemasan.

    1) takaran saji bersatuan ml                      (kasus normal)
    2) format 'jumlah per kemasan (X ml)'             (kemasan sekali konsumsi; saji=1)
    3) takaran ada tapi TANPA satuan -> heuristik: ml utk kemasan cair, g utk sachet
    4) tidak ada volume / satuan g (serbuk)           -> None (atau estimasi seduh)

    return: (vol_ml, sumber, sajian_efektif, catatan: list)
    """
    cat = []
    tk_n, tk_u = to_number(row.get("takaran")), unit_of(row.get("takaran"))
    jm_raw = row.get("jumlah_per_kemasan") or row.get("jumlah")
    jm_n, jm_u = to_number(jm_raw), unit_of(jm_raw)
    sajian = to_number(row.get("sajian"))
    jenis = str(row.get("jenis", "")).lower()

    if tk_n and not tk_u:                                    # (3) heuristik satuan kosong
        tk_u = "g" if "sachet" in jenis else "ml"
        cat.append(f"satuan takaran kosong -> diasumsikan {tk_u}")

    if tk_n and tk_u == "ml":
        return tk_n, "takaran_saji", (sajian if sajian else 1.0), cat
    if jm_n and jm_u == "ml":
        cat.append("memakai 'jumlah per kemasan' (kemasan sekali konsumsi)")
        return jm_n, "jumlah_per_kemasan", 1.0, cat

    if tk_n and tk_u == "g":
        vskn = to_number(row.get("_vol_seduh_skenario"))     # override dari analisis sensitivitas
        if vskn:
            cat.append(f"skenario sensitivitas: asumsi seduhan {vskn:g} ml/saji (ESTIMASI)")
            return vskn, "seduh_skenario", (sajian if sajian else 1.0), cat
        vlab = to_number(row.get("volume_seduh"))            # anotasi dari petunjuk penyajian label
        if vlab:
            cat.append(f"seduhan {vlab:g} ml/saji dari petunjuk penyajian label")
            return vlab, "seduh_label", (sajian if sajian else 1.0), cat
        if SERBUK_POLICY == "seduh":
            vd = float(VOLUME_SEDUH_DEFAULT)
            cat.append(f"ESTIMASI: asumsi seduhan {vd:g} ml/saji "
                       f"(jangkar: contoh Lampiran I PerBPOM 26/2021, 200 ml = 1 gelas; bukan nilai resmi)")
            return vd, "seduh_asumsi", (sajian if sajian else 1.0), cat
        if SERBUK_POLICY == "per100g_proxy":
            cat.append("PROKSI per 100 g serbuk (bukan per 100 ml siap-minum) -- hati-hati")
            return tk_n, "per100g_proxy", (sajian if sajian else 1.0), cat
        cat.append("serbuk (takaran dlm g): per 100 ml siap-minum tak dapat dihitung dari label")
        return None, None, (sajian if sajian else 1.0), cat

    if jm_n and jm_u == "g":                # kemasan SEKALI KONSUMSI berisi serbuk (X g) -> sajian = 1
        vskn = to_number(row.get("_vol_seduh_skenario"))
        if vskn:
            cat.append(f"serbuk sekali konsumsi ({jm_n:g} g/kemasan); skenario sensitivitas: seduhan {vskn:g} ml (ESTIMASI)")
            return vskn, "seduh_skenario", 1.0, cat
        vlab = to_number(row.get("volume_seduh"))
        if vlab:
            cat.append(f"serbuk sekali konsumsi ({jm_n:g} g/kemasan); seduhan {vlab:g} ml dari petunjuk penyajian label")
            return vlab, "seduh_label", 1.0, cat
        if SERBUK_POLICY == "seduh":
            vd = float(VOLUME_SEDUH_DEFAULT)
            cat.append(f"serbuk sekali konsumsi ({jm_n:g} g/kemasan); ESTIMASI: asumsi seduhan {vd:g} ml/saji "
                       f"(jangkar: contoh Lampiran I PerBPOM 26/2021, 200 ml = 1 gelas; bukan nilai resmi)")
            return vd, "seduh_asumsi", 1.0, cat
        cat.append("serbuk sekali konsumsi (g/kemasan): per 100 ml tidak dihitung (SERBUK_POLICY)")
        return None, None, 1.0, cat

    cat.append("volume basis tidak ditemukan pada label")
    return None, None, (sajian if sajian else 1.0), cat


def nl_level_zat(zat, per100):
    """Map nilai per 100 ml -> level, dgn pembulatan 1 desimal (Lampiran butir 8-9)."""
    if per100 is None:
        return None
    x = round(per100 + 1e-9, 1)
    a, b, c = NL_BATAS[zat]
    return "A" if x <= a else "B" if x <= b else "C" if x <= c else "D"


def nutri_level(row):
    """Hitung Nutri-Level dari satu baris field hasil baca model.

    row: dict dgn kunci takaran, sajian, jumlah_per_kemasan, gula, laktosa,
    lemak_jenuh, lemak, garam (=natrium mg).

    return: dict berisi per-zat level, level_akhir (terburuk), komponen penentu,
    nilai per 100 ml, lapis-2 (% batas harian per kemasan), dan catatan.
    """
    cat = []
    gula_t = to_number(row.get("gula"))
    laktosa = to_number(row.get("laktosa"))
    lj = to_number(row.get("lemak_jenuh"))
    natrium = to_number(row.get("garam"))          # field 'garam' = NATRIUM (mg)
    lemak_t = to_number(row.get("lemak"))          # lemak total: hanya utk lapis-2 AKG

    # --- konsistensi fisik: lemak jenuh tidak mungkin > lemak total ---
    # Jika lemak total terbaca 0, maka lemak jenuh pasti 0 (subset dari total).
    if lemak_t is not None and lemak_t == 0:
        if lj is None or lj > 0:
            cat.append("lemak total = 0 -> lemak jenuh dipaksa 0 (lemak jenuh subset lemak total)")
        lj = 0.0
    elif lemak_t is not None and lj is not None and lj > lemak_t:
        cat.append(f"lemak jenuh ({lj:g}) > lemak total ({lemak_t:g}) -> dibatasi ke lemak total")
        lj = lemak_t

    # --- koreksi laktosa (Lampiran butir 5) ---
    gula_lv = gula_t
    if gula_t is not None and laktosa is not None:
        gula_lv = max(gula_t - laktosa, 0.0)
        cat.append(f"gula utk level = gula_total - laktosa = {gula_t:g} - {laktosa:g} = {gula_lv:g} g")

    vol, sumber_vol, sajian, cat_v = _basis_volume(row)
    cat += cat_v
    per100, level = {}, {}
    if vol:
        for zat, val in (("gula", gula_lv), ("garam", natrium), ("lemak_jenuh", lj)):
            p = None if val is None else val / vol * 100.0
            per100[zat] = p
            lv = nl_level_zat(zat, p)
            if lv is not None:
                level[zat] = lv
        # lemak total per 100 ml (untuk tampilan saja; bukan penentu Nutri-Level)
        per100["lemak"] = None if lemak_t is None else lemak_t / vol * 100.0

    level_akhir, penentu = None, None
    if level:
        worst = max(level.values(), key=NL_URUT.get)
        kandidat = [z for z, lv in level.items() if lv == worst]
        # tie-break antar zat pada level sama: paling dekat ke batas D (rasio thd batas atas C)
        penentu = max(kandidat, key=lambda z: (per100[z] or 0) / NL_BATAS[z][2])
        level_akhir = worst
        if level_akhir == "A":
            cat.append("level A numerik; syarat 'tanpa BTP pemanis' perlu cek daftar komposisi")

    # --- lapis-2: % batas harian per KEMASAN UTUH (Permenkes 30/2013) ---
    f = (sajian or 1.0)
    kem = {
        "gula_g":     None if gula_t is None else gula_t * f,
        "natrium_mg": None if natrium is None else natrium * f,
        "lemak_g":    None if lemak_t is None else lemak_t * f,
    }
    pct = {
        "gula":    None if kem["gula_g"] is None else kem["gula_g"] / AKG_HARIAN["gula"] * 100,
        "natrium": None if kem["natrium_mg"] is None else kem["natrium_mg"] / AKG_HARIAN["natrium"] * 100,
        "lemak":   None if kem["lemak_g"] is None else kem["lemak_g"] / AKG_HARIAN["lemak"] * 100,
    }
    return {
        "vol_ml": vol, "sumber_volume": sumber_vol, "sajian_per_kemasan": f,
        "per100": per100, "level": level,
        "level_akhir": level_akhir, "penentu": penentu,
        "per_kemasan": kem, "pct_harian_kemasan": pct,
        "catatan": cat,
    }


def _is_serbuk(row):
    """Produk serbuk = takaran saji dalam gram (atau tanpa satuan tapi jenis sachet),
    ATAU tanpa takaran tetapi `jumlah_per_kemasan` dalam gram (sekali konsumsi)."""
    tk_n, tk_u = to_number(row.get("takaran")), unit_of(row.get("takaran"))
    if tk_n:
        if not tk_u:
            tk_u = "g" if "sachet" in str(row.get("jenis", "")).lower() else "ml"
        return tk_u == "g"
    jm_raw = row.get("jumlah_per_kemasan") or row.get("jumlah")
    return bool(to_number(jm_raw)) and unit_of(jm_raw) == "g"


def nutri_level_sensitivitas(row, volumes=None):
    """Analisis sensitivitas volume seduhan untuk produk SERBUK tanpa anotasi volume.

    nutri_level dihitung pada tiap asumsi volume (default 150/200/250 ml), lalu
    dirangkum apakah level akhirnya STABIL. Produk cair dihitung sekali saja.

    return: {per_volume, level_per_volume, stabil, level_rentang, serbuk_asumsi, utama}
    """
    volumes = list(volumes or VOLUME_SEDUH_SENSITIVITAS)
    serbuk_asumsi = _is_serbuk(row) and not to_number(row.get("volume_seduh"))
    per_volume = {}
    if serbuk_asumsi:
        for v in volumes:
            r = dict(row)
            r["_vol_seduh_skenario"] = f"{v} ml"
            per_volume[v] = nutri_level(r)
    else:
        c = nutri_level(row)
        for v in volumes:
            per_volume[v] = c
    level_per_volume = {v: per_volume[v]["level_akhir"] for v in volumes}
    ada = sorted({l for l in level_per_volume.values() if l}, key=NL_URUT.get)
    stabil = len(ada) <= 1
    level_rentang = (ada[0] if len(ada) == 1 else (f"{ada[0]}-{ada[-1]}" if ada else None))
    v_utama = VOLUME_SEDUH_DEFAULT if VOLUME_SEDUH_DEFAULT in per_volume else volumes[len(volumes) // 2]
    return {"per_volume": per_volume, "level_per_volume": level_per_volume,
            "stabil": stabil, "level_rentang": level_rentang,
            "serbuk_asumsi": serbuk_asumsi, "utama": per_volume[v_utama]}
