"""Tahap GENERATE untuk niche kutipan.

Tugas: buat draf carousel (beberapa slide) + caption dari topik & tokoh
yang dipilih tahap research. Jumlah slide DINAMIS mengikuti config.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    """Generate slide-slide carousel dan caption."""
    max_slides = cfg["content"]["max_slides"]

    prompt = (
        f"Kamu adalah content writer Instagram Indonesia.\n"
        f"Topik: {state.topic}\nTokoh: {state.subject}\n\n"
        f"Buat carousel {max_slides} slide tentang pemikiran {state.subject} "
        f"yang relevan dengan topik di atas. Slide 1 = hook yang memancing rasa "
        f"penasaran. Slide terakhir = ajakan follow/refleksi.\n\n"
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
