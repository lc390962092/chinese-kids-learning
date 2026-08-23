#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成指定食物的写实风格图片"""
import json
import requests
import time
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "food_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "images" / "food"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_WORDS = ['披萨', '酸奶', '奶酪', '鸡蛋', '包子', '馒头', '面条']

def realistic_prompt(word, english):
    prompts = {
        '披萨': 'A realistic slice of pizza with melted cheese, pepperoni and herbs, food photography, clean white background, soft natural lighting, appetizing, detailed texture, no text, no watermark',
        '酸奶': 'A realistic cup of white yogurt with a spoon, creamy texture, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark',
        '奶酪': 'A realistic wedge of yellow cheese with holes, food photography, clean white background, soft natural lighting, appetizing, detailed texture, no text, no watermark',
        '鸡蛋': 'A realistic fried egg with bright yellow yolk and white egg white, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark',
        '包子': 'A realistic steamed stuffed bun (baozi), fluffy white bun, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark',
        '馒头': 'A realistic steamed bun (mantou), white fluffy bun, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark',
        '面条': 'A realistic bowl of noodles with chopsticks, steam rising, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark',
    }
    return prompts.get(word, f"A realistic {english}, food photography, clean white background, soft natural lighting, appetizing, no text, no watermark")

with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

items = [w for w in data["words"] if w["word"] in TARGET_WORDS]
print(f"需要重新生成 {len(items)} 张食物图片", flush=True)

def download_with_retry(item, max_retries=5):
    file_name = item['file']
    word = item['word']
    prompt = realistic_prompt(word, item.get('english', word))
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=512&height=512&seed={abs(hash(file_name + 'realistic')) % 100000}&nologo=true&private=true&nofeed=true&model=flux"
    
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

print("食物写实图片重新生成完成", flush=True)
