import html
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, unquote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def _get(url, timeout=20):
    req = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
        },
    )
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "ignore")


def _ddg(page, limit):
    soup = BeautifulSoup(page, "html.parser")
    out = []
    for a in soup.select(".result__a")[:limit]:
        href = unquote(a.get("href", ""))
        box = a.parent.parent
        sn = box.select_one(".result__snippet")
        if href.startswith(("http://", "https://")):
            out.append(
                {
                    "title": html.unescape(a.get_text(" ", strip=True)),
                    "snippet": html.unescape(
                        sn.get_text(" ", strip=True) if sn else ""
                    ),
                    "url": href.split("#")[0],
                }
            )
    return out


def _bing(page, limit):
    soup = BeautifulSoup(page, "html.parser")
    out = []
    for item in soup.select("li.b_algo")[:limit]:
        a = item.select_one("h2 a")
        sn = item.select_one(".b_caption p")
        if not a:
            continue
        href = a.get("href", "")
        if href.startswith(("http://", "https://")):
            out.append(
                {
                    "title": html.unescape(a.get_text(" ", strip=True)),
                    "snippet": html.unescape(
                        sn.get_text(" ", strip=True) if sn else ""
                    ),
                    "url": href.split("#")[0],
                }
            )
    return out


def _google_news(page, limit):
    root = ET.fromstring(page)
    out = []
    for item in root.findall(".//item")[:limit]:
        title = item.findtext("title", "") or ""
        link = item.findtext("link", "") or ""
        desc = item.findtext("description", "") or ""
        if link:
            snippet = BeautifulSoup(
                html.unescape(desc), "html.parser"
            ).get_text(" ", strip=True)
            out.append(
                {
                    "title": title.strip(),
                    "snippet": snippet,
                    "url": link.strip(),
                }
            )
    return out


def _dedupe(items, limit):
    out = []
    seen = set()
    for item in items:
        url = item.get("url", "").split("#")[0]
        if not url or url in seen:
            continue
        seen.add(url)
        item["url"] = url
        out.append(item)
        if len(out) >= limit:
            break
    return out


def search_news(query, limit=10):
    """Best-effort Google News RSS lookup. Failure is non-fatal."""
    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=id&gl=ID&ceid=ID:id"
    )
    try:
        items = _google_news(_get(url, 20), limit)
        if items:
            print(
                f"[WEB][NEWS] Google News OK | query={query!r} | {len(items)} results",
                flush=True,
            )
            return items
        print(
            f"[WEB][NEWS] Google News empty | query={query!r}",
            flush=True,
        )
    except Exception as exc:
        print(
            f"[WEB][NEWS] Google News failed | query={query!r}: {exc}",
            flush=True,
        )
    return []


def search_web(query, limit=10):
    providers = [
        (
            "DuckDuckGo",
            "https://html.duckduckgo.com/html/?q=" + quote_plus(query),
            _ddg,
        ),
        (
            "Bing",
            "https://www.bing.com/search?q=" + quote_plus(query),
            _bing,
        ),
    ]
    for name, url, parser in providers:
        for attempt in range(2):
            try:
                items = parser(_get(url, 20), limit)
                if items:
                    print(
                        f"[WEB][SEARCH] {name} OK | query={query!r} | {len(items)} results",
                        flush=True,
                    )
                    return items
                print(
                    f"[WEB][SEARCH] {name} empty/unparseable | query={query!r}",
                    flush=True,
                )
                break
            except Exception as exc:
                print(
                    f"[WEB][SEARCH] {name} failed attempt {attempt + 1} | query={query!r}: {exc}",
                    flush=True,
                )
                if attempt == 0:
                    time.sleep(1)
    return []


def search_current_indonesia(limit=10):
    """Collect current Indonesian news from multiple independent query/provider paths."""
    queries = [
        "Indonesia berita terbaru",
        "Indonesia hari ini",
        "berita nasional Indonesia",
    ]
    results = []

    for query in queries:
        results.extend(search_news(query, limit))
        if len(_dedupe(results, limit)) >= limit:
            break

    results = _dedupe(results, limit)
    if results:
        print(
            f"[WEB][CURRENT] Google News aggregate OK | {len(results)} results",
            flush=True,
        )
        return results

    print(
        "[WEB][CURRENT] Google News unavailable; falling back to general web search",
        flush=True,
    )

    fallback_queries = [
        "Indonesia berita terbaru hari ini",
        "berita nasional Indonesia terbaru",
        "Indonesia current news",
    ]
    for query in fallback_queries:
        results.extend(search_web(query, limit))
        results = _dedupe(results, limit)
        if len(results) >= limit:
            break

    if results:
        print(
            f"[WEB][CURRENT] Fallback search OK | {len(results)} results",
            flush=True,
        )
    else:
        print("[WEB][CURRENT] All research providers returned no results", flush=True)
    return results[:limit]


def fetch_page_text(url, max_chars=16000):
    try:
        raw = _get(url, 15)
        soup = BeautifulSoup(raw[:300000], "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()
        return " ".join(soup.stripped_strings)[:max_chars]
    except Exception as exc:
        print(f"[WEB] fetch failed {url}: {exc}", flush=True)
        return ""
