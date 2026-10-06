import os
from typing import Callable, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def research_topic(query: str) -> str:
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah research assistant untuk konten media sosial Indonesia. "
                    "Gunakan web search untuk mencari informasi aktual. Prioritaskan sumber "
                    "kredibel dan informasi terbaru. Jawab ringkas dalam bahasa Indonesia."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Cari topik yang sedang relevan atau ramai dibicarakan di Indonesia "
                    f"berdasarkan permintaan berikut:\n\n{query}\n\n"
                    "Berikan 5 topik potensial. Untuk setiap topik sertakan topik, alasan "
                    "relevan, dan sumber."
                ),
            },
        ],
    )
    return response.choices[0].message.content or "Tidak ada hasil riset."


def research_quotes(topic: str) -> str:
    """Mencari kandidat quote yang relevan beserta sumbernya."""
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah peneliti kutipan. Gunakan web search. "
                    "Jangan mengarang kutipan. Cari kutipan yang benar-benar terdokumentasi. "
                    "Jika kutipan hanya tersedia dalam bahasa lain, tampilkan teks aslinya "
                    "dan terjemahan Indonesia. Sertakan sumber yang dapat ditelusuri."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Topik terpilih: {topic}\n\n"
                    "Cari 5 kandidat kutipan dari tokoh yang relevan. "
                    "Untuk setiap kandidat berikan: TOKOH, QUOTE ASLI, "
                    "TERJEMAHAN INDONESIA, KARYA/PERISTIWA, dan SUMBER. "
                    "Jangan menyebut kutipan sebagai valid hanya karena muncul di situs "
                    "quote populer."
                ),
            },
        ],
    )
    return response.choices[0].message.content or "Tidak ada kandidat quote."


def verify_quote(quote: str, person: str, source_hint: str = "") -> str:
    """Memverifikasi apakah quote benar-benar dapat dipertanggungjawabkan."""
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah fact-checker kutipan. Gunakan web search secara aktif. "
                    "Jangan menganggap sebuah quote benar hanya karena banyak situs "
                    "mengulangnya. Cari sumber primer jika memungkinkan: buku, pidato, "
                    "transkrip, wawancara, arsip, atau penerbit. Jika tidak dapat diverifikasi, "
                    "nyatakan TIDAK TERVERIFIKASI."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tokoh: {person}\n"
                    f"Quote: {quote}\n"
                    f"Sumber awal: {source_hint}\n\n"
                    "Periksa atribusi quote ini. Jawab dengan format:\n"
                    "STATUS: VERIFIED / UNCERTAIN / REJECTED\n"
                    "EVIDENCE: bukti singkat\n"
                    "PRIMARY_SOURCE: sumber primer jika ditemukan\n"
                    "SECONDARY_SOURCES: sumber sekunder yang mendukung\n"
                    "NOTES: catatan tentang terjemahan, konteks, atau atribusi."
                ),
            },
        ],
    )
    return response.choices[0].message.content or "Verifikasi gagal."


TOOLS: Dict[str, Callable] = {
    "research_topic": research_topic,
    "research_quotes": research_quotes,
    "verify_quote": verify_quote,
}


def run_tool(tool_name: str, **kwargs) -> str:
    if tool_name not in TOOLS:
        raise ValueError(f"Tool tidak ditemukan: {tool_name}")
    return TOOLS[tool_name](**kwargs)
