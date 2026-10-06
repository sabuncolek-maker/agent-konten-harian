import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_agent(goal: str, tool_result: str | None = None) -> str:
    if tool_result is None:
        prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Tool tersedia:
- research_topic: mencari topik relevan.

Tentukan langkah berikutnya.
Jika membutuhkan riset, jawab PERSIS:
TOOL: research_topic
Jika tidak, jelaskan langkah yang harus dilakukan."""
    else:
        prompt = f"""Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Hasil research_topic:
{tool_result}

Analisis hasil tersebut. Pilih satu topik paling potensial dan jelaskan alasannya.
Jangan memanggil tool lagi pada tahap ini."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
