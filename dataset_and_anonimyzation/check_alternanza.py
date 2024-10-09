import json

# Percorso del file JSON
file_path = '/leonardo_work/try24_facchian/datasets_json/anonymized_dataset_2_settembre.json'

# Caricare i dati JSON dal file
with open(file_path, 'r') as file:
    data = json.load(file)


#### Step 1: eliminare i ticket con 0 o 1 mail
print(f"Numero di conversazioni originali: {len(data)}")

# Filtrare le conversazioni che hanno più di un'email
filtered_data = [conversation for conversation in data if len(conversation.get("**Emails_ticket", [])) > 1]

# Visualizzare il risultato filtrato
print(f"Numero di conversazioni rimanenti: {len(filtered_data)}")


#### Step 2: fixare quelle che hanno le due mail finali inviate dallo stesso autore
for ticket in filtered_data:
    emails = ticket.get("**Emails_ticket", [])
    
    # Ottenere l'ultimo e il penultimo "Who"
    last_who = emails[-1].get("@@Who")
    second_last_who = emails[-2].get("@@Who")
    
    # Confrontare i due "Who"
    if last_who == second_last_who:
        # Se sono uguali, rimuovere l'ultima email
        emails.pop()

#### Step 3: controllare se ora ce ne sono alcune con 0 o 1 messaggio, ed eliminare
filtered_data2 = [conversation for conversation in filtered_data if len(conversation.get("**Emails_ticket", [])) > 1]

# Visualizzare il risultato filtrato
print(f"Numero di conversazioni rimanenti: {len(filtered_data2)}")        


#### Step 4: contare la perfetta alternanza
def check_alternation(emails):
    """Controlla se c'è una alternanza perfetta tra 'user' e 'support'."""
    last_who = None
    for email in emails:
        current_who = email.get("@@Who")
        if last_who == current_who:  # Controlla se il current e il last sono uguali
            return False
        last_who = current_who
    return True

# Contatore per i ticket con alternanza perfetta
perfect_alternation_count = 0

# Iterare attraverso ogni ticket
for ticket in filtered_data2:
    emails = ticket.get("**Emails_ticket", [])
    if len(emails) > 1 and check_alternation(emails):
        perfect_alternation_count += 1

print(f"Numero di ticket con alternanza perfetta: {perfect_alternation_count} \n\n") # circa il 35-40% sono buoni

print(json.dumps(filtered_data2[127], indent=4, ensure_ascii=False))

with open(file_path, 'w') as file:
    json.dump(filtered_data2, file, indent=4, ensure_ascii=False)

print(f"I dati sono stati sovrascritti con successo nel file: {file_path}")

