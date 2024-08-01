import re
import os
import pandas as pd
import numpy as np

# 第一个表
def extraction_table1(source_folder,qa_folder):
    all_extracted_info = []
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        with open(file_path, mode='r', encoding='utf-8') as file:
            content = file.read()
        content = re.split(r'--Page \d+--',content)

        extracted_info = {}
        extracted_info['公告类型'] = ['问询与回复']

        # 公告标题
        type_match_pattern = re.compile(r'\b(关于|首次)(.*?)(回复|说明|意见|答复)', re.DOTALL)
        type_match_content = []
        for page_content in content[:3]:
            matches = type_match_pattern.findall(page_content)
            if matches:
                matches = ''.join(matches[0])
                type_match_content = [matches.replace('\n','')]
                break
            else:
                type_match_content = ['未找到标题']
        extracted_info['公告标题'] = type_match_content

        # 公告日期
        date_match_pattern = re.compile(r'(\n[一二壹贰零]*年[一二三四五六七八九十]*月)|([\d]+年[\d]*月[\d]*日)')
        date_match_content = []
        for page_content in content[:2]:
            matches = [list(match) for match in date_match_pattern.findall(page_content)]
            if matches:
                matches = ''.join(matches[0]).strip()
                date_match_content = matches.replace('\n','')
                break
            else:
                date_match_content = ['未找到日期']
        extracted_info['公告日期'] = date_match_content

        # 公告页数
        extracted_info['公告页数'] = len(content)

        # 回复人类型
        replier_match_pattern1 = re.compile(r'[与同]([^\n]{1,4})证券股份有限公司')
        replier_match_pattern2 = re.compile(r'[、及\n]([^\n]{1,4})会计师事务所')
        replier_match_pattern3 = re.compile(r'[、及]([^\n]{1,4})律师事务所')
        replier_match_content = []
        for page_content in content[:3]:
            matches1 = replier_match_pattern1.findall(page_content)
            matches2 = replier_match_pattern2.findall(page_content)
            matches3 = replier_match_pattern3.findall(page_content)
            if matches1:
                replier_match_content += [match.replace('\n','')+'证券股份有限公司' for match in matches1]
            if matches2:
                replier_match_content += [match.replace('\n','')+'会计师事务所' for match in matches2]
            if matches3:
                replier_match_content += [match.replace('\n','')+'律师事务所' for match in matches2]
        extracted_info['保荐机构'] = list(np.unique(np.array(replier_match_content)))

        # 问询轮次
        stage_match_pattern = re.compile(r'《.*?的([^\n]{2,3})审核问询函》',re.DOTALL)
        stage_match_content = []
        for page_content in content[:1]:
            matches = stage_match_pattern.findall(page_content)
            if matches:
                stage_match_content += [match.replace('\n','') for match in matches]
                break
            else:
                stage_match_content = ['首轮']
        extracted_info['问询轮次'] = stage_match_content

        # 企业名称
        name_match_pattern = re.compile(r'关于(.*?)股份有限公司',re.DOTALL)
        name_match_content = []
        for page_content in content[:1]:
            matches = name_match_pattern.findall(page_content)
            if matches:
                for match in matches:
                    name_match_content = [match.replace('\n','')+'股份有限公司']
                    break
            else:
                name_match_content = ['未找到企业名称']
        extracted_info['企业名称'] = name_match_content

        # 公告地址
        address_match_pattern = re.compile(r'\n[（]*中国（上海）自由贸易试验区.*?路.*?号[）]*')
        address_match_content = []
        for page_content in content[:1]:
            matches = address_match_pattern.findall(page_content)
            matches = [match for match in matches if '上海' or '深圳' in match]
            if matches:
                for match in matches:
                    address_match_content = [match.replace('\n','')]
            else:
                address_match_content = ['未找到公告地址']
        extracted_info['公告地址'] = address_match_content

        # 问题总数
        qa_match_pattern = re.compile(r'<Question/>:.*?</Question>',re.DOTALL)
        if filename in os.listdir(qa_folder):
            file_path = os.path.join(qa_folder, filename)
            with open(file_path, mode='r', encoding='utf-8') as file:
                content = file.read()
                qa_match_content = qa_match_pattern.findall(content)
                if qa_match_content:
                    extracted_info['问题总数'] = len(qa_match_content)
        else:
            extracted_info['问题总数'] = ['未识别问题']

        extracted_info['文件名'] = filename

        all_extracted_info.append(extracted_info)

    # 转换为DataFrame
    df = pd.DataFrame(all_extracted_info)

    # 显示DataFrame
    print(df)

    # 保存DataFrame到Excel文件
    df.to_excel('extracted_info_table1.xlsx', index=False)

# 文件夹路径
source_folder = 'data_txt'
qa_folder = 'qa_txt'
extraction_table1(source_folder,qa_folder)