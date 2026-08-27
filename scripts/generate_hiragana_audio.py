#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成平假名模块的日语音频"""
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


def safe_filename(kana):
    return kana.replace("ー", "-").replace("っ", "xtsu").replace("ん", "nn")


async def main():
    module_file = BASE_DIR / "content" / "hiragana_module.json"
    if not module_file.exists():
        print(f"未找到 {module_file}")
        return

    with open(module_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = []
    for section in data.get("sections", []):
        sec_id = section["id"]
        output_dir = BASE_DIR / "assets" / "audio" / "hiragana" / sec_id
        output_dir.mkdir(parents=True, exist_ok=True)
        for idx, item in enumerate(section.get("items", [])):
            kana = item.get("kana", "")
            text = item.get("example_word", "")
            if not kana or not text:
                continue
            key = safe_filename(kana)
            output_path = output_dir / f"{idx:02d}_{key}.mp3"
            if output_path.exists():
                print(f"跳过已存在 {output_path}")
                continue
            tasks.append(speak_and_save(text, output_path))

    if tasks:
        print(f"开始生成 {len(tasks)} 个平假名日语音频...")
        await asyncio.gather(*tasks)
    else:
        print("没有需要生成的音频")

    print("\n平假名日语音频全部完成！")


if __name__ == "__main__":
    asyncio.run(main())
