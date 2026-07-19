#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成水果蔬菜模块音频"""
import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "fruit_vegetable_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "fruits_vegetables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ {output_path}")

async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"开始生成 {len(data['words'])} 个水果蔬菜音频...")
    
    for item in data["words"]:
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        english = item["english"]
        
        word_text = f"{word}，{pinyin}"
        await speak_and_save(word_text, OUTPUT_DIR / f"{english}_word.mp3", rate="+0%")
        
        sentence_dir = OUTPUT_DIR / "sentences"
        sentence_dir.mkdir(parents=True, exist_ok=True)
        await speak_and_save(sentence, sentence_dir / f"{english}_sentence.mp3", rate="+0%")
    
    print("\n音频全部完成！")

if __name__ == "__main__":
    asyncio.run(main())
