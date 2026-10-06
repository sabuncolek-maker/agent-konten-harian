import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_agent(goal: str) -> str:
    """Ask the LLM to make a first-step plan for the given goal."""
    prompt = f"""
Kamu adalah AI Agent pembuat konten.

Tujuan:
{goal}

Tentukan apa yang harus dilakukan untuk mencapai tujuan tersebut.

Jawab dengan:
1. Tujuan
2. Analisis singkat
3. Langkah berikutnya
""".strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
