from agent.brain import ask

def generate_content(topic: str, person: str, quote: str, verification: str, revision_feedback: str = "") -> str:
    return ask(f"""Buat konten Instagram quote untuk audiens Indonesia.
TOPIK: {topic}
TOKOH: {person}
QUOTE ASLI: {quote}
HASIL VERIFIKASI: {verification}
FEEDBACK REVISI: {revision_feedback or "tidak ada"}

Aturan: jangan mengubah kata-kata quote asli; buat HOOK, QUOTE, ATRIBUSI, KONTEKS singkat, dan CAPTION; gunakan bahasa Indonesia natural; jangan clickbait menyesatkan; jangan menyajikan parafrase sebagai kutipan langsung.""")
