import json
import time
from agent.brain import ask, VERIFICATION_MODEL
from tools.research import web_search


def verify_quote(person: str, quote: str, source_hint: str = "") -> str:
    queries = [
        f'"{quote}" "{person}"',
        f'"{person}" "{quote}" interview',
        f'"{person}" "{quote}" speech',
        f'"{person}" interview exact quote',
    ]
    evidence, seen = [], set()
    started = time.monotonic()
    print(f"[VERIFY] START | {person} | {quote}", flush=True)

    for query in queries:
        for item in web_search(query, 6):
            if item["url"] not in seen:
                seen.add(item["url"])
                evidence.append(item)

    if not evidence:
        result = {"status": "UNCERTAIN", "confidence": 0, "evidence": [], "source": "", "url": "", "reason": "Tidak ada bukti web."}
        print(f"[VERIFY] DONE {time.monotonic()-started:.1f}s | UNCERTAIN", flush=True)
        return json.dumps(result, ensure_ascii=False)

    compact = "\n".join(
        f"[{i}] {x['title']} | {x['snippet']} | {x['url']}"
        for i, x in enumerate(evidence[:20], 1)
    )
    raw = ask(f"""Fact-check kutipan secara konservatif.
TOKOH: {person}
QUOTE: {quote}
SUMBER AWAL: {source_hint}

BUKTI WEB:
{compact}

VERIFIED hanya jika bukti cukup kuat bahwa tokoh benar-benar mengucapkan atau menulis kata-kata tersebut.
Parafrase, quote-site, repost tanpa sumber, atau snippet yang hanya kebetulan cocok = UNCERTAIN.
Banyak situs yang menyalin sumber yang sama bukan bukti independen.
REJECTED hanya bila ada bukti kuat bahwa atribusinya salah.

Jawab JSON VALID saja:
{{"status":"VERIFIED|UNCERTAIN|REJECTED","confidence":0,"evidence":"...","source":"...","url":"...","reason":"..."}}""", model=VERIFICATION_MODEL, max_tokens=800)

    try:
        data = json.loads(raw)
        status = str(data.get("status", "UNCERTAIN")).upper()
        if status not in {"VERIFIED", "UNCERTAIN", "REJECTED"}:
            status = "UNCERTAIN"
        data["status"] = status
    except Exception:
        data = {"status": "UNCERTAIN", "confidence": 0, "evidence": [], "source": "", "url": "", "reason": "Verifier tidak menghasilkan JSON valid."}

    print(f"[VERIFY] DONE {time.monotonic()-started:.1f}s | {data['status']}", flush=True)
    return json.dumps(data, ensure_ascii=False)
