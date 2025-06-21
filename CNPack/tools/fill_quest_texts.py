import re
import json
import os

# 读取语言文件，并将所有值中的换行符替换为 \n 字符串
with open('d:/mc/mod/MCE2/CNPack/kubejs/assets/modpack/lang/en_us.json', 'r', encoding='utf-8') as f:
    lang_raw = json.load(f)
lang = {k: v.replace('\n', '\\n') for k, v in lang_raw.items()}

# SNBT 文件目录
snbt_dir = 'd:/mc/mod/MCE2/CNPack/config/ftbquests/quests'

def replace_key(match):
    key = match.group(1)
    return lang.get(key, match.group(0))

pattern = re.compile(r'\{([^\{\}]+)\}')

for root, dirs, files in os.walk(snbt_dir):
    for filename in files:
        if filename.endswith('.snbt'):
            file_path = os.path.join(root, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                snbt = f.read()
            snbt_new = pattern.sub(replace_key, snbt)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(snbt_new)
            print(f"{filename} 回填完成，已覆盖原文件")