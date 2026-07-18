#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载交通工具图片
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
import time

BASE_DIR = Path('/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁')
CONTENT_FILE = BASE_DIR / 'content' / 'vehicle_module.json'
IMAGE_DIR = BASE_DIR / 'assets' / 'images' / 'vehicles'
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = "cute cartoon, flat illustration, big round eyes, rounded shapes, pastel colors, friendly expression, white background, children's book style, vector art, minimalist, clean design, no text, no watermark, no gradient background"

with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

items = data['words']

def download_one(item, max_retries=3):
    prompt = f"{item['image_prompt']}, {STYLE_BASE}"
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=400&height=400&nologo=true&seed=42"
    output_path = IMAGE_DIR / f"{item['english']}.png"
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
                with open(output_path, 'wb') as f:
                    f.write(content)
            return ('ok', item['word'], len(content))
        except Exception as e:
            print(f"  {item['word']} 第 {attempt+1} 次失败: {e}")
            time.sleep(5)
    return ('fail', item['word'], 'max retries')

print(f'开始下载 {len(items)} 张交通工具图片...')
for i, item in enumerate(items):
    if i > 0:
        time.sleep(8)
    status, word, info = download_one(item)
    if status == 'ok':
        print(f"✓ {word} - {info} bytes")
    else:
        print(f"✗ {word} - {info}")

print('下载完成。')
