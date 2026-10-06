import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Current Groq production model with built-in browser search capability.
MODEL = os.getenv("AGENT_MODEL", "openai/gpt-oss-120b")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "openai/gpt-oss-120b")

def ask(prompt: str, model: str | None = None) -> str:
    response = client.chat.completions.create(
        model=model or MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()
