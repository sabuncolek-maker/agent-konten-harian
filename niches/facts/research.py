"""Tahap RESEARCH untuk niche fakta unik.

Tugas: pilih SATU fakta menarik tentang flora/fauna/alam Indonesia.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    used = [s.lower() for s in memory["used_subjects"]]
    prompt = (
        "Kamu adalah editor konten edukasi Indonesia. "
        "Pilih SATU fakta unik yang benar-benar ada tentang flora, fauna, "
        "atau fenomena alam Indonesia (misal: hewan endemik, tumbuhan langka). "
        "Fakta harus spesifik, bukan opini.\n\n"
        "Jawab HANYA JSON valid:\n"
        '{"fact": "<fakta dalam 1 kalimat>", "subject": "<nama hewan/tumbuhan/fenomena>"}'
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"],
                    temperature=cfg["llm"]["temperature"])
    data = _parse_json(raw, ["fact", "subject"])

    for _ in range(3):  # anti-duplikat, sama seperti niche quotes
        if data["subject"].strip().lower() not in used:
            break
        raw = brain.ask(
            prompt + f"\n\nPENTING: jangan pilih {data['subject']}, sudah pernah dipakai.",
            model=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"],
        )
        data = _parse_json(raw, ["fact", "subject"])

    state.topic = data["fact"]
    state.subject = data["subject"]
    print(f"[RESEARCH] fakta: {state.topic}", flush=True)


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
