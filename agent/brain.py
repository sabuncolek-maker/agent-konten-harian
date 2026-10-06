import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("AGENT_MODEL", "llama-3.3-70b-versatile")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "groq/compound")

def ask(prompt: str, model: str | None = None) -> str:
    response = client.chat.completions.create(
        model=model or MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()
