# We create the index and all the other things that were necessary for RAG.


import os
import pickle
import numpy as np
import torch
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import faiss

from transformers import pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EMBEDDING_MODEL = "/leonardo_work/try24_facchian/prove/embedding_model_new"
LLAMA_MODEL = '.'
DOCS_CINECA = "/leonardo_work/try24_facchian/RAG_docs/output_texts"
INDEX_PATH = '/leonardo_work/try24_facchian/RAG_docs/faiss_index.bin'
CHUNKS_PATH = '/leonardo_work/try24_facchian/RAG_docs/chunks/faiss_docs.pkl'

print('Import ok')


# Definizione del modello Hugging Face salvato localmente
huggingface_embeddings = HuggingFaceBgeEmbeddings(
    model_name = EMBEDDING_MODEL,  
    model_kwargs = {'device': DEVICE, 'trust_remote_code': True},
    encode_kwargs = {'normalize_embeddings': True}
)


print('Modello di embedding importato')

docs_before_split = []
filenames = sorted(os.listdir(DOCS_CINECA))[:1]  # Prendi solo i primi 3 file
for filename in filenames:
    if filename.endswith(".txt"):
        with open(os.path.join(DOCS_CINECA, filename), "r", encoding="utf-8") as f:
            docs_before_split.append(Document(page_content=f.read()))

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=30,
)
docs_after_split = text_splitter.split_documents(docs_before_split)          

print('Documenti splittati')


#### Ora entra in gioco FAISS
vectorstore = FAISS.from_documents(docs_after_split, huggingface_embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}) # Verrà usato dentro RetrievalQA, quando combineremo LLM e Retriever

faiss.write_index(vectorstore.index, INDEX_PATH)

with open(CHUNKS_PATH, "wb") as f:
    pickle.dump(docs_after_split, f)

print('Tutto ok')