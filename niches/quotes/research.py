"""Tahap RESEARCH untuk niche kutipan.

Tugas: pilih SATU isu/topik Indonesia yang sedang relevan + tokoh yang cocok.
Output disimpan ke state.topic dan state.subject.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    """Pilih kutipan dari bank terverifikasi (bukan dari LLM).

    KENAPA dari bank: LLM terbukti tidak bisa diandalkan untuk mengingat
    kutipan verbatim — 3 tokoh berbeda semua gagal verifikasi karena salah
    atribusi (John Dewey dikira Ki Hajar Dewantara, parafrasa diklaim asli).
    Bank berisi kutipan yang sudah dipastikan benar, jadi tahap generate
    tinggal membungkusnya dengan slide yang menarik.
    """
    import json
    import os
    import random

    # Baca scope dari config: indonesia | internasional | campuran
    scope = cfg.get("quotes", {}).get("scope", "campuran").strip().lower()

    # Cari file bank (relatif terhadap root repo)
    bank_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "data", "quotes_verified.json")
    with open(bank_path, encoding="utf-8") as f:
        bank = json.load(f)

    # Filter scope
    if scope in ("indonesia", "internasional"):
        pool = [q for q in bank if q["scope"] == scope]
    else:  # campuran atau tidak dikenal → semua
        pool = bank
    if scope == "campuran":
        print(f"[RESEARCH] scope: campuran ({len(pool)} kutipan)", flush=True)
    else:
        print(f"[RESEARCH] scope: {scope} ({len(pool)} kutipan)", flush=True)

    # Hindari yang sudah pernah dipakai (memory) + ditolak di run ini
    used = set(s.lower() for s in memory.get("used_subjects", []))
    rejected = set(s.lower() for s in getattr(state, "rejected_subjects", []))
    # KENAPA hindari per kutipan (bukan per tokoh): satu tokoh bisa punya
    # beberapa kutipan di bank, jadi yang dihindari adalah kutipan spesifik.
    used_quotes = set(s.lower() for s in memory.get("used_quotes", []))
    candidates = [q for q in pool
                  if q["quote"].lower() not in used_quotes
                  and q["figure"].lower() not in rejected]
    if not candidates:
        # Semua sudah dipakai → reset, pakai semua lagi kecuali yang ditolak
        print("[RESEARCH] semua kutipan sudah pernah dipakai, mulai dari awal",
              flush=True)
        candidates = [q for q in pool if q["figure"].lower() not in rejected]
    if not candidates:
        raise RuntimeError("Tidak ada kutipan tersisa di bank untuk scope ini.")

    pick = random.choice(candidates)
    state.topic = pick.get("theme", "")
    state.subject = pick["figure"]
    # Simpan data kutipan untuk dipakai tahap generate & verify
    state.verified_quote = pick["quote"]
    state.quote_honorific = pick.get("honorific", pick["figure"])
    state.quote_context = pick.get("context", "")
    # Tandai kutipan ini sudah dipakai agar tidak diulang
    used_quotes.add(pick["quote"].lower())
    memory["used_quotes"] = sorted(used_quotes)
    print(f"[RESEARCH] kutipan: {pick['figure']} — \"{pick['quote'][:60]}...\"",
          flush=True)


def _parse_json(raw: str, required_keys: list) -> dict:
    """Ambil JSON dari jawaban LLM dan pastikan key yang dibutuhkan ada.

    ATURAN KERAS #3: validasi dulu, jangan langsung akses key.
    KENAPA: LLM kadang menjawab tanpa JSON / key tidak lengkap → tanpa validasi
    ini program crash dengan KeyError yang membingungkan.
    """
    import json
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"LLM tidak mengembalikan JSON. Jawaban: {raw[:200]}")
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON dari LLM tidak valid: {exc}. Jawaban: {raw[:200]}")
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"JSON LLM kehilangan key: {missing}. Dapat: {list(data.keys())}")
    return data
