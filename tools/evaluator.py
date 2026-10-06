import re
from agent.brain import ask, FAST_MODEL

def evaluate_content(content: str) -> str:
    return ask(f"""Kamu adalah editor quality-control untuk konten Instagram Indonesia.

Evaluasi draft di bawah secara objektif. Fokus pada:
- hook dan daya tarik
- relevansi Indonesia
- hubungan TOPIK dengan QUOTE
- akurasi quote dan atribusi
- risiko misleading
- keterbacaan
- kualitas caption dan CTA

JANGAN mengarang fakta baru.
JANGAN mempertanyakan hal yang sudah jelas di bagian verifikasi kecuali ada konflik nyata.

WAJIB jawab PERSIS dalam format berikut. Baris SCORE dan DECISION harus selalu ada dan harus berupa angka/status yang valid:

SCORE: <0-100>
DECISION: <PASS atau FAIL>
ISSUES: <maksimal 3 masalah konkret; tulis NONE jika tidak ada>
REVISION: <maksimal 3 instruksi perbaikan konkret; tulis NONE jika tidak ada>

Aturan keputusan:
- PASS hanya jika score >= 75 dan tidak ada masalah faktual/atribusi yang serius.
- FAIL jika ada masalah serius atau score < 75.

KONTEN:
{content}""", model=FAST_MODEL, max_tokens=500)

def parse_evaluation(result: str) -> tuple[int, str, str]:
    score_match = re.search(r"(?im)^\s*SCORE\s*:\s*(\d{1,3})\s*$", result)
    decision_match = re.search(r"(?im)^\s*DECISION\s*:\s*(PASS|FAIL)\s*$", result)
    score = max(0, min(100, int(score_match.group(1)))) if score_match else 0
    decision = decision_match.group(1).upper() if decision_match else "FAIL"
    return score, decision, result
