# Agent Konten Harian — Kutipan

Tahap 1 proyek AI Agent konten kutipan.

## Tujuan tahap 1

Membuktikan alur dasar:

**Goal → AI → rencana**

Pada tahap ini belum ada research API, generator gambar, evaluator, database, atau publisher.

## Menjalankan lokal

1. Buat environment Python.
2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Salin `.env.example` menjadi `.env`.
4. Isi `GROQ_API_KEY` dengan API key Groq.
5. Jalankan:

```bash
python main.py
```

## Catatan

Jangan commit file `.env`. File tersebut sudah masuk `.gitignore`.

Tahap berikutnya adalah membuat **tool-calling**, sehingga agent dapat memilih dan menjalankan tools seperti research topic, bukan hanya menghasilkan teks.
