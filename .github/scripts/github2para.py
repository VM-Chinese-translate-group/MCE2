import asyncio
import json
import os
from pprint import pprint
from collections import OrderedDict

import paratranz_client
from pydantic import ValidationError

from LangSpliter import split_and_process_all

configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key["Token"] = os.environ["API_TOKEN"]


async def upload_file(api_client, project_id, path, file, existing_files_dict):
    api_instance = paratranz_client.FilesApi(api_client)
    
    # 构建 Paratranz 中的完整文件路径
    file_name = os.path.basename(file)
    full_path = path + file_name
    
    # 检查文件是否已存在
    existing_file = existing_files_dict.get(full_path)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if existing_file:
                # 如果文件存在，直接更新
                print(f"正在更新文件: {full_path} (ID: {existing_file.id})")
                await api_instance.update_file(
                    project_id, file_id=existing_file.id, file=file
                )
                print(f"文件更新成功: {full_path}")
            else:
                # 如果文件不存在，创建新文件
                print(f"正在创建新文件: {full_path} 在路径: {path}")
                api_response = await api_instance.create_file(
                    project_id, file=file, path=path
                )
                print(f"文件创建成功: {full_path}")
                pprint(api_response)
            break
        except ValidationError as error:
            # 这是一个已知的 SDK 问题，有时即使成功也会抛出校验错误
            print(f"文件上传处理完成 (忽略校验错误): {full_path}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"上传失败 {file}: {e}。正在尝试第 {attempt + 1} 次重试... ({wait_time}s)")
                await asyncio.sleep(wait_time)
            else:
                print(f"上传文件 {file} 彻底失败，已达到最大重试次数: {e}")


def get_filelist(dir):
    filelist = []
    for root, _, files in os.walk(dir):
        for file in files:
            if "en_us" in file and file.endswith(".json"):
                filelist.append(os.path.join(root, file))
    return filelist


def handle_ftb_quests_snbt():
    """
    检查是否存在 FTB Quests 的 en_us.snbt 文件。
    如果存在，则使用 LangSpliter 将其拆分为多个 JSON 文件，以便上传。
    """
    snbt_file = "Source/config/ftbquests/quests/lang/en_us.snbt"
    chapters_dir = "Source/config/ftbquests/quests/chapters"
    chapter_groups_file = "Source/config/ftbquests/quests/chapter_groups.snbt"
    # 定义拆分后的JSON文件输出目录，与para2github.py的逻辑保持一致
    output_json_dir = "Source/kubejs/assets/quests/lang"

    if os.path.exists(snbt_file):
        print(f"检测到 SNBT 文件: {snbt_file}，将进行自动拆分...")

        # 确保输出目录存在
        os.makedirs(output_json_dir, exist_ok=True)

        # 调用 LangSpliter 的拆分函数
        # flatten_single_lines=False 是为了让多行文本在Paratranz中成为多个独立的词条，便于翻译
        split_and_process_all(
            source_lang_file=snbt_file,
            chapters_dir=chapters_dir,
            chapter_groups_file=chapter_groups_file,
            output_dir=output_json_dir,
            flatten_single_lines=False,
        )
        print("SNBT 文件已成功拆分为 JSON，准备上传。")
    else:
        print("未检测到 FTB Quests 的 en_us.snbt 文件，跳过拆分步骤。")


def handle_modpack_lang_split():
    """
    将 Source/kubejs/assets/modpack/lang/en_us.json 按照不同的键名开头拆分成不同的文件。
    这样可以优化 Paratranz 的翻译体验，避免单个大文件。
    """
    target_file = "Source/kubejs/assets/modpack/lang/en_us.json"
    if not os.path.exists(target_file):
        print(f"未检测到 {target_file}，跳过拆分。")
        return

    print(f"检测到 {target_file}，开始按照键名前缀进行拆分...")
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
        print(f"成功读取 {target_file}，包含 {len(data)} 条条目")
    except Exception as e:
        print(f"读取 {target_file} 失败: {e}")
        return

    split_data = {}
    for key, value in data.items():
        # ... (逻辑保持不变)
        if key.startswith("ftbquests.chapter."):
            parts = key.split(".")
            if len(parts) >= 3:
                chapter_id = parts[2]
                filename = f"en_us_chapter_{chapter_id}.json"
            else:
                filename = "en_us_others.json"
        elif key.startswith("ftbquests.loot_table."):
            filename = "en_us_loot_tables.json"
        elif key.startswith("ftbquests.chapter_groups."):
            filename = "en_us_chapter_groups.json"
        else:
            filename = "en_us_others.json"

        if filename not in split_data:
            split_data[filename] = OrderedDict()
        split_data[filename][key] = value

    output_dir = os.path.dirname(target_file)
    for filename, content in split_data.items():
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        print(f"  -> 已生成拆分文件: {output_path} ({len(content)} 条目)")

    # 移除原始大文件，以防被 get_filelist 搜到重复上传
    try:
        os.remove(target_file)
        print(f"原始大文件 {target_file} 已成功移除。")
    except Exception as e:
        print(f"移除原始文件失败: {e}")


async def main():
    print(">>> 启动工作流脚本...")
    try:
        handle_ftb_quests_snbt()
        handle_modpack_lang_split()

        print(">>> 扫描 Source 目录寻找翻译文件...")
        files = get_filelist("./Source")
        print(f">>> 找到 {len(files)} 个待上传文件")
        
        if not files:
            print("警告: 未找到任何 en_us.json 文件。")
            return

        tasks = []
        # 检查环境变量
        project_id_str = os.environ.get("PROJECT_ID")
        api_token = os.environ.get("API_TOKEN")
        
        if not project_id_str or not api_token:
            print("错误: 环境变量 PROJECT_ID 或 API_TOKEN 未设置。")
            return
            
        project_id = int(project_id_str)
        print(f">>> 项目 ID: {project_id}")

        async with paratranz_client.ApiClient(configuration) as api_client:
            api_instance = paratranz_client.FilesApi(api_client)
            print(">>> 正在从 ParaTranz 获取现有文件列表...")
            try:
                existing_files_list = await api_instance.get_files(project_id)
                existing_files_dict = {f.name: f for f in existing_files_list}
                print(f">>> 成功获取 {len(existing_files_dict)} 个现有文件")
            except Exception as e:
                print(f"警告: 获取现有文件列表失败 (可能项目是空的): {e}")
                existing_files_dict = {}

            sem = asyncio.Semaphore(1)

            async def upload_with_limit(path, file):
                async with sem:
                    await upload_file(api_client, project_id, path, file, existing_files_dict)

            for file in files:
                path = os.path.relpath(os.path.dirname(file), "./Source")
                if path == ".":
                    path = ""
                path = path.replace("\\", "/")
                if path:
                    path += "/"

                print(f"准备上传: {file} -> ParaTranz 路径: {path}")
                tasks.append(upload_with_limit(path=path, file=file))

            await asyncio.gather(*tasks)
            print(">>> 所有上传任务已提交。")
            
    except Exception as e:
        print(f"致命错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
