import os
import re
import shutil

source_folder=r'data_txt'
target_folder1=r'qa_txt'
target_folder2=r'origin_directory_txt'
mid_folder=r'mid'

def copy_file(src_file, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # 如果目标文件夹不存在，创建它

    shutil.copy(src_file, dest_folder)  # 复制文件到目标文件夹

def first_select(source_folder, target_folder1,target_folder2, mid_folder):
    if not os.path.exists(target_folder1):
        os.makedirs(target_folder1)

    if not os.path.exists(mid_folder):
        os.makedirs(mid_folder)

    for filename in os.listdir(source_folder):
        if filename.endswith('.txt'):
            filename_all=os.path.join(source_folder,filename)

        with open(filename_all,'r',encoding='utf-8') as file:
            content=file.read()

        # 将内容分割为页
        pages = re.sub(r'\b\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}\b|\b\d{1,2}-\d{1,2}-\d{1,2}\b', '', content)
        pages = re.split(r'--Page \d+--',pages)[0:4]  # 仅取前5页


        # 删除--Page i--的标签
        content = re.sub(r'--Page \d+--','',content)

        # 删除分页的标签
        content = re.sub(r'\b(\d+)-(\d+)-(\d+)-(\d+)|\b(\d+)-(\d+)-(\d+)', '', content)

        # 定义目录正则表达式
        directory_pattern=re.compile(r'^(目录\n|\s*目\s*录)', re.IGNORECASE | re.MULTILINE)

        # 定义问题与答案的正则表达式
        qa_pattern=re.compile(r'(\n问题[\s、\d一二三四五六七八九十].*|\n问询问题)(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n【发行人.*?)(?=\n问题|$|\n问询问题)',re.DOTALL)

        # 检查目录是否存在
        page_content='\n'.join(pages)
        has_directory = bool(directory_pattern.search(page_content))

        txt_file_path=os.path.join(target_folder1,filename)

        if not has_directory:
            qa_pairs = qa_pattern.findall(content)

            with open(txt_file_path,'w',encoding='utf-8') as output_file:
                for i,(question,answer) in enumerate(qa_pairs,1):
                    question = re.sub(r'\n\s*\n',r'\n',question.strip())
                    answer = re.sub(r'\n\s*\n',r'\n',answer.strip())
                    output_file.write(f"<Question/>:\n{question.strip()}\n</Question>\n\n<Answer/>:\n{answer.strip()}\n</Answer>\n\n")

            print(f"提取的问题和答案已写入 {txt_file_path}")

        else:
            # 提取目录内容
            directory_contents = []
            directory_content = ''
            directory_start = False
            directory_file_path=os.path.join(mid_folder,filename)
            for line in page_content.split('\n'):
                if directory_pattern.match(line):
                    if directory_start:
                        directory_contents.append(directory_content.strip())
                    directory_start = True
                    directory_content = line + '\n'
                elif directory_start:
                    directory_content += line + '\n'
                    if not line.strip():  # 遇到空行，认为目录结束
                        directory_contents.append(directory_content.strip())
                        directory_start = False
                        directory_content = ''

            # 如果最后一个目录内容未结束，也需加入目录内容列表
            if directory_content.strip():
                directory_contents.append(directory_content.strip())

            with open(directory_file_path, 'w', encoding='utf-8') as directory_file:
                    for dir_content in directory_contents:
                        directory_file.write(dir_content + '\n\n')

            copy_file_name = os.path.join(source_folder,filename)
            copy_file(copy_file_name,target_folder2)
            print(f"目录已提取并写入 {txt_file_path}")


    # 检查目标文件夹中的文件是否为空并删除空文件
    target_name1 = []
    for filename in os.listdir(target_folder1):
        target_filename = os.path.join(target_folder1, filename)
        with open(target_filename, 'r', encoding='utf-8') as target_file:
            target_content = target_file.read()
            if not target_content.strip():  # 检查文件内容是否为空
                target_file.close()  # 确保文件已关闭
                os.remove(target_filename)
                target_name1.append(filename)

    print(f"以下qa_txt文件已被删除，因为它们是空的：{target_name1}")
    return target_name1

first_select(source_folder,target_folder1,target_folder2,mid_folder)


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
    target_folder = 'qa_txt'
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
                                                rf'(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n【发行人.*?)(?=\n{next_title})', re.DOTALL)
                    else:
                        qa_pattern = re.compile(rf'(\n{title}.*?)'
                                                r'(\n回答.*?|\n回复.*?|\n【回复】.*?|\n问题回复.*?|\n回复：.*?|\n【发行人.*?)($)',
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


missing_files = directory_select('mid', 'data_txt')
target_folder = 'qa_txt'
# 检查目标文件夹中的文件是否为空并删除空文件
target_name = []
for filename in os.listdir(target_folder):
    target_filename = os.path.join(target_folder, filename)
    with open(target_filename, 'r', encoding='utf-8') as target_file:
        target_content = target_file.read()
        if not target_content.strip():  # 检查文件内容是否为空
            target_file.close()  # 确保文件已关闭
            os.remove(target_filename)
            target_name.append(filename)

print(f"以下q是空的：{target_name}")

missing_files_in_target = [filename for filename in os.listdir(source_folder) if filename not in os.listdir(target_folder1)]
print(f"以下文件无法通过上述操作进行提取：{missing_files_in_target}")








