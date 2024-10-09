### In questo file creeremo il dataset da usere per il fine-tuning di Llama3.

# - Prenderemo i dati anonimizzati in json, salvati precedentemente.
# - Ogni ticket verrà convertito nel formato {"role": who; "content": body}
# - A ogni ticket verrà applicato il chat_template e la tokenizzazione
# - Il dataset sarà pronto per essere utilizzato nel processo di finetuning

import json

# ---> 1 <---
file_path = "/leonardo_work/try24_facchian/datasets_json/anonymized_dataset_2_settembre.json" #anonymized_dataset_v3_alternate.json <-- sui 4mila dati
with open(file_path, 'r') as file:
    data = json.load(file)

#data = [item for item in data if item.get("**Length_ticket", 0) == 2]
#data = [item for item in data if item.get("**Length_ticket", 0) < 5]
data = [item for item in data if item.get("**Length_ticket", 0) % 2 == 0]
print('Length of the datset:', len(data))
#data = data[100:1100] # qui prima facevo fino a 1100, per avere solo 1000 dati. Ora sono pronto a fare di più.

dataset = []
for ticket in data:
  single_chat = []

  mails = ticket['**Emails_ticket'] # lista di dizionari
  prompt_dict = {"role": "system", "content": "Sei un assistente per il gruppo di User Assistance and Support presso il consorzio CINECA. Usa i seguenti pezzi di contesto, quando presenti, per rispondere alla domanda alla fine."}
  single_chat.append(prompt_dict)

  for m in mails:
    if m['@@Who'] == 'system':
       role = 'system'
    elif m['@@Who'] == 'user':   
       role = 'user'
    else:
       role = 'assistant'
    aux_dict = {"role": role,
                 "content": m['@@Body']}
    single_chat.append(aux_dict)

  dataset.append(single_chat)

# counter = 0 
# for index, ticket in enumerate(dataset):
#    if ticket[1]['role'] != 'user':
#       print(f"{index + 100} non ha user")
#       counter += 1
#    if ticket[2]['role'] != 'assistant':
#       print(f"{index + 100} non ha assistant")
#       counter += 1
   
# print(counter)

# --

# Lo salvo
percorso_dataset_finetuning = '/leonardo_work/try24_facchian/datasets_json/dataset_finetuning_2_settembre.json' #dataset_finetuning3.json <-- quello dei 4mila dati
with open(percorso_dataset_finetuning, 'w') as f:
    json.dump(dataset, f)

print('Dataset salvato')    