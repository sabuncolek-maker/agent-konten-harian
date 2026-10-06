import json
from pathlib import Path
PATH = Path('data/memory.json')
def load_memory():
    if not PATH.exists(): return {'used_quotes': [], 'used_topics': [], 'published': []}
    return json.loads(PATH.read_text(encoding='utf-8'))
def save_memory(memory):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding='utf-8')
