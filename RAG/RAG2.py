# This is the main script to do RAG.
# Use thif for the experiments. Rather than RAG.py,
# here we laod the entire index with all the documents.

import os
import pickle
import numpy as np
import pandas as pd
import torch
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
import faiss

from transformers import pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EMBEDDING_MODEL = "/leonardo_work/try24_facchian/prove/embedding_model"
LLAMA_MODEL = './Finetuned-plus-quant'
INDEX_PATH = '/leonardo_work/try24_facchian/RAG_docs/faiss_index.bin'
CHUNKS_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/faiss_docs.pkl'
DOCSTORE_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/docstore.pkl'
INDEX_TO_DOCSTORE_ID_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/index_to_docstore_id.pkl'

# Definizione del modello Hugging Face salvato localmente
huggingface_embeddings = HuggingFaceBgeEmbeddings(
    model_name = EMBEDDING_MODEL,  
    model_kwargs = {'device': DEVICE},
    encode_kwargs = {'normalize_embeddings': True}
)


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

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

print('Indice FAISS, docstore e mappa caricati con successo.')

# Definizione del modello Hugging Face per la generazione del testo
hf = HuggingFacePipeline.from_model_id(
    model_id = LLAMA_MODEL,
    device = 0,
    task = "text-generation",
    pipeline_kwargs = {"temperature": 0.95, "max_new_tokens": 200}
)

# Definizione del prompt template
prompt_template = """**********\n Sei un assistente per il gruppo di User Assistance and Support presso il consorzio CINECA. Usa i seguenti pezzi di contesto, quando presenti, per rispondere alla domanda alla fine.

{context}

Question: {question}

Helpful Answer:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Creazione della catena RetrievalQA
retrievalQA = RetrievalQA.from_chain_type(
    llm=hf,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

## Esecuzione della query
# question = """How many GPUs does Leonardo's compute nodes host?"""
# result = retrievalQA.invoke({"query": question})
# print(result['result'])


############ Iterare sul dataset ############
test_set = pd.read_csv('/leonardo_work/try24_facchian/prove/test_set_classification_EN.csv')


for index, row in test_set.iterrows():
    question = row['Question']

    context = ""
    retrieved_docs = retriever.get_relevant_documents(question)
    if retrieved_docs:
        context = "\n".join([doc.page_content for doc in retrieved_docs])

    if LLAMA_MODEL == "/leonardo_work/try24_facchian/prove/third_finetuning_10k.json/checkpoint-6765":
        question = f"""
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Sei un assistente per il gruppo di User Assistance and Support presso il consorzio CINECA. Usa i seguenti pezzi di contesto, quando presenti, per rispondere alla domanda alla fine.<|eot_id|><|start_header_id|>user<|end_header_id|>
        {context}
        {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """

    elif LLAMA_MODEL == '.': 
        x = 1

    generated_text = retrievalQA.invoke({"query": question})
    generated_text = generated_text['result'].replace('\n', ' ').strip()
    generated_text = generated_text.split("Helpful Answer: ")[-1].strip()
    test_set.at[index, 'Model_Answer'] = generated_text

    # print(f"Question:\n{question}\n\n---------------------------------------")
    # print(f'Answer:\n{generated_text}\n\n---------------------------------------')
    # print(f"Context:\n{context}")


test_set.to_csv('/leonardo_work/try24_facchian/prove/results_RAG_classification_finetuned_quantized.csv', index=False, sep = '|')    