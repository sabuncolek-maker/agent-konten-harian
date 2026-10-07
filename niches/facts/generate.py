"""Tahap GENERATE untuk niche fakta unik."""

from agent import brain


def run(state, cfg, memory) -> None:
    max_slides = cfg["content"]["max_slides"]
    prompt = (
        "Kamu adalah content writer Instagram Indonesia.\n"
        f"Fakta: {state.topic}\nSubjek: {state.subject}\n\n"
        f"Buat carousel {max_slides} slide yang menjelaskan fakta ini dengan "
        "bahasa sederhana dan memancing rasa penasaran. Slide 1 = hook. "
        "Slide terakhir = ajakan follow.\n\n"
        "Jawab HANYA JSON valid:\n"
        '{"slides": ["<teks slide 1>", ...], "caption": "<caption + hashtag>"}'
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"],
                    temperature=cfg["llm"]["temperature"],
                    max_tokens=cfg["llm"]["max_tokens"])
    data = _parse_json(raw, ["slides", "caption"])
    slides = [s for s in data["slides"] if isinstance(s, str) and s.strip()]
    if len(slides) < 2:
        raise ValueError(f"LLM hanya mengembalikan {len(slides)} slide, minimal 2.")
    state.slides = slides[:max_slides]
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
