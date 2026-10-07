"""Tahap GENERATE untuk niche kutipan.

Tugas: buat draf carousel (beberapa slide) + caption dari topik & tokoh
yang dipilih tahap research. Jumlah slide DINAMIS mengikuti config.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    """Generate slide-slide carousel dan caption."""
    max_slides = cfg["content"]["max_slides"]

    # ATURAN KERAS #5: kutipan harus ASLI, bukan karangan.
    # KENAPA: LLM suka mengarang kutipan yang terdengar meyakinkan tapi palsu
    # (halusinasi) — apalagi kalau diminta membuat kutipan tokoh lama tentang
    # topik modern. Verifier akan menolaknya dan run jadi sia-sia.
    # Solusi: pakai kutipan asli yang memang dikenal luas, lalu KAITKAN ke
    # topik modern lewat penjelasan di slide — bukan dengan mengarang kutipan baru.
    # Ambil kutipan terverifikasi dari state (diisi tahap research dari bank).
    # KENAPA tidak minta LLM bikin kutipan: LLM terbukti mengarang atribusi.
    quote = getattr(state, "verified_quote", "")
    honorific = getattr(state, "quote_honorific", state.subject)
    qcontext = getattr(state, "quote_context", "")
    if not quote:
        raise RuntimeError("Tidak ada kutipan terverifikasi di state. Research gagal?")
    prompt = (
        f"Kamu adalah content writer Instagram Indonesia.\n"
        f"KUTIPAN ASLI (JANGAN diubah, JANGAN diparafrasa, tulis persis seperti ini):\n"
        f"\"{quote}\" — {honorific}\n"
        f"Konteks kutipan: {qcontext}\n"
        f"Tema: {state.topic}\n\n"
        f"Buat carousel {max_slides} slide tentang {state.subject}.\n"
        f"ATURAN WAJIB:\n"
        f"1. Kutipan di atas SUDAH terverifikasi benar — tulis PERSIS seperti itu, "
        f"jangan diubah atau diparafrasa.\n"
        f"2. Slide 1 = hook yang memancing rasa penasaran (jangan langsung "
        f"tampilkan kutipannya).\n"
        f"3. Slide 2 = tampilkan kutipan persis + nama {honorific}.\n"
        f"4. Slide 3-4 = jelaskan makna kutipan dan kaitannya dengan kehidupan "
        f"sehari-hari, dengan bumbu puitis/filosofis/humor yang sopan.\n"
        f"5. Slide terakhir = ajakan follow/refleksi yang ringan.\n\n"
        "Jawab HANYA JSON valid, tanpa teks lain:\n"
        '{"slides": ["<teks slide 1>", "<teks slide 2>", ...], '
        '"caption": "<caption Instagram + 3 hashtag>"}'
    )
    # Ambil gaya bahasa dari config (cfg["style"]["tone"]).
    # KENAPA pakai .get(): kalau config lama tidak punya bagian "style",
    # kode tetap jalan tanpa error — tone jadi string kosong.
    tone = cfg.get("style", {}).get("tone", "").strip()
    if tone:
        prompt = f"Gaya bahasa yang WAJIB dipakai:\n{tone}\n\n" + prompt
    raw = brain.ask(prompt, model=cfg["llm"]["model"],
                    temperature=cfg["llm"]["temperature"],
                    max_tokens=cfg["llm"]["max_tokens"])

    data = _parse_json(raw, ["slides", "caption"])

    # ATURAN KERAS #4: jangan hardcode jumlah slide.
    # KENAPA: kalau LLM mengembalikan 4 slide padahal config minta 5, kode yang
    # hardcode slide_1..slide_5 akan error. Kita pakai apa pun yang diberikan,
    # asal minimal 2 slide (syarat carousel).
    slides = [s for s in data["slides"] if isinstance(s, str) and s.strip()]
    if len(slides) < 2:
        raise ValueError(f"LLM hanya mengembalikan {len(slides)} slide, minimal 2.")

    state.slides = slides[:max_slides]  # potong kalau kebanyakan, jangan error
    state.caption = data["caption"]
    print(f"[GENERATE] {len(state.slides)} slide dibuat.", flush=True)


def _parse_json(raw: str, required_keys: list) -> dict:
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
