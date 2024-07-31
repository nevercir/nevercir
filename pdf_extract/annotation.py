import json
import os
from transformers import LayoutXLMTokenizer,LayoutLMForQuestionAnswering,TrainingArguments,Trainer

input_paths = []
for filename in os.listdir('qa_txt'):
    input_paths.append(os.path.join('qa_txt',filename))
output_path = "processed_data.json"


# Define a function to process the input files and extract the labeled data
def process_labeled_data(input_paths, output_path):
    processed_data = []
    for path in input_paths:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            questions = content.split("<Question/>:")
            for question in questions[1:]:
                question_text = question.split("<Answer/>:")[0].strip()
                answer_text = question.split("<Answer/>:")[1].strip()

                # 删除 question_text 末尾的 </Question> 标签
                if question_text.endswith("\n</Question>"):
                    question_text = question_text[:-len("\n</Question>")].strip()

                # 删除 answer_text 末尾的 </Answer> 标签
                if answer_text.endswith("\n</Answer>"):
                    answer_text = answer_text[:-len("\n</Answer>")].strip()

                processed_data.append({
                    "question": question_text,
                    "answer": answer_text
                })

    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(processed_data, outfile, ensure_ascii=False, indent=4)


# Process the data and save it to the output file
process_labeled_data(input_paths, output_path)

from datasets import load_dataset

dataset = load_dataset('json', data_files='processed_data.json', split='train')

# 加载 LayoutLM tokenizer
tokenizer = LayoutXLMTokenizer.from_pretrained('microsoft/layoutlm-base-uncased')

def preprocess_function(examples):
    questions = [ex["question"] for ex in examples]
    contexts = [ex["answer"] for ex in examples]
    inputs = tokenizer(questions, contexts, max_length=512, truncation=True, padding="max_length", return_tensors="pt")
    return inputs

# 应用预处理函数到数据集
encoded_dataset = dataset.map(preprocess_function, batched=True)

# 加载 LayoutLM 模型
model = LayoutLMForQuestionAnswering.from_pretrained('microsoft/layoutlm-base-uncased')

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
)

# 初始化 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset,
)

print('开始训练')
# 开始训练
trainer.train()
print('训练结束')

# 评估模型性能
results = trainer.evaluate()
print(results)

# 保存微调后的模型
model.save_pretrained("fine-tuned-model")
tokenizer.save_pretrained("fine-tuned-tokenizer")












