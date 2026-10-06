from agent.brain import ask

def generate_content(topic: str, person: str, quote: str, verification: str, revision_feedback: str = "") -> str:
    return ask(
        f"""Buat konten Instagram quote untuk audiens Indonesia.

TOPIK: {topic}
TOKOH: {person}
QUOTE ASLI: {quote}
HASIL VERIFIKASI: {verification}
FEEDBACK REVISI: {revision_feedback or "tidak ada"}

Aturan:
1. Jangan mengubah kata-kata quote asli.
2. Jangan menyebut quote VERIFIED jika verifikasi tidak jelas.
3. Buat HOOK singkat, QUOTE, ATRIBUSI, KONTEKS singkat, dan CAPTION.
4. Bahasa Indonesia natural, tidak kaku, tidak clickbait menyesatkan.
5. Jika quote ternyata bukan kutipan langsung, jangan menyajikannya sebagai kutipan langsung."""
    )
