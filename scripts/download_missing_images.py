#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
from pathlib import Path
import time

BASE_DIR = Path('/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁')
CONTENT_FILE = BASE_DIR / 'content' / 'animal_module.json'
IMAGE_DIR = BASE_DIR / 'assets' / 'images' / 'animals'
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = "cute cartoon, flat illustration, big round eyes, rounded shapes, pastel colors, friendly expression, white background, children's book style, vector art, minimalist, clean design, no text, no watermark, no gradient background"

with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = [item for item in data['words'] if not (IMAGE_DIR / f"{item['english']}.png").exists()]

def download_image(prompt, output_path, width=512, height=512):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42&enhance=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as response:
        content = response.read()
        with open(output_path, 'wb') as f:
            f.write(content)
    return len(content)

print(f'开始下载剩余 {len(missing)} 张图片...')
success = []
failed = []
for item in missing:
    prompt = f"{item['image_prompt']}, {STYLE_BASE}"
    output_path = IMAGE_DIR / f"{item['english']}.png"
    try:
        size = download_image(prompt, output_path)
        success.append(item['word'])
        print(f"✓ {item['word']} ({item['english']}.png) - {size} bytes")
    except Exception as e:
        failed.append((item['word'], str(e)))
        print(f"✗ {item['word']} 失败: {e}")
    time.sleep(2)

print(f"\n成功: {len(success)}，失败: {len(failed)}")
if failed:
    print('失败列表:', failed)
