from agent.brain import ask, RESEARCH_MODEL

def research_quotes(topic: str) -> str:
    return ask(
        f"""Gunakan browser search sungguhan.

Cari 5 kutipan yang benar-benar terdokumentasi dan relevan dengan topik:
{topic}

Syarat WAJIB:
- Kutipan harus berasal dari manusia nyata yang dapat diidentifikasi.
- Prioritaskan sumber primer: buku, pidato, wawancara, transkrip, arsip resmi, atau publikasi asli.
- Jangan gunakan respons AI, Reddit, forum, screenshot percakapan, blog anonim, atau halaman yang hanya menyalin quote sebagai bukti utama.
- Jangan membuat quote dari ingatan.
- Jika hanya parafrase, tandai PARAFRASE dan jangan jadikan kandidat quote langsung.

Untuk setiap kandidat berikan:
TOKOH:
QUOTE:
KONTEKS:
SUMBER PRIMER:
URL:

Jika tidak menemukan bukti yang cukup, katakan TIDAK ADA KANDIDAT TERVERIFIKASI.""",
        model=RESEARCH_MODEL,
        web_search=True,
        max_tokens=2200,
    )
