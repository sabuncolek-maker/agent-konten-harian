import html
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, unquote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def _get(url, timeout=20):
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"})
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
            out.append({
                "title": html.unescape(a.get_text(" ", strip=True)),
                "snippet": html.unescape(sn.get_text(" ", strip=True) if sn else ""),
                "url": href.split("#")[0],
            })
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
            out.append({
                "title": html.unescape(a.get_text(" ", strip=True)),
                "snippet": html.unescape(sn.get_text(" ", strip=True) if sn else ""),
                "url": href.split("#")[0],
            })
    return out


def _google_news(page, limit):
    root = ET.fromstring(page)
    out = []
    for item in root.findall(".//item")[:limit]:
        title = item.findtext("title", "") or ""
        link = item.findtext("link", "") or ""
        desc = item.findtext("description", "") or ""
        source = item.find("source")
        source_name = source.text.strip() if source is not None and source.text else ""
        if link:
            snippet = BeautifulSoup(html.unescape(desc), "html.parser").get_text(" ", strip=True)
            out.append({
                "title": title.strip(),
                "snippet": snippet,
                "url": link.strip(),
                "source": source_name,
            })
    return out


def search_news(query, limit=10):
    url = "https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=id&gl=ID&ceid=ID:id"
    try:
        items = _google_news(_get(url, 20), limit)
        if items:
            print(f"[WEB][NEWS] Google News OK | {len(items)} results", flush=True)
            return items
        print("[WEB][NEWS] Google News returned no results", flush=True)
    except Exception as exc:
        print(f"[WEB][NEWS] Google News failed: {exc}", flush=True)
    return []


def search_web(query, limit=10):
    providers = [
        ("DuckDuckGo", "https://html.duckduckgo.com/html/?q=" + quote_plus(query), _ddg),
        ("Bing", "https://www.bing.com/search?q=" + quote_plus(query), _bing),
    ]
    for name, url, parser in providers:
        for attempt in range(2):
            try:
                items = parser(_get(url, 20), limit)
                if items:
                    print(f"[WEB][SEARCH] {name} OK | {len(items)} results", flush=True)
                    return items
                print(f"[WEB][SEARCH] {name} returned no parseable results", flush=True)
                break
            except Exception as exc:
                print(f"[WEB][SEARCH] {name} failed attempt {attempt + 1}: {exc}", flush=True)
                if attempt == 0:
                    time.sleep(1)
    return []


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
