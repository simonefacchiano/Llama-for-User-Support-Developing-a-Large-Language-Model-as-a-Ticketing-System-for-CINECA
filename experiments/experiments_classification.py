# Questo script è dedicato ai soli esperimenti per il finetuning

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import pandas as pd


list_of_models = ['finetuned'] #aggiungerci llama3.1 #'finetuned', 

for which_model in list_of_models:
    test_set = pd.read_csv('/leonardo_work/try24_facchian/prove/test_set_classification.csv')

    if 'Model_Answer' in test_set.columns:
        test_set = test_set.drop(columns=['Model_Answer'])
        test_set['Model_Answer'] = None
    else:
        test_set['Model_Answer'] = None

    if which_model == 'finetuned':
        
        # Loading the model    
        base_model_id = '.'
        model_id = "/leonardo_work/try24_facchian/prove/third_finetuning_10k.json/checkpoint-6765" #third

        tokenizer = AutoTokenizer.from_pretrained(base_model_id)
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

    print('Modello caricato')


    for index, row in test_set.iterrows():
        question = row['Question']

        if which_model == 'finetuned':
            formatted_question = f"""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            Sei un membro del gruppo di User Assistance and Support presso il consorzio CINECA. Sei frutto del lavoro per una tesi di laurea sugli LLMs, in particolare quelli della famiglia Llama di Meta. Ricevi domande dagli utenti a cui devi rispondere cordialmente, fornendo informazioni precise e senza inventare nulla. Sii cordiale. Non mandare simboli, link o percorsi a meno che non ti sia richiesto dall'utente. Per favore, non firmarti mai col nome di persone, e non chiamare l'utente con un nome a meno che non te lo dica lui.<|eot_id|><|start_header_id|>user<|end_header_id|>
            {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """

            max_length = 400
        else:
            formatted_question = question 
            max_length = 300   

        inputs = tokenizer(formatted_question, return_tensors="pt", padding=True)

        # Genera la risposta dal modello
        output = model.generate(
            inputs.input_ids.to(model.device),
            attention_mask = inputs.attention_mask.to(model.device),
            max_length = max_length,  # Lunghezza massima della risposta generata
            do_sample = True,
            temperature = 0.95  # Regola la diversità della risposta
        )

        # Decodifica la risposta generata
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        generated_text = generated_text.replace('\n', ' ').strip()
        test_set.at[index, 'Model_Answer'] = generated_text


    print('Esperimento eseguito con successo.\n', test_set.head())    

    # Salvataggio di nuovo:
    if which_model == 'finetuned':
        test_set.to_csv('/leonardo_work/try24_facchian/prove/results_finetuned_classification_v2.csv', index=False, sep = '|')
        print('Salvati i risultati per il modello finetunato')
    elif which_model == 'llama3':
        test_set.to_csv('/leonardo_work/try24_facchian/prove/results_base_classification.csv', index=False, sep = '|')
        print('Salvati i risultati per il modello llama3')