import asyncio
import json
import os
from pprint import pprint

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
                await api_instance.update_file(
                    project_id, file_id=existing_file.id, file=file
                )
                print(f"文件已更新！文件路径为：{full_path}")
            else:
                # 如果文件不存在，创建新文件
                api_response = await api_instance.create_file(
                    project_id, file=file, path=path
                )
                pprint(api_response)
            break # 成功则退出重试循环
        except ValidationError as error:
            print(f"文件上传成功{path}{file_name}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s
                print(f"上传文件 {file} 失败: {e}。正在重试 ({attempt + 1}/{max_retries})... 等待 {wait_time} 秒")
                await asyncio.sleep(wait_time)
            else:
                print(f"上传文件 {file} 时发生未知错误，已达到最大重试次数: {e}")


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


async def main():
    handle_ftb_quests_snbt()

    files = get_filelist("./Source")
    tasks = []

    if not files:
        print("在 'Source' 目录中未找到任何 'en_us.json' 文件。请检查文件是否存在。")
        return

    # 预先获取文件列表
    project_id = int(os.environ["PROJECT_ID"])
    
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        try:
            existing_files_list = await api_instance.get_files(project_id)
            # 转换为字典以进行 O(1) 查找
            existing_files_dict = {f.name: f for f in existing_files_list}
        except Exception as e:
            print(f"获取文件列表失败: {e}")
            existing_files_dict = {}

        # 限制并发数为 1
        sem = asyncio.Semaphore(1)

        async def upload_with_limit(path, file):
            async with sem:
                await upload_file(api_client, project_id, path, file, existing_files_dict)

        for file in files:
            # 使用 os.path.relpath 获取相对于 'Source' 目录的正确路径
            path = os.path.relpath(os.path.dirname(file), "./Source")

            # 如果文件直接位于 Source 目录下，relpath 会返回 "."，将其转换为空路径
            if path == ".":
                path = ""

            # 统一路径分隔符为 '/'
            path = path.replace("\\", "/")

            # 如果路径非空（不是根目录），确保它以 '/' 结尾
            if path:
                path += "/"

            print(f"准备上传 {file} 到 Paratranz 路径: '{path}'")
            tasks.append(upload_with_limit(path=path, file=file))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
