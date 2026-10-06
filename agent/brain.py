import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("YTCLIP_BASE_URL", "https://ai-api.ytclip.org/v1")
API_KEY = os.getenv("YTCLIP_API_KEY")

if not API_KEY:
    raise RuntimeError("YTCLIP_API_KEY belum diset.")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

MODEL = os.getenv("AGENT_MODEL", "deepseek-v4-pro")
FAST_MODEL = os.getenv("FAST_MODEL", "mimo-v2.6-flash")
VERIFICATION_MODEL = os.getenv("VERIFICATION_MODEL", "deepseek-v4-pro")

class RateLimitError(RuntimeError):
    pass

def ask(prompt: str, model: str | None = None, max_tokens: int = 1600) -> str:
    try:
        response = client.chat.completions.create(
            model=model or MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        if status == 429:
            raise RateLimitError("API ytclip rate limit tercapai.") from exc
        raise
