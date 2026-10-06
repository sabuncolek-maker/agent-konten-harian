from agent.brain import ask, RESEARCH_MODEL

def research_topic(query: str) -> str:
    return ask(
        f"""Cari dengan web search 5 topik yang sedang aktual dan relevan di Indonesia untuk tujuan: {query}
Prioritaskan sumber kredibel dan terbaru. Untuk setiap topik berikan TOPIK, ALASAN RELEVAN, dan SUMBER.
Jangan mengarang fakta atau tren.""",
        model=RESEARCH_MODEL,
    )
