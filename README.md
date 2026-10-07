# 🤖 AI Content Agent — Multi-Niche, Multi-AI, Config-Driven

Satu kode, banyak niche, banyak AI. Ganti niche = ganti file config. Ganti AI = ganti secret. **Tanpa ubah kode.**

## Cara Kerja

```
research → generate → verify → evaluate → render → publish → simpan memory
```

1. **research** — pilih topik & subjek (lewati yang sudah pernah dipakai)
2. **generate** — buat draf carousel via LLM (jumlah slide dinamis)
3. **verify** — verifikasi konservatif: ragu = tolak, run dibatalkan dengan aman
4. **evaluate** — skor 0-100, harus ≥ 75 (coba ulang maks 3x)
5. **render** — tiap slide jadi gambar 1080×1350 via Playwright
6. **publish** — posting carousel ke Instagram via Graph API
7. **memory** — riwayat disimpan **HANYA jika publish sukses** ⚠️

## 🤖 Pilih AI Sesukamu (Multi-Provider)

Agent ini tidak dikunci ke satu AI. Pilih via environment variable `LLM_PROVIDER`:

| Provider | Secret yang dibutuhkan | Model default | Gratis? |
|----------|----------------------|---------------|---------|
| `groq` (default) | `GROQ_API_KEY` | `gpt-oss-120b` | ✅ Gratis |
| `gemini` | `GEMINI_API_KEY` | `gemini-2.0-flash` | ✅ Free tier |
| `openrouter` | `OPENROUTER_API_KEY` | `deepseek/deepseek-chat:free` | ✅ Banyak model gratis |

Mau pakai model khusus? Set `LLM_MODEL` (opsional, menimpa default):
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=anthropic/claude-3.5-sonnet   # contoh model berbayar
```

**Kenapa dinamis?** Kalau satu provider limit/error, tinggal ganti secret → jalan lagi. Semua kode lain tidak perlu diubah karena semua panggilan LLM lewat satu pintu (`agent/brain.py`).

## Cara Pakai (Lokal)

```bash
# 1. Install
pip install -r requirements.txt
playwright install chromium

# 2. Isi kredensial
cp .env.example .env
# lalu edit .env:
#   LLM_PROVIDER=groq          # atau: gemini / openrouter
#   GROQ_API_KEY=...           # sesuai provider pilihan
#   IG_USER_ID, IG_ACCESS_TOKEN, IMGBB_API_KEY

# 3. Jalanin
python main.py --config config/quotes.yaml   # niche kutipan
python main.py --config config/facts.yaml    # niche fakta unik
```

## Cara Tambah Niche Baru (misal: `pantun`)

1. Buat folder `niches/pantun/` berisi `research.py`, `generate.py`, `verify.py`
   (tiap file punya fungsi `run(state, cfg, memory)` — contoh di `niches/quotes/`)
2. Buat file `config/pantun.yaml` (contoh di `config/quotes.yaml`)
3. Jalanin: `python main.py --config config/pantun.yaml`

Tidak perlu ubah `orchestrator.py` sama sekali — niche di-load dinamis.

## Setup GitHub Actions

1. Buka repo → **Settings → Secrets and variables → Actions**
2. Tambahkan secrets:
   - **AI (pilih salah satu):** `GROQ_API_KEY` / `GEMINI_API_KEY` / `OPENROUTER_API_KEY`
   - **Opsional:** `LLM_PROVIDER` (default: `groq`), `LLM_MODEL`
   - **Instagram:** `IG_USER_ID`, `IG_ACCESS_TOKEN`, `IMGBB_API_KEY`
3. Buat file `.github/workflows/daily.yml` manual ([contoh isi](https://github.com/sabuncolek-maker/agent-konten-harian)) — jalan otomatis tiap hari 07:00 WIB

> ⚠️ File workflow harus dibuat manual via web GitHub (GitHub App tidak punya akses ke folder `.github/workflows/`).

## Struktur

```
config/          # 1 file YAML per niche
agent/           # inti: config_loader, brain (multi-provider LLM),
                 #       orchestrator, state, memory
niches/          # 1 folder per niche: research.py, generate.py, verify.py
tools/           # publisher (IG), image (render), evaluator (skor)
data/            # memory.json (riwayat) — dibuat otomatis
```

## Aturan Keras (dari audit)

1. Memory disimpan HANYA setelah publish sukses
2. Publisher return True/False jujur — tidak ada silent failure
3. JSON dari LLM selalu divalidasi sebelum dipakai
4. Jumlah slide dinamis, tidak hardcode
5. Tidak ada kredensial hardcoded — semua via env vars
6. Semua dependency di-pin versinya di `requirements.txt`
