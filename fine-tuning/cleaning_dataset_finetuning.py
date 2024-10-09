# Questo file serve a pulire il dataset creato per il finetuning

import re
import json

# Funzione per pulire il contenuto di una singola stringa
def remove_ending_date(text):

    #Mandiamo a capo la stringa di "Il ... ha scritto:"
    pattern = r"^(Il .*?20\d{2}.*? ha scritto:)$"
    text = re.sub(pattern, r"\n\1", text)

    # Mandiamo a capo la stringa di "On ... wrote:"
    pattern = r"(On .*?(?:\d{2}/\d{2}/\d{2}|\d{2}.\d{2}.\d{2}|20\d{2}).*? wrote:)"
    text = re.sub(pattern, r"\n\1", text)
  
    # Rimuovi "Il ... ha scritto:"
    pattern = r"^(Il .*?20\d{2}.*? ha scritto:)$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
          
    # Rimuovi "On ... wrote:"
    pattern = r"^(On\s+.*?(?:\d{2}/\d{2}/\d{2}|\d{2}\.\d{2}\.\d{2}|20\d{2}).*?\s+wrote:)"
    text = re.sub(pattern, "", text, flags=re.MULTILINE|re.DOTALL)
    
    # Rimuovi le firme come "-- Nome Cognome"
    pattern = r"\n--\s*([\w\s]+\n){3,}"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Rimuovi "From:", "To:", "Subject:", "Sent:" e simili
    email_metadata_pattern = r"^(From:[^\n]*\n(?:Sent:[^\n]*\n)?(?:To:[^\n]*\n)?(?:Subject:[^\n]*\n)?)"
    text = re.sub(email_metadata_pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Rimuovi eventuali "Show quoted text"
    quoted_text_pattern = r"Show quoted text"
    text = re.sub(quoted_text_pattern, "", text, flags=re.IGNORECASE)
    
    # Rimuovi dettagli come "CINECA", "Phone", "E-mail"
    details_pattern = r"CINECA - .*|Phone:.*|E-mail:.*|Fax:.*|ItalyTel:.*"
    text = re.sub(details_pattern, "", text, re.MULTILINE)
    
    # Rimouovere i tanti \n consecutivi
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Rimuovi firme di tipo "--", "---", ecc.
    pattern = r"^--+\s*$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Cancella blocchi di "----" se ci sono più di 15 trattini consecutivi
    pattern = r"-{15,}"
    text = re.sub(pattern, "", text)

    pattern = r"Il\s+[A-Z][a-z]{2}\s+\d{1,2}\s+[A-Za-z]+\s+30\d{2}.*?\s+scritto:$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+[A-Z][a-z]{2}\s+\d{1,2}\s+[A-Za-z]+\s+20\d{2}.*?\s+scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno \d{1,2} [a-z]{3} 20\d{2}, alle ore \d{2}:\d{2}, [\w\s]+ via RT <[^>]+> ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno \w{3} \d{1,2} \w{3} 20\d{2} alle ore \d{2}:\d{2} [\w\s]+(?: via RT)? <[^>]+> ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il \d{1,2}/\d{1,2}/20\d{2} \d{2}:\d{2}, [^,]+(?: via RT)? ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno \w{3} \d{1,2} \w{3} 20\d{2} alle ore \d{2}:\d{2} [\w\s]+(?: <[^>]+>)? via RT <[^>]+> ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}, [^,]+ ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il \w{3} \d{1,2} \w{3} 20\d{2}, \d{2}:\d{2} [\w\s]+ via RT <[^>]+> ha scritto"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il \d{4}-\d{2}-\d{2} \d{2}:\d{2} [\w\s]+ via RT ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"From:[^\n]+(?:\n(?:Sent:|To:)[^\n]*)+.*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"-{4,} Forwarded message --[\s\S]*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"[A-Z][a-z]+ [A-Z][a-z]+ via RT ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno \w{3} \d{1,2} \w{3} 20\d{2} alle ore \d{2}:\d{2} [\w\.\@]+(?: via RT)?(?: <[^>]+>)? ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno (?:\w{3} \d{1,2} \w{3} 20\d{2}|\d{2}/\d{2}/\d{2}),? alle ore \d{2}:\d{2} [\"']?[\w\.\@ ]+[\"']?(?: via RT)?(?: <[^>]+>)? ha scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il giorno \d{1,2}/\d{1,2}/\d{2,4},? \d{2}:\d{2}.*(?:\n.*)*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(Il giorno \w{3,9} \d{1,2} \w{3,9} \d{2,4},? alle \d{2}:\d{2}|Il \d{1,2}/\d{1,2}/\d{2,4} \d{2}:\d{2},.*? via RT|HPC User Support .*? via RT).*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"inviato da iphone.*"
    text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'(Sent from my iPhone|Envoyé de mon iPhone|Enviado do meu iPhone).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r"Il\s+\d{1,2}/\d{1,2}/\d{2,4}\s+\d{2}:\d{2},\s+.*?(via\s+RT\s+)?ha\s+scritto:(\s*\n\s*)*"
    text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r"Il\s+\d{1,2}[/\.]\d{1,2}[/\.]\d{2,4}\s+\d{2}:\d{2},\s+.*?(via\s+RT\s+)?ha\s+scritto:(\s*\n\s*)*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+\d{1,2}\s+\w{3,}\s+\d{4}\s+\d{1,2}:\d{2}\s+(AM|PM),?\s+.*?ha\s+scritto:(\s*\n\s*)*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+(giorno\s+)?(?:\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4}|20\d{2}-\d{2}-\d{2})\s+\d{1,2}:\d{2}.*?ha\s+scritto:(\s*\n\s*)*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+giorno\s+\w{1,9}\s+\d{1,2}\s+\w{3,9}\s+\d{4},?\s+.*?ha\s+scritto:.*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(?:\w+\s+){1,4}(?:via RT\s*)?ha\s+scritto:\s*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(?:\w+\s+){1,4}via RT\s*<[^>]+>\s*ha\s+scritto:\s*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(?:\w+\s+){1,4}via RT\"?\s*<[^>]+>\s*ha\s+scritto:\s*-{2,}.*?$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+\w{3}\s+\d{1,2}\s+\w{3}\s+20\d{2},\s+\d{2}:\d{2}\s+[^\n]+>\s+ha\s+scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"\"[^\"]+via RT\"\s+ha\s+scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+\d{1,2}\s+\w{3}\s+20\d{2},\s+\d{2}:\d{2}\s+\+\d{4},\s+[^\n]+via RT\s*,\s+ha\s+scritto:"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il\s+\w{3}\s+\d{1,2}\s+\w{3}\s+\d{4}.*scritto:.*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"Il \d{1,2} \w+ 20\d{2}, \d{1,2}:\d{2} [+-]\d{4}, .*?, ha scritto:.*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(--+|\bBest regards\b|\bbest regards\b|\bRegards\b)[\s\S]*?(\n\s*\n|$)"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(--+)[\s\S]*?(\n\s*\n|$)"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"--\s*Marani Alessandro\s+-\s+HPC User Support[\s\S]*?(\n\s*\n|$)"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"From:.*?To:.*?Subject:.*?(\n\n|$)"
    text = re.sub(pattern, "", text, flags=re.DOTALL)

    pattern = r"--\s*[A-Z][a-z]+ [A-Z][a-z]+,\s*PhD.*"
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r', PhD.*'
    text = re.sub(pattern, '', text)

    pattern = r"_____+\s*.*"
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r"Le\s+\w{3}\.\s+\d{2}.*?a écrit\s*:|Le\s+\d{2}/\d{2}/\d{4}.*?a écrit\s*:"
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    pattern = r".*?\s?via RT a écrit\s*:|.*?RT a écrit\s*:"
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    pattern = r"On \d{2}\.\d{2}\.\d{2} \d{2}:\d{2}, [\w\s]+wrote\s*:|[\w\s]+via RT wrote\s*:"
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    pattern = r"On \d{2}/\d{2}/\d{2} \d{2}:\d{2}, [\w\s]+(?:via\s+RT)?\s*wrote\s*:"
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    pattern = r"Giustino CAE Engineer.*"
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r"[Tt]el:.*"
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r"(Cordiali saluti,? [A-Z][a-z]+(?: [A-Z][a-z]+)?)\s*.*"
    text = re.sub(pattern, r"\1", text, flags=re.DOTALL)

    pattern = r"(cordiali saluti,? [A-Z][a-z]+(?: [A-Z][a-z]+)?)\s*.*"
    text = re.sub(pattern, r"\1", text, flags=re.DOTALL)

    pattern = r"(cordiali saluti[, -]*)[A-Z][a-z]+(?: [A-Z][a-z]+)?\s*.*"
    text = re.sub(pattern, r"\1", text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r"\b(?:Il|On)\s*$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    pattern = r"(ciao)(?:\s*Dr\..*)"
    text = re.sub(pattern, r"\1", text)

    pattern = r'--\s+" Considerate la vostra semenza.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On \d{1,2}/\d{1,2}/\d{2,4}.*?via\s+RT wrote:.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Ing\. Lubomír.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On\s+\d{1,2}/\d{1,2}/\d{2,4}.*?wrote:.*'
    pattern = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On\s+\d{1,2}/\d{1,2}/\d{2,4}.*?wrote:.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'\bwrote:$'
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    pattern = r'ENEA Italian National Agency.*'
    text = re.sub(pattern, '', text)

    pattern = r'\*{3,}.*'
    text = re.sub(pattern, '', text)

    pattern = r'\+{3,}.*'
    text = re.sub(pattern, '', text)

    pattern = r'(?:\w{3,9} \d{1,2}, \d{4} \d{1,2}:\d{2} (?:AM|PM),.*? wrote:)|(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},.*? wrote:)'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On \d{1,2}-\w{3}-\d{2} \d{2}:\d{2}, [A-Za-z\s]+via RT.*'
    text = re.sub(pattern, '', text)

    pattern = r'On\s+\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2},?\s+[A-Za-z]+\s+[A-Za-z]+.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On \d{2}/\d{2}/\d{2} \d{2}:\d{2} (AM|PM).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On \d{1,2}/\d{1,2}/\d{2} \d{1,2}:\d{2} [APM]{2}.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Da:.*?via RT.*Inviato:.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'[Tt][Ee][Ll]\.?:.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'\* \* \*.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    pattern = r'\_ \_ \_.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'\*\+\*.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'\- \- \-.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'PMP®.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'(- PhD|\(PhD\)).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Ph\.D\.\s+(-|HPC|postdoctoral|Post-doctoral|Quantum|, Space|CINECA|istituto|research|candidate|doctoral|ass(?:istant)?|Student\s*-).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'- HPC Department.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'HPC Specialist.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'[Vv]ia\s+(?!RT|rt)[A-Za-z.]+\s*[A-Za-z]*\s*,?\s*\d+.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Hull Designer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    pattern = r' wo \d+.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'AC Ing\..*'
    text = re.sub(pattern, '', text)

    pattern = r'(?<!To whom it may concern,\sOur group at the University of Trento,\s)Department of.*'
    text = re.sub(pattern, '', text)

    pattern = r'\| Department.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Tel\. \+39.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    pattern = r'[Mm]ob[:\.\s]+[+]39.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'[Mm]obile[:\.\s]+[+]39.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Ph\.D\. CFD.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Graduate Engineer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'PhD Student KU.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Missatge de.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'via RT.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'WIDMER PIIM.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Ph\.D\. student, Physics.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'απόρρητες.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Doctoral School in.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'm ob:.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'\+\d{1,3}\s*\d{2,5}\s*\d{2,5}\s*\d{2,5}.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'PhD student in Nanosciences.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'CAE Engineer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Chief Technical Officer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Senior CFD.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Senior Research.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Senior Lecturer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Senior Specialisr.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'\b(phone|Phone|M|T)\s*[:]?[\s\+\-\.\d]+'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'CMC .*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'CAE Engineer.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Strategic Planning.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Business Unit.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Business Development.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'DIT KACEM.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Research Scientist.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'United Kingdom.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'professore ordinario.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Full Professor.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Associate Professor.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Professore Associato.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Assistant Professor.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'PhD Student Dept. of.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'R&D Engineer.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'R&D Dept.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Tel +39.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Aversa CE.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Ph.D. Researcher at.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'PhD Student Laboratory.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Ph.D. Assegnista.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Ph.D. CETEMPS.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Garobbio Miguelañez PhD.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Στις.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'OGS -.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Ricercatore Dipartimento.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'PhD Ricercatore.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Ricercatore - Researcher.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'PhD Student in Energetics Politecnico di Torino.*'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

    pattern = r'Parma (Italy).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'Torino - Italy.*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'(Parma|Roma|Torino|Milano|Bologna) \(Italy\).*'
    text = re.sub(pattern, '', text, flags=re.DOTALL)

    pattern = r'On \d{2}/\d{2}/\d{4} \d{2}:\d{2}.*?$'
    text = re.sub(pattern, '', text, flags=re.DOTALL | re.MULTILINE)

    pattern = r'On \d{2}/\d{2}/\d{2} \d{2}:\d{2}'
    text = re.sub(pattern, '', text)

    pattern = r', Sofia N\..*'
    text = re.sub(pattern, '', text)

    #### Da qui, mai eseguito

    pattern = r'(?<=Saluti, ).*'
    text = re.sub(pattern, '', text)


    ############################################################################
    text = re.sub(r'\bAlessandro\b', 'Alessio', text)  # Alessandro -> Alessio
    text = re.sub(r'\bMarani\b', 'De Carli', text)  # Marani -> De Carli
    text = re.sub(r'\bNeva\b', 'Asia', text)  # Neva -> Asia
    text = re.sub(r'\bSusana\b', 'Sofia', text)  # Susana -> Sofia
    text = re.sub(r'\bMinguez\b', 'De Santis', text)  # Minguez -> De Santis
    text = re.sub(r'\bBueno\b', 'Boni', text)  # Bueno -> Boni
    text = re.sub(r'\bMarabotti\b', 'Del Bianco', text)
    pattern_isa = r' isa(?=\s*$)'
    text = re.sub(pattern_isa, ' Gianna', text)
    pattern_silviag = r'SilviaG'
    text = re.sub(pattern_silviag, 'Simona Galliani', text)

    text = re.sub(r'\s+', ' ', text)

    pattern = r',$'
    text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    return text.strip()

# Funzione per attraversare il JSON e pulire il contenuto dei campi "content"
def clean_json_content(data):
    if isinstance(data, list):
        for item in data:
            clean_json_content(item)  # Chiamata ricorsiva
    elif isinstance(data, dict):
        if "content" in data:
            data["content"] = remove_ending_date(data["content"])  # Pulisci il contenuto
        for key in data:
            clean_json_content(data[key])  # Chiamata ricorsiva per eventuali sotto-dizionari o liste

# Percorsi per i file di input e output
input_path = "/leonardo_work/try24_facchian/datasets_json/dataset_finetuning_2_settembre.json"
output_path = "/leonardo_work/try24_facchian/datasets_json/dataset_finetuning_2_settembre_clean.json"

# Esempio di utilizzo
if __name__ == "__main__":
    # Carica il JSON dal file
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_json = json.load(f)

    # Pulisci il contenuto del JSON
    clean_json_content(raw_json)
    
    # Salva il risultato in un nuovo file JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(raw_json, f, ensure_ascii=False, indent=4)

    print(f"Pulizia completata e salvata in '{output_path}'")
