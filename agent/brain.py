import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("YTCLIP_BASE_URL", "https://ai-api.ytclip.org/v1")
API_KEY = os.getenv("YTCLIP_API_KEY")
API_TIMEOUT = float(os.getenv("YTCLIP_TIMEOUT", "90"))

if not API_KEY:
    raise RuntimeError("YTCLIP_API_KEY belum diset.")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=API_TIMEOUT)

MODEL = os.getenv("AGENT_MODEL", "deepseek-v4-pro")
FAST_MODEL = os.getenv("FAST_MODEL", "deepseek-v4.1-flash")
VERIFICATION_MODEL = os.getenv("VERIFICATION_MODEL", "deepseek-v4-pro")

class RateLimitError(RuntimeError):
    pass

def ask(prompt: str, model: str | None = None, max_tokens: int = 1600) -> str:
    selected_model = model or MODEL
    started = time.monotonic()
    try:
        print(f"[LLM] {selected_model} START", flush=True)
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        message = response.choices[0].message
        content = (message.content or "").strip()

        if not content:
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                content = str(reasoning).strip()

        if not content:
            raise RuntimeError(f"Model {selected_model} mengembalikan respons kosong.")

        print(f"[LLM] {selected_model} DONE {time.monotonic() - started:.1f}s", flush=True)
        return content
    except Exception as exc:
        print(f"[LLM] {selected_model} ERROR {time.monotonic() - started:.1f}s: {exc}", flush=True)
        status = getattr(exc, "status_code", None)
        if status == 429:
            raise RateLimitError("API ytclip rate limit tercapai.") from exc
        raise
