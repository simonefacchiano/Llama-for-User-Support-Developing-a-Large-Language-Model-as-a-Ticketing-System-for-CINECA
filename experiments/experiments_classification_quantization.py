# In this file, we make the quantized model answer the "classification" questions:
import os
import pickle
import numpy as np
import pandas as pd
import torch
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
import faiss

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Imposta il dispositivo
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Definizione dei percorsi
EMBEDDING_MODEL = "/leonardo_work/try24_facchian/prove/embedding_model"
INDEX_PATH = '/leonardo_work/try24_facchian/RAG_docs/faiss_index.bin'
CHUNKS_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/faiss_docs.pkl'
DOCSTORE_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/docstore.pkl'
INDEX_TO_DOCSTORE_ID_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/index_to_docstore_id.pkl'

# Inizializza il modello di embedding Hugging Face
huggingface_embeddings = HuggingFaceBgeEmbeddings(
    model_name=EMBEDDING_MODEL,  
    model_kwargs={'device': DEVICE},
    encode_kwargs={'normalize_embeddings': True}
)

# Caricamento del tokenizer e del modello Llama
base_model_id = '.'  # Definisci il percorso del tokenizer
model_id = './Llama-3-quant'  # Modello Llama quantizzato

# Inizializza il modello e il tokenizer
model = AutoModelForCausalLM.from_pretrained(model_id, 
                                             device_map='auto', 
                                             load_in_8bit=True)    

tokenizer = AutoTokenizer.from_pretrained(base_model_id)
tokenizer.pad_token = tokenizer.eos_token

#### Carica l'indice FAISS e i chunks

# Carica l'indice FAISS
print('Caricamento indice FAISS...')
index = faiss.read_index(INDEX_PATH)

# Carica i documenti (chunks) salvati
print('Caricamento dei documenti (chunks)...\n')
with open(CHUNKS_PATH, "rb") as f:
    docs_after_split = pickle.load(f)

# Carica il docstore salvato
print('Caricamento del docstore...')
with open(DOCSTORE_PATH, "rb") as f:
    docstore = pickle.load(f)    

# Carica la mappa index_to_docstore_id
print('Caricamento della mappa index_to_docstore_id...')
with open(INDEX_TO_DOCSTORE_ID_PATH, "rb") as f:
    index_to_docstore_id = pickle.load(f)

# Crea il vectorstore utilizzando l'indice FAISS e i chunks caricati
vectorstore = FAISS(
    embedding_function=huggingface_embeddings, 
    index=index, 
    docstore=docstore, 
    index_to_docstore_id=index_to_docstore_id
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

print('Indice FAISS, docstore e mappa caricati con successo.')

# Definizione del modello Hugging Face per la generazione del testo con HuggingFacePipeline
pipeline_model = pipeline(
    task="text-generation",
    model=model,  # Ora utilizziamo il modello caricato
    tokenizer=tokenizer,
    temperature=0.95,
    max_new_tokens=200
)

# Definizione del prompt template
prompt_template = """**********\n Use the following pieces of context to answer the question at the end.

{context}

Question: {question}

Helpful Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Creazione della catena RetrievalQA
retrievalQA = RetrievalQA.from_chain_type(
    llm=HuggingFacePipeline(pipeline=pipeline_model),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

############ Iterare sul dataset ############
test_set = pd.read_csv('/leonardo_work/try24_facchian/prove/test_set_classification_EN.csv')

for index, row in test_set.iterrows():
    question = row['Question']

    generated_text = retrievalQA.invoke({"query": question})
    generated_text = generated_text['result'].replace('\n', ' ').strip()
    generated_text = generated_text.split("Helpful Answer: ")[-1].strip()
    test_set.at[index, 'Model_Answer'] = generated_text

    print(f"Question:\n{question}\n\n---------------------------------------")
    print(f'Answer:\n{generated_text}')

    print(f'Risposta alla domanda {index} effettuata')

# Salva i risultati in un file CSV
test_set.to_csv('/leonardo_work/try24_facchian/prove/results_quantized_classification.csv', index=False, sep='|')
