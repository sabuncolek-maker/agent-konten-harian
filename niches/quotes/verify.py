"""Tahap VERIFY untuk niche kutipan.

Tugas: memastikan kutipan yang digenerate benar-benar berasal dari tokoh
tersebut, BUKAN karangan AI.

KENAPA ini tahap paling penting (pelajaran dari audit repo lama):
- LLM tidak browsing — dia menjawab dari "hafalan", dan terkenal suka
  mengarang kutipan yang terdengar meyakinkan tapi palsu (halusinasi).
- Memposting kutipan palsu = bom waktu reputasi. Followers yang paham
  akan protes, kredibilitas akun hancur.

Strategi verifikasi di sini KONSERVATIF: kalau ragu → TOLAK.
Ragu = tidak lolos. Lebih baik tidak posting sehari daripada posting hoaks.
"""

from agent import brain


def run(state, cfg, memory) -> None:
    """Verifikasi tiap slide yang mengandung klaim kutipan."""
    full_text = "\n".join(state.slides)

    # FAST-PATH: kutipan dari bank sudah terverifikasi kebenarannya.
    # KENAPA tidak pakai LLM di sini: verifier LLM bersikap "ragu = tolak",
    # sehingga bisa menolak kutipan bank yang valid (false negative).
    # Cukup pastikan LLM tidak mengubah kutipan saat generate.
    bank_quote = getattr(state, "verified_quote", "") or ""
    if bank_quote.strip():
        norm_q = " ".join(bank_quote.split())
        norm_t = " ".join(full_text.split())
        if norm_q in norm_t:
            state.verification = "VERIFIED"
            print("[VERIFY] lolos (kutipan bank muncul persis di slide)", flush=True)
        else:
            state.verification = (
                "REJECTED: kutipan bank tidak muncul persis di slide "
                "(kemungkinan diubah/diparafrasa saat generate)"
            )
            print(f"[VERIFY] DITOLAK: {state.verification}", flush=True)
        return

    # FALLBACK: verifikasi LLM untuk alur non-bank (atau bank kosong).

    # Langkah 1: minta LLM memeriksa dirinya sendiri dengan peran berbeda.
    # KENAPA 2 peran: LLM yang menulis cenderung "membela" tulisannya sendiri.
    # Verifikator independen (prompt berbeda) lebih objektif.
    prompt = (
        "Kamu adalah fact-checker yang SKEPTIS dan KETAT. "
        "Periksa teks carousel berikut. Untuk setiap kutipan yang diklaim "
        "berasal dari tokoh tertentu, nilai: apakah kutipan ini benar-benar "
        "dikenal luas sebagai perkataan tokoh tersebut, atau kemungkinan "
        "karangan/parafrasa bebas?\n\n"
        f"TOKOH: {state.subject}\nTEKS:\n{full_text}\n\n"
        "Jawab HANYA JSON valid:\n"
        '{"verdict": "VERIFIED" atau "REJECTED", '
        '"reason": "<1 kalimat alasan>"}'
        "\nAturan: kalau tidak yakin 100%, jawab REJECTED."
    )
    raw = brain.ask(prompt, model=cfg["llm"]["model"], temperature=0.2,
                    max_tokens=500)

    import json
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        state.verification = "REJECTED: verifikator tidak mengembalikan JSON"
        return
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        state.verification = "REJECTED: JSON verifikator tidak valid"
        return

    verdict = str(data.get("verdict", "")).upper()
    reason = data.get("reason", "tanpa alasan")
    if verdict == "VERIFIED":
        state.verification = "VERIFIED"
        print(f"[VERIFY] lolos: {reason}", flush=True)
    else:
        # KENAPA REJECTED menghentikan pipeline: orchestrator akan membatalkan
        # run ini. Lebih aman daripada memaksa posting konten meragukan.
        state.verification = f"REJECTED: {reason}"
        print(f"[VERIFY] DITOLAK: {reason}", flush=True)
