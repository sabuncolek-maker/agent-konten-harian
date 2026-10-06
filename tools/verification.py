from agent.brain import ask, RESEARCH_MODEL

def verify_quote(person: str, quote: str, source_hint: str = "") -> str:
    return ask(
        f"""Fact-check kutipan berikut menggunakan web search.
TOKOH: {person}
QUOTE: {quote}
SUMBER AWAL: {source_hint}

Tentukan tepat satu:
STATUS: VERIFIED
STATUS: UNCERTAIN
STATUS: REJECTED

VERIFIED hanya jika ada bukti yang cukup bahwa tokoh tersebut benar-benar mengucapkannya/menuliskannya dengan makna yang sama.
Jika bukti lemah, sumber sekunder saja, atau quote kemungkinan salah atribusi, gunakan UNCERTAIN.
Jika terbukti palsu/salah atribusi, gunakan REJECTED.
Sertakan BUKTI dan SUMBER.""",
        model=RESEARCH_MODEL,
    )
