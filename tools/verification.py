import json
import time
from urllib.parse import urlparse

from agent.brain import ask, VERIFICATION_MODEL
from tools.web import search_web, fetch_page_text


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
        for item in search_web(query, 6):
            if item["url"] not in seen:
                seen.add(item["url"])
                evidence.append(item)

    if not evidence:
        result = {
            "status": "UNCERTAIN",
            "confidence": 0,
            "evidence": [],
            "source": "",
            "url": "",
            "reason": "Tidak ada bukti web.",
        }
        print(
            f"[VERIFY] DONE {time.monotonic()-started:.1f}s | UNCERTAIN",
            flush=True,
        )
        return json.dumps(result, ensure_ascii=False)

    pages = []
    urls = [source_hint] + [x["url"] for x in evidence[:4]]
    seen_pages = set()
    for url in urls:
        if url and url not in seen_pages:
            seen_pages.add(url)
            text = fetch_page_text(url)
            if text:
                pages.append(
                    {
                        "url": url,
                        "domain": urlparse(url).netloc,
                        "text": text,
                    }
                )

    compact = "\n".join(
        f"[SEARCH {i}] {x['title']} | {x['snippet']} | {x['url']}"
        for i, x in enumerate(evidence[:15], 1)
    )
    page_evidence = "\n\n".join(
        f"[PAGE {i}] URL={x['url']} DOMAIN={x['domain']}\n{x['text']}"
        for i, x in enumerate(pages[:5], 1)
    ) or "(Tidak ada halaman sumber yang berhasil diambil.)"

    raw = ask(
        f"""Fact-check kutipan secara konservatif.
TOKOH: {person}
QUOTE: {quote}
SUMBER KANDIDAT: {source_hint}

PENTING:
- Search result adalah petunjuk, bukan bukti final.
- PAGE adalah isi halaman sumber yang berhasil diambil.
- VERIFIED hanya jika PAGE atau bukti primer/sekunder kredibel secara jelas mendukung bahwa TOKOH benar-benar mengucapkan/menulis quote tersebut.
- Quote harus cocok secara substansi; jangan menganggap potongan kata yang berbeda sebagai quote yang sama.
- Jika hanya quote-site, repost, Pinterest, Goodreads tanpa sumber primer, atau snippet search = UNCERTAIN.
- Jika atribusi jelas salah = REJECTED.
- Jangan menaikkan status hanya karena banyak situs menyalin teks yang sama.

SEARCH RESULTS:
{compact}

PAGE CONTENT:
{page_evidence}

Jawab JSON VALID saja:
{{"status":"VERIFIED|UNCERTAIN|REJECTED","confidence":0,"evidence":"...","source":"...","url":"...","reason":"..."}}""",
        model=VERIFICATION_MODEL,
        max_tokens=900,
    )

    try:
        data = json.loads(raw)
        status = str(data.get("status", "UNCERTAIN")).upper()
        if status not in {"VERIFIED", "UNCERTAIN", "REJECTED"}:
            status = "UNCERTAIN"
        data["status"] = status
    except Exception:
        data = {
            "status": "UNCERTAIN",
            "confidence": 0,
            "evidence": [],
            "source": "",
            "url": "",
            "reason": "Verifier tidak menghasilkan JSON valid.",
        }

    print(
        f"[VERIFY] DONE {time.monotonic()-started:.1f}s | {data['status']}",
        flush=True,
    )
    return json.dumps(data, ensure_ascii=False)
