#!/usr/bin/env python3
import os
import time
import urllib.parse
import urllib.request

base_dir = "/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁"
images_dir = os.path.join(base_dir, "assets/images/animals")

animals = [
    {"name_zh": "袋鼠", "name_en": "kangaroo"},
    {"name_zh": "考拉", "name_en": "koala"},
    {"name_zh": "斑马", "name_en": "zebra"},
    {"name_zh": "河马", "name_en": "hippo"},
    {"name_zh": "犀牛", "name_en": "rhino"},
    {"name_zh": "鳄鱼", "name_en": "crocodile"},
    {"name_zh": "鸵鸟", "name_en": "ostrich"},
    {"name_zh": "孔雀", "name_en": "peacock"},
    {"name_zh": "天鹅", "name_en": "swan"},
    {"name_zh": "燕子", "name_en": "swallow"},
    {"name_zh": "刺猬", "name_en": "hedgehog"},
    {"name_zh": "松鼠", "name_en": "squirrel"},
    {"name_zh": "狐狸", "name_en": "fox"},
    {"name_zh": "大灰狼", "name_en": "wolf"},
    {"name_zh": "豹子", "name_en": "leopard"},
    {"name_zh": "骆驼", "name_en": "camel"},
    {"name_zh": "蜘蛛", "name_en": "spider"},
    {"name_zh": "蚯蚓", "name_en": "earthworm"},
    {"name_zh": "萤火虫", "name_en": "firefly"},
    {"name_zh": "飞蛾", "name_en": "moth"},
    {"name_zh": "螳螂", "name_en": "mantis"},
    {"name_zh": "知了", "name_en": "cicada"},
    {"name_zh": "蚱蜢", "name_en": "grasshopper"},
    {"name_zh": "蝎子", "name_en": "scorpion"},
    {"name_zh": "蜈蚣", "name_en": "centipede"},
    {"name_zh": "海马", "name_en": "seahorse"},
    {"name_zh": "水母", "name_en": "jellyfish"},
    {"name_zh": "贝壳", "name_en": "seashell"},
    {"name_zh": "龙虾", "name_en": "lobster"},
    {"name_zh": "海胆", "name_en": "sea_urchin"},
    {"name_zh": "海参", "name_en": "sea_cucumber"},
    {"name_zh": "海葵", "name_en": "anemone"},
    {"name_zh": "鳗鱼", "name_en": "eel"},
    {"name_zh": "蝙蝠", "name_en": "bat"},
    {"name_zh": "乌鸦", "name_en": "crow"},
    {"name_zh": "鹦鹉", "name_en": "parrot"},
    {"name_zh": "老鹰", "name_en": "eagle"},
    {"name_zh": "鸽子", "name_en": "pigeon"},
    {"name_zh": "啄木鸟", "name_en": "woodpecker"},
    {"name_zh": "变色龙", "name_en": "chameleon"},
]

style_prompt = "cute cartoon illustration for children, simple flat design, soft pastel colors, friendly expression, clean white background, no text, no watermark, suitable for 3-6 year old kids"

log_path = os.path.join(base_dir, "generate_animals.log")

# 计算已生成数量，从上次断点继续
existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
pending = [a for a in animals if a["name_en"] not in existing]

with open(log_path, "a", encoding="utf-8") as log:
    log.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Resuming: {len(pending)} pending\n")

    for i, animal in enumerate(pending, 1):
        output_path = os.path.join(images_dir, f"{animal['name_en']}.png")
        if os.path.exists(output_path):
            log.write(f"[{i}/{len(pending)}] {animal['name_en']} exists, skip\n")
            continue

        prompt = f"A cute cartoon {animal['name_en']}, {style_prompt}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed=42&enhance=false"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                log.write(f"[{i}/{len(pending)}] Generating {animal['name_en']} ... attempt {attempt+1}\n")
                log.flush()
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (children-app)"})
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = resp.read()
                    with open(output_path, "wb") as f:
                        f.write(data)
                file_size = os.path.getsize(output_path)
                log.write(f"[{i}/{len(pending)}] {animal['name_en']} saved ({file_size} bytes)\n")
                time.sleep(1)
                break
            except Exception as e:
                log.write(f"[{i}/{len(pending)}] {animal['name_en']} error: {e}\n")
                if attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    log.write(f"Retrying in {wait}s...\n")
                    log.flush()
                    time.sleep(wait)
                else:
                    log.write(f"[{i}/{len(pending)}] {animal['name_en']} FAILED after {max_retries} attempts\n")

    # 最终统计
    final_existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
    missing = [a["name_en"] for a in animals if a["name_en"] not in final_existing]
    log.write(f"\nFinal: {len(final_existing)} files, missing: {len(missing)}\n")
    if missing:
        log.write(f"Missing: {missing}\n")
    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Done\n")

print(f"Done. Missing: {len(missing)}")
if missing:
    print(missing)
