# 🤖 AI Content Agent — Multi-Niche, Config-Driven

Satu kode, banyak niche. Ganti niche = ganti file config, **tanpa ubah kode**.

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

## Cara Pakai (Lokal)

```bash
# 1. Install
pip install -r requirements.txt
playwright install chromium

# 2. Isi kredensial
cp .env.example .env
# lalu edit .env: GROQ_API_KEY, IG_USER_ID, IG_ACCESS_TOKEN, IMGBB_API_KEY

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
2. Tambahkan secrets: `GROQ_API_KEY`, `IG_USER_ID`, `IG_ACCESS_TOKEN`, `IMGBB_API_KEY`
3. Workflow `.github/workflows/daily.yml` jalan otomatis tiap hari 07:00 WIB

## Struktur

```
config/          # 1 file YAML per niche
agent/           # inti: config_loader, brain (LLM), orchestrator, state, memory
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
