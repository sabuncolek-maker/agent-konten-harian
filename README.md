# Agent Konten Harian — Kutipan

## STEP 4 — Quote Research + Verification

Agent sekarang memiliki tiga tool utama:

- `research_topic` → mencari topik aktual.
- `research_quotes` → mencari kandidat quote yang relevan.
- `verify_quote` → melakukan fact-checking atribusi quote.

Alur:

```
Goal
 ↓
Research Topic
 ↓
Agent memilih topik
 ↓
Research Quotes
 ↓
Agent memilih kandidat
 ↓
Verify Quote
 ↓
Agent
 ├── APPROVE
 ├── RESEARCH_ANOTHER_QUOTE
 └── REJECT
```

### Prinsip verifikasi

Quote **tidak dianggap benar hanya karena sering muncul di internet**.

Agent diminta mencari sumber primer bila memungkinkan, seperti buku, pidato, transkrip, wawancara, arsip, atau penerbit.

Status verifikasi:

- **VERIFIED** → boleh digunakan sebagai direct quote.
- **UNCERTAIN** → jangan digunakan sebagai direct quote.
- **REJECTED** → jangan digunakan.

### Menjalankan

```bash
pip install -r requirements.txt
python main.py
```

Pastikan `.env` berisi `GROQ_API_KEY`.

Tahap ini belum membuat gambar atau mempublikasikan konten. Fokusnya adalah memastikan agent memiliki pipeline riset dan verifikasi quote sebelum masuk ke produksi konten.
