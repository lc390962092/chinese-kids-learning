#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成身体部位模块音频（含中文单词、句子、日语读音）
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "body_parts_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "body_parts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
JAPANESE_VOICE = "ja-JP-NanamiNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"  ✓ 已生成: {output_path.name}")

async def main():
    if not CONTENT_FILE.exists():
        print(f"Error: {CONTENT_FILE} not found.")
        return

    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    words = data.get("words", [])
    print(f"开始生成 {len(words)} 个身体部位词语的音频...")
    
    for idx, item in enumerate(words, 1):
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["summary"]
        english = item["english"].replace(" ", "_")
        japanese_reading = item.get("japanese_reading", "")
        
        print(f"\n[{idx}/{len(words)}] 生成: {word}")
        
        word_text = f"{word}，{pinyin}"
        word_path = OUTPUT_DIR / f"{english}_word.mp3"
        await speak_and_save(word_text, word_path)
        
        sentence_dir = OUTPUT_DIR / "sentences"
        sentence_dir.mkdir(parents=True, exist_ok=True)
        sentence_path = sentence_dir / f"{english}_sentence.mp3"
        await speak_and_save(sentence, sentence_path)
        
        if japanese_reading:
            japanese_dir = OUTPUT_DIR / "japanese"
            japanese_dir.mkdir(parents=True, exist_ok=True)
            japanese_path = japanese_dir / f"{english}_japanese.mp3"
            await speak_and_save(japanese_reading, japanese_path, voice=JAPANESE_VOICE, rate="+0%")
        
    print("\n身体部位音频全部处理完成！")
    print(f"保存路径: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
