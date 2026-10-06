import html
import re
from urllib.parse import quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

from agent.brain import ask, MODEL

def web_search(query: str, limit: int = 6) -> list[dict]:
    """Real web search using DuckDuckGo HTML; model is never asked to invent browsing."""
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as response:
        page = response.read().decode("utf-8", errors="ignore")

    blocks = re.findall(r'<div class="result results_links results_links_deep web-result">(.*?)</div>\s*</div>', page, re.S)
    results = []
    for block in blocks[:limit]:
        title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.S)
        snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</a?>', block, re.S)
        href_match = re.search(r'class="result__a"[^>]*href="([^"]+)"', block, re.S)
        if not title_match or not href_match:
            continue
        title = re.sub(r"<[^>]+>", "", html.unescape(title_match.group(1))).strip()
        snippet = re.sub(r"<[^>]+>", "", html.unescape(snippet_match.group(1))).strip() if snippet_match else ""
        href = unquote(href_match.group(1))
        results.append({"title": title, "snippet": snippet, "url": href})
    return results

def research_topic(query: str, memory_topics: list[str] | None = None) -> str:
    memory_topics = memory_topics or []
    searches = [
        f"Indonesia berita terbaru hari ini {query}",
        f"Indonesia tren sosial terbaru masyarakat {query}",
        f"site:kompas.com Indonesia terbaru {query}",
    ]
    evidence = []
    for q in searches:
        try:
            evidence.extend(web_search(q, 4))
        except Exception as exc:
            evidence.append({"title": "SEARCH_ERROR", "snippet": str(exc), "url": ""})

    compact = "\n".join(
        f"- {x['title']} | {x['snippet']} | {x['url']}" for x in evidence[:12]
    )

    return ask(f"""Kamu adalah research planner untuk agent konten Indonesia.
Gunakan HANYA bukti web yang diberikan di bawah. Jangan mengaku browsing sendiri.

Tujuan:
{query}

Topik yang sudah dipakai:
{memory_topics}

Pilih SATU topik yang paling relevan, aktual, aman, dan punya bukti cukup.
Jangan pilih topik yang sama dengan memory.
Jawab persis:

TOPIK: ...
ALASAN: ...
FAKTA: ...
SUMBER:
- URL | judul

BUKTI WEB:
{compact}
""", model=MODEL, max_tokens=1300)
