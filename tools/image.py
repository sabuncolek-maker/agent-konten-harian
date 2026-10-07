"""Render tiap slide jadi gambar PNG 1080x1350 pakai Playwright.

KENAPA Playwright (bukan PIL manual):
- Template HTML/CSS jauh lebih fleksibel untuk desain rapi (gradient,
  tipografi, dsb) dibanding menggambar piksel per piksel dengan PIL.
- Hasilnya konsisten seperti "desain web", bukan gambar buatan kode.

KENAPA ukuran 1080x1350: itu rasio 4:5, ukuran optimal carousel Instagram
(memenuhi layar HP tanpa kepotong).
"""

from pathlib import Path
from jinja2 import Template

WIDTH, HEIGHT = 1080, 1350
TEMPLATE_PATH = Path(__file__).parent / "template_carousel.html"


def render_slides(slides: list, niche_label: str, out_dir: str = "data/slides") -> list:
    """Render setiap teks slide jadi file PNG. Kembalikan list path file.

    Jumlah slide DINAMIS — mengikuti panjang list `slides` (aturan keras #4).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))

    # Bersihkan hasil render lama supaya tidak tercampur dengan run baru.
    for old in out.glob("slide_*.png"):
        old.unlink()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright belum terinstall. Jalankan: pip install playwright && playwright install chromium"
        ) from exc

    paths = []
    total = len(slides)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        for i, text in enumerate(slides, start=1):
            html = template.render(
                slide_text=text,
                slide_num=i,
                total_slides=total,
                niche_label=niche_label,
                pct=int(i / total * 100),
            )
            page.set_content(html)
            path = out / f"slide_{i}.png"
            page.screenshot(path=str(path))
            paths.append(str(path))
            print(f"[IMAGE] slide {i}/{total} → {path}", flush=True)
        browser.close()
    return paths
