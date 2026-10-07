"""Tahap RESEARCH untuk niche kutipan.

Tugas: pilih SATU isu/topik Indonesia yang sedang relevan + tokoh yang cocok.
Output disimpan ke state.topic dan state.subject.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    """Pilih topik & tokoh. Melewati tokoh yang sudah pernah dipakai."""
    import random
    used = [s.lower() for s in memory["used_subjects"]]
    # Ide A: hindari juga tokoh yang ditolak verifikasi di run ini.
    # KENAPA: tanpa ini, retry bisa memilih tokoh yang sama berulang-ulang.
    rejected = [s.lower() for s in getattr(state, "rejected_subjects", [])]
    banned = used + rejected

    # Baca mood dari config (default: serius, sesuai perilaku lama).
    # KENAPA ada mood: tidak semua hari cocok untuk topik berat — kadang
    # konten ringan/fun lebih cocok untuk akun pribadi.
    mood = cfg.get("research", {}).get("mood", "serius").strip().lower()
    if mood == "campuran":
        mood = random.choice(["serius", "ringan"])
    print(f"[RESEARCH] mood: {mood}", flush=True)

    if mood == "ringan":
        brief = (
            "Pilih SATU topik RINGAN dan fun seputar tokoh Indonesia: kisah unik, "
            "fakta menarik, kebiasaan lucu, atau pelajaran hidup yang ringan dan "
            "menghibur. Hindari isu berat/politik/konflik. "
        )
    else:  # serius
        brief = (
            "Pilih SATU isu sosial/masyarakat Indonesia yang sedang relevan saat ini. "
        )

    prompt = (
        "Kamu adalah riset editor media Indonesia. "
        + brief +
        "lalu pilih SATU tokoh Indonesia (pahlawan, budayawan, ulama, ilmuwan, "
        "atau negarawan) yang pemikirannya relevan dengan topik itu.\n\n"
        "Jawab HANYA dalam format JSON valid, tanpa teks lain:\n"
        '{"topic": "<topik dalam 1 kalimat>", "person": "<nama tokoh>", '
        '"reason": "<kenapa relevan, 1 kalimat>"}'
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"],
                    temperature=cfg["llm"]["temperature"])

    data = _parse_json(raw, ["topic", "person"])

    # Anti-duplikat: kalau tokoh sudah dipakai, minta LLM pilih yang lain (maks 3x).
    # KENAPA: tanpa ini, agent bisa posting tokoh yang sama berulang-ulang.
    for _ in range(3):
        if data["person"].strip().lower() not in banned:
            break
        raw = brain.ask(
            prompt + f"\n\nPENTING: jangan pilih {data['person']}, sudah pernah dipakai. Pilih tokoh lain.",
            model=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"],
        )
        data = _parse_json(raw, ["topic", "person"])

    state.topic = data["topic"]
    state.subject = data["person"]
    print(f"[RESEARCH] topik: {state.topic} | tokoh: {state.subject}", flush=True)


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
