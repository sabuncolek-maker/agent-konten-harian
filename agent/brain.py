"""Klien LLM multi-provider: Groq, Gemini, OpenRouter.

CARA PAKAI (via environment variables / GitHub Secrets):
    LLM_PROVIDER=groq        → pakai Groq (GROQ_API_KEY wajib)
    LLM_PROVIDER=gemini      → pakai Google Gemini (GEMINI_API_KEY wajib)
    LLM_PROVIDER=openrouter  → pakai OpenRouter (OPENROUTER_API_KEY wajib)
    LLM_MODEL=<nama-model>   → opsional, timpa model default tiap provider

KENAPA dibuat dinamis (bukan hardcode Groq):
- User bebas pilih AI sesuai kebutuhan/budget tanpa ubah kode.
- Kalau satu provider limit/error, tinggal ganti secret → jalan lagi.
- Semua provider diseragamkan lewat satu fungsi ask() — kode lain
  (niches/, tools/) tidak perlu tahu AI apa yang dipakai di belakang.

KENAPA validasi API key dilakukan saat fungsi dipanggil (lazy), bukan saat import:
- Kalau dicek saat import, maka `import brain` saja sudah crash kalau key belum diset.
- Akibatnya: tidak bisa unit-test fungsi lain, tidak bisa jalanin --help, dsb.
"""

import os

# Model default tiap provider (bisa ditimpa via LLM_MODEL).
# Dipilih yang gratis/murah & cukup pintar untuk generate konten.
_DEFAULT_MODELS = {
    "groq": "gpt-oss-120b",
    "gemini": "gemini-2.0-flash",
    "openrouter": "google/gemma-4-31b-it:free",  # update Okt 2026: deepseek free sudah tidak tersedia
}

# Model gratis cadangan untuk OpenRouter (urutan prioritas).
# KENAPA: model gratis berbagi rate limit publik — kalau satu penuh (429)
# atau hilang (404), otomatis coba yang berikutnya tanpa campur tangan user.
_FALLBACK_FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "thinkingmachines/inkling:free",
]


def _get_provider() -> str:
    """Baca provider dari env. Default: groq (kompatibel dengan setup lama)."""
    provider = os.environ.get("LLM_PROVIDER", "groq").strip().lower()
    if provider not in _DEFAULT_MODELS:
        raise RuntimeError(
            f"LLM_PROVIDER '{provider}' tidak dikenal. "
            f"Pilih salah satu: {', '.join(_DEFAULT_MODELS)}"
        )
    return provider


def _get_model(provider: str) -> str:
    """Model dari env LLM_MODEL, atau default per provider."""
    return os.environ.get("LLM_MODEL", "").strip() or _DEFAULT_MODELS[provider]


def _ask_groq(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """Kirim prompt via Groq (gratis): https://console.groq.com"""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY belum diset. Isi di .env atau GitHub Secrets. "
            "Dapatkan gratis di https://console.groq.com"
        )
    from groq import Groq  # import di sini: kalau package belum install, error-nya jelas
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()


def _ask_gemini(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """Kirim prompt via Google Gemini (ada free tier): https://aistudio.google.com"""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY belum diset. Isi di .env atau GitHub Secrets. "
            "Dapatkan di https://aistudio.google.com/apikey"
        )
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model)
    resp = gen_model.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
    )
    return (resp.text or "").strip()


def _ask_openrouter(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """Kirim prompt via OpenRouter (1 API untuk ratusan model): https://openrouter.ai

    KENAPA pakai package `openai`: OpenRouter sengaja dibuat kompatibel dengan
    format API OpenAI, jadi cukup arahkan base_url ke server mereka.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY belum diset. Isi di .env atau GitHub Secrets. "
            "Dapatkan di https://openrouter.ai/keys"
        )
    import time
    from openai import OpenAI, RateLimitError, NotFoundError
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # Susun daftar coba: model utama dulu, lalu cadangan (tanpa duplikat).
    # KENAPA: tier gratis sering 429 (penuh) / 404 (model ditarik) — daripada
    # run gagal total, coba model gratis lain secara otomatis.
    candidates = [model] + [m for m in _FALLBACK_FREE_MODELS if m != model]

    # KENAPA ada ronde ulang: rate limit gratisan biasanya pulih dalam
    # puluhan detik. Daripada gagal, tunggu 30 detik lalu coba semua lagi
    # (maksimal 3 ronde).
    last_err = None
    for round_no in range(1, 4):
        for cand in candidates:
            try:
                resp = client.chat.completions.create(
                    model=cand,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text = (resp.choices[0].message.content or "").strip()
                if cand != model:
                    print(f"[LLM] fallback: {model} gagal, pakai {cand}", flush=True)
                return text
            except (RateLimitError, NotFoundError) as exc:
                print(f"[LLM] {cand} tidak bisa dipakai ({type(exc).__name__}), coba berikutnya...",
                      flush=True)
                last_err = exc
        if round_no < 3:
            print(f"[LLM] ronde {round_no} habis, tunggu 30 detik sebelum coba lagi...",
                  flush=True)
            time.sleep(30)
    raise RuntimeError(
        f"Semua model gratis habis/tidak tersedia setelah 3 ronde. Terakhir: {last_err}"
    )


# Peta provider → fungsi pengirimnya. Nambah provider baru = tambah 1 baris + 1 fungsi.
_SENDER = {
    "groq": _ask_groq,
    "gemini": _ask_gemini,
    "openrouter": _ask_openrouter,
}


def ask(prompt: str, model: str = "", temperature: float = 0.7,
        max_tokens: int = 1500) -> str:
    """Kirim satu prompt ke LLM, kembalikan teks jawabannya.

    Provider & model diambil dari env (LLM_PROVIDER, LLM_MODEL).
    Parameter `model` di sini opsional: kalau diisi, menimpa env untuk
    panggilan ini saja (berguna untuk pakai model khusus di satu langkah).

    Raises:
        RuntimeError: kalau provider tidak dikenal, API key belum diset,
            atau LLM mengembalikan teks kosong.
    """
    provider = _get_provider()
    use_model = model.strip() or _get_model(provider)
    print(f"[LLM] {provider}/{use_model} ...", flush=True)
    text = _SENDER[provider](prompt, use_model, temperature, max_tokens)
    if not text:
        raise RuntimeError(f"Model {use_model} mengembalikan jawaban kosong.")
    print(f"[LLM] {use_model} OK ({len(text)} karakter)", flush=True)
    return text
