"""Posting carousel ke Instagram via Meta Graph API.

Alur resmi Instagram Content Publishing (carousel):
  1. Upload tiap gambar ke host publik (Graph API hanya terima URL publik,
     tidak bisa terima file lokal) → dapat image_url
  2. Untuk tiap gambar: POST /{ig-id}/media?image_url=...&is_carousel_item=true
     → dapat container ID per gambar
  3. POST /{ig-id}/media?media_type=CAROUSEL&children=id1,id2,...&caption=...
     → dapat carousel container ID
  4. Tunggu container berstatus FINISHED (polling, ada batas waktu!)
  5. POST /{ig-id}/media_publish?creation_id=... → TERBIT

ATURAN KERAS #2: fungsi ini return True/False yang JUJUR.
- True  = benar-benar terbit (media_publish sukses).
- False = gagal di langkah mana pun, dengan pesan error yang jelas.
- TIDAK BOLEH ada "return True" palsu saat timeout (silent failure) —
  itu bug yang pernah ada di repo lama.
"""

import os
import time
import requests

GRAPH = "https://graph.facebook.com/v21.0"  # versi API dipin (pelajaran audit)


def _env(name: str) -> str:
    """Ambil env var, raise error jelas kalau belum diset."""
    val = os.getenv(name)
    if not val:
        raise RuntimeError(
            f"{name} belum diset. Lihat .env.example untuk daftar yang dibutuhkan."
        )
    return val


def _upload_to_imgbb(image_path: str) -> str:
    """Upload gambar lokal ke ImgBB, kembalikan URL publiknya."""
    key = _env("IMGBB_API_KEY")
    with open(image_path, "rb") as f:
        r = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": key},
            files={"image": f},
            timeout=60,
        )
    r.raise_for_status()
    url = r.json()["data"]["url"]
    print(f"[PUBLISH] gambar terupload: {url[:60]}...", flush=True)
    return url


def _create_item_container(ig_id: str, token: str, image_url: str) -> str:
    """Buat container untuk 1 gambar carousel. Kembalikan container ID."""
    r = requests.post(
        f"{GRAPH}/{ig_id}/media",
        data={"image_url": image_url, "is_carousel_item": True,
              "access_token": token},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["id"]


def _wait_ready(container_id: str, token: str, timeout_s: int = 120) -> bool:
    """Tunggu container berstatus FINISHED.

    KENAPA tidak return True diam-diam saat timeout (beda dengan kode lama):
    kalau container belum siap lalu kita paksa publish, posting bisa gagal
    atau tidak lengkap — dan kita tidak akan tahu kenapa. Lebih baik lapor
    gagal dengan jelas.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        r.raise_for_status()
        status = r.json().get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print(f"[PUBLISH] container ERROR: {container_id}", flush=True)
            return False
        time.sleep(5)
    print(f"[PUBLISH] TIMEOUT menunggu container {container_id}", flush=True)
    return False


def publish_carousel(image_paths: list, caption: str) -> bool:
    """Posting carousel. True jika terbit, False jika gagal di langkah mana pun."""
    try:
        ig_id = _env("IG_USER_ID")
        token = _env("IG_ACCESS_TOKEN")

        if len(image_paths) < 2:
            print("[PUBLISH] GAGAL: carousel butuh minimal 2 gambar.", flush=True)
            return False

        # 1-2. Upload + buat container per gambar (dinamis, tidak hardcode jumlah)
        children = []
        for path in image_paths:
            url = _upload_to_imgbb(path)
            cid = _create_item_container(ig_id, token, url)
            children.append(cid)

        # 3. Buat container carousel
        r = requests.post(
            f"{GRAPH}/{ig_id}/media",
            data={"media_type": "CAROUSEL", "children": ",".join(children),
                  "caption": caption, "access_token": token},
            timeout=60,
        )
        r.raise_for_status()
        carousel_id = r.json()["id"]

        # 4. Tunggu siap (dengan timeout yang jujur)
        if not _wait_ready(carousel_id, token):
            return False

        # 5. Terbitkan
        r = requests.post(
            f"{GRAPH}/{ig_id}/media_publish",
            data={"creation_id": carousel_id, "access_token": token},
            timeout=60,
        )
        r.raise_for_status()
        print(f"[PUBLISH] SUKSES terbit! media id: {r.json().get('id')}", flush=True)
        return True

    except Exception as exc:
        # KENAPA tangkap semua: publisher tidak boleh crash misterius.
        # Kegagalan dilaporkan sebagai False + pesan, orchestrator yang putuskan.
        print(f"[PUBLISH] GAGAL: {exc}", flush=True)
        return False
