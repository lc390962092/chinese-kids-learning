#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并发下载缺失图片，带超时重试
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

BASE_DIR = Path('/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁')
CONTENT_FILE = BASE_DIR / 'content' / 'animal_module.json'
IMAGE_DIR = BASE_DIR / 'assets' / 'images' / 'animals'
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = "cute cartoon, flat illustration, big round eyes, rounded shapes, pastel colors, friendly expression, white background, children's book style, vector art, minimalist, clean design, no text, no watermark, no gradient background"

with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = [item for item in data['words'] if not (IMAGE_DIR / f"{item['english']}.png").exists()]

def download_one(item, max_retries=2):
    prompt = f"{item['image_prompt']}, {STYLE_BASE}"
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=400&height=400&nologo=true&seed=42&enhance=false"
    output_path = IMAGE_DIR / f"{item['english']}.png"
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                with open(output_path, 'wb') as f:
                    f.write(content)
            return ('ok', item['word'], len(content))
        except Exception as e:
            if attempt == max_retries - 1:
                return ('fail', item['word'], str(e))
            time.sleep(1)

print(f'并发下载剩余 {len(missing)} 张图片...')
results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(download_one, item): item for item in missing}
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        status, word, info = result
        if status == 'ok':
            print(f"✓ {word} - {info} bytes")
        else:
            print(f"✗ {word} - {info}")

ok = sum(1 for r in results if r[0] == 'ok')
fail = sum(1 for r in results if r[0] == 'fail')
print(f"\n成功: {ok}，失败: {fail}")
