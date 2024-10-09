import re
import pickle
import sacrebleu
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import pickle
import evaluate

# Percorso del file pickle
eval_path = '/leonardo_work/try24_facchian/datasets_json/eval_dataset.pkl'
which_model = 'quant' # Possible options: finetuned ; llama3 ; quant; llama3.1
rouge = evaluate.load('rouge')

print(f'Modello impostato su: {which_model}')


# Import the model of choice:
if which_model == 'finetuned':
    
    # Loading the model    
    model_id = "/leonardo_work/try24_facchian/prove/third_finetuning_10k_plus.json/checkpoint-6765" #third

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token


    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

elif which_model == 'llama3':
    model_id = '.'

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token


    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )   

elif which_model  == 'quant':
    base_model_id = '.'
    model_id = './Finetuned-plus-quant'
    model = AutoModelForCausalLM.from_pretrained(model_id, 
                                                  device_map='auto',
                                                  load_in_8bit=True)    
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_id)
    tokenizer.pad_token = tokenizer.eos_token

    

print('Modello caricato')


# Load the dataset, and create a set of:
# Questions
# Reference answers from the human assistant
with open(eval_path, 'rb') as f:
    eval_dataset = pickle.load(f)
    eval_dataset = [{'decoded_text': item['decoded_text']} for item in eval_dataset]


# Funzione per estrarre i primi segmenti di "user\n" e "assistant\n"
def extract_segments(text):
    # Trova tutti i segmenti che iniziano con "user\n" e "assistant\n"
    user_segments = re.findall(r'user\n(.*?)((system|user|assistant)\n|$)', text, re.DOTALL)
    assistant_segments = re.findall(r'assistant\n(.*?)((system|user|assistant)\n|$)', text, re.DOTALL)

    # Prendi solo il primo segmento trovato, se esiste
    user_question = user_segments[0][0].strip() if user_segments else None
    assistant_answer = assistant_segments[0][0].strip() if assistant_segments else None
    
    return user_question, assistant_answer

# Liste per memorizzare le references e predictions
questions = []
answer_reference = []
answer_predictions = []

# Estrai i primi segmenti per ogni testo
for i in range(len(eval_dataset)):
    user_q, assistant_a = extract_segments(eval_dataset[i]['decoded_text'])

    if 30 <= len(assistant_a) <= 300:
        # Aggiungi alle liste se sono stati trovati segmenti validi
        if user_q is not None:
            questions.append(user_q)
        if assistant_a is not None:
            answer_reference.append([assistant_a])
    

print('Liste riempite con successo')        

# Now, use the model to answer the different questions. The answers will be stored in a list, that will be used to compute ROUGE and BLEU scores
#questions = questions[:500]
#answer_reference = answer_reference[:500]

counter = 0
for question in questions:
    counter += 1
    print(f"Processing question number {counter}...")

    if which_model == 'finetuned':
        formatted_question = f"""
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Sei un assistente per il gruppo di User Assistance and Support presso il consorzio CINECA. Usa i seguenti pezzi di contesto, quando presenti, per rispondere alla domanda alla fine.<|eot_id|><|start_header_id|>user<|end_header_id|>
        {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """

        max_length = 50
    else:
        formatted_question = question 
        max_length = 50   

    inputs = tokenizer(formatted_question, return_tensors="pt", padding=True)

    # Genera la risposta dal modello
    output = model.generate(
        inputs.input_ids.to(model.device),
        attention_mask=inputs.attention_mask.to(model.device),
        max_new_tokens=max_length,  # Lunghezza massima della risposta generata
        do_sample=True,
        temperature=0.95  # Regola la diversità della risposta
    )

    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    
    start_idx = decoded_output.rfind("assistant\n")
    if start_idx != -1:
        # Estrarre la risposta vera e propria, rimuovendo spazi e newline aggiuntivi
        assistant_response = decoded_output[start_idx + len("assistant\n"):].strip()
    else:
        # Se non si trova il tag "assistant\n", consideriamo tutta la risposta
        assistant_response = decoded_output.strip()

    answer_predictions.append(assistant_response)



# print(answer_reference)
# print('\n-----------------------------\n')
# print(answer_predictions)
# print('\n-----------------------------\n')

print('\n\nFinal result:')
# Occhio. Il primo argomento deve essere le predictions, intese come una *lista di stringhe*.
# Il secondo argomento sono le reference, e sono una *lista di liste* di stringhe
bleu = sacrebleu.corpus_bleu(answer_predictions, answer_reference)
print(f"BLEU Score: {bleu.score}")

rouge = rouge.compute(predictions=answer_predictions, references=answer_reference)
print(f"ROUGE Score: {rouge}")

with open('/leonardo_work/try24_facchian/prove/answers_experiments_BLEU_finetuned_quantized.pkl', 'wb') as file:
    pickle.dump(answer_predictions, file)