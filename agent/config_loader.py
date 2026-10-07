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

    _validate_optional_fields(cfg, path)
    return cfg


def _validate_optional_fields(cfg: dict, path: str) -> None:
    """Validasi field opsional yang ditambahkan belakangan.

    KENAPA ini ada (pelajaran audit): field baru seperti research.mood atau
    quotes.scope sebelumnya tidak divalidasi — typo (misal "scop") tidak
    ketahuan dan diam-diam memakai nilai default. Sekarang typo = error jelas.
    """
    mood = cfg.get("research", {}).get("mood")
    if mood and mood not in ("serius", "ringan", "campuran"):
        raise ValueError(
            f"Config {path}: research.mood '{mood}' tidak valid. "
            "Pilih: serius, ringan, campuran."
        )

    retries = cfg.get("verification", {}).get("max_retries")
    if retries is not None and (not isinstance(retries, int) or retries < 0):
        raise ValueError(
            f"Config {path}: verification.max_retries harus angka bulat >= 0."
        )

    scope = cfg.get("quotes", {}).get("scope")
    if scope and scope not in ("indonesia", "internasional", "campuran"):
        raise ValueError(
            f"Config {path}: quotes.scope '{scope}' tidak valid. "
            "Pilih: indonesia, internasional, campuran."
        )

    max_tokens = cfg.get("llm", {}).get("max_tokens")
    if max_tokens is not None and (
        not isinstance(max_tokens, int) or max_tokens <= 0
    ):
        raise ValueError(
            f"Config {path}: llm.max_tokens harus angka bulat > 0."
        )

    tone = cfg.get("style", {}).get("tone")
    if tone is not None and not str(tone).strip():
        raise ValueError(f"Config {path}: style.tone tidak boleh kosong.")
