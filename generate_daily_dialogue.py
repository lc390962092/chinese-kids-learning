#!/usr/bin/env python3
import os
import time
import urllib.parse
import urllib.request

base_dir = "/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁"
images_dir = os.path.join(base_dir, "assets/images/daily_dialogue")
os.makedirs(images_dir, exist_ok=True)

daily_items = [
    {"name_zh": "你好", "name_en": "hello", "scene": "a smiling Asian child waving hello to a friend"},
    {"name_zh": "再见", "name_en": "goodbye", "scene": "a smiling Asian child waving goodbye at school gate"},
    {"name_zh": "谢谢", "name_en": "thank_you", "scene": "a happy Asian child receiving an apple from grandmother and saying thanks"},
    {"name_zh": "对不起", "name_en": "sorry", "scene": "an Asian child gently apologizing to a friend after bumping into them"},
    {"name_zh": "我饿了", "name_en": "im_hungry", "scene": "an Asian child sitting at table touching tummy, bowl of noodles in front"},
    {"name_zh": "我渴了", "name_en": "im_thirsty", "scene": "an Asian child holding an empty cup, wanting water"},
    {"name_zh": "好吃", "name_en": "delicious", "scene": "an Asian child happily eating a small cake"},
    {"name_zh": "吃饱了", "name_en": "im_full", "name_en_alt": "full", "scene": "an Asian child patting full tummy after meal"},
    {"name_zh": "我想", "name_en": "i_want", "scene": "an Asian child pointing excitedly toward a playground"},
    {"name_zh": "帮忙", "name_en": "help", "scene": "an Asian child asking father to help reach a toy on high shelf"},
    {"name_zh": "洗手", "name_en": "wash_hands", "scene": "an Asian child washing hands with soap bubbles at sink"},
    {"name_zh": "刷牙", "name_en": "brush_teeth", "scene": "an Asian child brushing teeth in bathroom with toothbrush"},
    {"name_zh": "穿衣服", "name_en": "get_dressed", "scene": "an Asian child putting on a sweater by themselves"},
    {"name_zh": "上厕所", "name_en": "go_potty", "scene": "an Asian child standing near a small potty chair"},
    {"name_zh": "起床", "name_en": "wake_up", "scene": "an Asian child stretching and waking up in bed with morning sun"},
    {"name_zh": "睡觉", "name_en": "sleep", "scene": "an Asian child lying in bed ready to sleep with a storybook"},
    {"name_zh": "一起玩", "name_en": "play_together", "scene": "two Asian children playing with colorful building blocks on floor"},
    {"name_zh": "分享", "name_en": "share", "scene": "an Asian child sharing cookies with another child"},
    {"name_zh": "排队", "name_en": "line_up", "scene": "Asian children lining up nicely in front of a slide"},
    {"name_zh": "开心", "name_en": "happy", "scene": "an Asian child laughing happily at a park"},
    {"name_zh": "难过", "name_en": "sad", "scene": "an Asian child looking sad with a broken toy on the ground"},
    {"name_zh": "害怕", "name_en": "scared", "scene": "an Asian child holding a pillow in a dimly lit bedroom"},
    {"name_zh": "疼", "name_en": "hurt", "scene": "an Asian child pointing to a scraped knee"},
    {"name_zh": "不要", "name_en": "no_want", "scene": "an Asian child gently shaking head and saying no at bedtime"},
]

style_prompt = "realistic lifestyle photography for young children, clean minimal background, soft natural lighting, warm and friendly atmosphere, the child is the clear main subject, easy for a 4-year-old to recognize, no cartoon, no illustration, no exaggerated big eyes, no text, no watermark"

log_path = os.path.join(base_dir, "generate_daily_dialogue.log")

existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
pending = [a for a in daily_items if a["name_en"] not in existing]

with open(log_path, "a", encoding="utf-8") as log:
    log.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Resuming: {len(pending)} pending\n")

    for i, item in enumerate(pending, 1):
        output_path = os.path.join(images_dir, f"{item['name_en']}.png")
        if os.path.exists(output_path):
            log.write(f"[{i}/{len(pending)}] {item['name_en']} exists, skip\n")
            continue

        prompt = f"{item['scene']}, {style_prompt}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed=42&enhance=false"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                log.write(f"[{i}/{len(pending)}] Generating {item['name_en']} ... attempt {attempt+1}\n")
                log.flush()
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (children-app)"})
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = resp.read()
                    with open(output_path, "wb") as f:
                        f.write(data)
                file_size = os.path.getsize(output_path)
                log.write(f"[{i}/{len(pending)}] {item['name_en']} saved ({file_size} bytes)\n")
                time.sleep(1)
                break
            except Exception as e:
                log.write(f"[{i}/{len(pending)}] {item['name_en']} error: {e}\n")
                if attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    log.write(f"Retrying in {wait}s...\n")
                    log.flush()
                    time.sleep(wait)
                else:
                    log.write(f"[{i}/{len(pending)}] {item['name_en']} FAILED after {max_retries} attempts\n")

    final_existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
    missing = [a["name_en"] for a in daily_items if a["name_en"] not in final_existing]
    log.write(f"\nFinal: {len(final_existing)} files, missing: {len(missing)}\n")
    if missing:
        log.write(f"Missing: {missing}\n")
    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Done\n")

print(f"Done. Missing: {len(missing)}")
if missing:
    print(missing)
