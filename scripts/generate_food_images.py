#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成常用食物模块图片（断点续跑 + 限速重试）"""
import json
import requests
import time
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "food_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "images" / "food"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["words"]

items_to_generate = []
for item in items:
    img_path = OUTPUT_DIR / f"{item['file']}.png"
    if img_path.exists() and img_path.stat().st_size > 1000:
        print(f"跳过已存在: {item['word']}", flush=True)
    else:
        items_to_generate.append(item)

print(f"需要生成 {len(items_to_generate)} 张图片", flush=True)

def download_with_retry(item, max_retries=5):
    file_name = item['file']
    word = item['word']
    prompt = item.get('image_prompt', f"A cute cartoon {item['english']}, flat illustration, big round eyes, friendly expression, white background, children's book style, vector art, minimalist, no text, no watermark")
    # 统一加上食物图片专用风格前缀
    prompt = f"A cute cartoon food illustration for children, flat 2D style, pastel colors, rounded shapes, clean white background, no text, no watermark. {prompt}"
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=512&height=512&seed={abs(hash(file_name)) % 100000}&nologo=true&private=true&nofeed=true&model=flux"
    
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                (OUTPUT_DIR / f"{file_name}.png").write_bytes(r.content)
                return True, len(r.content)
            elif r.status_code == 429:
                wait = 30 * (2 ** attempt)
                print(f"  [{word}] 429 限流，等待 {wait} 秒后重试...", flush=True)
                time.sleep(wait)
            else:
                print(f"  [{word}] HTTP {r.status_code}，等待 10 秒后重试...", flush=True)
                time.sleep(10)
        except Exception as e:
            print(f"  [{word}] 错误: {e}，等待 10 秒后重试...", flush=True)
            time.sleep(10)
    return False, 0

for i, item in enumerate(items_to_generate, 1):
    success, size = download_with_retry(item)
    if success:
        print(f"[{i}/{len(items_to_generate)}] 成功: {item['word']} ({item['file']}) - {size} bytes", flush=True)
    else:
        print(f"[{i}/{len(items_to_generate)}] 失败: {item['word']} ({item['file']})", flush=True)
    
    time.sleep(3)

print("图片生成完成", flush=True)
