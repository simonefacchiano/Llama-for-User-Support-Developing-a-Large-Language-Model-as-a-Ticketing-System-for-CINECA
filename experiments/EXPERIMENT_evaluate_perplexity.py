# In questo file facciamo la valutazione di un modello dal punto di vista della perplexity

import os
import torch
import pandas as pd
import random
from transformers import AutoTokenizer, AutoModelForCausalLM
from time import time


def evaluate_peplexity(model_id, test_set, output_folder, min_token = 100, max_token = 200, device = 'cuda'):
    """
    Prende in input:
    - model_id: il path per caricare il modello
    - test_set: un file .txt (italiano o inglese) con domande di vario genere
    - output_folder: percprsp dove salverà i risultati in formato CSV
    - min_token e max_token: numero minimo/massimo di token da generare
    - device

    Fa la seguente cosa:
    - definisce il modello
    - apre il dataset
    - crea il CSV

    - per ogni prompt nel test_set, campiona il numero di tokens da generare e genera una risposta. Poi:
        - calcola il tempo di generazione
        - calcola la perplexity sulla risposta generate
    """
    
    if model_id == './Finetuned-plus-quant':
    
        # Loading the model    
        base_model_id = '.'

        tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        tokenizer.pad_token = tokenizer.eos_token


        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
        ).to(device)

    elif model_id == '.':

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.pad_token = tokenizer.eos_token


        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
        ).to(device)

    if model_id == '.':
        model_name = 'llama3'
    elif model_id == './Finetuned-plus-quant':
        model_name = 'finetuned'    
    else:
        model_name = 'llama 3.1'    

    # Carica il test_set
    with open(test_set, 'r') as f:
        prompts = f.readlines()

    # Crea un DataFrame vuoto
    dataset = pd.DataFrame(columns=["Model", "Prompt", "Answer", "Perplexity", "N. Token", "Time"])    

    for prompt in prompts:
        print('Analizzo prompt...')
        model.eval()

        # Tokenizza il prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Campiona il numero di token da generare
        num_new_tokens = random.randint(min_token, max_token)

        # Generazione del testo
        start_time = time()
        print('Genero...')
        outputs = model.generate(inputs['input_ids'],
                                  max_new_tokens=num_new_tokens)
        end_time = time()

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_text = generated_text.replace("\n", " ")
        generated_text = f"""{generated_text}"""

        def calculate_perplexity(text):
            inputs = tokenizer(text, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                ppl = torch.exp(loss)
            return ppl.item()
        
        perplexity_value = calculate_perplexity(generated_text)

        # Creiamo una riga con i risultati
        new_row = pd.DataFrame({
            "Model": [model_name],
            "Prompt": [prompt.strip()],
            "Answer": [generated_text.strip()],
            "Perplexity": [perplexity_value],
            "N. Token": [num_new_tokens],
            "Time": [end_time - start_time]
        })

        # Aggiungi la nuova riga al DataFrame esistente
        dataset = pd.concat([dataset, new_row], ignore_index=True)
    
    # Salva i risultati in formato CSV
    dataset.to_csv(output_folder, index=False, sep = '|')

    return



#m = "." # BASE
m = './Finetuned-plus-quant' # FINETUNED

list_test_sets = ['/leonardo_work/try24_facchian/prove/dataset_perplexity_ita.txt',
                  '/leonardo_work/try24_facchian/prove/dataset_perplexity_en.txt']

for test_set in list_test_sets:
    if m == '.':
        if test_set == '/leonardo_work/try24_facchian/prove/dataset_perplexity_ita.txt':
            output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_base_ITA.csv'
        else:
            output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_base_EN.csv'    
    
    elif m == './Finetuned-plus-quant':
        if test_set == '/leonardo_work/try24_facchian/prove/dataset_perplexity_ita.txt':
            output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_finetuned_quantized_ITA.csv'   
        else:
            output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_finetuned_quantized_EN.csv'     
    
    evaluate_peplexity(model_id = m, test_set = test_set, output_folder = output_folder)

    print(f"Esperimento completato e salvato in {output_folder}")    
        


