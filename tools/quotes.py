import json
from agent.brain import ask,FAST_MODEL
from tools.web import search_web,fetch_page_text
def find_quotes(topic,context,used):
 raw=ask(f"""Buat 5 query web untuk menemukan kutipan asli dari tokoh atau pendahulu yang relevan. Tema: {topic}\nKonteks: {context}\nJangan membuat nama tokoh atau kutipan. JSON saja: {{"queries":["","","","",""]}}""",FAST_MODEL,500)
 data=json.loads(raw[raw.find("{"):raw.rfind("}")+1]); results=[]; seen=set()
 for q in data.get("queries",[]):
  for x in search_web(str(q),5):
   if x["url"] not in seen: seen.add(x["url"]); results.append(x)
 return results[:20]
def choose_quote(candidates,context):
 compact="\n".join(f"[{i}] {x['title']} | {x['snippet']} | {x['url']}" for i,x in enumerate(candidates,1))
 raw=ask(f"""Pilih satu halaman sumber yang paling mungkin memuat kutipan langsung dari tokoh nyata. Jangan menulis kutipan berdasarkan snippet. Jika tidak ada, indeks 0.\nKonteks: {context}\nKANDIDAT:\n{compact}\nJSON: {{"index":0}}""",FAST_MODEL,300)
 idx=int(json.loads(raw[raw.find("{"):raw.rfind("}")+1])["index"])
 if idx<1 or idx>len(candidates): return None
 page=candidates[idx-1]; body=fetch_page_text(page["url"])
 if not body: return None
 raw2=ask(f"""Ekstrak satu kutipan yang benar-benar tertulis di halaman berikut. Jangan parafrase dan jangan melengkapi kata. Jika tidak jelas, kosongkan. JSON: {{"person":"","quote":""}}\nPAGE:\n{body}""",FAST_MODEL,700)
 data=json.loads(raw2[raw2.find("{"):raw2.rfind("}")+1])
 if not data.get("person") or not data.get("quote"): return None
 return {"person":data["person"].strip(),"quote":data["quote"].strip(),"url":page["url"]}
