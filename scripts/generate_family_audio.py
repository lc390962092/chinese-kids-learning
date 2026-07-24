#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Edge TTS 生成称谓模块音频
需要依赖：edge-tts (pip install edge-tts)
"""

import json
import asyncio
import sys
from pathlib import Path

# 确保 edge-tts 库存在
try:
    import edge_tts
except ImportError:
    print("Warning: 'edge_tts' module not found. Please install it with 'pip install edge-tts'.")
    print("We will define the generator script but you need to run it after installing the dependencies.")

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "family_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "family"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"  # 标准女声

async def speak_and_save(text, output_path, voice=VOICE):
    """保存合成音频"""
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(str(output_path))
        print(f"  ✓ 已生成: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ 失败: {output_path.name} - {e}")
        return False

async def main():
    if 'edge_tts' not in sys.modules:
        print("Error: edge-tts is not installed. Run 'pip install edge-tts' first.")
        return

    if not CONTENT_FILE.exists():
        print(f"Error: {CONTENT_FILE} not found.")
        return

    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    words = data.get("words", [])
    print(f"开始生成 {len(words)} 个称谓的音频...")
    
    for idx, item in enumerate(words, 1):
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        english = item["english"].replace(" ", "_")
        
        print(f"\n[{idx}/{len(words)}] 生成: {word}")
        
        # 1. 单词拼音读音
        word_text = f"{word}，{pinyin}"
        word_path = OUTPUT_DIR / f"{english}_word.mp3"
        await speak_and_save(word_text, word_path)
        
        # 2. 完整句子读音
        sentence_dir = OUTPUT_DIR / "sentences"
        sentence_dir.mkdir(parents=True, exist_ok=True)
        sentence_path = sentence_dir / f"{english}_sentence.mp3"
        await speak_and_save(sentence, sentence_path)
        
    print("\n称谓音频全部处理完成！")
    print(f"保存路径: {OUTPUT_DIR}")

if __name__ == "__main__":
    if 'edge_tts' in sys.modules:
        asyncio.run(main())
    else:
        print("To generate local audio files, run:")
        print("  pip install edge-tts")
        print("  python3 scripts/generate_family_audio.py")
