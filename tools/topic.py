import json
from agent.brain import ask,FAST_MODEL
def choose_topic(goal,evidence,used):
 compact="\n".join(f"[{i}] {x['title']} | {x['snippet']} | {x['url']}" for i,x in enumerate(evidence,1))
 raw=ask(f"""Pilih satu kondisi/isu aktual Indonesia yang paling relevan untuk konten quote.\nTujuan: {goal}\nTopik yang sudah dipakai: {used}\nGunakan hanya bukti di bawah. Jangan mengarang fakta/URL.\nJawab JSON: {{"topic":"","context":"","facts":[],"source_urls":[]}}\nBUKTI:\n{compact}""",FAST_MODEL,900)
 data=json.loads(raw[raw.find("{"):raw.rfind("}")+1]); return data["topic"].strip(),json.dumps(data,ensure_ascii=False)
