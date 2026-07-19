#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成拼音模块音频（避免读成英语字母）"""
import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "pinyin_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "pinyin"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"

# 声母呼读音
INITIALS_READ = {
    "b": "bō", "p": "pō", "m": "mō", "f": "fō",
    "d": "dē", "t": "tē", "n": "nē", "l": "lē",
    "g": "gē", "k": "kē", "h": "hē",
    "j": "jī", "q": "qī", "x": "xī",
    "zh": "zhī", "ch": "chī", "sh": "shī", "r": "rì"
}

# 韵母本音（带声调示例）
FINALS_READ = {
    "a": "ā", "o": "ō", "e": "ē", "i": "yī", "u": "wū", "ü": "yū",
    "ai": "āi", "ei": "ēi", "ao": "āo", "ou": "ōu", "iu": "iū",
    "ie": "iē", "üe": "yuē",
    "an": "ān", "en": "ēn", "ang": "āng", "eng": "ēng", "ing": "īng"
}

TONE_READ = {1: "ā", 2: "á", 3: "ǎ", 4: "à"}

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
        
        if section["id"] == "initials":
            for i, item in enumerate(section["items"]):
                pinyin = item["pinyin"]
                example = item["example_word"]
                read = INITIALS_READ.get(pinyin, pinyin)
                # 避免单独读字母，读呼读音+例字，如 "bō，波"
                text = f"{read}，{example}"
                filename = f"{i:02d}_{pinyin}.mp3"
                await speak_and_save(text, section_dir / filename)
        
        elif section["id"] == "finals":
            for i, item in enumerate(section["items"]):
                pinyin = item["pinyin"]
                example = item["example_word"]
                read = FINALS_READ.get(pinyin, pinyin)
                # 读本音+例字，如 "ā，啊"
                text = f"{read}，{example}"
                filename = f"{i:02d}_{pinyin}.mp3"
                await speak_and_save(text, section_dir / filename)
        
        elif section["id"] == "tones":
            for i, item in enumerate(section["items"]):
                tone = item["tone"]
                tone_name = item["name"]
                read = TONE_READ[tone]
                example = item["examples"][0]
                # 读 "一声，ā，啊"
                text = f"{tone_name}，{read}，{example['word']}"
                filename = f"{i:02d}_tone{tone}.mp3"
                await speak_and_save(text, section_dir / filename)
    
    print("\n拼音音频全部重新生成完成！")

if __name__ == "__main__":
    asyncio.run(main())
