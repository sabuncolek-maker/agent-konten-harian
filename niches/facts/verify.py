"""Tahap VERIFY untuk niche fakta unik.

KENAPA: LLM bisa mengarang "fakta" yang terdengar ilmiah tapi salah
(misal: mengklaim hewan yang tidak ada). Verifikator skeptis menilai
apakah fakta ini masuk akal secara biologis/geografis. Ragu = tolak.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    full_text = "\n".join(state.slides)
    prompt = (
        "Kamu adalah fact-checker sains yang SKEPTIS. Periksa apakah fakta "
        "berikut masuk akal secara ilmiah dan geografis (spesies benar-benar "
        "ada, lokasi sesuai habitat aslinya, tidak ada klaim mustahil).\n\n"
        f"SUBJEK: {state.subject}\nTEKS:\n{full_text}\n\n"
        "Jawab HANYA JSON valid:\n"
        '{"verdict": "VERIFIED" atau "REJECTED", "reason": "<1 kalimat>"}'
        "\nAturan: kalau tidak yakin 100%, jawab REJECTED."
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"], temperature=0.2,
                    max_tokens=500)
    import json
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        state.verification = "REJECTED: verifikator tidak mengembalikan JSON"
        return
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        state.verification = "REJECTED: JSON verifikator tidak valid"
        return
    verdict = str(data.get("verdict", "")).upper()
    reason = data.get("reason", "tanpa alasan")
    if verdict == "VERIFIED":
        state.verification = "VERIFIED"
        print(f"[VERIFY] lolos: {reason}", flush=True)
    else:
        state.verification = f"REJECTED: {reason}"
        print(f"[VERIFY] DITOLAK: {reason}", flush=True)
