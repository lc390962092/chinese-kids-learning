#!/usr/bin/env python3
"""Regenerate selected food module images as realistic food photography."""
import hashlib
import json
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "content" / "food_module.json"
IMAGE_DIR = ROOT / "assets" / "images" / "food"

# Items to regenerate: word -> file
TARGET_WORDS = ["饺子", "糖果"]

STYLE = (
    "Realistic food photography, appetizing, clean white background, "
    "soft natural lighting, vivid colors, shallow depth of field, "
    "no text, no watermark, no cartoon, no illustration"
)

PROMPTS = {
    "饺子": (
        "A top-down realistic food photo of a white ceramic plate holding "
        "six Chinese jiaozi dumplings arranged neatly, "
        "each dumpling is a clear half-moon crescent shape with pinched pleats only along the curved outer edge, "
        "the flat straight edge is smooth, thin translucent wrappers, steam rising, "
        "clean white background, professional food photography, 8k"
    ),
    "包子": (
        "A bamboo steamer basket with several freshly steamed Chinese baozi buns, "
        "each a round white fluffy bun with a classic spiral twist pleat on top, "
        "soft puffy dough, one bun gently pulled open showing savory minced pork filling, "
        "clean white background, realistic food photography"
    ),
    "饼干": (
        "A stack of homemade chocolate chip cookies on a simple white plate, "
        "golden brown crispy edges, melted chocolate chips, one cookie broken in half, "
        "crumbs scattered naturally, clean white background, realistic food photography"
    ),
    "糖果": (
        "A realistic food photo of a small pile of classic individually wrapped hard candies on a white plate, "
        "each candy wrapped in shiny metallic foil or clear cellophane with crinkled twisted wrapper ends, "
        "mix of red, green, yellow, blue, pink wrappers, "
        "clearly visible separate small candies, "
        "clean white background, professional food photography, 8k"
    ),
}


def stable_seed(word: str) -> int:
    h = hashlib.sha256((word + "_realistic_food_v1").encode()).hexdigest()
    return int(h[:8], 16)


def download_image(prompt: str, seed: int, output: Path) -> bool:
    encoded = urllib.parse.quote(prompt)
    # 使用 flux 模型以获得更好的写实食物摄影效果
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=512&height=512&seed={seed}"
        f"&nologo=true&private=true&nofeed=true&model=flux"
    )
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                output.write_bytes(r.content)
                return True
            elif r.status_code == 429:
                wait = 30 * (2 ** attempt)
                print(f"  429 for {output.name}, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code} for {output.name}")
                time.sleep(10)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(10)
    return False


def backup(path: Path) -> None:
    bak = path.with_suffix(path.suffix + ".bak")
    if path.exists() and not bak.exists():
        bak.write_bytes(path.read_bytes())


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    items = data.get("words", [])
    ok = []
    failed = []
    for item in items:
        word = item["word"]
        if word not in TARGET_WORDS:
            continue
        file = item["file"]
        out = IMAGE_DIR / f"{file}.png"
        prompt = PROMPTS[word] + ", " + STYLE
        seed = stable_seed(word)
        print(f"Generating: {word} ({file}.png) seed={seed}")
        backup(out)
        if download_image(prompt, seed, out):
            size = out.stat().st_size
            print(f"  OK: {size} bytes")
            ok.append(word)
        else:
            print(f"  FAILED")
            failed.append(word)
        time.sleep(2)
    print("\nDone.")
    print("OK:", ok)
    print("Failed:", failed)


if __name__ == "__main__":
    main()
