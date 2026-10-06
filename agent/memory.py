import json
from pathlib import Path

PATH = Path("data/memory.json")
DEFAULT = {"used_quotes": [], "used_topics": [], "published": []}


def load_memory():
    if not PATH.exists():
        return {k: list(v) for k, v in DEFAULT.items()}
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        for key, value in DEFAULT.items():
            data.setdefault(key, list(value))
        return data
    except Exception as exc:
        print(f"[MEMORY] Invalid memory.json: {exc}; using empty memory", flush=True)
        return {k: list(v) for k, v in DEFAULT.items()}


def save_memory(memory):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(PATH)
