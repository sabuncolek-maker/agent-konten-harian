from agent.brain import ask, RESEARCH_MODEL

def research_quotes(topic: str) -> str:
    return ask(
        f"""Cari dengan web search 5 kutipan yang benar-benar terdokumentasi dan relevan dengan topik: {topic}.
Prioritaskan sumber primer seperti buku, pidato, wawancara, transkrip, atau arsip tepercaya.
Untuk setiap kandidat berikan TOKOH, QUOTE, KONTEKS, dan SUMBER.
Jangan membuat quote dari ingatan. Jika hanya parafrase, tandai PARAFRASE.""",
        model=RESEARCH_MODEL,
    )
