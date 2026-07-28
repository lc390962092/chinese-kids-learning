#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成形状和颜色模块的日语音频"""
import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VOICE = "ja-JP-NanamiNeural"

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ {output_path}")

async def generate_for_module(module_name, data_list, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in data_list:
        english = item.get("english") or item.get("file") or item.get("word")
        reading = item.get("japanese_reading")
        if not reading or not english:
            print(f"跳过 {item.get('word')}，缺少 japanese_reading 或 english")
            continue
        await speak_and_save(reading, output_dir / f"{english}_jp.mp3", rate="+0%")

async def main():
    # 形状
    shapes_file = BASE_DIR / "content" / "shapes_module.json"
    if shapes_file.exists():
        with open(shapes_file, "r", encoding="utf-8") as f:
            shapes_data = json.load(f)
        shapes_dir = BASE_DIR / "assets" / "audio" / "shapes" / "japanese"
        print(f"开始生成 {len(shapes_data['words'])} 个形状日语音频...")
        await generate_for_module("shapes", shapes_data["words"], shapes_dir)
    else:
        print(f"未找到 {shapes_file}")

    # 颜色
    colors_file = BASE_DIR / "content" / "colors_module.json"
    if colors_file.exists():
        with open(colors_file, "r", encoding="utf-8") as f:
            colors_data = json.load(f)
        colors_dir = BASE_DIR / "assets" / "audio" / "colors" / "japanese"
        print(f"开始生成 {len(colors_data['words'])} 个颜色日语音频...")
        await generate_for_module("colors", colors_data["words"], colors_dir)
    else:
        print(f"未找到 {colors_file}")

    print("\n日语音频全部完成！")

if __name__ == "__main__":
    asyncio.run(main())
