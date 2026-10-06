# Agent Konten Harian — Kutipan

Agent yang mencari kondisi aktual Indonesia, menemukan kutipan tokoh yang relevan, memverifikasi atribusinya, lalu menyusun konten Instagram.

## Alur

```
Riset berita Indonesia (Google News, fallback DuckDuckGo/Bing)
 ↓
Pilih topik
 ↓
Cari halaman sumber kutipan → ekstrak quote dari halaman
 ↓
Verifikasi quote
 ├── VERIFIED   → lanjut
 └── UNCERTAIN / REJECTED → berhenti
 ↓
Buat konten → evaluasi (maks. 3 percobaan, skor minimal 75)
 ↓
Buat prompt gambar → publish (belum dikonfigurasi)
```

Quote hanya dipakai bila berstatus **VERIFIED**. Quote yang muncul di banyak situs tidak otomatis dianggap benar.

Topik dan quote yang sudah dipakai disimpan di `data/memory.json` agar tidak berulang.

## Menjalankan

```bash
pip install -r requirements.txt
cp .env.example .env   # isi YTCLIP_API_KEY
python main.py
```

Workflow harian ada di `.github/workflows/daily-agent.yml` (butuh secret `YTCLIP_API_KEY`).

Tahap publikasi ke Instagram belum diimplementasikan (`tools/publisher.py` masih stub).
