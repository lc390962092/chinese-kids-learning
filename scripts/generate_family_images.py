#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "family_module.json"
IMAGE_DIR = BASE_DIR / "assets" / "images" / "family"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = "cute cartoon, flat illustration, big round eyes, rounded shapes, pastel colors, friendly expression, white background, children's book style, vector art, minimalist, clean design, no text, no watermark, no gradient background"

def download_image(prompt, output_path, width=512, height=512):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42&enhance=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (children-app)'})
    with urllib.request.urlopen(req, timeout=180) as response:
        content = response.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    return len(content)

def main():
    if not CONTENT_FILE.exists():
        print(f"Error: {CONTENT_FILE} not found.")
        return

    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    words = data.get("words", [])
    print(f"Found {len(words)} family terms. Checking image files...")

    success = []
    failed = []

    for idx, item in enumerate(words, 1):
        english_name = item['english'].replace(" ", "_")
        output_path = IMAGE_DIR / f"{english_name}.png"
        
        if output_path.exists():
            print(f"[{idx}/{len(words)}] - {item['word']} ({english_name}.png) already exists, skipping.")
            continue

        prompt = f"{item['image_prompt']}, {STYLE_BASE}"
        print(f"[{idx}/{len(words)}] Generating image for {item['word']} ({english_name}.png)...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                size = download_image(prompt, output_path)
                success.append(item['word'])
                print(f"  ✓ Saved {size} bytes.")
                time.sleep(1.5)
                break
            except Exception as e:
                print(f"  ✗ Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    failed.append((item['word'], str(e)))

    print(f"\nGeneration complete! Success: {len(success)}, Failed: {len(failed)}")
    if failed:
        print("Failed list:", failed)

if __name__ == "__main__":
    main()
