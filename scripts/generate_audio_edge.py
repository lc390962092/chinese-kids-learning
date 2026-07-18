#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Edge TTS（Microsoft 在线免费 TTS）生成动物模块音频
优点：无需 Azure 账号，无需 Windows 语音包，中文童声自然
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 中文童声/女声推荐
# VOICE = "zh-CN-XiaoyiNeural"  # 女童声
# VOICE = "zh-CN-YunxiNeural"   # 男童声
VOICE = "zh-CN-XiaoxiaoNeural"   # 女声，清晰标准


async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    """生成单个音频文件"""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ 已生成: {output_path}")


async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"开始生成 {len(data['words'])} 个动物的音频...")
    
    for item in data["words"]:
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        sound = item["sound"]
        english = item["english"]
        
        print(f"\n生成: {word}")
        
        # 1. 单词读音：猫，māo
        word_text = f"{word}，{pinyin}"
        await speak_and_save(word_text, OUTPUT_DIR / f"{english}_word.mp3", rate="+0%")
        
        # 2. 例句读音
        sentence_dir = OUTPUT_DIR / "sentences"
        sentence_dir.mkdir(parents=True, exist_ok=True)
        await speak_and_save(sentence, sentence_dir / f"{english}_sentence.mp3", rate="+0%")
        
        # 3. 叫声（可选）
        if sound != "无":
            await speak_and_save(sound, OUTPUT_DIR / f"{english}_sound.mp3", rate="+0%")
    
    print("\n全部完成！")
    print(f"音频保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
