import os
import re
def parse_directory(text):
    directories = []
    lines = text.split('\n')

    for line in lines:
        # 第一种目录格式
        match1 = re.match(r'(\d+)\s*(.*?)\s*[\.\·]{3,}\s*(\d+)', line, re.DOTALL)
        if match1:
            number, title, page = match1.groups()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([f'{number}{title}', int(page)])
            continue

        # 第二种目录格式
        match2 = re.match(r'([一二三四五六七八九十]+[、\d]*.*?)第\s*(\d+)[—\-–]\d+\s*页', line)
        if match2:
            title, page = match2.groups()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, int(page)])
            continue

        # 第三种目录格式
        match3 = re.match(r'(问题\d+[、\d]*.*?)[\.\·]{3,}\s*(\d+)', line)
        if match3:
            title, page = match3.groups()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, int(page)])
            continue

        # 第四种目录格式
        match4 = re.match(r'([一二三四五六七八九十]+、\s*.*)', line)
        if match4:
            title = match4.group(1).strip()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, 1])
            continue

        # 第五种目录格式
        match5 = re.match(r'(问题[\d一二三四五六七八九十](\.\d+)*[、\d]*.*?)\s*\.{3,}\s*(\d+)', line)
        if match5:
            title, page = match5.groups()[0], match5.groups()[2]
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, int(page)])  # 只添加子问题
            continue

        # 第六种目录格式
        match6 = re.match(r'(问题[一二三四五六七八九十]+|保荐机构总体意见)\s*\.{3,}\s*(\d+)', line)
        if match6:
            title, page = match6.groups()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, int(page)])
            continue

        # 第七种目录格式
        match7 = re.match(r'(审核问询函的回复)\s*(\d+)', line)
        if match7:
            title, page = match7.groups()
            title = re.sub(r'[\.…]{3,}', '', title).strip()  # 删除标题中的...符号
            directories.append([title, int(page)])
            continue


    unique_directories = []
    for i in range(len(directories)):
        if i == len(directories) - 1 or directories[i][1] != directories[i + 1][1]:
            unique_directories.append(directories[i])
    directories = unique_directories

    print(directories)
    return directories


def directory_select(directory_folder, txt_folder):
    directory_file_list = os.listdir(directory_folder)
    target_folder = 'opo_txt'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder, exist_ok=True)

    missing_directories = []  # 用于保存未能提取目录的文件名

    for filename in os.listdir(txt_folder):
        if filename in directory_file_list:
            directory_filename = os.path.join(directory_folder, filename)
            with open(directory_filename, 'r', encoding='utf-8') as f:  # 读取目录内容
                text = f.read()
                directories = parse_directory(text)

            if not directories:
                missing_directories.append(filename)
                continue

            txt_filename = os.path.join(txt_folder, filename)
            with open(txt_filename, 'r', encoding='utf-8') as f:
                file = f.read()
                pages = re.split(r'--Page \d+--', file)

            directory_dict = {item[0]: item[1] for item in directories}
            page_list = list(directory_dict.values())

            # 检查第一个目录标题页码是否包含目录内容，如果是，则页码加1
            if any('目录' in line for line in pages[page_list[0]].split('\n')):
                page_list[0] += 1

            combined_content = ''.join(pages[page_list[0]:])  # 只考虑目录页后的内容

            titles = list(directory_dict.keys())

            qa_pairs = []
            if len(titles) < 2:
                qa_pattern = re.compile(r'(\n\d+[、].*?|\n问题[\s、\d一二三四五六七八九十].*?)(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n【发行人.*?)(?=\n问题|$)', re.DOTALL)
                qa_pairs = qa_pattern.findall(combined_content)
            else:
                for i, title in enumerate(titles):
                    if i < len(titles) - 1:
                        next_title = titles[i + 1]
                        qa_pattern = re.compile(rf'(\n{title}.*?)'
                                                rf'(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n【发行人.*?|\n发行人说明.*?|\n一、发行人说明)(?=\n{next_title})', re.DOTALL)
                    else:
                        qa_pattern = re.compile(rf'(\n{title}.*?)'
                                                r'(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n回复：.*?|\n【发行人.*?|\n发行人说明.*?|\n一、发行人说明)($)',
                                                re.DOTALL)

                    qa_pairs.extend(qa_pattern.findall(combined_content))

            qa_pairs = [pair for pair in qa_pairs if all(pair)]

            target_name = os.path.join(target_folder, filename)
            with open(target_name, 'a', encoding='utf-8') as output_file:
                for (question, answer) in qa_pairs:
                    question = re.sub(r'\n\s*\n', r'\n', question.strip())
                    answer = re.sub(r'\n\s*\n', r'\n', answer.strip())
                    output_file.write(
                            f"<Question/>:\n{question.strip()}\n</Question>\n\n<Answer/>:\n{answer.strip()}\n</Answer>\n\n")

    if missing_directories:
        print(f'未能提取目录的文件: {missing_directories}')
    else:
        print('所有目录均被正确提取')

    return missing_directories


missing_files = directory_select('mid1', 'data_txt1')
target_folder = 'opo_txt'
# 检查目标文件夹中的文件是否为空并删除空文件
target_name = []
for filename in os.listdir(target_folder):
    target_filename = os.path.join(target_folder, filename)
    with open(target_filename, 'r', encoding='utf-8') as target_file:
        target_content = target_file.read()
        if not target_content.strip():  # 检查文件内容是否为空
            target_file.close()  # 确保文件已关闭
            target_name.append(filename)

print(f"以下q是空的：{target_name}")


