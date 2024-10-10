# In this file, we take the "raw" files, we chunk them, and we save them as txt in the folder "chunks"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

# Funzione per caricare tutti i file di testo dalla directory e creare oggetti Document
def load_txt_files(directory_path):
    docs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                # Crea un oggetto Document per ogni file .txt
                docs.append(Document(page_content=text, metadata={"source": filename}))
    return docs

# Funzione per calcolare la lunghezza media dei documenti
def avg_doc_length(docs):
    return sum([len(doc.page_content) for doc in docs]) // len(docs)

# Carica i file di testo dalla directory
directory_path = "/leonardo_work/try24_facchian/RAG_docs/output_texts"
docs_before_split = load_txt_files(directory_path)

# Definisci il text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Numero di caratteri per chunk
    chunk_overlap=50  # Sovrapposizione tra i chunk
)

# Dividi i documenti in chunk
docs_after_split = text_splitter.split_documents(docs_before_split)

# Calcola la lunghezza media dei documenti prima e dopo il chunking
avg_char_before_split = avg_doc_length(docs_before_split)
avg_char_after_split = avg_doc_length(docs_after_split)

# Stampa i risultati
print(f'Before split, there were {len(docs_before_split)} documents loaded, with average characters equal to {avg_char_before_split}.')
print(f'After split, there were {len(docs_after_split)} documents (chunks), with average characters equal to {avg_char_after_split} (average chunk length).')

# Salva i chunk nella cartella "chunks"
chunk_folder = "/leonardo_work/try24_facchian/RAG_docs/chunks"
os.makedirs(chunk_folder, exist_ok=True)  # Crea la cartella se non esiste

# Salva ogni chunk come file separato
for i, chunk in enumerate(docs_after_split):
    chunk_filename = f"chunk_{i + 1}.txt"
    chunk_path = os.path.join(chunk_folder, chunk_filename)
    with open(chunk_path, "w", encoding="utf-8") as file:
        file.write(chunk.page_content)
    print(f"Salvato: {chunk_path}")
