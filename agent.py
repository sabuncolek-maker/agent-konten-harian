import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_agent(goal: str) -> str:
    """Agent menentukan tindakan berikutnya."""
    prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Tool tersedia:
- research_topic(query): mencari topik aktual di internet.

Untuk tahap ini, kamu WAJIB melakukan riset terlebih dahulu.

Jawab PERSIS dalam format:
TOOL: research_topic
QUERY: <permintaan riset yang jelas>

Jangan memberikan jawaban lain."""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()


def analyze_research(goal: str, research_result: str) -> str:
    """Agent menganalisis hasil research dan memilih topik."""
    prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Hasil riset internet:
{research_result}

Pilih satu topik paling potensial untuk dijadikan konten quote Instagram.

Berikan:
1. Topik terpilih
2. Alasan pemilihan
3. Sudut pandang konten
4. Langkah berikutnya

Jangan membuat quote dulu."""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()
