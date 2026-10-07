"""Titik masuk agent.

Cara pakai:
    python main.py --config config/quotes.yaml   # niche kutipan
    python main.py --config config/facts.yaml    # niche fakta unik

KENAPA pakai argumen --config (bukan hardcode):
- Satu kode untuk semua niche. Mau jalanin niche lain? Ganti argumen saja.
- GitHub Actions bisa menjadwalkan tiap niche sebagai job terpisah.
"""

import argparse
import sys

from agent.orchestrator import run


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Content Agent multi-niche")
    parser.add_argument(
        "--config", required=True,
        help="Path file config niche, misal: config/quotes.yaml",
    )
    args = parser.parse_args()

    state = run(args.config)

    print("\n=== HASIL AGENT ===")
    print(f"Niche      : {state.niche}")
    print(f"Subjek     : {state.subject}")
    print(f"Verifikasi : {state.verification}")
    print(f"Skor       : {state.score}")
    print(f"Terbit     : {'YA ✅' if state.published else 'TIDAK ❌'}")
    if state.error:
        print(f"Catatan    : {state.error}")

    # Exit code 0 = run selesai normal: sukses ATAU verifikasi ditolak
    # (tidak ada konten hari ini = kondisi normal, bukan error).
    # Exit code 1 = ada yang perlu perhatian: publish gagal, skor rendah,
    # atau error tak terduga. KENAPA "gagal" sekarang = 1: sebelumnya kata
    # "gagal" ikut dianggap sukses, sehingga "Publish gagal" tidak terlihat
    # sebagai kegagalan di GitHub Actions (bug yang ditemukan saat audit).
    return 0 if not state.error or "ditolak" in state.error.lower() else 1


if __name__ == "__main__":
    sys.exit(main())
