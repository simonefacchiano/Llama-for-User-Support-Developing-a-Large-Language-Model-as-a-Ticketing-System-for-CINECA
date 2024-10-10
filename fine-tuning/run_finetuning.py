# This script performs fine-tuning of a pre-trained LLM model (Llama3-8b-Instruct).
# It loads and formats a dataset of conversation templates, tokenizes the data,
# and prepares it for training.

import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, ProgressCallback
from datasets import Dataset, load_dataset, DatasetDict
from trl import DataCollatorForCompletionOnlyLM
import torch
import json
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
import wandb

print('Librerie importate')

model_id = "." ##Llama3-8b-Instruct

tokenizer = AutoTokenizer.from_pretrained(model_id) # TO UNDERSTAND WHETER TO SET: padding='right'
tokenizer.pad_token = tokenizer.eos_token # to set the pad token -->  recommends someone to use a new one in a multi-turn setup
#tokenizer.add_special_tokens({'pad_token':'[PAD]'})
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16, #torch.float16, torch.bfloat16
    device_map="auto",
)
print('The model and checkpoint have been successfully imported \n', '-'*50)

print(f"Model size without quantization: {model.get_memory_footprint():,} bytes")


## Print the names of the layers. We need ot because we will probably freeze the layers
# for name, param in model.named_parameters():
#     print(name)


for name, param in model.named_parameters():
    # Originally, the layers we finetuned were: 'layers.29', 'layers.30', 'layers.31', 'norm', 'lm_head'
    # In the *plus versions, we added 27 and 28
    # In the *minus version, it was only 31
    if not any(nd in name for nd in ['layers.29', 'layers.30', 'layers.31', 'norm', 'lm_head']):
        param.requires_grad = False


with open('/leonardo_work/try24_facchian/datasets_json/dataset_finetuning_2_settembre_clean.json', 'r') as f:
    dataset = json.load(f)

print(f"The length of the dataset used is: {len(dataset)}")  


### As seen in the tutorial, let's create a pandas dataframe:
def apply_template_to_chat(chat):
    # Here you need to integrate the apply_chat_template function you mentioned
    formatted_chat = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    return formatted_chat

# Apply the function to all conversations
formatted_chats = [apply_template_to_chat(chat) for chat in dataset]

# Create the DataFrame
df = pd.DataFrame(formatted_chats, columns=['template_formatted_conversation_turns']) # each row is a formatted conversation

# Now tokenize each chat. NOTE: padding and truncation are not yet applied!
dataset = Dataset.from_list(df['template_formatted_conversation_turns'].apply(lambda x: tokenizer(x, return_length=True, padding='max_length', truncation=True, max_length=1024)).to_list())

dataset_dict = DatasetDict({
    'train': dataset
})
split_datasets = dataset_dict['train'].train_test_split(test_size=0.2, seed=42)

train_dataset = split_datasets['train']
eval_dataset = split_datasets['test']

# Here we filter the two datasets. There are 2-3 entries without the instruction template. We filter the datasets to avoid having eval_loss as NaN:
eval_dataset = [e for e in eval_dataset if '<|start_header_id|>user<|end_header_id|>' in tokenizer.decode(e['input_ids']) and '<|start_header_id|>assistant<|end_header_id|>' in tokenizer.decode(e['input_ids'])]
train_dataset = [e for e in train_dataset if '<|start_header_id|>user<|end_header_id|>' in tokenizer.decode(e['input_ids']) and '<|start_header_id|>assistant<|end_header_id|>' in tokenizer.decode(e['input_ids'])]

# Save the train_dataset with pickle
with open('/leonardo_work/try24_facchian/datasets_json/train_dataset.pkl', 'wb') as f:
    pickle.dump(train_dataset, f)

# Save the eval_dataset with pickle
for i in range(len(eval_dataset)):
    eval_dataset[i]['decoded_text'] = tokenizer.decode(eval_dataset[i]['input_ids'], skip_special_tokens=True)

with open('/leonardo_work/try24_facchian/datasets_json/eval_dataset.pkl', 'wb') as f:
    pickle.dump(eval_dataset, f)

# Load the train_dataset with pickle
with open('/leonardo_work/try24_facchian/datasets_json/train_dataset.pkl', 'rb') as f:
    train_dataset = pickle.load(f)

with open('/leonardo_work/try24_facchian/datasets_json/eval_dataset.pkl', 'rb') as f:
    eval_dataset = pickle.load(f)
    eval_dataset_decoded = [{'decoded_text': item['decoded_text']} for item in eval_dataset]


# Define the settings to mask the responses from user support:
response_template = '<|start_header_id|>assistant<|end_header_id|>' #'assistant'
instruction_template = '<|start_header_id|>user<|end_header_id|>' # 'user'
collator = DataCollatorForCompletionOnlyLM(instruction_template=instruction_template, 
                                           response_template=response_template, tokenizer=tokenizer)




### Training settings
training_args = TrainingArguments(
    output_dir='/leonardo_work/try24_facchian/prove/third_finetuning_10k.json', # first_finetuning_4k --> quello dei 4mila dati, su questo funzionava, second_finetuning_10k è quello su cui ho fatto l'esperimento
    report_to='none',
    learning_rate=1e-5,
    num_train_epochs=1,
    weight_decay=0.1,
    logging_steps=5,
    evaluation_strategy="epoch",
    per_device_train_batch_size=1,  # Each "batch" is already pre-tokenized and padded
    per_device_eval_batch_size=1,
    save_strategy="epoch",
    group_by_length=True,  
    length_column_name='length' 
)

# Output_dir:
# - third_finetuning_10k_minus.json is the finetuning from layer 30 onwards.
# - third_finetuning_10k.json is the finetuning from layer 29 onwards, which is the original.
# - third_finetuning_10k_plus.json is the finetuning from layer 28 onwards, if it fits in memory.

# Trainer configuration
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=collator
)


# WARNING:
# https://github.com/huggingface/trl/issues/1053#issuecomment-1964981262
# if the labels of any eval batch contain only -100s then the entire eval_loss will be NaN.
# fixed with per_device_eval_batch_size>1

## Avviare il training
print('\n\n START THE TRAINING')
trainer.train()
print('\n\n TRAINING COMPLETED')

print('Congratulations!!! You have successfully performed finetuning!')