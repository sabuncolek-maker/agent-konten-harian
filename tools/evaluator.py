import re
from agent.brain import ask

def evaluate_content(content: str) -> str:
    return ask(
        f"""Evaluasi draft konten Instagram berikut secara ketat.

Periksa:
- hook
- relevansi Indonesia
- akurasi quote dan atribusi
- potensi misleading
- keterbacaan
- daya tarik
- caption

Jawab dengan format:
SCORE: 0-100
DECISION: PASS atau FAIL
ISSUES: ...
REVISION: ...

KONTEN:
{content}"""
    )

def parse_evaluation(result: str) -> tuple[int, str, str]:
    score_match = re.search(r"SCORE\s*:\s*(\d+)", result, re.I)
    decision_match = re.search(r"DECISION\s*:\s*(PASS|FAIL)", result, re.I)
    score = int(score_match.group(1)) if score_match else 0
    decision = decision_match.group(1).upper() if decision_match else "FAIL"
    return score, decision, result
