# Agent Konten Harian — Kutipan

## STEP 2 — Agent + Tool

Alur tahap ini:

Goal → Agent → pilih tool → Python menjalankan tool → hasil kembali ke Agent → Agent mengambil keputusan.

Tool pertama adalah `research_topic()`. Saat ini tool memakai **mock data** (data contoh), bukan internet/API nyata. Tujuannya menguji mekanisme agent terlebih dahulu.

Jalankan:

```bash
pip install -r requirements.txt
python main.py
```

Tahap berikutnya: mengganti mock research dengan research tool/API nyata.
