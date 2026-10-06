import json

from agent.brain import ask, FAST_MODEL


def choose_topic(goal, evidence, used):
    compact = "\n".join(
        f"[{i}] {x['title']} | {x.get('snippet','')} | {x['url']}"
        for i, x in enumerate(evidence, 1)
    )
    raw = ask(
        f"""Pilih satu kondisi/isu aktual Indonesia yang paling relevan untuk konten quote.
Tujuan: {goal}
Topik yang sudah dipakai: {used}
Gunakan hanya bukti berita di bawah. Jangan mengarang fakta, tanggal, tokoh, atau URL.
Pilih isu yang cukup jelas untuk dijelaskan dalam satu konten.
Jawab JSON saja:
{{"topic":"","context":"","facts":[],"source_urls":[]}}
BUKTI BERITA:
{compact}""",
        FAST_MODEL,
        900,
    )
    data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
    return data["topic"].strip(), json.dumps(data, ensure_ascii=False)
