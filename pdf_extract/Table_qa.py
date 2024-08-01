import re
import os
import pandas as pd

def extraction_qa(qa_folder):
    all_extracted_info_question = []
    all_extracted_info_answer = []
    for filename in os.listdir(qa_folder):
        file_path = os.path.join(qa_folder, filename)
        with open(file_path, mode='r', encoding='utf-8') as f:
            content = f.read()

        extracted_info_question = {}
        extracted_info_answer = {}

        question_pattern = re.compile(r'<Question/>:(.*?)</Question>', re.DOTALL)
        answer_pattern = re.compile(r'<Answer/>:(.*?)</Answer>', re.DOTALL)
        questions = question_pattern.findall(content)
        answers = answer_pattern.findall(content)

        for i,question in enumerate(questions,1):
            if question:
                extracted_info_question['问题'+str(i)] = question

        for i,answer in enumerate(answers,1):
            if answer:
                extracted_info_answer['回答'+str(i)] = answer

        extracted_info_question['文件名'] = filename
        extracted_info_answer['文件名'] = filename

        all_extracted_info_question.append(extracted_info_question)
        all_extracted_info_answer.append(extracted_info_answer)

    df_question = pd.DataFrame(all_extracted_info_question)
    df_answer = pd.DataFrame(all_extracted_info_answer)
    print(df_question,df_answer)

    df_question.to_excel('extracted_info_question.xlsx',index=False)
    df_answer.to_excel('extracted_info_answer.xlsx',index=False)

qa_folder = 'qa_txt'
extraction_qa(qa_folder)