import os
import shutil

folders_to_delete = ['qa_txt', 'mid']

for folder in folders_to_delete:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"文件夹 {folder} 及其内容已删除")
    else:
        print(f"文件夹 {folder} 不存在")
