## Calcola le principali statistiche per il dataset utilizzato per fare fine-tuning.

import pandas as pd
import numpy as np
from datetime import timedelta
import json

# Funzione per convertire la durata in minuti totali
def convert_duration_to_minutes(duration):
    days, hours, minutes = 0, 0, 0
    if "days" in duration:
        days = int(duration.split(" days")[0])
        rest = duration.split(", ")[1:]
        for part in rest:
            if "hours" in part:
                hours = int(part.split(" ")[0])
            elif "minutes" in part:
                minutes = int(part.split(" ")[0])
    return days * 1440 + hours * 60 + minutes

def remove_outliers(data):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [x for x in data if lower_bound <= x <= upper_bound]

# Caricamento del dataset JSON
with open('/leonardo_work/try24_facchian/datasets_json/anonymized_dataset_2_settembre.json', 'r') as f:
    tickets = json.load(f)

# Creare liste per durata in minuti e lunghezza dei ticket
durations = [convert_duration_to_minutes(ticket["**Duration_ticket"]) for ticket in tickets]
length_tickets = [ticket["**Length_ticket"] for ticket in tickets]

# Lunghezza delle email e tempo tra le email
length_mails = []
time_between_mails = []

for ticket in tickets:
    for email in ticket["**Emails_ticket"]:
        length_mails.append(email["@@Length_mail"])
        if email["@@Time_from_previous"]:
            time_between_mails.append(convert_duration_to_minutes(email["@@Time_from_previous"]))

durations = remove_outliers(durations)
length_tickets = remove_outliers(length_tickets)
length_mails = remove_outliers(length_mails)
time_between_mails = remove_outliers(time_between_mails)            

# Calcolo delle statistiche
print(f"La lunghezza media del ticket è di {np.mean(length_tickets):.2f} scambi")
print(f"La durata media del ticket è di {(np.mean(durations)/60):.2f} ore")
print(f"La lunghezza media delle email è di {np.mean(length_mails):.2f} caratteri")
if time_between_mails:
    print(f"Il tempo medio tra due email è di {(np.mean(time_between_mails)/60):.2f} ore")
else:
    print("Non ci sono sufficienti dati per calcolare il tempo medio tra le email")

# 33232 file nella cartella /leonardo_work/try24_facchian/tts_tickets
# 105992 file nella cartella /leonardo_work/try24_facchian/tts_tickets_messages