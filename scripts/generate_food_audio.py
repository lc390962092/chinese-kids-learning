#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 Edge TTS 生成食物模块全部音频"""
import json
import asyncio
from pathlib import Path
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "food_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "food"

VOICE_ZH = "zh-CN-XiaoxiaoNeural"
VOICE_JA = "ja-JP-NanamiNeural"
VOICE_EN = "en-US-AriaNeural"

RATE_ZH = "+0%"
RATE_JA = "+0%"
RATE_EN = "+0%"


def ensure_dirs():
    for sub in ["", "sentences", "measure", "japanese", "english", "encyclopedia"]:
        (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)


async def speak_and_save(text, output_path, voice, rate="+0%"):
    if not text or text == "无":
        print(f"  跳过: {output_path}")
        return
    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"  已存在: {output_path}")
        return
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"  ✓ 已生成: {output_path}")


async def main():
    ensure_dirs()
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("words", [])
    print(f"开始生成 {len(items)} 个食物音频...")

    for item in items:
        file_key = item.get("file")
        word = item.get("word", "")
        pinyin = item.get("pinyin", "")
        sentence = item.get("sentence", "")
        measure_word = item.get("measure_word", "")
        japanese_reading = item.get("japanese_reading", "")
        english = item.get("english", "")
        intro = item.get("intro", "")
        where = item.get("where", "")
        use = item.get("use", "")
        fun_fact = item.get("fun_fact", "")

        print(f"\n处理: {word}")

        # 读音: 词语 + 拼音
        await speak_and_save(
            f"{word}，{pinyin}",
            OUTPUT_DIR / f"{file_key}_word.mp3",
            VOICE_ZH, RATE_ZH
        )

        # 句子
        await speak_and_save(
            sentence,
            OUTPUT_DIR / "sentences" / f"{file_key}_sentence.mp3",
            VOICE_ZH, RATE_ZH
        )

        # 量词: 一[量词][词语]
        measure_text = f"一{measure_word}{word}"
        await speak_and_save(
            measure_text,
            OUTPUT_DIR / "measure" / f"{file_key}_measure.mp3",
            VOICE_ZH, RATE_ZH
        )

        # 日语读音
        await speak_and_save(
            japanese_reading,
            OUTPUT_DIR / "japanese" / f"{file_key}_japanese.mp3",
            VOICE_JA, RATE_JA
        )

        # 英语
        await speak_and_save(
            english,
            OUTPUT_DIR / "english" / f"{file_key}_english.mp3",
            VOICE_EN, RATE_EN
        )

        # 百科: 简介 + 从哪里来 + 怎么吃 + 小知识
        encyclopedia_text = f"{intro}{where}{use}{fun_fact}"
        await speak_and_save(
            encyclopedia_text,
            OUTPUT_DIR / "encyclopedia" / f"{file_key}_encyclopedia.mp3",
            VOICE_ZH, RATE_ZH
        )

    print("\n食物音频生成完成！")


if __name__ == "__main__":
    asyncio.run(main())
