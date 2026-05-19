#!/usr/bin/env python3
"""
Batch convert images in assets/images/couples/ to WebP.
Creates .webp files alongside originals and keeps originals unchanged.

Usage:
  python scripts\convert_to_webp.py

Requirements: Python 3 and network access to install Pillow if not present.
"""
from __future__ import annotations
import os
import sys
import subprocess

try:
    from PIL import Image
except Exception:
    print('Pillow not found — installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image


def convert_file(path: str, out_path: str, max_side: int = 1600, quality: int = 85) -> bool:
    try:
        with Image.open(path) as im:
            # Convert palette/rgba to RGB
            if im.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif im.mode != 'RGB':
                im = im.convert('RGB')

            w, h = im.size
            largest = max(w, h)
            if largest > max_side:
                scale = max_side / float(largest)
                new_size = (int(w * scale), int(h * scale))
                im = im.resize(new_size, Image.LANCZOS)

            im.save(out_path, 'WEBP', quality=quality, method=6)
        return True
    except Exception as e:
        print(f'Failed: {path} -> {e}')
        return False


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    couple_dir = os.path.join(repo_root, 'assets', 'images', 'couples')

    if not os.path.isdir(couple_dir):
        print('Directory not found:', couple_dir)
        sys.exit(1)

    exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    files = sorted([f for f in os.listdir(couple_dir) if f.lower().endswith(exts)])
    if not files:
        print('No images found in', couple_dir)
        return

    print(f'Found {len(files)} image(s) in {couple_dir}.')
    converted = 0
    for name in files:
        src = os.path.join(couple_dir, name)
        base, _ = os.path.splitext(name)
        out = os.path.join(couple_dir, base + '.webp')
        if os.path.exists(out):
            print('Skipping (exists):', out)
            continue
        print('Converting:', name)
        ok = convert_file(src, out)
        if ok:
            converted += 1

    print(f'Done. Converted {converted}/{len(files)} images. WebP files are alongside originals.')


if __name__ == '__main__':
    main()
