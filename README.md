# Agent Konten Harian — Kutipan

## STEP 3 — Research Internet

Pada tahap ini mock data dari STEP 2 diganti dengan research nyata.

Alurnya:

```
Goal
  ↓
Agent
  ↓
Agent memilih research_topic + membuat query
  ↓
Research Tool
  ↓
Groq Web Search
  ↓
Hasil internet
  ↓
Agent
  ↓
Memilih topik paling potensial
```

### Teknologi research

Research menggunakan **Groq Web Search** melalui model `groq/compound`, sehingga aplikasi tidak perlu menambahkan API search pihak ketiga pada tahap ini.

Groq mendukung built-in web search dan model `groq/compound` untuk melakukan pencarian web. 

### Menjalankan

```bash
pip install -r requirements.txt
python main.py
```

Pastikan `.env` berisi:

```
GROQ_API_KEY=API_KEY_KAMU
```

### Output yang diharapkan

Agent akan menghasilkan keputusan seperti:

```
TOOL: research_topic
QUERY: topik yang sedang ramai dan relevan di Indonesia untuk konten quote
```

Kemudian research tool benar-benar mencari informasi di internet dan hasilnya diberikan kembali kepada agent.

### Belum dilakukan

- mencari quote tokoh
- verifikasi quote
- membuat gambar
- evaluator
- database
- publish Instagram

Itu akan ditambahkan bertahap pada step berikutnya.
