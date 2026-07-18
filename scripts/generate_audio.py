#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成动物模块音频
使用 Azure TTS 免费额度（每月 50 万字符）

使用前：
1. 在 Azure 创建 Speech 资源
2. 设置环境变量：AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION
3. 安装依赖：pip install azure-cognitiveservices-speech
"""

import os
import json
import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

# 配置
AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY", "YOUR_KEY_HERE")
AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "japaneast")
VOICE = "zh-CN-XiaoxiaoNeural"  # 女声，清晰自然
# VOICE = "zh-CN-YunxiNeural"   # 童声/年轻男声，可选

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "audio" / "animals"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def synthesize(text, output_path, voice=VOICE):
    """合成一个音频文件"""
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_synthesis_voice_name = voice
    speech_config.speech_synthesis_output_format = (
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    
    audio_config = speechsdk.audio.AudioConfig(filename=str(output_path))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"✓ 已生成: {output_path}")
        return True
    else:
        print(f"✗ 失败: {output_path}")
        print(f"  原因: {result.reason}")
        if result.cancellation_details:
            print(f"  详情: {result.cancellation_details.reason}")
        return False


def generate_word_audio(word, pinyin, english):
    """生成单词读音：猫，māo"""
    text = f"{word}，{pinyin}"
    output = OUTPUT_DIR / f"{english}_word.mp3"
    synthesize(text, output)


def generate_sentence_audio(sentence, english):
    """生成例句读音"""
    output = OUTPUT_DIR / "sentences" / f"{english}_sentence.mp3"
    output.parent.mkdir(parents=True, exist_ok=True)
    synthesize(sentence, output)


def generate_sound_audio(sound, english):
    """生成叫声（可选）"""
    if sound == "无":
        return
    output = OUTPUT_DIR / f"{english}_sound.mp3"
    synthesize(sound, output)


def main():
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
        generate_word_audio(word, pinyin, english)
        generate_sentence_audio(sentence, english)
        generate_sound_audio(sound, english)
    
    print("\n全部完成！")
    print(f"音频保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
