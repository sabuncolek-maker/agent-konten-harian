import time

from agent.brain import ask, VERIFICATION_MODEL
from tools.research import web_search


def _extract_status(text: str) -> str:
    upper = text.upper()
    for status in ("VERIFIED", "UNCERTAIN", "REJECTED"):
        if f"STATUS: {status}" in upper:
            return status
    return "UNKNOWN"


def verify_quote(person: str, quote: str, source_hint: str = "") -> str:
    queries = [
        f'"{quote}" "{person}"',
        f'"{person}" "{quote}" interview',
        f'"{person}" "{quote}" book speech',
    ]

    evidence = []
    seen_urls = set()
    started = time.monotonic()

    print(
        f"[VERIFY] START | person={person!r} | quote={quote!r}",
        flush=True,
    )

    for query in queries:
        try:
            for item in web_search(query, 5):
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    evidence.append(item)
        except Exception as exc:
            print(f"[VERIFY] Search error: {type(exc).__name__}: {exc}", flush=True)

    web_evidence = "\n".join(
        f"- {r['title']} | {r['snippet']} | {r['url']}"
        for r in evidence[:15]
    )

    if not web_evidence:
        result = (
            "STATUS: UNCERTAIN\n"
            "BUKTI: Tidak ada bukti web yang ditemukan.\n"
            "SUMBER: -\n"
            "URL: -\n"
            "ALASAN: Tidak ada bukti independen untuk memverifikasi atribusi."
        )
        print(f"[VERIFY] DONE {time.monotonic() - started:.1f}s | UNCERTAIN", flush=True)
        return result

    result = ask(
        f"""Fact-check kutipan secara ketat.

TOKOH: {person}
QUOTE: {quote}
SUMBER AWAL: {source_hint}

Bukti web yang ditemukan:
{web_evidence}

Tentukan tepat satu status:
STATUS: VERIFIED
STATUS: UNCERTAIN
STATUS: REJECTED

VERIFIED hanya jika bukti cukup kuat bahwa manusia tersebut benar-benar mengucapkan/menulis quote itu.
Prioritaskan sumber primer atau media kredibel yang mengutip sumber primer.
Jangan menganggap banyak situs yang saling menyalin sebagai bukti independen.
Jika hanya parafrase, jangan VERIFIED.
Jika tokoh/quote tidak dapat dipastikan, UNCERTAIN.
Jika jelas salah atribusi, REJECTED.

Jawab PERSIS:
STATUS: ...
BUKTI: ...
SUMBER: ...
URL: ...
ALASAN: ...
""",
        model=VERIFICATION_MODEL,
        max_tokens=1000,
    )

    status = _extract_status(result)
    print(
        f"[VERIFY] DONE {time.monotonic() - started:.1f}s | {status}",
        flush=True,
    )
    return result
