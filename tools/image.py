from agent.brain import ask

def generate_image_prompt(content: str) -> str:
    return ask(
        f"""Buat prompt visual untuk gambar Instagram rasio 4:5 berdasarkan konten berikut.
Fokus pada visual yang relevan dengan makna quote, desain premium, tipografi jelas, ruang aman untuk teks, dan tanpa teks tambahan yang mengubah quote.
KONTEN:
{content}"""
    )
