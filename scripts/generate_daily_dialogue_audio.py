#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成日常情景对话模块音频（中文词语、句子、日语、英语）
"""

import json
import asyncio
import edge_tts
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "daily_dialogue"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-XiaoxiaoNeural"
JAPANESE_VOICE = "ja-JP-NanamiNeural"
ENGLISH_VOICE = "en-US-AnaNeural"

# 与 daily_dialogue.html 中 allItems 保持一致
allItems = [
    { "word": "你好", "pinyin": "nǐ hǎo", "file": "hello", "english": "Hello", "sentence": "见到朋友说：你好！", "japanese_reading": "こんにちは" },
    { "word": "再见", "pinyin": "zài jiàn", "file": "goodbye", "english": "Goodbye", "sentence": "放学了，我跟老师说再见。", "japanese_reading": "さようなら" },
    { "word": "谢谢", "pinyin": "xiè xie", "file": "thank_you", "english": "Thank you", "sentence": "奶奶给我苹果，我说谢谢。", "japanese_reading": "ありがとう" },
    { "word": "对不起", "pinyin": "duì bu qǐ", "file": "sorry", "english": "Sorry", "sentence": "撞到小朋友，我马上说对不起。", "japanese_reading": "ごめんなさい" },
    { "word": "我饿了", "pinyin": "wǒ è le", "file": "im_hungry", "english": "I'm hungry", "sentence": "我饿了，想吃面条。", "japanese_reading": "おなかがすいた" },
    { "word": "我渴了", "pinyin": "wǒ kě le", "file": "im_thirsty", "english": "I'm thirsty", "sentence": "我渴了，想喝水。", "japanese_reading": "のどがかわいた" },
    { "word": "好吃", "pinyin": "hǎo chī", "file": "delicious", "english": "Delicious", "sentence": "这个蛋糕真好吃！", "japanese_reading": "おいしい" },
    { "word": "吃饱了", "pinyin": "chī bǎo le", "file": "im_full", "english": "I'm full", "sentence": "我吃饱了，谢谢妈妈。", "japanese_reading": "おなかいっぱい" },
    { "word": "我想", "pinyin": "wǒ xiǎng", "file": "i_want", "english": "I want to", "sentence": "我想去公园玩。", "japanese_reading": "したい" },
    { "word": "帮忙", "pinyin": "bāng máng", "file": "help", "english": "Help", "sentence": "玩具太高了，请爸爸帮忙。", "japanese_reading": "てつだって" },
    { "word": "洗手", "pinyin": "xǐ shǒu", "file": "wash_hands", "english": "Wash hands", "sentence": "吃饭前，我把手洗干净。", "japanese_reading": "てをあらう" },
    { "word": "刷牙", "pinyin": "shuā yá", "file": "brush_teeth", "english": "Brush teeth", "sentence": "早上起床后，我要刷牙。", "japanese_reading": "はをみがく" },
    { "word": "穿衣服", "pinyin": "chuān yī fu", "file": "get_dressed", "english": "Get dressed", "sentence": "天气冷了，我自己穿衣服。", "japanese_reading": "ふくをきる" },
    { "word": "上厕所", "pinyin": "shàng cè suǒ", "file": "go_potty", "english": "Go potty", "sentence": "我想上厕所。", "japanese_reading": "といれにいく" },
    { "word": "起床", "pinyin": "qǐ chuáng", "file": "wake_up", "english": "Wake up", "sentence": "早上太阳出来了，我起床啦。", "japanese_reading": "おきる" },
    { "word": "睡觉", "pinyin": "shuì jiào", "file": "sleep", "english": "Sleep", "sentence": "晚上该睡觉了，我要听故事。", "japanese_reading": "ねる" },
    { "word": "一起玩", "pinyin": "yī qǐ wán", "file": "play_together", "english": "Play together", "sentence": "我们一起玩积木吧！", "japanese_reading": "いっしょにあそぼう" },
    { "word": "分享", "pinyin": "fēn xiǎng", "file": "share", "english": "Share", "sentence": "我把饼干分给小朋友吃。", "japanese_reading": "わけあう" },
    { "word": "排队", "pinyin": "pái duì", "file": "line_up", "english": "Line up", "sentence": "大家在滑梯前面排队。", "japanese_reading": "れつにならぶ" },
    { "word": "开心", "pinyin": "kāi xīn", "file": "happy", "english": "Happy", "sentence": "今天去公园，我很开心。", "japanese_reading": "うれしい" },
    { "word": "难过", "pinyin": "nán guò", "file": "sad", "english": "Sad", "sentence": "玩具坏了，我有点难过。", "japanese_reading": "かなしい" },
    { "word": "害怕", "pinyin": "hài pà", "file": "scared", "english": "Scared", "sentence": "天黑的时候，我有点害怕。", "japanese_reading": "こわい" },
    { "word": "疼", "pinyin": "téng", "file": "hurt", "english": "It hurts", "sentence": "我的膝盖摔疼了。", "japanese_reading": "いたい" },
    { "word": "不要", "pinyin": "bù yào", "file": "no_want", "english": "I don't want", "sentence": "我现在不想睡觉。", "japanese_reading": "いや" },
]

async def speak_and_save(text, output_path, voice=VOICE, rate="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(output_path))
    print(f"✓ 已生成: {output_path}")

async def main():
    sentence_dir = OUTPUT_DIR / "sentences"
    sentence_dir.mkdir(parents=True, exist_ok=True)
    japanese_dir = OUTPUT_DIR / "japanese"
    japanese_dir.mkdir(parents=True, exist_ok=True)
    english_dir = OUTPUT_DIR / "english"
    english_dir.mkdir(parents=True, exist_ok=True)

    print(f"开始生成 {len(allItems)} 个日常情景对话音频...\n")

    for item in allItems:
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
