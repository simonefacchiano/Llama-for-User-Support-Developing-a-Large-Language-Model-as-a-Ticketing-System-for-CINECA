# Questo file si pone l'obiettivo di organizzare meglio il file "parse_simone.py"
# Organizza meglio il codice, e prova a renderlo più efficace.
# Inoltre, crea il grande dataset contenente tutti i meta-dati.


html_content = '''

'''
import os
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import datetime
from dateutil import parser

from anonymize_data import consistent_anonimization


def compute_date_difference(date1_str, date2_str):
    '''
    This function takes as input two dates. It sorts them in descending order,
    and computes the time difference between the two
    '''
    # Formato della data
    date_format = "%a %b %d %H:%M:%S %Y"
    
    # Conversione delle stringhe in oggetti datetime
    date1 = datetime.strptime(date1_str, date_format)
    date2 = datetime.strptime(date2_str, date_format)
    
    # Assicurarsi che date1 sia sempre precedente a date2
    if date1 > date2:
        date1, date2 = date2, date1
    
    # Calcolo della differenza
    delta = date2 - date1
    
    # Estrazione dei giorni, ore e minuti
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days} days, {hours} hours, {minutes} minutes"
  
def extract_email(text):
    # Regex che cerca un pattern di nome seguito da un indirizzo email tra < e >
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if match:
        email = match.group(0).strip()  # Estrae l'email
        return email
    return None

def check_if_email(string):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Use re.match() to check if the email matches the pattern
    if re.match(email_pattern, string):
        return True
    else:
        return False

def remove_endings(body_text):
    '''
    Questa funzione cerca il pattern "Show quoted text" nell'email e rimuove tutto ciò che segue,
    inclusa la stringa stessa. Rimuove anche le righe che iniziano con "Il ... ha scritto" e "On ... wrote",
    presumendo che siano citazioni di messaggi precedenti.

    Args:
    body_text (str): Il contenuto HTML o testuale dell'email da processare.

    Returns:
    str: Il contenuto modificato senza il testo quotato e senza le linee di citazione tipiche.
    '''
    
    # Crea un pattern regex per trovare "Show quoted text" e tutto ciò che segue fino alla fine del contenuto
    pattern_show = r"Show quoted text.*"
    body_text = re.sub(pattern_show, "", body_text, flags=re.DOTALL)
    
    # Mandiamo a capo la stringa di "Il ... ha scritto:"
    pattern = r"^(Il .*?20\d{2}.*? ha scritto:)$"
    body_text = re.sub(pattern, r"\n\1", body_text) #

    # Mandiamo a capo la stringa di "On ... wrote:"
    pattern = r"(On .*?(?:\d{2}/\d{2}/\d{2}|\d{2}.\d{2}.\d{2}|20\d{2}).*? wrote:)" # r"(On .*?(?:\d{2}/\d{2}/\d{2}|20\d{2}).*? wrote:)
    body_text = re.sub(pattern, r"\n\1", body_text)
  
    # Rimuovi il "Il giorno tot X ha scritto:"
    pattern =  r"^(Il .*?20\d{2}.*? ha scritto:)$"
    body_text = re.sub(pattern, "", body_text, flags=re.MULTILINE)
          
    # Rimuovi il "On ... wrote:"
    pattern = r"^(On\s+.*?(?:\d{2}/\d{2}/\d{2}|\d{2}\.\d{2}\.\d{2}|20\d{2}).*?\s+wrote:)"  #r"^(On .*?20\d{2}.*? wrote:)$"
    body_text = re.sub(pattern, "", body_text, flags=re.MULTILINE|re.DOTALL)
    
    return body_text

def extract_name_opener(content):
    '''Often the opener of the ticket has the following format:
    username (Name Surname). This functions extracts the name of the opener'''
    # Verifica se il contenuto ha la struttura username (nome cognome)
    if re.match(r'^\w+\s\([a-zA-Z\s\.]+\)$', content):
        # Estrae il contenuto tra parentesi
        match = re.search(r'\((.*?)\)', content)
        if match:
            testo = match.group(1)
            # Pulisce il contenuto eliminando singole lettere seguite da un punto
            parole = testo.split()
            parole_pulite = [parola for parola in parole if not (len(parola) == 2 and parola[1] == '.')]
            return ' '.join(parole_pulite)
    return content

def extract_username(content):
    '''This is to be read after extract_name_opener.
    Since the opener is often in the format "username (Name Surname)",
    this function extacts the username of the opener'''
    # Verifica se il contenuto ha la struttura username (nome cognome)
    if re.match(r'^\w+\s\([a-zA-Z\s\.]+\)$', content):
        # Estrae lo username prima della parentesi
        username = re.match(r'^(\w+)\s', content).group(1)
        return username
    return None

def guess_username(name_surname):
    '''
    Certe volte non compare il nome utente nell'intestazione della mail.
    In tal caso, lo compongo io nel formato standard:
    prima lettera del nome, prime sette del cognome'''
    if not name_surname:
       return ''
    
    
    # Divide il nome completo in nome e cognome
    parts = name_surname.split()

    if len(parts) < 2:
       return parts[0]
    else:
        first_name = parts[0]  # Nome
        last_name = parts[-1]  # Cognome

        # Prendo la prima lettera del nome
        first_letter = first_name[0].lower()

        # Prendo le prime 7 lettere del cognome, se disponibili, altrimenti prendoe tutto il cognome
        first_seven_last = last_name[:7].lower()

        # Compongo l'username
        username = first_letter + first_seven_last
        return username


def extract_emails(html_content):
  '''
  This function is the main parser of the HTML content.
  It takes as input the HTML of the entire ticket. It then extracts all the emails one by one.
  The emails are stored in a list. The list contains not only body of the email, but also some
  metadata, such as: ID, date, authors, time from previous email, status, length...
  '''
  emails = []
  email_id = 0
  opener = None
  taken_by = 'Not yet assigned'
  last_time_email = None
  who = None
  current_status = 'new'
  to = None
  from_ = None
  from_email = None
  subject = None
  
  Author = None
  Username = None
  
  soup = BeautifulSoup(html_content, 'html.parser')
  target_divs = soup.find_all('div', class_=['transaction Ticket-transaction message odd', # messaggio
                                             'transaction Ticket-transaction message even', # messaggio
                                             'transaction Ticket-transaction basics even',
                                             'transaction Ticket-transaction basics odd']) # in background, il ticket è preso in carico e si cambia lo status
        
  for idx, div in enumerate(target_divs):
    
    # Case 1. Email, metadata and actual text
    if 'message odd' in " ".join(div.get('class', [])):        
        metadata_div = div.find('div', class_='metadata')
        if metadata_div:
          date_div = metadata_div.find('span', class_='date')
          date = date_div.get_text(strip=True) # Data di apertura del ticket
            
          description_span = div.find('span', class_='description')
          if description_span:
            author_div = metadata_div.find('span', class_='user')
            author = author_div.get_text(strip=True) # username (Name Surname)
            author_name_surname = extract_name_opener(author) # Name Surname
            author_username = extract_username(author) # nsurname, ma può essere None se non era presente nel nome originale

            if not author_username:
               author_username = guess_username(author_name_surname)
            
            if not Author:
              # Se la variabile Author era ancora None, significa che non avevamo ancora incontrato il nome del'autore.
              # Pertanto, colui o colei che apre la mail verrà segnato/a come autore/autrice.
              Author = author_name_surname
            if not Username:  
              # Stessa cosa con lo Username
              Username = author_username
            
            author_email_a_tag = str(author_div.find('a'))
            if from_email is None:
              from_email = extract_email(author_email_a_tag) # Email di Author

            if not opener:
              '''Se la variabile "author" è ancora None, significa che è la prima mail che incontriamo.
              Quindi, l'autore della primissima mail verrà considerato l'opener del ticket'''
              opener = author
              
            if author == opener:
              who = 'user'
            else:
              who = 'support'  
          
        table = div.find('div', class_='content').find('table')
        if table:
          rows = table.find_all('tr')
          for row in rows:
            key, value = row.find_all('td')
            if key.text.strip() == "To:":
                to = value.text.strip()
            elif key.text.strip() == "From:":
                from_ = value.text.strip()
            elif key.text.strip() == "Subject:":
                subject = value.text.strip()
                
        message_stanza = div.find('div', class_='message-stanza')   
        
        message_stanza = div.find('div', class_='message-stanza')
        if message_stanza:
            desired_text = ''
            
            cutoff_element = message_stanza.find('div', class_='message-stanza-folder')

            if cutoff_element:
                for elem in message_stanza.children:
                    if elem == cutoff_element:
                        break
                    if isinstance(elem, str):
                        desired_text += elem.strip() + ' '
                    else:
                        desired_text += elem.get_text(separator=' ', strip=True) + ' '
            else:
                desired_text = message_stanza.get_text(separator=' ', strip=True)

            message_text = desired_text.strip()
        else:
            message_text = ''

        
        if last_time_email:
          time_diff = compute_date_difference(date, last_time_email)
        else:
          time_diff = None 
      
        if "Comments added" not in description_span.get_text():
            email_dict = {'@@ID_email': email_id,
                        '@@Date': date,
                        '@@To': to,
                        '@@Who': who,
                        '@@Author_Name': Author, #from_, # si chiamava From
                        '@@Author_username': Username, # questo è nuovo 
                        '@@Author_email': from_email, #from_, # si chiamava Email_author
                        '@@Subject': subject,
                        '@@Length_mail': len(message_text),
                        '@@Taken_by': taken_by,
                        '@@Status': current_status,
                        '@@Time_from_previous': time_diff,
                        '@@Body': remove_endings(message_text),
                        }
            emails.append(email_dict)
                
            email_id += 1
            last_time_email = date
        
    # Case 2. This contains information not directly reported in the body of the email    
    elif 'basics even' in " ".join(div.get('class', [])):
        '''Ticket preso in carico, aggiornamento dello status'''
        description_span = div.find('span', class_='description')
        
        if description_span and "Status changed from" in description_span.text:
          status_change_match = re.search(r"Status changed from '(\w+)' to '(\w+)'", description_span.text)
          if status_change_match:
            current_status = status_change_match.group(2).lower()

          user_span = description_span.find('span', class_='user')
          if user_span:
            if (taken_by == 'Not yet assigned') and (user_span.get_text(strip=True) != 'The RT System itself'): #user_span.get_text(strip=True) != 
              taken_by = user_span.get_text(strip=True)           
              
    # Case 3. Similar to case 2.        
    elif 'basics odd' in " ".join(div.get('class', [])):       
      '''Ticket preso in carico, aggiornamento dello status'''
      description_span = div.find('span', class_='description')
            
      if description_span and "Status changed from" in description_span.text:
        status_change_match = re.search(r"Status changed from '(\w+)' to '(\w+)'", description_span.text)
        if status_change_match:
          current_status = status_change_match.group(2).lower()

        user_span = description_span.find('span', class_='user')
        if user_span:
          if (taken_by == 'Not yet assigned') and (user_span.get_text(strip=True) != 'The RT System itself'): #user_span.get_text(strip=True) != 
            taken_by = user_span.get_text(strip=True) 
                                    

    # NOTE: caso 2 e caso 3 sono identici. Li ho separati solo per facilitare il debug 
                                    
    # Case 4, similar to case 1. Email, metadata and actual text            
    elif 'message even' in " ".join(div.get('class', [])):
        '''Risposta di user support'''
        
        metadata_div = div.find('div', class_='metadata')
        if metadata_div:
          date_div = metadata_div.find('span', class_='date')
          date = date_div.get_text(strip=True)
            
          description_span = div.find('span', class_='description')
          if description_span:
            author_div = metadata_div.find('span', class_='user')
            author = author_div.get_text(strip=True)
            # Probabilmente qui andrà fatto un check per vedere se sono stati aggiunti dei commenti.
            # In tal caso, va tolto.

            if "Comments added" in description_span.get_text():
               continue

            if not opener:
              '''Se la variabile "author" è ancora None, significa che è la prima mail che incontriamo.
              Quindi, l'autore della primissima mail verrà considerato l'opener del ticket'''
              opener = author
                            
            if author == opener:
              who = 'user'
            else:
              who = 'support'            

        message_stanza = div.find('div', class_='message-stanza')         

        if message_stanza:
          cutoff_element = message_stanza.find('div', class_='message-stanza-folder')

          if cutoff_element:
            desired_text = ''
            for elem in message_stanza.children:
                if elem == cutoff_element:
                    break
                if isinstance(elem, str):
                    desired_text += elem.strip() + ' '
                else:
                    desired_text += elem.get_text(separator=' ', strip=True) + ' '
          else:
            desired_text = message_stanza.get_text(separator=' ', strip=True)          
        # else:
        #     desired_text = message_stanza.get_text(separator=' ', strip=True)

        message_text = desired_text.strip() 

            
        if last_time_email:
          time_diff = compute_date_difference(date, last_time_email)
        else:
          time_diff = None    
        
        if "Comments added" not in description_span.get_text():
            another_email_dict = {'@@ID_email': email_id,
                        '@@Date': date,
                        '@@To': from_ if who=='support' else to,
                        '@@Who': who,
                        '@@Author_Name': Author, #to if who=='support' else from_, # si chiamava From
                        '@@Author_username': Username, # questo è nuovo 
                        '@@Author_email': from_email, # si chiamava Email_author
                        '@@Subject': subject,
                        '@@Length_mail': len(message_text),
                        '@@Taken_by': taken_by,
                        '@@Status': current_status,
                        '@@Time_from_previous': time_diff,
                        '@@Body': remove_endings(message_text),
                        }
            emails.append(another_email_dict)    
            
            email_id += 1
            last_time_email = date
  
  if len(emails) > 0: # necessario perché alcune email sono vuote
    emails[-1]['@@Status'] = current_status # se dopo l'ultima mail inviata lo status viene modificato, così almeno siamo in grado di riconoscerlo
    for i in range(1, len(emails)):
      emails[i]['@@Taken_by'] = taken_by

  return(emails)


# ---------------------------------------------------------------------------------------------------------------- #
## Se vuoi provare extract_email sulla singola mail, runna questo codice:
# extracted = extract_emails(html_content)    
# for extr in extracted:
#   print(extr); print('')

# src_folder = '/leonardo_work/try24_facchian/tts_tickets'
# for filename in os.listdir(src_folder)[215:225]:
#     if filename.endswith('.log'):
#         print('\n --**--**--**--**--**--**--**--** \n', filename, '\n --**--**--**--**--**--**--**--**')
#         file_path = os.path.join(src_folder, filename)
#         with open(file_path, 'r') as file:
#             html_content = file.read()
        
#         extracted = extract_emails(html_content)
#         for extr in extracted:
#             print(extr)
#             print('')
# ---------------------------------------------------------------------------------------------------------------- #
         


def extract_ticket_number(name_log):
    number = name_log[7:14]
    return number


def create_dataset(source_folder, destination_folder, save_as, save_only_part = None, display = False, show_entries = None, save = True):
  '''
  This function creates the JSON dataset that will eventually be fed to the LLM.
  Each entry of the dataset is one ticket. Specifically, each ticket consists in:
  - Metadata of the ticket
  - Emails, and metadata of the emails
  
  -> source_folder tells you where are the raw HTMLs
  -> destination_folder tells you where you want to save the dataset
  -> save_as is a parameter you can set to decide the name of the JSON file
  -> save_only_part is set if you only want to process N HTMLs from the source_folder
  -> display is a bool. If True, it prints the first "show_entries" entries
  -> save is a bool. If true, it saves
  '''
  
  log_files = sorted([f for f in os.listdir(source_folder) if f.endswith('.log')]) # sorted files in source_folder 
  tickets = [] # initialize an empy list. This will be filled with the tickets
  
  if save_only_part:
    # If asked, it only processed the irst N files from source_folder
    log_files = log_files[:save_only_part]
    
  if show_entries:
    log_files = log_files[:show_entries]
    
  n_files = len(log_files)  
  
  
  for file_idx, filename in enumerate(log_files):
    if file_idx % 500 == 0:
      print(f"\nProcessing file n. {file_idx} of {n_files}...")
    
    ticket_id = extract_ticket_number(filename)
    file_path = os.path.join(source_folder, filename)

    try: 
      with open(file_path, 'r') as file:
        html_content = file.read()
        extracted_emails = extract_emails(html_content) # parsing of the email

        # Creating metadata of the entire ticket
        if extracted_emails:
          len_ticket = len(extracted_emails) # total number of emails in the ticket
          open_date = extracted_emails[0]['@@Date'] # opening date of the ticket
          close_date = extracted_emails[-1]['@@Date'] # closure date of the ticket
          date_diff = compute_date_difference(open_date, close_date) # duration of the ticket
          opener_ticket = extracted_emails[0]['@@Author_Name'] # name of the opener (user)
          taken_by_operator = extracted_emails[-1]['@@Taken_by'] # name of the operator who took the ticket
          last_status = extracted_emails[-1]['@@Status'] # final status of the ticket: can be new (never opened), open, resolved
          subject_ticket = extracted_emails[0]['@@Subject'] # subject of the ticket
          email_author = extracted_emails[0]['@@Author_email']
          
        else:
          # We need this else because for the moment some tickets cannot be parsed (errors, mesages too long...)
          len_ticket = 0  
          open_date = None
          close_date = None
          date_diff = 0
          opener_ticket = None
          taken_by_operator = None
          last_status = None
          subject_ticket = None   
    
    except Exception as e:
      print(f"Error processing ticket ID {ticket_id}: {str(e)}")
          
    
    # Sometimes we don't have access to the name of the user, but only to his/her email.
    # This is a problem because we can't anonymize the data effectively. So, we double check
    # whether we have accesso to an email in the form: name.surname@domain.com.
    # We try to extract the name from here
    if opener_ticket:
      if check_if_email(opener_ticket):
        pattern = r'([a-zA-Z]+)\.([a-zA-Z]+)@'
        match = re.match(pattern, opener_ticket)
        if match:
          opener_ticket = f'{match.group(1)} {match.group(2)}'  
        
    ticket_dictionary = {
      '**ID_ticket': ticket_id, # ID del ticket
      '**Open_date_ticket': open_date, # Open date del ticket
      '**Closure_Date_ticke': close_date, # Closure date del ticket
      '**Duration_ticket': date_diff, # Lunghezza temporale del ticket
      '**Opener_ticket': opener_ticket, # Nome della persone che ha aperto il ticket
      '**Status_ticket': last_status, # Status del ticket
      '**Languages_ticket': ['Not yet assigned'], # Lingue usate nel ticket
      '**Length_ticket': len_ticket, # Numero di mail del ticket
      '**Email_author': email_author, 
      '**Subject_ticket': subject_ticket, # Oggetto del ticket
      '**Taken_by_ticket': taken_by_operator, # Chi ha preso in carico il ticket
      '**Emails_ticket': extracted_emails # Lista di email del ticket
    }
      
    # Anonymize  
    ticket_dictionary = consistent_anonimization(ticket_dictionary)  
    
    # Add to the dataset
    tickets.append(ticket_dictionary)   
    
  if display:
    if show_entries:
      print(tickets[:show_entries])   
    else:
      print(tickets)
    
  if save:
    # Saving details:
    if not save_as.endswith('.json'):
      save_as += '.json' # add .jons to the file name
    full_path = os.path.join(destination_folder, save_as)  
    
    print(f"\n*** Saving in: {full_path} ***")  
    
    with open(full_path, 'w') as file:
      json.dump(tickets, file, indent=4) # 'indent=4' to make the file more readable
    
    if os.path.exists(full_path):
      print("\n*** File saved successfully ***\n")
    else:
      print("\n*** Failed to save the file: file already present ***\n")  
    
  
  return('Saving complete')

  
  # print(f"Saving to: {full_path}")  
  # with open(full_path, 'w') as file:
  #     json.dump(tickets, file, indent=4)  # 'indent=4' to make the file more readable
  # if os.path.exists(full_path):
  #   print("File saved successfully.")
  # else:
  #   print("Failed to save the file.") 


create_dataset(source_folder = '/leonardo_work/try24_facchian/tts_tickets',
               destination_folder = '/leonardo_work/try24_facchian/datasets_json',
               save_as = 'anonymized_dataset_25_agosto',
               display = False,
               save_only_part = 20000,
               save = True)