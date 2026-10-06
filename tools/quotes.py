import time

from tools.research import web_search


def research_quotes(topic: str, used_quotes: list[str] | None = None) -> str:
    """Collect multiple quote candidates from real web search for one topic."""
    used_quotes = used_quotes or []
    queries = [
        f'"{topic}" quote interview speech',
        f'"{topic}" quote book speech',
        f'"{topic}" "said" quote',
    ]

    results = []
    seen_urls = set()

    started = time.monotonic()
    print("[QUOTE] Web search START", flush=True)

    for query in queries:
        try:
            for item in web_search(query, 6):
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    results.append(item)
        except Exception as exc:
            print(f"[QUOTE] Search error: {type(exc).__name__}: {exc}", flush=True)

    candidates = []
    used_normalized = {q.strip().lower() for q in used_quotes if q}

    for item in results:
        text = f"{item.get('title', '')} {item.get('snippet', '')}".strip()
        if not text:
            continue
        if any(u in text.lower() for u in used_normalized):
            continue
        candidates.append(item)

    candidates = candidates[:18]

    print(
        f"[QUOTE] Web search DONE {time.monotonic() - started:.1f}s | "
        f"{len(candidates)} candidates",
        flush=True,
    )

    if not candidates:
        raise RuntimeError("Web search quote tidak menghasilkan kandidat.")

    return "\n\n".join(
        f"CANDIDATE {i}:\n"
        f"TITLE: {r['title']}\n"
        f"SNIPPET: {r['snippet']}\n"
        f"URL: {r['url']}"
        for i, r in enumerate(candidates, 1)
    )
