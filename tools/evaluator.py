from agent.brain import ask

def evaluate_content(content):
    return ask(f'''Evaluasi draft Instagram berikut. Periksa hook, relevansi Indonesia, atribusi, akurasi, risiko misleading, dan daya tarik. Berikan SCORE 0-100, PASS/FAIL, alasan, dan perbaikan.
KONTEN:
{content}''')
