"""Menilai kualitas konten dengan skor 0-100.

KENAPA ada tahap ini: LLM kadang menghasilkan konten yang datar, terlalu
panjang, atau tidak cocok untuk Instagram. Daripada posting asal-asalan,
lebih baik dinilai dulu — kalau skor < 75, orchestrator akan minta generate
ulang (maksimal sesuai config).
"""

from agent import brain


def evaluate(state, cfg) -> int:
    """Kembalikan skor 0-100 untuk konten di state."""
    full_text = "\n".join(state.slides)
    prompt = (
        "Kamu adalah editor media sosial yang ketat. Nilai konten carousel "
        "Instagram berikut dengan skor 0-100.\n\n"
        "Kriteria:\n"
        "- Hook slide 1 memancing penasaran (0-30)\n"
        "- Bahasa sederhana & cocok untuk audiens Indonesia (0-25)\n"
        "- Struktur jelas, tidak bertele-tele (0-25)\n"
        "- Ada ajakan interaksi/follow di akhir (0-20)\n\n"
        f"TEKS:\n{full_text}\n\nCAPTION:\n{state.caption}\n\n"
        "Jawab HANYA JSON valid:\n"
        '{"score": <angka 0-100>, "feedback": "<1 kalimat saran perbaikan>"}'
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"], temperature=0.3,
                    max_tokens=400)
    import json
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        # KENAPA default 0: kalau evaluator gagal, jangan asal lolos.
        # Lebih aman dianggap gagal → orchestrator akan coba lagi / batalkan.
        print("[EVAL] evaluator tidak mengembalikan JSON → skor 0", flush=True)
        return 0
    try:
        data = json.loads(raw[start:end + 1])
        score = int(data.get("score", 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        print("[EVAL] JSON evaluator tidak valid → skor 0", flush=True)
        return 0
    score = max(0, min(100, score))  # jaga-jaga kalau LLM ngasih 150 / -5
    print(f"[EVAL] skor: {score} | {data.get('feedback','')}", flush=True)
    return score
