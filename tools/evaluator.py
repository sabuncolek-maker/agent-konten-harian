import re
from agent.brain import ask, FAST_MODEL

def evaluate_content(content: str) -> str:
    return ask(f"""Evaluasi draft Instagram secara ketat.

Periksa:
- hook
- relevansi Indonesia
- akurasi quote dan atribusi
- potensi misleading
- keterbacaan
- daya tarik
- kualitas caption

Jawab tanpa markdown pada label:
SCORE: 0-100
DECISION: PASS atau FAIL
ISSUES: ...
REVISION: ...

KONTEN:
{content}""", model=FAST_MODEL, max_tokens=700)

def parse_evaluation(result: str) -> tuple[int, str, str]:
    score_match = re.search(r"SCORE\s*:?\s*(\d{1,3})", result, re.I)
    decision_match = re.search(r"DECISION\s*:?\s*(PASS|FAIL)", result, re.I)
    score = int(score_match.group(1)) if score_match else 0
    decision = decision_match.group(1).upper() if decision_match else "FAIL"
    return score, decision, result
