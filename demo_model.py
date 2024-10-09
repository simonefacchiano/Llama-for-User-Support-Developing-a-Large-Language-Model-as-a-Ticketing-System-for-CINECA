# In questo file, puoi eseguire una demo del tuo modello.

print('Eseguo il codice...')

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

which_model = 'finetuned_plus'

if which_model == 'finetuned':
    model_id = '/leonardo_work/try24_facchian/prove/third_finetuning_10k.json/checkpoint-6773'
elif which_model == 'finetuned_minus':
    model_id = "/leonardo_work/try24_facchian/prove/third_finetuning_10k_minus.json/checkpoint-6765"
elif which_model == 'finetuned_plus':
    model_id = "/leonardo_work/try24_facchian/prove/third_finetuning_10k_plus.json/checkpoint-6765"


tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token


model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

print('Modello importato! Processo la tua domanda...')

question = 'Buongiorno, sono un utente Cineca. Come mi connetto a Leonardo?'
question = f"""
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Sei un assistente per il gruppo di User Assistance and Support presso il consorzio CINECA. Usa i seguenti pezzi di contesto, quando presenti, per rispondere alla domanda alla fine.<|eot_id|><|start_header_id|>user<|end_header_id|>
        {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """
inputs = tokenizer(question, return_tensors="pt", padding=True)

output = model.generate(
        inputs.input_ids.to(model.device),
        attention_mask=inputs.attention_mask.to(model.device),
        max_new_tokens=100,  # Lunghezza massima della risposta generata
        do_sample=True,
        temperature=0.98  # Regola la diversità della risposta
    )

decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)

start_idx = decoded_output.rfind("assistant\n")
if start_idx != -1:
    # Estrarre la risposta vera e propria, rimuovendo spazi e newline aggiuntivi
    assistant_response = decoded_output[start_idx + len("assistant\n"):].strip()
else:
    # Se non si trova il tag "assistant\n", consideriamo tutta la risposta
    assistant_response = decoded_output.strip()

print(assistant_response)