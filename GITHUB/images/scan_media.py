#!/usr/bin/env python3
"""Scan project folders and write media.json (images + videos only).

Run from repo root or this folder after uploading new media:
  python GITHUB/images/scan_media.py
"""
from __future__ import annotations

import json
from pathlib import Path

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
VIDEO_EXT = {".mp4", ".webm", ".ogg", ".mov"}
SKIP_NAMES = {"project.json", "media.json", "projects.json", ".ds_store", "thumbs.db"}

ROOT = Path(__file__).resolve().parent


def is_media(name: str) -> bool:
    lower = name.lower()
    if lower in SKIP_NAMES or name.startswith("."):
        return False
    # skip broken/empty names like ".png"
    stem = Path(name).stem
    if not stem:
        return False
    return Path(name).suffix.lower() in IMAGE_EXT | VIDEO_EXT


def scan_folder(folder: Path) -> list[str]:
    files = [p.name for p in folder.iterdir() if p.is_file() and is_media(p.name)]
    # videos first, then images; natural-ish alpha within each group
    videos = sorted(f for f in files if Path(f).suffix.lower() in VIDEO_EXT)
    images = sorted(f for f in files if Path(f).suffix.lower() in IMAGE_EXT)
    return videos + images


def main() -> None:
    manifest_path = ROOT / "projects.json"
    if manifest_path.exists():
        folders = json.loads(manifest_path.read_text(encoding="utf-8")).get("projects", [])
    else:
        folders = [p.name for p in ROOT.iterdir() if p.is_dir() and (p / "project.json").exists()]

    index = {}
    for name in folders:
        folder = ROOT / name
        if not folder.is_dir():
            print(f"skip missing folder: {name}")
            continue
        files = scan_folder(folder)
        media = {"files": files}
        (folder / "media.json").write_text(
            json.dumps(media, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        index[name] = files
        print(f"{name}: {len(files)} media file(s)")

    (ROOT / "media-index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote media.json per folder + {ROOT / 'media-index.json'}")


if __name__ == "__main__":
    main()
