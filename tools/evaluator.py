import re
from agent.brain import ask,FAST_MODEL
def evaluate_content(topic,quote,content):
 return ask(f"""Nilai konten secara objektif. Fokus hook, relevansi, hubungan quote-kondisi, akurasi quote, misleading, keterbacaan.\nTOPIK:{topic}\nQUOTE:{quote}\nKONTEN:{content}\nFormat wajib:\nSCORE: <0-100>\nDECISION: <PASS/FAIL>\nREVISION: <maks 3 poin>""",FAST_MODEL,450)
def parse_evaluation(raw):
 m=re.search(r"(?im)^\s*SCORE\s*:\s*(\d+)",raw); d=re.search(r"(?im)^\s*DECISION\s*:\s*(PASS|FAIL)",raw); return (min(100,int(m.group(1))) if m else 0,d.group(1) if d else "FAIL",raw)
