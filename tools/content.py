from agent.brain import ask, MODEL

def generate_content(topic: str, person: str, quote: str, verification: str, revision_feedback: str = "") -> str:
    return ask(f"""Buat konten Instagram quote untuk audiens Indonesia.

TOPIK: {topic}
TOKOH: {person}
QUOTE ASLI: {quote}
HASIL VERIFIKASI: {verification}
FEEDBACK REVISI:
{revision_feedback or "Tidak ada. Buat draft pertama."}

Tujuan:
Membuat konten yang relevan dengan topik, tetapi TIDAK memaksakan hubungan antara quote dan topik.

Aturan wajib:
- Jangan mengubah satu kata pun dari QUOTE ASLI.
- Jangan menyajikan parafrase sebagai kutipan langsung.
- Gunakan hanya fakta yang ada di TOPIK dan HASIL VERIFIKASI.
- Jangan membuat klaim spesifik tentang orang, video, kejadian, atau berita yang tidak didukung.
- Jika topik menyebut figur publik/politik, gunakan bahasa deskriptif dan netral; jangan mengajak audiens mendukung atau menyerang figur tersebut.
- Jelaskan konteks hubungan quote dengan topik sebagai INTERPRETASI, bukan seolah-olah tokoh tersebut sedang membahas topik tersebut.
- Jangan menggunakan markdown.
- Bahasa Indonesia natural, ringkas, dan cocok untuk caption Instagram.
- Buat HOOK, QUOTE, ATRIBUSI, KONTEKS, CAPTION, dan CTA.
- Jangan menulis sumber sebagai "terverifikasi" jika sumbernya hanya sumber sekunder; cukup tulis sumber sesuai hasil verifikasi.
- Jangan gunakan hashtag berlebihan.

Jika FEEDBACK REVISI berisi masalah, perbaiki masalah tersebut secara eksplisit.

Output hanya draft konten siap pakai.
""", model=MODEL, max_tokens=1100)
