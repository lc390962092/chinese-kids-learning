#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成拼音模块音频
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "pinyin_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "pinyin"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ {output_path}")

async def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for section in data["sections"]:
        section_dir = OUTPUT_DIR / section["id"]
        section_dir.mkdir(parents=True, exist_ok=True)
        
        if section["id"] in ["initials", "finals"]:
            for i, item in enumerate(section["items"]):
                pinyin = item["pinyin"]
                example = item["example_word"]
                # 声母/韵母音频：b，爸
                text = f"{pinyin}，{example}"
                filename = f"{i:02d}_{pinyin}.mp3"
                await speak_and_save(text, section_dir / filename)
        
        elif section["id"] == "tones":
            for i, item in enumerate(section["items"]):
                tone_name = item["name"]
                example = item["examples"][0]
                # 声调音频：一声，mā，妈
                text = f"{tone_name}，{example['pinyin']}，{example['word']}"
                filename = f"{i:02d}_tone{item['tone']}.mp3"
                await speak_and_save(text, section_dir / filename)
    
    print("\n拼音音频全部完成！")

if __name__ == "__main__":
    asyncio.run(main())
