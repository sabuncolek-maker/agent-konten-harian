import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("AGENT_MODEL", "openai/gpt-oss-120b")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "openai/gpt-oss-120b")

def ask(prompt: str, model: str | None = None, web_search: bool = False) -> str:
    kwargs = {
        "model": model or MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 4096,
    }
    if web_search:
        kwargs["tools"] = [{"type": "browser_search"}]
        kwargs["tool_choice"] = "required"
    response = client.chat.completions.create(**kwargs)
    return (response.choices[0].message.content or "").strip()
