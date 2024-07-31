import os
import pdfplumber
import re

source_folder = r'data'
target_folder = 'data_txt'

if not os.path.exists(target_folder):
    os.makedirs(target_folder)

for filename in os.listdir(source_folder):  # 遍历pdf文件
    if filename.endswith('.pdf'):
        file_path = os.path.join(source_folder, filename)

        with pdfplumber.open(file_path) as pdf:
            text = ''

            for i, page in enumerate(pdf.pages, 1):
                # 提取页面文本
                page_text = page.extract_text()

                # 处理表格
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        table_text = '\n<Table/>\n'
                        for row in table:
                            row_text = ' | '.join([str(cell) if cell is not None else '' for cell in row])
                            table_text += row_text + '\n'
                        table_text += '</Table>\n'

                        # 构建原始表格内容字符串
                        original_table_text = '\n'.join(
                            [' '.join([str(cell) if cell is not None else '' for cell in row]) for row in table])

                        # 使用正则表达式替换原文本中的表格内容
                        page_text = page_text.replace(original_table_text, table_text)

                if page_text:
                    # 去除每页末尾的类似于n-n-n或n-n-n-n的分页符
                    page_text = re.sub(r'\b(\d+-)+\d+\b$', '', page_text, flags=re.MULTILINE)

                    # 保留原有的段落格式
                    lines = page_text.split('\n')
                    page_text = ''
                    for line in lines:
                        if line.strip():
                            line = line.replace(' ','')
                            page_text += line + '\n'
                        else:
                            page_text += '\n'

                    # 在每页文本末尾添加页码标记
                    page_text += f'\n\n--Page {i}--\n\n'

                    text += page_text

        txt_file_path = os.path.join(target_folder, filename.replace('.pdf', '.txt'))

        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        print(f'{filename} 转换成功')
