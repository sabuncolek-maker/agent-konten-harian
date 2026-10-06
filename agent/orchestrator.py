import json
from agent.brain import RateLimitError
from agent.memory import load_memory,save_memory
from agent.state import AgentState
from tools.web import search_web
from tools.topic import choose_topic
from tools.quotes import find_quotes,choose_quote
from tools.verification import verify_quote
from tools.content import generate_content
from tools.evaluator import evaluate_content,parse_evaluation
from tools.image import generate_image_prompt
from tools.publisher import publish
def run(goal):
 s=AgentState(goal=goal); mem=load_memory()
 try:
  s.log("Mengamati kondisi Indonesia."); ev=search_web(goal,10)
  if not ev: raise RuntimeError("Riset web tidak menghasilkan bukti.")
  s.topic,s.context=choose_topic(goal,ev,mem.get("used_topics",[])); s.log(f"Kondisi terpilih: {s.topic}")
  s.log("Mencari quote dari tokoh/pendahulu."); c=find_quotes(s.topic,s.context,mem.get("used_quotes",[]))
  if not c: raise RuntimeError("Tidak menemukan kandidat quote.")
  q=choose_quote(c,s.context)
  if not q: raise RuntimeError("Tidak ada kandidat quote yang layak.")
  s.person,s.quote,s.source=q["person"],q["quote"],q["url"]; s.log(f"Kandidat quote: {s.person} — {s.quote}")
  s.verification=verify_quote(s.person,s.quote,s.source)
  if json.loads(s.verification).get("status")!="VERIFIED": s.status="STOPPED_QUOTE_NOT_VERIFIED"; s.log("Quote tidak terverifikasi; agent berhenti."); save_memory(mem); return s
  for attempt in range(3):
   s.content=generate_content(s.topic,s.context,s.person,s.quote,s.verification); s.evaluation=evaluate_content(s.topic,s.quote,s.content); score,decision,_=parse_evaluation(s.evaluation); s.log(f"Evaluasi {score}/100 — {decision}")
   if decision=="PASS" and score>=75: break
   if attempt==2: s.status="STOPPED_CONTENT_FAILED"; save_memory(mem); return s
  s.image_prompt=generate_image_prompt(s.content); s.status=publish(s.content).get("status","READY")
  mem.setdefault("used_quotes",[]).append(s.quote); mem.setdefault("used_topics",[]).append(s.topic); mem.setdefault("published",[]).append({"topic":s.topic,"person":s.person,"quote":s.quote,"source":s.source,"status":s.status}); save_memory(mem); return s
 except RateLimitError as e: s.status="RATE_LIMITED"; s.log(str(e)); save_memory(mem); return s
 except Exception as e: s.status="ERROR"; s.log(f"Error: {type(e).__name__}: {e}"); save_memory(mem); return s
