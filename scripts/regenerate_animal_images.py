#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成指定动物的卡通风格图片"""
import json
import requests
import time
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "images" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_WORDS = ['三角龙', '翼龙', '鲨鱼', '蝴蝶', '海豚', '剑龙']

def cartoon_prompt(word, english):
    prompts = {
        '三角龙': 'A cute cartoon triceratops dinosaur, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
        '翼龙': 'A cute cartoon pterosaur flying dinosaur, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
        '鲨鱼': 'A cute cartoon shark, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
        '蝴蝶': 'A cute cartoon butterfly, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
        '海豚': 'A cute cartoon dolphin, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
        '剑龙': 'A cute cartoon stegosaurus dinosaur, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark',
    }
    return prompts.get(word, f"A cute cartoon {english}, friendly smiling face, big round eyes, bright pastel colors, flat 2D illustration, clean white background, children book style, vector art, minimalist, no text, no watermark")

with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

items = [w for w in data["words"] if w["word"] in TARGET_WORDS]
print(f"需要重新生成 {len(items)} 张动物图片", flush=True)

def download_with_retry(item, max_retries=5):
    file_name = item['file']
    word = item['word']
    prompt = cartoon_prompt(word, item.get('english', word))
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=512&height=512&seed={abs(hash(file_name + 'cartoon')) % 100000}&nologo=true&private=true&nofeed=true&model=flux"
    
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

for i, item in enumerate(items, 1):
    success, size = download_with_retry(item)
    if success:
        print(f"[{i}/{len(items)}] 成功: {item['word']} ({item['file']}) - {size} bytes", flush=True)
    else:
        print(f"[{i}/{len(items)}] 失败: {item['word']} ({item['file']})", flush=True)
    time.sleep(3)

print("动物图片重新生成完成", flush=True)
