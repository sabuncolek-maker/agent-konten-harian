import html
import json
import time
from urllib.parse import quote_plus, unquote
from urllib.request import Request, urlopen
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from agent.brain import ask, MODEL, FAST_MODEL

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def _parse_results(page: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(page, "html.parser")
    results, seen = [], set()
    nodes = soup.select(".result") or soup.select("article")
    for item in nodes:
        link = item.select_one(".result__a") or item.select_one("a[href]")
        if not link:
            continue
        href = unquote(link.get("href", ""))
        if not href.startswith(("http://", "https://")):
            continue
        title = link.get_text(" ", strip=True)
        snippet_node = item.select_one(".result__snippet") or item.select_one(".result__body")
        snippet = snippet_node.get_text(" ", strip=True) if snippet_node else item.get_text(" ", strip=True)
        key = href.split("#", 1)[0]
        if title and key not in seen:
            seen.add(key)
            results.append({"title": html.unescape(title), "snippet": html.unescape(snippet), "url": key})
        if len(results) >= limit:
            break
    return results


def web_search(query: str, limit: int = 6, retries: int = 2) -> list[dict]:
    """Real web search with retry and DDG HTML/lite fallback."""
    endpoints = [
        "https://html.duckduckgo.com/html/?q=" + quote_plus(query),
        "https://lite.duckduckgo.com/lite/?q=" + quote_plus(query),
    ]
    last_error = None
    for attempt in range(retries + 1):
        for url in endpoints:
            try:
                req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
                with urlopen(req, timeout=20) as response:
                    page = response.read().decode("utf-8", errors="ignore")
                results = _parse_results(page, limit)
                if results:
                    return results
            except Exception as exc:
                last_error = exc
        if attempt < retries:
            time.sleep(1.2 * (attempt + 1))
    if last_error:
        print(f"[WEB] search failed: {type(last_error).__name__}: {last_error}", flush=True)
    return []


def fetch_page_text(url: str, max_chars: int = 12000) -> str:
    """Fetch readable text from one real source page for verification."""
    if not url or not url.startswith(("http://", "https://")):
        return ""
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        with urlopen(req, timeout=15) as response:
            raw = response.read(300000).decode("utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:max_chars]
    except Exception as exc:
        print(f"[WEB] page fetch failed for {url}: {type(exc).__name__}: {exc}", flush=True)
        return ""


def source_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _compact(evidence: list[dict], limit: int = 20) -> str:
    return "\n".join(
        f"[{i}] {x['title']} | {x['snippet']} | {x['url']}"
        for i, x in enumerate(evidence[:limit], 1)
    )


def research_topic(goal: str, memory_topics: list[str] | None = None) -> str:
    memory_topics = memory_topics or []
    searches = [
        f"Indonesia berita terbaru hari ini {goal}",
        f"Indonesia tren sosial terbaru masyarakat {goal}",
        f"site:kompas.com {goal}",
        f"site:tempo.co {goal}",
        f"site:antaranews.com {goal}",
    ]
    evidence, seen = [], set()
    for query in searches:
        for item in web_search(query, 5):
            if item["url"] not in seen:
                seen.add(item["url"])
                evidence.append(item)

    if not evidence:
        raise RuntimeError("Web search topik gagal menghasilkan bukti. Agent tidak boleh mengarang.")

    prompt = f"""Kamu adalah research analyst untuk agent konten Indonesia.
TUJUAN:
{goal}

TOPIK YANG SUDAH DIPAKAI:
{memory_topics}

Gunakan HANYA bukti web. Pilih satu isu aktual yang relevan, aman, punya bukti kuat, dan belum dipakai.
Pertahankan nama tokoh, organisasi, tempat, peristiwa, dan konteks penting jika muncul dalam bukti.
Jangan mengubah isu menjadi slogan generik. Jangan membuat fakta atau URL.

Jawab JSON VALID saja:
{{"topic":"...","context":"...","angle":"...","facts":["..."],"sources":["..."]}}

BUKTI WEB:
{_compact(evidence)}
"""
    return ask(prompt, model=MODEL, max_tokens=1200)


def build_quote_search_intents(topic_research: str) -> list[str]:
    result = ask(f"""Buat tepat 5 query pencarian web untuk menemukan kutipan langsung yang relevan dengan konteks berikut.
Jangan mencari kalimat persis dari TOPIK. Cari berdasarkan tema quote.
Utamakan wawancara, pidato, buku, universitas, museum, organisasi resmi, atau media kredibel.
Jangan membuat nama tokoh atau quote.
Jawab JSON VALID saja:
{{"queries":["...","...","...","...","..."]}}

KONTEKS:
{topic_research}""", model=FAST_MODEL, max_tokens=500)
    try:
        data = json.loads(result)
        return [str(q).strip() for q in data.get("queries", []) if str(q).strip()][:5]
    except Exception:
        lines = [line.strip(" -•\t\"") for line in result.splitlines() if line.strip()]
        return lines[:5]
