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

    # Exit code 0 = run selesai normal (termasuk konten ditolak verifikasi).
    # Exit code 1 = error tak terduga. KENAPA dibedakan: supaya GitHub Actions
    # bisa membedakan "tidak ada konten hari ini (normal)" vs "ada yang rusak".
    return 0 if not state.error or "ditolak" in state.error.lower() or "gagal" in state.error.lower() else 1


if __name__ == "__main__":
    sys.exit(main())
