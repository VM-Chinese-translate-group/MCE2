import json
import os
import re

def load_lang_file(lang_file_path):
    """加载语言文件"""
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_snbt_file(file_path, lang_data):
    """直接根据key回填所有字段，自动处理description数组，保留\\n为字符串内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_key(match):
        key = match.group(1)
        if key not in lang_data:
            return f'"{key}"'
        value = lang_data[key].replace('\\', '\\\\').replace('\n', r'\\n')
        before = content[:match.start()]
        desc_array_match = re.search(r'description:\s*\[\s*$', before[-50:], re.DOTALL)
        if desc_array_match or ('.description.' in key):
            # 这里不分割，直接作为一行字符串，保留\\n
            return f'"{value}"'
        else:
            return f'"{value}"'

    # 替换所有形如 "xxx.xxx.xxx" 的key
    # 先处理description数组
    def desc_array_replacer(match):
        arr = match.group(0)
        # 找到所有key
        keys = re.findall(r'"([^"\n]+?)"', arr)
        new_lines = []
        for key in keys:
            if key in lang_data:
                val = lang_data[key].replace('\\', '\\\\').replace('\n', r'\\n')
                new_lines.append(f'    "{val}"')
            else:
                new_lines.append(f'    "{key}"')
        return 'description: [\n' + ',\n'.join(new_lines) + '\n]'
    # 先处理description: [ ... ]
    content = re.sub(r'description:\s*\[[^\]]*\]', desc_array_replacer, content, flags=re.DOTALL)
    # 再处理所有字符串key
    content = re.sub(r'"([a-zA-Z0-9_.]+)"', replace_key, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # 配置路径
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lang_file_path = os.path.join(base_path, 'kubejs', 'assets', 'modpack', 'lang', 'en_us.json')
    quests_dir = os.path.join(base_path, 'config', 'ftbquests', 'quests', 'chapters')
    
    # 加载语言文件
    lang_data = load_lang_file(lang_file_path)
    
    # 处理所有snbt文件
    for file_name in os.listdir(quests_dir):
        if file_name.endswith('.snbt'):
            file_path = os.path.join(quests_dir, file_name)
            print(f"Processing {file_name}...")
            try:
                process_snbt_file(file_path, lang_data)
                print(f"Successfully processed {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")

if __name__ == "__main__":
    main()
