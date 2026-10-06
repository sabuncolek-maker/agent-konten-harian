from agent.brain import ask, RESEARCH_MODEL

def research_topic(query: str) -> str:
    return ask(
        f"""Gunakan browser search sungguhan untuk melakukan riset terbaru.

Cari 5 topik yang sedang aktual dan relevan di Indonesia untuk tujuan:
{query}

Prioritaskan informasi terbaru dan sumber kredibel.
Untuk setiap topik berikan:
TOPIK
ALASAN RELEVAN
FAKTA TERKINI
SUMBER

Jangan mengarang tren, data, atau sumber.
Jika informasi tidak dapat diverifikasi dari web, jangan masukkan.""",
        model=RESEARCH_MODEL,
        web_search=True,
        max_tokens=1800,
    )
