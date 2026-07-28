#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成动词与动作模块音频（中文词语、句子、日语、英语）
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "action_verbs_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "action_verbs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
JAPANESE_VOICE = "ja-JP-NanamiNeural"
ENGLISH_VOICE = "en-US-AnaNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ 已生成: {output_path}")

async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data["words"]

    sentence_dir = OUTPUT_DIR / "sentences"
    sentence_dir.mkdir(parents=True, exist_ok=True)
    japanese_dir = OUTPUT_DIR / "japanese"
    japanese_dir.mkdir(parents=True, exist_ok=True)
    english_dir = OUTPUT_DIR / "english"
    english_dir.mkdir(parents=True, exist_ok=True)

    print(f"开始生成 {len(items)} 个动词与动作音频...\n")

    for item in items:
        file = item["file"]
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        english = item["english"]
        japanese_reading = item["japanese_reading"]

        print(f"生成: {word}")

        # 中文词语读音
        await speak_and_save(f"{word}，{pinyin}", OUTPUT_DIR / f"{file}_word.mp3", voice=VOICE, rate="+0%")

        # 中文句子
        await speak_and_save(sentence, sentence_dir / f"{file}_sentence.mp3", voice=VOICE, rate="+0%")

        # 日语读音（仅假名）
        await speak_and_save(japanese_reading, japanese_dir / f"{file}_japanese.mp3", voice=JAPANESE_VOICE, rate="+0%")

        # 英语
        await speak_and_save(english, english_dir / f"{file}_english.mp3", voice=ENGLISH_VOICE, rate="+0%")

    print("\n全部完成！")

if __name__ == "__main__":
    asyncio.run(main())
