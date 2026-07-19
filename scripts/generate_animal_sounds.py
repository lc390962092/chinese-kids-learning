#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 Edge TTS 生成缺失的动物叫声音频"""
import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"

async def speak_and_save(text, output_path, rate="+0%"):
    if text == "无":
        print(f"  跳过: {output_path}")
        return
    communicate = edge_tts.Communicate(text=text, voice=VOICE, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ 已生成: {output_path}")

async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    items_to_generate = []
    for item in data["words"]:
        sound_path = OUTPUT_DIR / f"{item['english']}_sound.mp3"
        if not sound_path.exists() or sound_path.stat().st_size < 1000:
            items_to_generate.append(item)
    
    print(f"需要生成 {len(items_to_generate)} 个叫声音频...")
    
    for item in items_to_generate:
        sound = item.get("sound", "无")
        output_path = OUTPUT_DIR / f"{item['english']}_sound.mp3"
        await speak_and_save(sound, output_path)
    
    print("\n叫声音频生成完成！")

if __name__ == "__main__":
    asyncio.run(main())
