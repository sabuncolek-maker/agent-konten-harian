"""Simpan & baca riwayat (memory) agent dalam file JSON.

ATURAN KERAS #1 (pelajaran dari audit):
    Memory HANYA ditulis SETELAH publisher mengembalikan True.
    Jangan pernah mencatat "sudah diposting" untuk sesuatu yang belum terposting —
    kalau tidak, item itu tidak akan pernah dipilih lagi padahal belum tayang.

KENAPA pakai atomic write (tulis ke file .tmp dulu, baru rename):
    Kalau proses mati di tengah penulisan (listrik mati, OOM), file asli tetap
    utuh. Tanpa ini, memory.json bisa korup → agent lupa semua riwayat.
"""

import json
from pathlib import Path

PATH = Path("data/memory.json")
DEFAULT = {"used_subjects": [], "published": []}


def load_memory() -> dict:
    """Baca memory. Kalau file rusak/tidak ada → kembalikan default kosong."""
    if not PATH.exists():
        return {k: list(v) for k, v in DEFAULT.items()}
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        for key, value in DEFAULT.items():
            data.setdefault(key, list(value))
        return data
    except Exception as exc:
        # KENAPA tidak crash: lebih baik mulai dari memory kosong daripada
        # seluruh run gagal hanya karena file riwayat korup.
        print(f"[MEMORY] memory.json rusak ({exc}); pakai memory kosong.", flush=True)
        return {k: list(v) for k, v in DEFAULT.items()}


def save_memory(memory: dict) -> None:
    """Simpan memory secara atomic. Panggil HANYA setelah publish sukses."""
    PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(PATH)  # rename itu atomic di hampir semua filesystem
    print("[MEMORY] tersimpan.", flush=True)


def already_used(memory: dict, subject: str) -> bool:
    """Cek apakah subjek sudah pernah dipakai (anti-duplikat)."""
    return subject.strip().lower() in [s.lower() for s in memory["used_subjects"]]


def mark_published(memory: dict, niche: str, subject: str) -> None:
    """Catat subjek sebagai sudah dipublikasikan.

    KENAPA dipisah jadi fungsi sendiri: supaya di orchestrator terlihat jelas
    bahwa pencatatan ini terjadi SETELAH publish sukses — bukan sebelumnya.
    """
    memory["used_subjects"].append(subject)
    memory["published"].append({"niche": niche, "subject": subject})
