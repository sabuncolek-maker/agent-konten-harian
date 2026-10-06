import html,time
from urllib.parse import quote_plus,unquote
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
def _ddg(page,limit):
 s=BeautifulSoup(page,"html.parser"); out=[]
 for a in s.select(".result__a")[:limit]:
  href=unquote(a.get("href","")); box=a.parent.parent; sn=box.select_one(".result__snippet")
  if href.startswith(("http://","https://")): out.append({"title":html.unescape(a.get_text(" ",strip=True)),"snippet":html.unescape(sn.get_text(" ",strip=True) if sn else ""), "url":href.split("#")[0]})
 return out
def search_web(query,limit=10):
 for attempt in range(3):
  try:
   req=Request("https://html.duckduckgo.com/html/?q="+quote_plus(query),headers={"User-Agent":UA})
   with urlopen(req,timeout=20) as r: out=_ddg(r.read().decode("utf-8","ignore"),limit)
   if out: print(f"[WEB] search OK | {len(out)} results",flush=True); return out
  except Exception as e: print(f"[WEB] search failed: {e}",flush=True)
  time.sleep(attempt+1)
 return []
def fetch_page_text(url,max_chars=16000):
 try:
  req=Request(url,headers={"User-Agent":UA})
  with urlopen(req,timeout=15) as r: raw=r.read(300000).decode("utf-8","ignore")
  soup=BeautifulSoup(raw,"html.parser")
  for n in soup(["script","style","noscript","svg"]): n.decompose()
  return " ".join(soup.stripped_strings)[:max_chars]
 except Exception as e: print(f"[WEB] fetch failed {url}: {e}",flush=True); return ""
