"""Wadah data yang dibawa agent sepanjang pipeline.

KENAPA pakai dataclass:
- Semua tahap (research → generate → verify → evaluate → publish) butuh akses
  ke data yang sama. Tanpa wadah resmi, data dioper via banyak variabel
  lepas → gampang typo & susah dilacak.
- Dataclass = struktur data yang rapi + tetap sederhana (bukan class berat).
"""

from dataclasses import dataclass, field


@dataclass
class AgentState:
    """Satu objek ini dibawa dari awal sampai akhir pipeline."""

    niche: str = ""            # nama niche aktif, misal "quotes"
    topic: str = ""            # topik/isu yang dipilih tahap research
    subject: str = ""          # subjek utama (tokoh / objek fakta)
    content: str = ""          # isi konten final (teks per slide)
    slides: list = field(default_factory=list)  # list teks per slide
    caption: str = ""          # caption Instagram
    verification: str = ""     # hasil verifikasi ("VERIFIED" / "REJECTED: alasan")
    score: int = 0             # skor evaluasi 0-100
    published: bool = False    # True HANYA jika publisher return True
    error: str = ""            # pesan error kalau pipeline gagal di tengah
    rejected_subjects: list = field(default_factory=list)  # tokoh yang ditolak verifikasi di run ini (ide A)
