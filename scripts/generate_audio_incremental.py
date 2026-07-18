#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量生成动物音频：只生成缺失的
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    if output_path.exists():
        return False
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ 已生成: {output_path}")
    return True

async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    generated = 0
    skipped = 0
    
    for item in data["words"]:
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        sound = item.get("sound", "无")
        english = item["english"]
        
        word_text = f"{word}，{pinyin}"
        word_path = OUTPUT_DIR / f"{english}_word.mp3"
        sentence_path = OUTPUT_DIR / "sentences" / f"{english}_sentence.mp3"
        sentence_path.parent.mkdir(parents=True, exist_ok=True)
        
        if await speak_and_save(word_text, word_path):
            generated += 1
        else:
            skipped += 1
        
        if await speak_and_save(sentence, sentence_path):
            generated += 1
        else:
            skipped += 1
        
        if sound != "无":
            sound_path = OUTPUT_DIR / f"{english}_sound.mp3"
            if await speak_and_save(sound, sound_path, rate="+0%"):
                generated += 1
            else:
                skipped += 1
    
    print(f"\n完成：生成 {generated} 个，跳过 {skipped} 个（已存在）")

if __name__ == "__main__":
    asyncio.run(main())
