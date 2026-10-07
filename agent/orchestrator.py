"""Konduktor utama: membaca config → memilih pipeline niche → menjalankan
tahap demi tahap dengan error handling yang jelas.

Urutan:
  research → generate → verify → evaluate (coba ulang maks N kali)
  → render gambar → publish → simpan memory (HANYA jika publish sukses)

KENAPA niche di-import dinamis (importlib):
- Orchestrator tidak perlu tahu daftar niche apa saja yang ada.
- Tambah niche baru = cukup bikin folder niches/<nama>/ + config — file ini
  TIDAK PERLU diubah sama sekali.
"""

import importlib

from agent import config_loader, memory
from agent.state import AgentState
from tools import evaluator, image as image_tool, publisher


def _load_niche_module(niche: str, step: str):
    """Import niches.<niche>.<step> secara dinamis."""
    try:
        return importlib.import_module(f"niches.{niche}.{step}")
    except ImportError as exc:
        raise RuntimeError(
            f"Niche '{niche}' tidak punya modul '{step}.py'. "
            f"Buat file niches/{niche}/{step}.py dulu."
        ) from exc


def run(config_path: str) -> AgentState:
    """Jalankan satu siklus agent penuh. Kembalikan state akhir."""
    cfg = config_loader.load_config(config_path)
    niche = cfg["niche"]
    state = AgentState(niche=niche)
    mem = memory.load_memory()

    try:
        # --- Tahap pipeline sesuai config (research/generate/verify) ---
        for step in cfg["pipeline"]:
            mod = _load_niche_module(niche, step)
            mod.run(state, cfg, mem)
            # Verifikasi bisa menolak konten → hentikan run ini dengan aman.
            if step == "verify" and state.verification.startswith("REJECTED"):
                state.error = f"Konten ditolak verifikasi: {state.verification}"
                print(f"[ORCHESTRATOR] {state.error}", flush=True)
                return state  # return, BUKAN crash — ini hasil yang valid

        # --- Evaluasi + coba ulang generate kalau skor kurang ---
        min_score = cfg["evaluation"]["min_score"]
        max_retries = cfg["evaluation"]["max_retries"]
        for attempt in range(max_retries + 1):
            state.score = evaluator.evaluate(state, cfg)
            if state.score >= min_score:
                break
            if attempt < max_retries:
                print(f"[ORCHESTRATOR] skor {state.score} < {min_score}, "
                      f"coba generate ulang ({attempt + 1}/{max_retries})", flush=True)
                gen_mod = _load_niche_module(niche, "generate")
                gen_mod.run(state, cfg, mem)
        else:
            # KENAPA pakai for-else: blok ini jalan kalau loop habis TANPA break,
            # artinya semua percobaan gagal mencapai skor minimal.
            state.error = f"Skor maksimal {state.score} < {min_score} setelah {max_retries}x coba."
            print(f"[ORCHESTRATOR] {state.error}", flush=True)
            return state

        # --- Render gambar (jumlah slide dinamis dari state.slides) ---
        label = {"quotes": "KUTIPAN", "facts": "FAKTA UNIK"}.get(niche, niche.upper())
        image_paths = image_tool.render_slides(state.slides, label)

        # --- Publish ---
        published = publisher.publish_carousel(image_paths, state.caption)
        state.published = published

        # --- ATURAN KERAS #1: simpan memory HANYA jika publish sukses ---
        # KENAPA: kalau dicatat sebelum sukses, item yang gagal tayang tidak
        # akan pernah dipilih lagi (dianggap sudah tayang) — data jadi bohong.
        if published:
            memory.mark_published(mem, niche, state.subject)
            memory.save_memory(mem)
        else:
            state.error = "Publish gagal, memory TIDAK disimpan (subjek bisa dicoba lagi besok)."

    except Exception as exc:
        # KENAPA tangkap di sini: supaya run yang gagal tetap menghasilkan
        # state yang informatif (bukan traceback mentah di log GitHub Actions).
        state.error = f"{type(exc).__name__}: {exc}"
        print(f"[ORCHESTRATOR] ERROR: {state.error}", flush=True)

    return state
