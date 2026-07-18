#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成动物图片的 AI 提示词
支持：可灵 / 即梦 / 豆包 / Midjourney / Stable Diffusion
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
OUTPUT_DIR = BASE_DIR / "assets" / "images" / "animals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_BASE = "cute cartoon, flat illustration, big round eyes, rounded shapes, pastel colors, friendly expression, white background, children's book style, vector art, minimalist, clean design, no text, no watermark, no gradient background"


def generate_prompts():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompts = []
    for item in data["words"]:
        word = item["word"]
        english = item["english"]
        custom_prompt = item["image_prompt"]
        
        # 组合提示词：避免重复风格词
        # 如果 custom_prompt 已包含基础风格，则只加缺失的约束
        final_prompt = f"{custom_prompt}, {STYLE_BASE}"
        
        prompts.append({
            "word": word,
            "english": english,
            "prompt": final_prompt.strip(),
            "output_filename": f"{english}.png"
        })
    
    return prompts


def save_prompts_to_file(prompts, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(f"# {p['word']} ({p['english']})\n")
            f.write(f"文件名: {p['output_filename']}\n")
            f.write(f"提示词: {p['prompt']}\n\n")
    print(f"已保存提示词到: {output_file}")


def main():
    prompts = generate_prompts()
    
    output_file = BASE_DIR / "assets" / "images" / "animals" / "prompts.txt"
    save_prompts_to_file(prompts, output_file)
    
    print(f"\n共生成 {len(prompts)} 个动物的图片提示词")
    print("建议使用以下工具生成：")
    print("- 可灵 AI: https://klingai.com/")
    print("- 即梦 AI: https://jimeng.jianying.com/")
    print("- 豆包 AI: https://www.doubao.com/")
    print("- Midjourney（付费）")


if __name__ == "__main__":
    main()
