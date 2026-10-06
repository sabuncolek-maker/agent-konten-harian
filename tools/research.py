import html
from urllib.parse import quote_plus, unquote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from agent.brain import ask, MODEL

def web_search(query: str, limit: int = 6) -> list[dict]:
    """Real web search from DuckDuckGo HTML. No fake browsing."""
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
        },
    )
    with urlopen(req, timeout=25) as response:
        page = response.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(page, "html.parser")
    results = []

    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        if not link:
            continue

        title = link.get_text(" ", strip=True)
        href = unquote(link.get("href", ""))

        snippet_node = item.select_one(".result__snippet")
        snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""

        if title and href:
            results.append({
                "title": html.unescape(title),
                "snippet": html.unescape(snippet),
                "url": href,
            })

        if len(results) >= limit:
            break

    return results

def research_topic(query: str, memory_topics: list[str] | None = None) -> str:
    memory_topics = memory_topics or []
    searches = [
        f"Indonesia berita terbaru hari ini {query}",
        f"Indonesia tren sosial terbaru masyarakat {query}",
        f"site:kompas.com Indonesia terbaru {query}",
    ]

    evidence = []
    seen = set()

    for q in searches:
        try:
            for item in web_search(q, 4):
                if item["url"] not in seen:
                    seen.add(item["url"])
                    evidence.append(item)
        except Exception as exc:
            evidence.append({
                "title": "SEARCH_ERROR",
                "snippet": str(exc),
                "url": "",
            })

    if not evidence:
        raise RuntimeError("Web search tidak menghasilkan bukti.")

    compact = "\n".join(
        f"- {x['title']} | {x['snippet']} | {x['url']}"
        for x in evidence[:12]
    )

    return ask(f"""Kamu adalah research planner untuk agent konten Indonesia.

Tujuan:
{query}

Topik yang sudah dipakai:
{memory_topics}

Gunakan HANYA bukti web di bawah. Pilih SATU topik yang:
1. relevan dengan masyarakat Indonesia,
2. aktual,
3. aman,
4. punya bukti web yang cukup,
5. belum ada di memory.

Jangan membuat fakta, tren, URL, atau topik baru di luar bukti.

Jawab PERSIS:
TOPIK: <satu topik>
ALASAN: <alasan singkat>
FAKTA: <fakta yang didukung bukti>
SUMBER: <URL sumber utama>

BUKTI WEB:
{compact}
""", model=MODEL, max_tokens=1200)
