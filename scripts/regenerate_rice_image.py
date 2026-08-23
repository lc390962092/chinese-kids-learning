#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成米饭图片"""
import requests
import time
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "assets" / "images" / "food"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = "A cute cartoon bowl of white steamed rice with chopsticks, flat 2D illustration, big friendly smile, rounded shapes, pastel colors, clean white background, children book style, vector art, minimalist, the rice clearly visible inside the bowl, no text, no watermark"
URL = f"https://image.pollinations.ai/prompt/{quote(PROMPT)}?width=512&height=512&seed=9527&nologo=true&private=true&nofeed=true&model=flux"

for attempt in range(5):
    try:
        r = requests.get(URL, timeout=60)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            (OUTPUT_DIR / "rice.png").write_bytes(r.content)
            print(f"✓ 米饭图片重新生成成功: {len(r.content)} bytes")
            break
        elif r.status_code == 429:
            wait = 30 * (2 ** attempt)
            print(f"429 限流，等待 {wait} 秒...")
            time.sleep(wait)
        else:
            print(f"HTTP {r.status_code}，等待 10 秒...")
            time.sleep(10)
    except Exception as e:
        print(f"错误: {e}，等待 10 秒...")
        time.sleep(10)
else:
    print("米饭图片生成失败")
