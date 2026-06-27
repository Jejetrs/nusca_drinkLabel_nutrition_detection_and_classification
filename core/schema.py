"""
core/schema.py
==============
Skema serialisasi/parse output model — HARUS sama dengan saat training agar
output decoder Donut/TrOCR terbaca benar.

Donut menghasilkan urutan bertag, mis:
    <s_gizi><s_takaran>250 ml</s_takaran><s_gula>19 g</s_gula>...</s_gizi>
TrOCR menghasilkan urutan flat, mis:
    takaran: 250 ml | gula: 19 g | garam: 20 mg
"""

from __future__ import annotations
import re

from config import TARGET_FIELDS, TASK_START, TASK_END

# Pemetaan kolom CSV (training) -> kunci internal. Hanya kunci dlm TARGET_FIELDS.
_FIELDS_ALL = [
    ("takaran_Saji", "takaran"), ("sajian_per_kemasan", "sajian"),
    ("jumlah_per_kemasan", "jumlah_per_kemasan"),
    ("energi_total", "energi"), ("lemak_total", "lemak"), ("lemak_jenuh", "lemak_jenuh"),
    ("protein", "protein"), ("karbohidrat_total", "karbohidrat"), ("serat", "serat"),
    ("gula_total", "gula"), ("sukrosa", "sukrosa"), ("Laktosa", "laktosa"),
    ("garam", "garam"),
]
KEYS = [k for _, k in _FIELDS_ALL if k in TARGET_FIELDS]

REC_SEP, KV_SEP = " | ", ": "


def _norm_val(v: str) -> str:
    return re.sub(r"\s+", " ", (v or "").strip())


def parse_flat(s: str) -> dict:
    """Parse urutan flat (TrOCR) -> dict {key: value}."""
    out = {}
    for part in (s or "").split(REC_SEP):
        if KV_SEP in part:
            k, v = part.split(KV_SEP, 1)
            k, v = k.strip(), _norm_val(v)
            if k in KEYS and v:
                out[k] = v
    return out


def parse_donut(s: str) -> dict:
    """Parse urutan bertag (Donut) -> dict {key: value}."""
    out = {}
    for k in KEYS:
        m = re.search(rf"<s_{k}>(.*?)</s_{k}>", s, flags=re.S)
        if m and _norm_val(m.group(1)):
            out[k] = _norm_val(m.group(1))
    return out


def clean_donut_seq(seq: str, tokenizer=None) -> str:
    """Bersihkan token spesial dari output mentah Donut sebelum parse."""
    specials = [TASK_START, TASK_END]
    if tokenizer is not None:
        specials += [tokenizer.eos_token, tokenizer.pad_token]
    for t in specials:
        if t:
            seq = seq.replace(t, "")
    return seq
