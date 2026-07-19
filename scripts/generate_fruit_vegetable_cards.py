#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动生成水果蔬菜词卡图片"""
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_FILE = BASE_DIR / "content" / "fruit_vegetable_module.json"
IMAGE_DIR = BASE_DIR / "assets" / "images" / "fruits_vegetables"
OUTPUT_DIR = BASE_DIR / "assets" / "cards" / "fruit_vegetable_cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CARD_WIDTH = 600
CARD_HEIGHT = 400


def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def create_card(item, output_path):
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#E8F5E9")
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle(
        [(10, 10), (CARD_WIDTH-10, CARD_HEIGHT-10)],
        radius=30,
        outline="#FF8C42",
        width=5
    )
    
    item_img_path = IMAGE_DIR / f"{item['english']}.png"
    if item_img_path.exists():
        item_img = Image.open(item_img_path).convert("RGBA")
        item_img.thumbnail((220, 220), Image.Resampling.LANCZOS)
        img.paste(item_img, (60, 90), item_img)
    
    font_char = get_font(100)
    draw.text((320, 80), item["word"], fill="#333333", font=font_char)
    
    font_pinyin = get_font(40)
    draw.text((320, 200), item["pinyin"], fill="#888888", font=font_pinyin)
    
    font_en = get_font(28)
    draw.text((320, 270), item["english"], fill="#AAAAAA", font=font_en)
    
    img.save(output_path, "PNG")
    print(f"✓ 已生成词卡: {output_path}")


def main():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"开始生成 {len(data['words'])} 张水果蔬菜词卡...")
    
    for item in data["words"]:
        output_path = OUTPUT_DIR / f"{item['english']}_card.png"
        create_card(item, output_path)
    
    print(f"\n全部完成！词卡保存位置: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
