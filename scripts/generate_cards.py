#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成动物词卡图片
需要依赖：Pillow
安装：pip install Pillow
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "animal_module.json"
IMAGE_DIR = BASE_DIR / "assets" / "images" / "animals"
OUTPUT_DIR = BASE_DIR / "assets" / "cards" / "animal_cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 卡片尺寸
CARD_WIDTH = 600
CARD_HEIGHT = 400


def get_font(size):
    """获取字体，优先使用系统中文字体"""
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
        "C:/Windows/Fonts/msyh.ttc",    # Windows 雅黑
        "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    # 如果找不到中文字体，用默认字体（可能无法显示中文）
    return ImageFont.load_default()


def create_card(animal, output_path):
    """创建一张词卡"""
    # 创建背景
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#FFF8E7")
    draw = ImageDraw.Draw(img)
    
    # 画圆角边框
    draw.rounded_rectangle(
        [(10, 10), (CARD_WIDTH-10, CARD_HEIGHT-10)],
        radius=30,
        outline="#FF6B6B",
        width=5
    )
    
    # 加载动物图片
    animal_img_path = IMAGE_DIR / f"{animal['english']}.png"
    if animal_img_path.exists():
        animal_img = Image.open(animal_img_path).convert("RGBA")
        # 保持比例缩放
        animal_img.thumbnail((220, 220), Image.Resampling.LANCZOS)
        # 贴到左边
        img.paste(animal_img, (60, 90), animal_img)
    
    # 写汉字
    font_char = get_font(100)
    draw.text((320, 80), animal["word"], fill="#333333", font=font_char)
    
    # 写拼音
    font_pinyin = get_font(40)
    draw.text((320, 200), animal["pinyin"], fill="#888888", font=font_pinyin)
    
    # 写英文
    font_en = get_font(28)
    draw.text((320, 270), animal["english"], fill="#AAAAAA", font=font_en)
    
    # 保存
    img.save(output_path, "PNG")
    print(f"✓ 已生成词卡: {output_path}")


def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"开始生成 {len(data['words'])} 张词卡...")
    
    for animal in data["words"]:
        output_path = OUTPUT_DIR / f"{animal['english']}_card.png"
        create_card(animal, output_path)
    
    print(f"\n全部完成！词卡保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
