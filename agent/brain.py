import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("AGENT_MODEL", "openai/gpt-oss-20b")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "openai/gpt-oss-20b")
VERIFICATION_MODEL = os.getenv("VERIFICATION_MODEL", "openai/gpt-oss-120b")

def ask(prompt: str, model: str | None = None, web_search: bool = False, max_tokens: int = 2048) -> str:
    kwargs = {
        "model": model or MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": max_tokens,
    }
    if web_search:
        kwargs["tools"] = [{"type": "browser_search"}]
        kwargs["tool_choice"] = "required"

    for attempt in range(3):
        try:
            response = client.chat.completions.create(**kwargs)
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            if getattr(exc, "status_code", None) == 429 and attempt < 2:
                time.sleep(10 * (attempt + 1))
                continue
            raise
