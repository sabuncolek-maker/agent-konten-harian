import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


def ask_agent(goal: str) -> str:
    prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Tool tersedia:
- research_topic(query): mencari topik aktual di internet.

Untuk tahap ini, WAJIB melakukan riset terlebih dahulu.
Jawab PERSIS:
TOOL: research_topic
QUERY: <permintaan riset yang jelas>"""
    return call_llm(prompt)


def analyze_research(goal: str, research_result: str) -> str:
    prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Hasil riset internet:
{research_result}

Pilih satu topik paling potensial untuk dijadikan konten quote Instagram.
Berikan:
1. Topik terpilih
2. Alasan
3. Sudut pandang konten
4. Langkah berikutnya

Jangan membuat quote dulu."""
    return call_llm(prompt)


def select_quote(topic: str, quote_research: str) -> str:
    prompt = f"""Kamu adalah editor kutipan yang sangat ketat.

Topik:
{topic}

Kandidat hasil research:
{quote_research}

Pilih SATU kandidat paling relevan untuk diverifikasi.
Prioritaskan:
- relevansi dengan topik,
- tokoh jelas,
- karya/peristiwa jelas,
- sumber yang bisa ditelusuri.

Jangan menganggap quote benar sebelum verifikasi.

Jawab PERSIS:
PERSON: <nama tokoh>
QUOTE: <quote asli>
SOURCE_HINT: <sumber yang diberikan peneliti>"""
    return call_llm(prompt)


def decide_after_verification(topic: str, quote: str, person: str, verification: str) -> str:
    prompt = f"""Kamu adalah editor fact-checking.

Topik: {topic}
Tokoh: {person}
Quote: {quote}

Hasil verifikasi:
{verification}

Aturan:
- VERIFIED → boleh lanjut ke tahap pembuatan konten.
- UNCERTAIN → jangan gunakan sebagai quote langsung; cari kandidat lain.
- REJECTED → tolak dan cari kandidat lain.

Jawab dengan salah satu:
APPROVE
RESEARCH_ANOTHER_QUOTE
REJECT"""
    return call_llm(prompt)
