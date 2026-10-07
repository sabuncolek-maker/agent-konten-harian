"""Klien LLM via Groq.

KENAPA validasi API key dilakukan saat fungsi dipanggil (lazy), bukan saat import:
- Kalau dicek saat import, maka `import brain` saja sudah crash kalau key belum diset.
- Akibatnya: tidak bisa unit-test fungsi lain, tidak bisa jalanin --help, dsb.
- Dengan lazy check, error baru muncul saat benar-benar mau pakai LLM — dan
  pesannya jelas memberitahu apa yang kurang.
"""

import os

_client = None  # dibuat sekali saja (singleton sederhana), hemat koneksi


def _get_client():
    """Buat (atau pakai ulang) klien Groq. Validasi API key DI SINI, bukan di import."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY belum diset. "
            "Buat file .env dari .env.example lalu isi GROQ_API_KEY. "
            "Dapatkan gratis di https://console.groq.com"
        )

    from groq import Groq  # import di sini: kalau package belum install, error-nya jelas
    _client = Groq(api_key=api_key)
    return _client


def ask(prompt: str, model: str = "gpt-oss-120b", temperature: float = 0.7,
        max_tokens: int = 1500) -> str:
    """Kirim satu prompt ke LLM, kembalikan teks jawabannya.

    Raises:
        RuntimeError: kalau API key belum diset atau LLM mengembalikan teks kosong.
    """
    client = _get_client()
    print(f"[LLM] {model} ...", flush=True)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    text = (resp.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError(f"Model {model} mengembalikan jawaban kosong.")
    print(f"[LLM] {model} OK ({len(text)} karakter)", flush=True)
    return text
