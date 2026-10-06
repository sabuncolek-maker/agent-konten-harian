import os
from typing import Callable, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def research_topic(query: str) -> str:
    """Mencari informasi/topik aktual di internet menggunakan Groq Web Search."""
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah research assistant untuk konten media sosial Indonesia. "
                    "Gunakan web search untuk mencari informasi aktual. "
                    "Prioritaskan sumber berita/media yang kredibel dan informasi terbaru. "
                    "Jawab ringkas dalam bahasa Indonesia."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Cari topik yang sedang relevan atau ramai dibicarakan di Indonesia "
                    f"berdasarkan permintaan berikut:\n\n{query}\n\n"
                    "Berikan 5 topik potensial. Untuk setiap topik sertakan: "
                    "topik, alasan relevan, dan sumber."
                ),
            },
        ],
    )

    return response.choices[0].message.content or "Tidak ada hasil riset."


TOOLS: Dict[str, Callable] = {
    "research_topic": research_topic,
}


def run_tool(tool_name: str, **kwargs) -> str:
    if tool_name not in TOOLS:
        raise ValueError(f"Tool tidak ditemukan: {tool_name}")

    return TOOLS[tool_name](**kwargs)
