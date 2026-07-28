#!/usr/bin/env python3
import os
import time
import urllib.parse
import urllib.request
import json

base_dir = "/mnt/e/kimicode/中文启蒙App_海外华裔3-6岁"
images_dir = os.path.join(base_dir, "assets/images/action_verbs")
os.makedirs(images_dir, exist_ok=True)

content_path = os.path.join(base_dir, "content/action_verbs_module.json")
with open(content_path, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["words"]

style_prompt = "realistic lifestyle photography for young children, clean minimal background, soft natural lighting, warm and friendly atmosphere, the child is the clear main subject, easy for a 4-year-old to recognize, no cartoon, no illustration, no exaggerated big eyes, no text, no watermark"

log_path = os.path.join(base_dir, "generate_action_verbs.log")

existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
pending = [a for a in items if a["file"] not in existing]

with open(log_path, "a", encoding="utf-8") as log:
    log.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Resuming: {len(pending)} pending\n")

    missing = []

    for i, item in enumerate(pending, 1):
        output_path = os.path.join(images_dir, f"{item['file']}.png")
        if os.path.exists(output_path):
            log.write(f"[{i}/{len(pending)}] {item['file']} exists, skip\n")
            continue

        prompt = f"an Asian child demonstrating the action: {item['english']}, {style_prompt}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed=42&enhance=false"

        max_retries = 3
        for attempt in range(max_retries):
            try:
                log.write(f"[{i}/{len(pending)}] Generating {item['file']} ... attempt {attempt+1}\n")
                log.flush()
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (children-app)"})
                with urllib.request.urlopen(req, timeout=90) as resp:
                    data = resp.read()
                    with open(output_path, "wb") as f:
                        f.write(data)
                file_size = os.path.getsize(output_path)
                log.write(f"[{i}/{len(pending)}] {item['file']} saved ({file_size} bytes)\n")
                time.sleep(1)
                break
            except Exception as e:
                log.write(f"[{i}/{len(pending)}] {item['file']} error: {e}\n")
                if attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    log.write(f"Retrying in {wait}s...\n")
                    log.flush()
                    time.sleep(wait)
                else:
                    log.write(f"[{i}/{len(pending)}] {item['file']} FAILED after {max_retries} attempts\n")
                    missing.append(item["file"])

    final_existing = {f[:-4] for f in os.listdir(images_dir) if f.endswith(".png")}
    missing_final = [a["file"] for a in items if a["file"] not in final_existing]
    log.write(f"\nFinal: {len(final_existing)} files, missing: {len(missing_final)}\n")
    if missing_final:
        log.write(f"Missing: {missing_final}\n")
    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Done\n")

print(f"Done. Missing: {len(missing_final)}")
if missing_final:
    print(missing_final)
