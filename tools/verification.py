from agent.brain import ask, RESEARCH_MODEL

def verify_quote(person: str, quote: str, source_hint: str = "") -> str:
    return ask(
        f"""Gunakan browser search sungguhan untuk fact-check kutipan berikut.

TOKOH: {person}
QUOTE: {quote}
SUMBER AWAL: {source_hint}

Tentukan tepat satu:
STATUS: VERIFIED
STATUS: UNCERTAIN
STATUS: REJECTED

VERIFIED hanya jika:
1. Tokoh adalah manusia nyata yang dapat diidentifikasi.
2. Ada sumber primer atau sumber kredibel yang menunjukkan tokoh benar-benar mengucapkan/menulis kutipan tersebut.
3. Makna kutipan sesuai dengan sumber.
4. Sumber dapat ditemukan dan diperiksa melalui web.

PENTING:
- Respons ChatGPT/AI tidak boleh diverifikasi sebagai quote tokoh.
- Reddit, forum, screenshot percakapan, atau blog anonim tidak cukup untuk STATUS: VERIFIED.
- Jika sumber primer tidak ditemukan, gunakan UNCERTAIN.
- Jika kutipan jelas salah atribusi, gunakan REJECTED.
- Jangan pernah menganggap kemunculan teks yang sama di banyak situs sebagai bukti kebenaran.

Sertakan:
BUKTI:
SUMBER:
URL:
ALASAN:""",
        model=RESEARCH_MODEL,
        web_search=True,
    )
