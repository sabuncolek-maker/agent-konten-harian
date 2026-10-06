import html
import json
import time
from urllib.parse import quote_plus, unquote, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from agent.brain import ask, MODEL, FAST_MODEL

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def _parse_ddg(page: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(page, "html.parser")
    results, seen = [], set()
    for item in (soup.select(".result") or soup.select("article")):
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


def _google_news_search(query: str, limit: int) -> list[dict]:
    url = "https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=id&gl=ID&ceid=ID:id"
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"})
    with urlopen(req, timeout=20) as response:
        raw = response.read(500000)
    root = ET.fromstring(raw)
    results = []
    for item in root.findall(".//item")[:limit]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = item.findtext("description", "").strip()
        if not link or not title:
            continue
        snippet = BeautifulSoup(description, "html.parser").get_text(" ", strip=True)
        results.append({
            "title": html.unescape(title),
            "snippet": html.unescape(snippet),
            "url": link,
        })
    return results


def _ddg_search(query: str, limit: int) -> list[dict]:
    for base in (
        "https://html.duckduckgo.com/html/?q=",
        "https://lite.duckduckgo.com/lite/?q=",
    ):
        url = base + quote_plus(query)
        req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        with urlopen(req, timeout=20) as response:
            page = response.read().decode("utf-8", errors="ignore")
        results = _parse_ddg(page, limit)
        if results:
            return results
    return []


def web_search(query: str, limit: int = 6, retries: int = 2) -> list[dict]:
    """Real search with Google News RSS as the reliable GitHub Actions path and DDG fallback."""
    last_error = None
    for attempt in range(retries + 1):
        for provider in (_google_news_search, _ddg_search):
            try:
                results = provider(query, limit)
                if results:
                    print(f"[WEB] {provider.__name__} OK | {query}", flush=True)
                    return results
            except Exception as exc:
                last_error = exc
                print(f"[WEB] {provider.__name__} failed | {type(exc).__name__}: {exc}", flush=True)
        if attempt < retries:
            time.sleep(1.0 * (attempt + 1))
    print(f"[WEB] ALL PROVIDERS FAILED | query={query!r} | last={last_error}", flush=True)
    return []


def fetch_page_text(url: str, max_chars: int = 12000) -> str:
    if not url or not url.startswith(("http://", "https://")):
        return ""
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"})
        with urlopen(req, timeout=15) as response:
            raw = response.read(300000).decode("utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()
        return " ".join(soup.stripped_strings)[:max_chars]
    except Exception as exc:
        print(f"[WEB] page fetch failed for {url}: {type(exc).__name__}: {exc}", flush=True)
        return ""


def source_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _extract_json_object(text: str) -> dict | None:
    """Parse JSON even when the model wraps it in markdown or extra text."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1).replace("```", "", 1).strip()
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            data = json.loads(cleaned[start:end + 1])
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _compact(evidence: list[dict], limit: int = 20) -> str:
    return "\n".join(f"[{i}] {x["title"]} | {x["snippet"]} | {x["url"]}" for i, x in enumerate(evidence[:limit], 1))


def research_topic(goal: str, memory_topics: list[str] | None = None) -> str:
    memory_topics = memory_topics or []
    searches = [
        f"Indonesia berita terbaru {goal}",
        f"Indonesia tren sosial masyarakat {goal}",
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
        raise RuntimeError("Web search topik gagal. Semua provider search tidak menghasilkan hasil; agent tidak mengarang.")

    prompt = f"""Kamu adalah research analyst untuk agent konten Indonesia.
TUJUAN:
{goal}

TOPIK YANG SUDAH DIPAKAI:
{memory_topics}

Gunakan HANYA bukti web. Pilih satu isu aktual yang relevan, aman, punya bukti cukup, dan belum dipakai.
Pertahankan nama tokoh, organisasi, tempat, peristiwa, dan konteks penting dari sumber.
Jangan mengubah isu menjadi slogan generik. Jangan membuat fakta atau URL.
Jawab JSON VALID saja:
{{"topic":"...","context":"...","angle":"...","facts":["..."],"sources":["..."]}}

BUKTI WEB:
{_compact(evidence)}
"""
    result = ask(prompt, model=MODEL, max_tokens=1200)
    data = _extract_json_object(result)
    if not data or not str(data.get("topic", "")).strip():
        print(f"[RESEARCH] Invalid JSON response: {result[:1000]!r}", flush=True)
        raise RuntimeError("Research model tidak menghasilkan JSON/topic yang valid.")
    return json.dumps(data, ensure_ascii=False)


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
        data = _extract_json_object(result)
        if data:
            return [str(q).strip() for q in data.get("queries", []) if str(q).strip()][:5]
        raise ValueError("JSON query tidak valid")
    except Exception:
        lines = [line.strip(' -•\\t"') for line in result.splitlines() if line.strip()]
        return lines[:5]
