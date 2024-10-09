print('Running the script')

# Librerie

import os
import re
import json

# pip install presidio_analyzer
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

#!pip install presidio-anonymizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import OperatorConfig

# !pip install Faker
from faker import Faker
# print(dir(Faker())) #per avere una lista dei metodi

# pip install langdetect
from langdetect import detect

print('Libraries succesfully installed')

# Configurazione motore NLP
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"},
               {"lang_code": "it", "model_name": "it_core_news_lg"}],
}

# Creazione motore NLP
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

# Creazione AnalyzerEngine
analyzer = AnalyzerEngine(nlp_engine=nlp_engine,
                          supported_languages=["en", "it"])

# Creazione AnonymizerEngine
anonymizer = AnonymizerEngine()

# Istanza di Faker per inglese e italiano
fake_en = Faker('en_US')
fake_it = Faker('it_IT')

# Funzione per rilevare la lingua e restituire l'operatore corretto
def get_operators_for_language(text):
    if not text.strip():  # Verifica se il testo è vuoto o contiene solo spazi vuoti. Altrimenti dà errore più avanti
        return None, None
    
    lang = detect(text)
    if lang == 'it':
        return fake_operators_it, 'it'
    else:
        return fake_operators_en, 'en'
    
    
# def is_full_name(name):
#     words_to_remove = ['Ciao', 'Caro', 'Gentile', 'Buongiorno', 'Buonasera', 'Salvo']
#     for word in words_to_remove:
#         name = name.replace(word, "")
#     return len(name.split()) > 1
        
        
words_to_remove = ['Ciao', 'Caro', 'Gentile', 'Buongiorno',  'Buonasera', 'Salve', "Buona giornata",
                   'From', "Grazie mille", "Hello", "Dear", "Regards", "Best regards",
                   "Avrei", "Cordiali", "Saluti", "Grazie"]
words_to_remove_lower = [word.lower() for word in words_to_remove]
words_to_remove = words_to_remove + words_to_remove_lower

def contains_special_or_numeric(name):
    return bool(re.search(r'[^A-Za-z\s\-+=]', name))
        
def custom_fake_name(name):
    
    if ("Marconi" in name) or ("Leonardo" in name) or ("Galileo" in name):
        return name
    
    if contains_special_or_numeric(name):
        return name
    
    if name.islower(): # greedy ma necessario in molti casi
        return name
    
    edit_name = name
    for word in words_to_remove:
        if word in edit_name:
            edit_name = edit_name.replace(word, "")
    
    
    if len(edit_name.split()) > 1:
        if edit_name.split()[0][-1] == 'a':
            first_name = fake_it.first_name_female()
            last_name = fake_it.last_name()
        else:
            first_name = fake_it.first_name_male()
            last_name = fake_it.last_name()    
        return f"{first_name} {last_name}" #{greeting} 
    elif len(edit_name.split()) == 1:
        if name[-1] == 'a':
            first_name = fake_it.first_name_female()
        else:
            first_name = fake_it.first_name_male()
        return f"{first_name}" #{greeting} 
    else:
        return name   
        

def remove_ending_date(text):

    # Mandiamo a capo la stringa di "Il ... ha scritto:"
    pattern = r"^(Il .*?20\d{2}.*? ha scritto:)$"
    text = re.sub(pattern, r"\n\1", text) #

    # Mandiamo a capo la stringa di "On ... wrote:"
    pattern = r"(On .*?(?:\d{2}/\d{2}/\d{2}|\d{2}.\d{2}.\d{2}|20\d{2}).*? wrote:)" # r"(On .*?(?:\d{2}/\d{2}/\d{2}|20\d{2}).*? wrote:)
    text = re.sub(pattern, r"\n\1", text)
  
    # Rimuovi il "Il giorno tot X ha scritto:"
    pattern =  r"^(Il .*?20\d{2}.*? ha scritto:)$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
          
    # Rimuovi il "On ... wrote:"
    pattern = r"^(On\s+.*?(?:\d{2}/\d{2}/\d{2}|\d{2}\.\d{2}\.\d{2}|20\d{2}).*?\s+wrote:)"  #r"^(On .*?20\d{2}.*? wrote:)$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE|re.DOTALL)
    
    # Rimuovi firma dell'università: |----- ; oppure ------  # --> l'ho commentata perché si triggerava quando non doveva
    pattern = r"\n--\s*([\w\s]+\n){3,}" # r"\s*\|*-*\|*\s*(.*\n)*?\s-*\|*\s*\|*"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Rimuovi firma sulla stessa riga:
    r"--\s(?:[A-Z][a-zA-Z]*\.?\s)?([A-Z][a-zA-Z]*\s[A-Z][a-zA-Z]*).*" # occhio a non cancellare roba importante
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Rimuovi From: ..., To: ..., Subject: ... Sent: ...
    email_metadata_pattern = r"^(From:[^\n]*\n(?:Sent:[^\n]*\n)?(?:To:[^\n]*\n)?(?:Subject:[^\n]*\n)?)"
    text = re.sub(email_metadata_pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove "show quoted text"
    quoted_text_pattern = r"Show quoted text"
    text = re.sub(quoted_text_pattern, "", text, flags=re.IGNORECASE)
    
    # Rimuovi i dettagli finali come "CINECA", "Phone", "E-mail"
    details_pattern = r"CINECA - .*|Phone:.*|E-mail:.*|Fax:.*|ItalyTel:.*"
    text = re.sub(details_pattern, "", text, re.MULTILINE)
    
    # Rimouovere i tanti \n
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Fixare la firma compromessa (nomi duplicati)
    pattern = r".*- HPC User Support$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    pattern = r"^Via.*Italy$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Regex per identificare le parole maiuscole consecutive
    pattern = r'([A-Z][a-z]+)([A-Z][a-z]+)\s([A-Z][a-z]+)'
    text = re.sub(pattern, r'\1 \2 \3', text)

    # Cancella gli "--" (spesso nelle firme)
    pattern = r"^--+\s*$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # Cancella tutti i blocchi di "----" quando ci sono più di 15 --- consecutivi
    pattern = r"-{15,}"
    text = re.sub(pattern, "", text)
    
    # Pattern per rilevare il footer con il link variabile
    pattern = r"This email has been checked for viruses by Avast antivirus [\s\S]*$"
    text = re.sub(pattern, "", text)

    # Seconda pulizia di "Il ... ha sritto"
    pattern =  r"^(Il .*?20\d{2}.*?)(?:\n.*? ha scritto:)$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    # Seconda pulizia di "On ... wrote"
    pattern =  r"^(On .*?20\d{2}.*?)(?:\n.*? wrote:)$"
    text = re.sub(pattern, "", text, flags=re.MULTILINE)

    # Rimouovere (di nuovo) i tanti \n
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Anonimizzare i percorsi dei file mascherando parti del percorso
    file_path_pattern = re.compile(r'(/[^/]+/).*?(/[^/]*\b)')
    text = re.sub(file_path_pattern, r'\1*!!*\2', text) # anonimizziamo con *!!*
    
    return text.strip()


# OperatorConfig per inglese
fake_operators_en = {
    "PERSON": OperatorConfig("custom", {"lambda": custom_fake_name}),
    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": lambda x: fake_en.phone_number()}),
    "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: x}), #fake_en.email()
    "LOCATION": OperatorConfig("custom", {"lambda": lambda x: x}),
    "DEFAULT": OperatorConfig(operator_name="mask", 
                              params={'chars_to_mask': 0, 
                                      'masking_char': '*',
                                      'from_end': True}),
    "DATE_TIME": OperatorConfig("custom", {"lambda": lambda x: x}),
    "URL": OperatorConfig("custom", {"lambda": lambda x: x}),
    "NRP": OperatorConfig("custom", {"lambda": lambda x: x})
}

# OperatorConfig per italiano: https://python.langchain.com/v0.1/docs/guides/productionization/safety/presidio_data_anonymization/
fake_operators_it = {
    "PERSON": OperatorConfig("custom", {"lambda": lambda x: x}), #"lambda": custom_fake_name
    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": lambda x: fake_it.phone_number()}),
    "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: x}), #fake_it.email()
    "LOCATION": OperatorConfig("custom", {"lambda": lambda x: x}),
    #"LOCATION": OperatorConfig("custom", {"lambda": lambda x: fake_it.street_address() if x not in words_to_remove else x}),
    "DEFAULT": OperatorConfig(operator_name="mask", 
                              params={'chars_to_mask': 0, 
                                      'masking_char': '*',
                                      'from_end': True}),
    "DATE_TIME": OperatorConfig("custom", {"lambda": lambda x: x}),
    "URL": OperatorConfig("custom", {"lambda": lambda x: x}),
    "IP_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: fake_it.ipv4_private()}),
    "NRP": OperatorConfig("custom", {"lambda": lambda x: x})
}

# Proviamo con i dati di Simone:
log_directory = '/leonardo_work/try24_facchian/tts_tickets_anonymized' # ogni file è un dizionario
counter_doc = 0

def retrieve_name_surname_user(text):
    '''Estrae Nome, Cognome e user dal dizionario'''
    # Cerca un pattern che potrebbe avere un prefisso seguito da un nome e un cognome tra parentesi
    match = re.match(r"(\w*)\s*\(([^)]+)\)", text)
    
    if match: # cerca usernaem (Nome Cognome)
        user = match.group(1).strip()  # Estrae il prefisso, rimuovendo spazi bianchi inutili
        name = match.group(2).strip()  # Estrae nome e cognome
        
        name = name.split()
        first_name = name[0].lower()
        surname = name[1].lower()
        
        return user, first_name, surname
    else:
        # Se non trova parentesi, assume che l'intero testo sia nome e cognome, e ritorna un temptative username
        text = text.replace(",", "") # elimino la virgola che compare in questi casi
        name = text.strip()
        name = name.split()
        
        first_name = name[0].lower()
        surname = name[1].lower()
        user = first_name[0] + surname[:7]
        return user, first_name, surname
    
def check_if_email(string):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Use re.match() to check if the email matches the pattern
    if re.match(email_pattern, string):
        return True
    else:
        return False
    
#######
print('\nNow running consistent_anonimization')

def consistent_anonimization(ticket):
    name_map = {}
    surname_map = {}
    username_map = {}
    email_map = {}
    
    # Info about the user
    if ticket['**Opener_ticket']:
        name_surname = ticket['**Opener_ticket']
        name_surname = name_surname.replace('"', '') # because for some reason sometimes the name is contained into a sub-string
        name_surname = name_surname.replace(',', '')
    else:
        return ticket # sistemare meglio

        
    # Separate Name from Surname.
    if len(name_surname.split()) >= 2:
        '''Usually, the name is in the form: Name Surname'''
        name = name_surname.split()[0].lower()
        surname = name_surname.split()[1].lower()
        username = name.lower()[0] + surname.lower()[:7]
    elif check_if_email(name_surname):
        '''It might happen that there is no name, but an email'''
        name = name_surname
        surname = None
        username = name_surname
    else:
        name = fake_it.first_name_male()
        surname = fake_it.last_name()  
        username = name.lower()[0] + surname.lower()[:7]   
    
    if ticket['**Email_author']:
        email_author = ticket['**Email_author']
    else:
        email_author = 'mariorossi@gmail.com'    
    
    # Generate a random name che abbia senso, se maschio --> maschio, se femmina --> femmina
    if surname:
        if name[-1] == 'a':
            '''Se il nome finisce con la "A", crea un nome femminile random --> heuristics 
            Per il cognome, invece, non ci interessa e lo generiamo sempre random'''
            fake_name = fake_it.first_name_female()
            fake_surname = fake_it.last_name()
        else:
            '''Qui invece controlla che il nome sia maschile, e ne genera uno fake di conseguenza'''
            fake_name = fake_it.first_name_male()
            fake_surname = fake_it.last_name() 
    else:
        fake_name = name
        fake_surname = fake_it.last_name()            
            
    '''Ora generiamo anche lo username di conseguenza'''
    if surname:
        fake_username = fake_name.lower()[0] +  fake_surname.lower()[:7] 
    else:
        fake_username = username      
    
    '''Infine generiamo la fake mail come <fake_name><fake_surname>@gmail.com'''
    if surname:
        fake_email = fake_name.lower() + fake_surname.lower() + '@gmail.com'
    else:
        fake_email = name    
        
    if not surname:
        surname = fake_surname   
        
    '''Creiamo il map tra nomi e cognomi. Probabilmente conviene farlo non all'interno di uno stesso testo, ma all'interno del ticket, così il mapping si resetta al ticket uccessivo'''    
    name_map[name] = fake_name
    surname_map[surname] = fake_surname 
    username_map[username] = fake_username  
    email_map[email_author] = fake_email
    
    # Info about the person who takes the ticket
    details_taken_by = ticket['**Taken_by_ticket']
    pattern = re.compile(r'(\w+)\s+\((\w+)\s+(\w+)\)')
    match = pattern.match(details_taken_by)
    
    # Estrai i valori se c'è una corrispondenza
    if match:
        username_taken_by, name_taken_by, surname_taken_by = match.groups()
        name_taken_by = name_taken_by.lower()
        surname_taken_by = surname_taken_by.lower()
    else:
        pattern_without_username = re.compile(r'(\w+)\s+(\w+)')
        match = pattern_without_username.match(details_taken_by)
        if match:
            name_taken_by, surname_taken_by = match.groups()
            username_taken_by = name_taken_by[0].lower() + surname_taken_by[:7].lower()
        else:
            username_taken_by, name_taken_by, surname_taken_by = details_taken_by, details_taken_by, details_taken_by    
    
    if name_taken_by != details_taken_by: # cioè se ha trovato il nome di chi prende in carico il ticket
        if name_taken_by[-1] == 'a':
            '''Se il nome finisce con la "A", crea un nome femminile random --> heuristics 
            Per il cognome, invece, non ci interessa e lo generiamo sempre random'''
            fake_name_taken_by = fake_it.first_name_female()
            fake_surname_taken_by = fake_it.last_name()
        else:
            '''Qui invece controlla che il nome sia maschile, e ne genera uno fake di conseguenza'''
            fake_name_taken_by = fake_it.first_name_male()
            fake_surname_taken_by = fake_it.last_name()   
    else:
        fake_name_taken_by = name_taken_by
        fake_surname_taken_by = surname_taken_by
        
    '''Ora generiamo anche lo username di conseguenza'''
    if name_taken_by != details_taken_by:
        fake_username_taken_by = fake_name_taken_by.lower()[0] +  fake_surname_taken_by.lower()[:7]   
    else:
        fake_username_taken_by = username_taken_by    
        
    
    '''Infine generiamo la fake mail come <fake_name><fake_surname>@gmail.com'''
    if name_taken_by != details_taken_by:
        fake_email_taken_by = fake_name_taken_by + fake_surname_taken_by + '@cineca.it'
    else:
        fake_email_taken_by = 'support@cineca.it'
        
    '''Creiamo il map tra nomi e cognomi. Probabilmente conviene farlo non all'interno di uno stesso testo, ma all'interno del ticket, così il mapping si resetta al ticket uccessivo'''    
    name_map[name_taken_by] = fake_name_taken_by
    surname_map[surname_taken_by] = fake_surname_taken_by 
    username_map[username_taken_by] = fake_username_taken_by  

    
    # Anonimizziamo i metadati a livello di ticket (per capirci, quelli con **)

    # **Opener_ticket
    asterisco_opener = ticket['**Opener_ticket']
    asterisco_opener_anonymized = ''
    if asterisco_opener != "":
        parts = asterisco_opener.split()
        for i, part in enumerate(parts):
            if part in name_map:
                    parts[i] = name_map[part]
                    asterisco_opener_anonymized += parts[i] + ' '
            elif part in surname_map:
                    parts[i] = surname_map[part]
                    asterisco_opener_anonymized += parts[i] + ' '
            elif part in username_map:
                    parts[i] = username_map[part]
                    asterisco_opener_anonymized += parts[i] + ' '

    asterisco_opener_anonymized = asterisco_opener_anonymized.rstrip()      

    # **Email_author
    asterisco_email_author = ticket['**Email_author']
    if asterisco_email_author in email_map:
        asterisco_email_author = email_map[asterisco_email_author]

    # **Taken_by_ticket
    asterisco_taken_by = ticket['**Taken_by_ticket']
    asterisco_taken_by_anonymized = ''
    if asterisco_taken_by != "Not yet assigned":
        parts = asterisco_taken_by.split()
        for i, part in enumerate(parts):
            if part in name_map:
                    parts[i] = name_map[part]
                    asterisco_taken_by_anonymized += parts[i] + ' '
            elif part in surname_map:
                    parts[i] = surname_map[part]
                    asterisco_taken_by_anonymized += parts[i] + ' '
            elif part in username_map:
                    parts[i] = username_map[part]
                    asterisco_taken_by_anonymized += parts[i] + ' '

    asterisco_taken_by_anonymized = asterisco_taken_by_anonymized.rstrip()   
    
    # Extract all the emails, and anonymize them
    for mail in ticket['**Emails_ticket']:
        text = mail['@@Body']
        
        # Replace name of the user in the text
        if name:
            name_regex = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
            text = name_regex.sub(name_map[name], text)
        if surname:    
            surname_regex = re.compile(r'\b' + re.escape(surname) + r'\b', re.IGNORECASE)
            text = surname_regex.sub(surname_map[surname], text)

        if username:
            username_regex = re.compile(r'\b' + re.escape(username) + r'\b', re.IGNORECASE)
            text = username_regex.sub(username_map[username], text)
 
        if email_author:
            email_regex = re.compile(r'\b' + re.escape(email_author) + r'\b', re.IGNORECASE)
            text = email_regex.sub(email_map[email_author], text)
        
        # Replace name of the user support in the text
        if name_regex:
            name_regex = re.compile(r'\b' + re.escape(name_taken_by) + r'\b', re.IGNORECASE)
            text = name_regex.sub(name_map[name_taken_by], text)

        if surname_taken_by:
            surname_regex = re.compile(r'\b' + re.escape(surname_taken_by) + r'\b', re.IGNORECASE)
            text = surname_regex.sub(surname_map[surname_taken_by], text)

        if username_taken_by:
            username_regex = re.compile(r'\b' + re.escape(username_taken_by) + r'\b', re.IGNORECASE)
            text = username_regex.sub(username_map[username_taken_by], text)
            
        mail['@@Body'] = text   


        # Anonimizzo i metadati all'interno delle singole mail.

        # @@Taken_by
        chiocciola_taken_by = mail['@@Taken_by']
        chiocciola_taken_by_anonymized = ''
        if chiocciola_taken_by != "Not yet assigned":
            parts = chiocciola_taken_by.split()
            for i, part in enumerate(parts):
                if part in name_map:
                        parts[i] = name_map[part]
                        chiocciola_taken_by_anonymized += parts[i] + ' '
                elif part in surname_map:
                        parts[i] = surname_map[part]
                        chiocciola_taken_by_anonymized += parts[i] + ' '
                elif part in username_map:
                        parts[i] = username_map[part]
                        chiocciola_taken_by_anonymized += parts[i] + ' '

        chiocciola_taken_by_anonymized = chiocciola_taken_by_anonymized.rstrip() 
        mail['@@Taken_by'] = chiocciola_taken_by_anonymized

        # @@Author_Name
        author_name = mail['@@Author_Name']
        author_name_anonymized = ''
        if author_name != "Not yet assigned":
            parts = author_name.split()
            for i, part in enumerate(parts):
                if part in name_map:
                    parts[i] = name_map[part]
                elif part in surname_map:
                    parts[i] = surname_map[part]
                author_name_anonymized += parts[i] + ' '
        author_name_anonymized = author_name_anonymized.rstrip()
        mail['@@Author_Name'] = author_name_anonymized

        # @@Author_username
        author_username = mail['@@Author_username']
        if author_username in username_map:
            mail['@@Author_username'] = username_map[author_username]

        # @@Author_email
        author_email = mail['@@Author_email']
        if author_email in email_map:
            mail['@@Author_email'] = email_map[author_email]

        
    return ticket


# def consistent_anonimization(tickets):
#     '''Anonymize Names, Surnames and emails in a consistent way'''
    
#     '''
#     Iniziamo con l'inizializzare dei dizionari vuoti, in cui andremo ad aggiungere le corrispondenze tra:
#     Nome Vero: Nome Generato
#     Cognome Vero: Cognome Generato
#     Email Vera: Email Generata
#     '''
#     name_map = {}
#     surname_map = {}
#     username_map = {}
#     email_map = {} # qui ci devo ancora lavorare
    
#     '''Ora iteriamo sulle varie email del ticket'''
#     for text in tickets:
        
#         '''Estraiamo nome, cognome, user e email'''
#         username, name, surname = retrieve_name_surname_user(text)
#         if text['@@email']:
#             email = text['@@email']
#         else:
#             # Se non c'è la mail, assumiamo che sia nomecognome@gmail.com
#             email = name + surname +'@gmail.com'
        
#         # Generate a random name che abbia senso, se maschio --> maschio, se femmina --> femmina
#         if name[-1] == 'a':
#             '''Se il nome finisce con la "A", crea un nome femminile random --> heuristics 
#             Per il cognome, invece, non ci interessa e lo generiamo sempre random'''
#             fake_name = fake_it.first_name_female()
#             fake_surname = fake_it.last_name()
#         else:
#             '''Qui invece controlla che il nome sia maschile, e ne genera uno fake di conseguenza'''
#             fake_name = fake_it.first_name_male()
#             fake_surname = fake_it.last_name()    
            
#         '''Ora generiamo anche lo username di conseguenza'''
#         fake_username = fake_name.lower()[0] +  fake_surname.lower()[:7]   
        
#         '''Infine generiamo la fake mail come <fake_name><fake_surname>@gmail.com'''
#         fake_email = fake_name + fake_surname + '@gmail.com'
            
#         '''Creiamo il map tra nomi e cognomi. Probabilmente conviene farlo non all'interno di uno stesso testo, ma all'interno del ticket, così il mapping si resetta al ticket uccessivo'''    
#         name_map[name] = fake_name
#         surname_map[surname] = fake_surname 
#         username_map[username] = fake_username  
#         email_map[email] = fake_email
            
#         # Regex to match the name and surname in the text
#         name_regex = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
#         surname_regex = re.compile(r'\b' + re.escape(surname) + r'\b', re.IGNORECASE)
#         username_regex = re.compile(r'\b' + re.escape(username) + r'\b', re.IGNORECASE)
#         email_regex = re.compile(r'\b' + re.escape(email) + r'\b', re.IGNORECASE)

#         # Replace names and surnames in the text
#         text = name_regex.sub(name_map[name], text)
#         text = surname_regex.sub(surname_map[surname], text)
#         text = username_regex.sub(username_map[username], text)
#         text = email_regex.sub(email_map[email, text])
        
#         return text    



# for filename in sorted(os.listdir(log_directory))[5:50]:
#     # Considera solo i file che terminano con .log
#     if filename.endswith('.log'):
#         file_path = os.path.join(log_directory, filename)
#         # print(file_path)
#         # Apri e leggi il file
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#             example_text = data['@@body']
#             date = data['@@date']
#             title = data['@@subject']
#             user, name, surname = retrieve_name_surname_user(data['@@user'])
            
#             print(example_text)
            # counter_doc +=1
            
            
            # # Rimouovere patterns
            # example_text_clean = remove_ending_date(example_text)
            
            # # Anonimizza nomi e congomi (e email appena risolvo come ottenere la mail del mittente nel parser)
            # example_text_clean = consistent_anonimization(example_text_clean)

            # ## Rilevamento lingua e selezione degli operatori per il testo inglese
            # operators, lang = get_operators_for_language(example_text_clean)
            # if lang is not None:  # Assicurati che la lingua sia stata rilevata correttamente
            #     results = analyzer.analyze(text=example_text_clean, language=lang)
            #     anonymized_text = anonymizer.anonymize(text=example_text_clean,
            #                                             analyzer_results=results,
            #                                             operators=operators).text
            #     # results = analyzer.analyze(text=example_text_clean, language=lang)
            #     # anonymized_text = anonymizer.anonymize(text=example_text_clean,
            #     #                                         analyzer_results=results,
            #     #                                         operators=operators).text
            #     #print(example_text); print(':'*110, '\n') 
            #     print(f"*** Message: {os.path.basename(file_path)} \n")
            #     print(f"@User: {user}"); print(f"@Name: {name}"); print(f"@Surname: {surname}"); print(f"@Date: {date} \n")
            #     print(f"@Subject: {title}")
            #     print(f"@Body: {example_text_clean}")
            #     #print(anonymized_text) # anonymized_text
            #     print('='*110, '\n\n')
            # else:
            #     print("@testo_vuoto Language detection failed for the provided text. Skipping analysis.")   


# #Togli commento se vuoi provare solo un testo
# analyzer = AnalyzerEngine()
# anonymizer = AnonymizerEngine()

# document = """module load intel intelmpi mkl fftw blas lapack scalapack szip zlib/1.2.8--gnu--6.1.0 hdf5module load env-skl                                                                                                                                                                          module load profile/astro idl python"""

# analyzer_results = analyzer.analyze(document, language = 'en')

# for res in analyzer_results:
#     print(res)

# # aaa = anonymizer.anonymize(
# #     text = document,
# # analyzer_results = analyzer_results, operators = fake_operators_it)
# # print(aaa)