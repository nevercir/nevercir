import pandas as pd
import re
import os


def judge_type(directory,question):
    count = 0
    question = question.replace('\n','')
    for element in directory:
        if element in question:
            count += 1
    return count


def Table_categorize(qa_folder):
    all_dict1 = []
    all_dict2 = []
    all_dict3 = []
    all_dict4 = []
    all_dict5 = []
    all_dict6 = []

    # 关键字词库建立
    directory1 = [
    "股份", "股权"
    "控股股东", "实际控制人", "股东结构", "股权变动", "股权激励",
    "持股比例", "股权稀释", "股东大会", "股份分配", "股东权益",
    "股东协议", "股东会决议", "股份制改革", "股东类型",
    "股权融资", "股东关系", "股权转让", "股东收益",
    "控股比例", "分红政策", "股东责任"
]

    directory2 = [
    "独立董事", "董事会", "监事会", "公司章程", "管理层",
    "内部控制", "治理结构", "独立性", "治理准则", "内部审计",
    "合规机制", "风险管理", "管理层持股", "审计委员会",
    "独立性声明", "治理评价", "董事会会议", "公司决策",
    "企业文化", "领导层", "公司政策", "决策流程",
    "治理责任", "信息披露", "内部治理", "公司伦理"
]

    directory3 = [
    "主营业务", "业务模式", "市场竞争", "行业地位", "客户群体",
    "产品线", "供应链", "业务增长", "市场份额", "业务扩展",
    "市场策略", "市场趋势", "销售渠道", "客户关系",
    "商业伙伴", "业务风险", "市场需求", "产品开发",
    "商业模式", "品牌价值", "市场定位", "产业链",
    "商业战略", "业务计划", "客户服务", "创新业务"
]

    directory4 = [
    "技术专利", "研发投入", "技术团队", "知识产权", "技术创新",
    "技术壁垒", "核心竞争力", "技术应用", "研发中心", "技术合作",
    "技术许可", "技术成果", "技术开发", "技术转让",
    "技术储备", "创新能力", "科技发展", "研发项目",
    "新技术", "技术标准", "技术评估", "技术平台",
    "研发能力", "创新项目", "技术趋势", "技术整合"
]

    directory5 = [
    "财务报表", "收入增长", "净利润", "资产负债", "现金流量",
    "财务指标", "成本控制", "财务风险", "财务分析", "盈利能力",
    "资产管理", "流动性", "资本结构", "会计政策",
    "财务预测", "收益质量", "管理费用", "资产负债表",
    "损益表", "利润分配", "财务规划", "税务筹划",
    "成本分析", "财务绩效", "审计报告", "财务健康",
    "财务透明度", "会计准则", "财务稳定性"
]

    directory6 = [
    "市场风险", "法律风险", "合规风险", "投资项目", "环境保护",
    "社会责任", "风险管理", "募集资金", "可持续发展", "合规管理",
    "惩处机制", "环境影响", "环保政策", "募投计划",
    "项目风险", "ESG因素", "绿色发展", "公益活动",
    "投资风险", "风险评估", "安全生产", "危机管理",
    "合规风险", "法律责任", "生态影响", "社会影响",
    "项目评估", "风险缓解", "环境责任", "社会贡献"
]

    for filename in os.listdir(qa_folder):
        file_path = os.path.join(qa_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 字典分类
        dict1 = {} # 发行人股权结构
        dict2 = {} # 公司治理与独立性
        dict3 = {} # 发行人业务
        dict4 = {} # 发行人核心技术
        dict5 = {} # 财务会计信息与管理层分析
        dict6 = {} # 风险、惩处、募投及环保事项

        dict1['文件名'] = filename
        dict2['文件名'] = filename
        dict3['文件名'] = filename
        dict4['文件名'] = filename
        dict5['文件名'] = filename
        dict6['文件名'] = filename

        # 问题提取
        question_pattern = re.compile(r'<Question/>:(.*?)</Question>', re.DOTALL)
        questions = question_pattern.findall(content)

        # 判断问题分类，若不属于返回空字符串
        for index, question in enumerate(questions,1):
            count_limit = 1
            if judge_type(directory1,question) > count_limit:
                dict1['问题' + str(index)] = question
            else:
                dict1['问题' + str(index)] = ''

            if judge_type(directory2,question) > count_limit:
                dict2['问题' + str(index)] = question
            else:
                dict2['问题' + str(index)] = ''

            if judge_type(directory3,question) > count_limit:
                dict3['问题' + str(index)] = question
            else:
                dict3['问题' + str(index)] = ''

            if judge_type(directory4,question) > count_limit:
                dict4['问题' + str(index)] = question
            else:
                dict4['问题' + str(index)] = ''

            if judge_type(directory5,question) > count_limit:
                dict5['问题' + str(index)] = question
            else:
                dict5['问题' + str(index)] = ''

            if judge_type(directory6,question) > count_limit:
                dict6['问题' + str(index)] = question
            else:
                dict6['问题' + str(index)] = ' '

            if judge_type(directory1,question) < count_limit and judge_type(directory2,question) < count_limit and judge_type(directory3,question) < count_limit and judge_type(directory4,question) < count_limit and judge_type(directory5,question) < count_limit and judge_type(directory6,question) < count_limit:
                print(f'{filename}的问题{index}没有被正确分类')

        all_dict1.append(dict1)
        all_dict2.append(dict2)
        all_dict3.append(dict3)
        all_dict4.append(dict4)
        all_dict5.append(dict5)
        all_dict6.append(dict6)

    df1 = pd.DataFrame(all_dict1)
    df2 = pd.DataFrame(all_dict2)
    df3 = pd.DataFrame(all_dict3)
    df4 = pd.DataFrame(all_dict4)
    df5 = pd.DataFrame(all_dict5)
    df6 = pd.DataFrame(all_dict6)

    df1.to_excel('发行人股权结构.xlsx', index=False)
    df2.to_excel('公司治理与独立性.xlsx', index=False)
    df3.to_excel('发行人业务.xlsx', index=False)
    df4.to_excel('发行人核心技术.xlsx', index=False)
    df5.to_excel('财务会计信息与管理层分析.xlsx', index=False)
    df6.to_excel('风险、惩处、募投及环保事项.xlsx', index=False)


qa_folder = 'qa_txt'
Table_categorize(qa_folder)

