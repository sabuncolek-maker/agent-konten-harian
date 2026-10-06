from agent.brain import ask, VERIFICATION_MODEL
from tools.research import web_search

def verify_quote(person: str, quote: str, source_hint: str = "") -> str:
    queries = [
        f'"{quote}" "{person}"',
        f'"{person}" "{quote}" interview',
        f'"{person}" "{quote}" book speech',
    ]
    evidence = []
    for query in queries:
        try:
            evidence.extend(web_search(query, 5))
        except Exception:
            continue

    web_evidence = "\n".join(
        f"- {r['title']} | {r['snippet']} | {r['url']}" for r in evidence[:15]
    )

    return ask(f"""Fact-check kutipan secara ketat.

TOKOH: {person}
QUOTE: {quote}
SUMBER AWAL: {source_hint}

Bukti web yang ditemukan:
{web_evidence}

Tentukan tepat satu:
STATUS: VERIFIED
STATUS: UNCERTAIN
STATUS: REJECTED

VERIFIED hanya jika bukti cukup kuat bahwa manusia tersebut benar-benar mengucapkan/menulis quote itu.
Prioritaskan sumber primer atau media kredibel yang mengutip sumber primer.
Jangan menganggap banyak situs yang saling menyalin sebagai bukti independen.
Jika hanya parafrase, jangan VERIFIED.
Jika tokoh/quote tidak dapat dipastikan, UNCERTAIN.
Jika jelas salah atribusi, REJECTED.

Jawab:
STATUS: ...
BUKTI: ...
SUMBER: ...
URL: ...
ALASAN: ...
""", model=VERIFICATION_MODEL, max_tokens=1700)
