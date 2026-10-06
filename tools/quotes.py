import json
from agent.brain import ask, MODEL
from tools.research import web_search, build_quote_search_intents


def research_quotes(topic_research: str, used_quotes: list[str] | None = None) -> list[dict]:
    used_quotes = used_quotes or []
    print("[QUOTE] Discovery START", flush=True)
    intents = build_quote_search_intents(topic_research)
    if not intents:
        raise RuntimeError("Quote search intent gagal dibuat.")

    results, seen = [], set()
    for query in intents:
        print(f"[QUOTE] SEARCH: {query}", flush=True)
        for item in web_search(query, 7):
            if item["url"] not in seen:
                seen.add(item["url"])
                results.append({**item, "query": query})

    used = {q.strip().lower() for q in used_quotes if q}
    filtered = []
    for item in results:
        blob = f"{item['title']} {item['snippet']}".lower()
        if used and any(q in blob for q in used):
            continue
        filtered.append(item)

    print(f"[QUOTE] Discovery DONE | intents={len(intents)} candidates={len(filtered)}", flush=True)
    if not filtered:
        raise RuntimeError("Quote discovery tidak menemukan kandidat. Agent tidak akan mengarang quote.")
    return filtered[:30]


def select_quote(candidates: list[dict], topic_research: str, rejected: list[str] | None = None) -> dict | None:
    rejected = rejected or []
    compact = "\n".join(
        f"CANDIDATE {i}: TITLE={x['title']} | SNIPPET={x['snippet']} | URL={x['url']}"
        for i, x in enumerate(candidates, 1)
    )
    result = ask(f"""Pilih satu kandidat yang PALING LAYAK diverifikasi sebagai quote langsung.
Jangan membuat quote baru. Jangan menganggap snippet sebagai transkrip.
Pilih hanya jika ada tokoh manusia nyata dan kandidat menunjukkan quote langsung atau sumber yang jelas.
Jika tidak layak, pilih null.

TOPIK:
{topic_research}

QUOTE YANG DITOLAK DALAM RUN INI:
{rejected}

Jawab JSON VALID:
{{"candidate_index":0,"person":"","quote":"","source_url":""}}

KANDIDAT:
{compact}""", model=MODEL, max_tokens=700)
    try:
        data = json.loads(result)
        idx = int(data.get("candidate_index", 0))
        if idx < 1 or idx > len(candidates):
            return None
        candidate = candidates[idx - 1].copy()
        candidate["person"] = str(data.get("person", "")).strip()
        candidate["quote"] = str(data.get("quote", "")).strip()
        candidate["source_url"] = candidate["url"]
        if not candidate["person"] or not candidate["quote"]:
            return None
        return candidate
    except Exception:
        return None
