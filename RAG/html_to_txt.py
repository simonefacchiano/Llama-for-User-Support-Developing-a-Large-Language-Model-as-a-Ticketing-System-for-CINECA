# Questo file contribuisce alla creazione del database per RAG.
# In questo script prendiamo degli HTML, e li convertiamo in txt.

import os
from bs4 import BeautifulSoup

# Definisci le cartelle
input_folder = "/leonardo_work/try24_facchian/RAG_docs"
output_folder = "/leonardo_work/try24_facchian/RAG_docs/output_texts"

# Crea la cartella di output se non esiste
os.makedirs(output_folder, exist_ok=True)

# Elenca tutti i file nella cartella di input
for filename in os.listdir(input_folder):
    # Controlla se il file ha l'estensione .html
    if filename.endswith(".html"):
        input_file_path = os.path.join(input_folder, filename)

        # Apri e leggi il contenuto del file HTML
        with open(input_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Usa BeautifulSoup per fare il parsing dell'HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Estrai il testo dall'HTML
        text = soup.get_text()

        # Definisci il percorso del file .txt corrispondente nella cartella di output
        output_file_name = filename.replace(".html", ".txt")
        output_file_path = os.path.join(output_folder, output_file_name)

        # Scrivi il testo estratto nel file di output .txt
        with open(output_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        print(f"File {filename} convertito in {output_file_name}")

print("Conversione completata per tutti i file HTML!")
