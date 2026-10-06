import os
import time
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
BASE_URL=os.getenv("YTCLIP_BASE_URL","https://ai-api.ytclip.org/v1")
API_KEY=os.getenv("YTCLIP_API_KEY")
TIMEOUT=float(os.getenv("YTCLIP_TIMEOUT","90"))
if not API_KEY: raise RuntimeError("YTCLIP_API_KEY belum diset.")
client=OpenAI(api_key=API_KEY,base_url=BASE_URL,timeout=TIMEOUT)
MODEL=os.getenv("AGENT_MODEL","deepseek-v4-pro")
FAST_MODEL=os.getenv("FAST_MODEL","deepseek-v4.1-flash")
VERIFICATION_MODEL=os.getenv("VERIFICATION_MODEL","deepseek-v4-pro")
class RateLimitError(RuntimeError): pass
def ask(prompt,model=None,max_tokens=1200):
    m=model or MODEL; started=time.monotonic(); print(f"[LLM] {m} START",flush=True)
    try:
        r=client.chat.completions.create(model=m,messages=[{"role":"user","content":prompt}],max_tokens=max_tokens)
        content=(r.choices[0].message.content or "").strip()
        if not content: raise RuntimeError(f"Model {m} mengembalikan content kosong.")
        print(f"[LLM] {m} DONE {time.monotonic()-started:.1f}s",flush=True); return content
    except Exception as exc:
        print(f"[LLM] {m} ERROR {time.monotonic()-started:.1f}s: {exc}",flush=True)
        if getattr(exc,"status_code",None)==429: raise RateLimitError("API ytclip rate limit tercapai.") from exc
        raise
