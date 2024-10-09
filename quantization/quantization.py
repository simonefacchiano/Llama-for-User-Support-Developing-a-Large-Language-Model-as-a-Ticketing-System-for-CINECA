from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
import re
import random
from time import time
torch.manual_seed(0)

def generate_text(model, input_text, max_length=50, temperature=0.95):
    input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)
    output = model.generate(inputs=input_ids,
                            max_new_tokens=max_length,
                            do_sample=True,
                            top_k=30,
                            temperature=temperature,  # sugli esperimenti del finetuing l'abbiamo messa a 0.95
                            pad_token_id=tokenizer.eos_token_id,
                            attention_mask=input_ids.new_ones(input_ids.shape))
    return tokenizer.decode(output[0], skip_special_tokens=True)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



model_id = "." ##Llama3-8b-Instruct

# Standard version:
start_time = time()
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16, #torch.float16, torch.bfloat16
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
end_time = time()
print(f"Model size: {model.get_memory_footprint():,} bytes")
print(f"Time to load: {round(end_time - start_time, 2)} seconds")


# Quantized version:
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
start_time = time()
model_int8 = AutoModelForCausalLM.from_pretrained(model_id,
                                             device_map='auto',
                                             load_in_8bit=True,
                                             )
end_time = time()
print(f"Model size after quantization: {model_int8.get_memory_footprint():,} bytes")
print(f"Time to load: {round(end_time - start_time, 2)} seconds")


output_dir = './Llama-3-quant'
model_int8.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)



############ Compute perplexity ############

def evaluate_peplexity(test_set, output_folder, min_token = 100, max_token = 200, device = 'cuda', save = True):
    """
    Prende in input:
    - model_name: il modello
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

    # Carica il test_set
    with open(test_set, 'r') as f:
        prompts = f.readlines()

    # Crea un DataFrame vuoto
    dataset = pd.DataFrame(columns=["Model", "Prompt", "Answer", "Perplexity", "N. Token", "Time"])    

    for prompt in prompts:
        print('Analizzo prompt...')
        model_int8.eval()

        # Tokenizza il prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Campiona il numero di token da generare
        num_new_tokens = random.randint(min_token, max_token)

        # Generazione del testo
        print('Genero...')
        start_time = time()
        outputs = model_int8.generate(inputs['input_ids'],
                                  max_new_tokens=num_new_tokens)
        end_time = time()

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_text = generated_text.replace("\n", " ")
        generated_text = f"""{generated_text}"""

        def calculate_perplexity(text):
            inputs = tokenizer(text, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model_int8(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
                ppl = torch.exp(loss)
            return ppl.item()
        
        perplexity_value = calculate_perplexity(generated_text)

        # Creiamo una riga con i risultati
        new_row = pd.DataFrame({
            "Model": ['quantized'],
            "Prompt": [prompt.strip()],
            "Answer": [generated_text.strip()],
            "Perplexity": [perplexity_value],
            "N. Token": [num_new_tokens],
            "Time": [end_time - start_time]
        })

        # Aggiungi la nuova riga al DataFrame esistente
        dataset = pd.concat([dataset, new_row], ignore_index=True)
    
    # Salva i risultati in formato CSV
    if save:
        dataset.to_csv(output_folder, index=False, sep = '|')

    return


list_test_sets = ['/leonardo_work/try24_facchian/prove/dataset_perplexity_ita.txt',
                  '/leonardo_work/try24_facchian/prove/dataset_perplexity_en.txt']

for test_set in list_test_sets:
    if test_set == '/leonardo_work/try24_facchian/prove/dataset_perplexity_ita.txt':
        output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_quantized_ITA.csv'
    else:
        output_folder = '/leonardo_work/try24_facchian/prove/results_perplexity_quantized_EN.csv'    
       
    evaluate_peplexity(test_set = test_set, output_folder = output_folder)

    print(f"Esperimento completato e salvato in {output_folder}")    