import asyncio
import json
from pathlib import Path

import edge_tts

# 生成时间主题音频（时段、整点、星期、日期）
# 词音频：只读当前词（中文/英文/日文假名）
# 例句音频：只读对应例句

PROJECT = Path('/mnt/e/kimicode/chinese-kids-learning')
CONTENT_DIR = PROJECT / 'content'
AUDIO_DIR = PROJECT / 'assets' / 'audio' / 'time'

VOICES = {
    'zh': 'zh-CN-XiaoxiaoNeural',
    'en': 'en-US-AnaNeural',
    'ja': 'ja-JP-NanamiNeural',
}


def iter_tasks(data):
    for sec in data['sections']:
        section_id = sec['id']
        for i, item in enumerate(sec['items']):
            base = AUDIO_DIR / section_id / f'{i:02d}'
            yield base / 'zh.mp3', item.get('time_cn') or item.get('weekday_cn') or item.get('date_cn', ''), 'zh'
            yield base / 'en.mp3', item.get('time_en') or item.get('weekday_en') or item.get('date_en', ''), 'en'
            yield base / 'ja.mp3', item.get('time_ja_kana') or item.get('weekday_ja_kana') or item.get('date_ja_kana') or item.get('date_ja') or '', 'ja'
            if 'sentence_cn' in item:
                sbase = AUDIO_DIR / section_id / 'sentences' / f'{i:02d}'
                yield sbase / 'cn_zh.mp3', item['sentence_cn'], 'zh'
                yield sbase / 'cn_en.mp3', item['sentence_en'], 'en'
                yield sbase / 'cn_ja.mp3', item.get('sentence_ja_kana') or item.get('sentence_ja', ''), 'ja'


async def generate(path: Path, text: str, lang: str):
    if not text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    voice = VOICES[lang]
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(path))
        print(f'OK {path.relative_to(PROJECT)}')
    except Exception as e:
        print(f'FAIL {path}: {e}')


async def main():
    with open(CONTENT_DIR / 'time_module.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = [generate(path, text, lang) for path, text, lang in iter_tasks(data)]
    print(f'total tasks: {len(tasks)}')
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())
