#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 本地 TTS 音频生成脚本
使用 Windows 自带 SAPI5 中文语音（免费，无需联网）

运行环境：Windows 10/11，安装了中文语言包
Python 依赖：pip install pyttsx3
"""

import json
import pyttsx3
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def list_voices(engine):
    """列出所有可用的语音，方便调试"""
    print("\n可用语音列表：")
    for voice in engine.getProperty("voices"):
        print(f"  - ID: {voice.id}")
        print(f"    Name: {voice.name}")
        print(f"    Languages: {voice.languages}")
    print()


def speak_and_save(engine, text, output_path, rate=150):
    """生成单个音频文件"""
    engine.setProperty("rate", rate)
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    print(f"✓ 已生成: {output_path}")


def main():
    engine = pyttsx3.init()
    
    # 列出可用语音，找到中文语音
    list_voices(engine)
    
    # 尝试设置中文语音（Windows 常见中文语音：Microsoft Huihui，Microsoft Yaoyao，Microsoft Kangkang）
    voices = engine.getProperty("voices")
    chinese_voice = None
    for voice in voices:
        if "chinese" in voice.name.lower() or "huihui" in voice.name.lower() or "yaoyao" in voice.name.lower() or "kangkang" in voice.name.lower():
            chinese_voice = voice.id
            break
    
    if chinese_voice:
        engine.setProperty("voice", chinese_voice)
        print(f"使用语音: {chinese_voice}")
    else:
        print("未找到中文语音，将使用默认语音。请检查 Windows 中文语言包是否已安装。")
    
    # 读取内容
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"\n开始生成 {len(data['words'])} 个动物的音频...")
    
    for item in data["words"]:
        word = item["word"]
        pinyin = item["pinyin"]
        sentence = item["sentence"]
        sound = item["sound"]
        english = item["english"]
        
        print(f"\n生成: {word}")
        
        # 1. 单词读音：猫，māo
        word_text = f"{word}，{pinyin}"
        speak_and_save(engine, word_text, OUTPUT_DIR / f"{english}_word.mp3")
        
        # 2. 例句读音
        sentence_dir = OUTPUT_DIR / "sentences"
        sentence_dir.mkdir(parents=True, exist_ok=True)
        speak_and_save(engine, sentence, sentence_dir / f"{english}_sentence.mp3")
        
        # 3. 叫声（可选）
        if sound != "无":
            speak_and_save(engine, sound, OUTPUT_DIR / f"{english}_sound.mp3")
    
    print("\n全部完成！")
    print(f"音频保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
