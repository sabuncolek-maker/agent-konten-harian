from agent.brain import ask,MODEL
def generate_content(topic,context,person,quote,verification):
 return ask(f"""Buat satu konten Instagram quote berbahasa Indonesia.\nKONDISI: {topic}\nKONTEKS: {context}\nTOKOH: {person}\nQUOTE: {quote}\nVERIFIKASI: {verification}\nHubungkan quote dengan kondisi sebagai interpretasi, bukan seolah tokoh sedang membahas kondisi tersebut. Quote harus 100% sama. Jangan membuat fakta baru. Output: HOOK, QUOTE, ATRIBUSI, KONTEKS, CAPTION, CTA. Ringkas dan natural.""",MODEL,1000)
