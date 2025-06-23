import re
import os
import glob
import datetime

# ===============================================================
# ▼▼▼ 请在这里设置您要处理的文件夹的完整路径 ▼▼▼
# ===============================================================

TARGET_FOLDER_PATH = r"./MCE2/CNPack/config/ftbquests/quests/chapters"

# ===============================================================
# ▲▲▲ 路径设置结束，通常无需修改下面的代码 ▲▲▲
# ===============================================================


def get_processed_parts(raw_content: str) -> list[str]:
    """包含了所有换行符处理规则的核心函数。"""
    content = raw_content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
    
    def replacer(m):
        n = len(m.group(0))
        if n >= 3 and n % 2 != 0:
            return '\n' * (n - 1)
        return m.group(0)
    processed_s = re.sub(r'\n+', replacer, content)

    if processed_s.strip('\n') == '' and processed_s != '':
        num_newlines = len(processed_s)
        if num_newlines == 1:
            parts = [""]
        else:
            num_blanks = num_newlines // 2
            parts = [''] * num_blanks
    else:
        parts = processed_s.split('\n')
        if processed_s.startswith('\n'):
            if parts: parts.pop(0)
        if processed_s.endswith('\n'):
            if parts: parts.pop()
    return parts


def process_snbt_block(match: re.Match) -> str:
    """这是一个回调函数，用于安全地处理 re.sub 找到的每一个匹配的代码块。"""
    original_full_block = match.group(0)
    indent = match.group(1)
    key = match.group(2)
    inside_content = match.group(3)

    # 查找块内部所有的字符串文字
    string_pattern = r'"((?:[^"\\]|\\.)*)"'
    found_strings_contents = [m.group(1) for m in re.finditer(string_pattern, inside_content, re.DOTALL)]

    # 如果没有任何字符串，或者没有任何字符串包含\n，则无需处理
    if not any('\\n' in s for s in found_strings_contents):
        return original_full_block

    # 处理所有字符串，并将它们平铺到一个新列表中
    all_parts = []
    for raw_content in found_strings_contents:
        # 无论是否包含\n，都通过处理函数，以保持逻辑统一
        # 对于不含\n的字符串，get_processed_parts会原样返回内容
        all_parts.extend(get_processed_parts(raw_content))

    # 用处理过的新列表，重构整个代码块（无逗号）
    new_block_lines = [f"{indent}{key}: ["]
    for part in all_parts:
        # 先转义反斜杠，再转义引号
        escaped_part = part.replace('\\', '\\\\').replace('"', '\\"')
        new_block_lines.append(f'{indent}  "{escaped_part}"')
    new_block_lines.append(f"{indent}]")
    
    return "\n".join(new_block_lines)


def process_file_in_place(file_path: str) -> bool:
    """使用“块替换”逻辑处理整个文件内容。"""
    # 这个正则表达式会匹配一个完整的、可能跨越多行的 description 或 hover 代码块
    # 它会捕获：1=缩进, 2=键(description/hover), 3=括号内的所有内容
    block_regex = re.compile(
        r'^(\s*)(description|hover):\s*\[(.*?)\n\s*\]',
        re.DOTALL | re.MULTILINE
    )

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        new_content = block_regex.sub(process_snbt_block, original_content)

        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return True

    except Exception as e:
        print(f"    ❌ 处理文件 '{os.path.basename(file_path)}' 时发生错误: {e}")

    return False

def run_batch_overwrite_processing(folder_path: str):
    """主函数，执行批量覆盖处理。"""
    print("=" * 60)
    print("⚠️  警告: 此脚本将直接修改并覆盖文件夹中的原始 .snbt 文件。")
    print(f"⚠️  当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  此操作无法撤销！开始前请务必备份您的数据！")
    print("=" * 60)

    if folder_path == r"在这里粘贴你的文件夹路径" or not os.path.isdir(folder_path):
        print(f"❌ 错误：请先在脚本中设置有效的 'TARGET_FOLDER_PATH'。")
        return

    try:
        confirm = input("> 请输入 'yes' 以确认您已备份并希望继续: ")
        if confirm.lower() != 'yes':
            print("🛑 操作已取消。没有文件被修改。")
            return
    except EOFError:
        print("\n🛑 在非交互式环境中运行，无法确认。操作已自动取消以确保安全。")
        return

    print("\n🔍 开始扫描和处理文件...")
    
    search_pattern = os.path.join(folder_path, "*.snbt")
    snbt_files = glob.glob(search_pattern)

    if not snbt_files:
        print(f"ℹ️ 在文件夹 '{folder_path}' 中没有找到任何 .snbt 文件。")
        return

    modified_count = 0
    checked_count = 0
    for file_path in snbt_files:
        checked_count += 1
        filename = os.path.basename(file_path)
        print(f"  -> 正在检查: {filename}", end='')
        
        if process_file_in_place(file_path):
            print(" ... 已修改并覆盖。")
            modified_count += 1
        else:
            print(" ... 无需修改。")
    
    print("-" * 60)
    print("🎉 全部完成！")
    print(f"   共检查了 {checked_count} 个文件。")
    print(f"   共修改了 {modified_count} 个文件。")


if __name__ == '__main__':
    run_batch_overwrite_processing(TARGET_FOLDER_PATH)