"""Membaca & memvalidasi file konfigurasi niche (YAML).

KENAPA ada file ini:
- Semua "keputusan" tentang niche (model LLM, jumlah slide, dsb) tinggal di file
  config, BUKAN di dalam kode. Akibatnya: ganti niche = ganti file config saja.
- Validasi di sini memastikan config yang rusak terdeteksi AWAL, sebelum agent
  jalan setengah lalu crash di tengah (buang-buang token & waktu).
"""

import yaml
from pathlib import Path

# Daftar key yang WAJIB ada di setiap config. Kalau kurang satu saja → error jelas.
REQUIRED_KEYS = ["niche", "llm", "pipeline", "content", "evaluation", "memory"]


def load_config(path: str) -> dict:
    """Baca file YAML dan pastikan strukturnya valid.

    Args:
        path: lokasi file config, misal "config/quotes.yaml"

    Returns:
        dict berisi konfigurasi yang sudah divalidasi.

    Raises:
        FileNotFoundError: kalau file config tidak ada.
        ValueError: kalau ada key wajib yang hilang (pesan error menyebut key-nya).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"File config tidak ditemukan: {path}. "
            f"Contoh yang valid: config/quotes.yaml"
        )

    with open(p, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Validasi: semua key wajib harus ada.
    # KENAPA: lebih baik gagal di sini dengan pesan jelas, daripada crash
    # misterius di tengah pipeline karena cfg["pipeline"] ternyata tidak ada.
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        raise ValueError(
            f"Config {path} tidak valid. Key yang hilang: {missing}. "
            f"Key wajib: {REQUIRED_KEYS}"
        )

    if not cfg["pipeline"]:
        raise ValueError(f"Config {path}: 'pipeline' tidak boleh kosong.")

    return cfg
