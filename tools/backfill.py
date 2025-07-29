import re
import json
import os

"""
把硬编码和混合翻译键的任务都根据语言文件替换为硬编码

还有 kubejs/assets/ftbquests_botania/lang/en_us.json 记得运行两次！
两个路径都是原整合包文件，需要手动复制到这里，用完记得删！

运行出错是因为整合包这行写的有问题，换成下面的转义（搜索key替换）
  "chapter.1.quest.2.task.1.title": "\u0026o\u00a7dSign here... here... and here \t\u00a7e\u00a7n((Click to complete))",
"""

with open("CNPack/kubejs/assets/modpack/lang/en_us.json", "r", encoding="utf-8") as f:
    lang_raw = json.load(f)
lang = {k: v.replace("\n", "\\n") for k, v in lang_raw.items()}

# SNBT 文件目录
snbt_dir = "CNPack/config/ftbquests/quests"


def replace_key(match):
    key = match.group(1)
    return lang.get(key, match.group(0))


pattern = re.compile(r"\{([^\{\}]+)\}")

for root, dirs, files in os.walk(snbt_dir):
    for filename in files:
        if filename.endswith(".snbt"):
            file_path = os.path.join(root, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                snbt = f.read()
            snbt_new = pattern.sub(replace_key, snbt)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(snbt_new)
            print(f"{filename} 回填完成，已覆盖原文件")
