from tools.research import web_search

def research_quotes(topic: str) -> str:
    queries = [
        f'"{topic}" quote interview speech',
        f'"{topic}" quote book speech',
        f'"{topic}" "said" quote',
    ]
    results = []
    for query in queries:
        try:
            results.extend(web_search(query, 5))
        except Exception:
            continue

    lines = []
    for r in results[:15]:
        lines.append(f"TITLE: {r['title']}\nSNIPPET: {r['snippet']}\nURL: {r['url']}")
    return "\n\n".join(lines)
