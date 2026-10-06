from agent.brain import ask,FAST_MODEL
def generate_image_prompt(content):
 return ask(f"""Buat prompt gambar Instagram berdasarkan konten berikut. Fokus visual, suasana, komposisi dan ruang untuk teks saat editing. Jangan membuat tulisan di gambar.\n{content}""",FAST_MODEL,500)
