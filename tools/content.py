from agent.brain import ask, MODEL

def generate_content(topic: str, person: str, quote: str, verification: str, revision_feedback: str = "") -> str:
    return ask(f"""Buat konten Instagram quote untuk audiens Indonesia.

TOPIK: {topic}
TOKOH: {person}
QUOTE ASLI: {quote}
HASIL VERIFIKASI: {verification}
FEEDBACK REVISI: {revision_feedback or "tidak ada"}

Aturan:
- Jangan mengubah kata-kata quote asli.
- Jangan menyajikan parafrase sebagai kutipan langsung.
- Buat HOOK, QUOTE, ATRIBUSI, KONTEKS singkat, dan CAPTION.
- Bahasa Indonesia natural dan mudah dipahami.
- Hook harus relevan dengan topik, bukan clickbait palsu.
- Jika verifikasi tidak jelas, jangan membuat konten.
""", model=MODEL, max_tokens=1300)
