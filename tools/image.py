from agent.brain import ask, FAST_MODEL

def generate_image_prompt(content: str) -> str:
    return ask(
        f"""Buat prompt visual premium untuk gambar Instagram rasio 4:5 berdasarkan konten berikut.
Fokus pada subjek, suasana, komposisi, pencahayaan, dan ruang aman untuk tipografi.
Jangan menambahkan quote baru atau mengubah makna.

KONTEN:
{content}""",
        model=FAST_MODEL,
        max_tokens=650,
    )
