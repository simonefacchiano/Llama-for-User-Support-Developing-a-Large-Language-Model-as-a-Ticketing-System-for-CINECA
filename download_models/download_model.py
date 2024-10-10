# Thanks to this file, you can install a new model.
# We used this for downloading the embedding model we used in RAG.

import os

model_dir = "/leonardo_work/try24_facchian/prove/embedding_model_new"  # <-- Change here

# Crea la cartella se non esiste
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Login in Hugging Face, la chiave è stata definita come variabile d'ambiente
os.system("huggingface-cli login --token $HUGGINGFACE_TOKEN")

# Scarica il modello
os.system(f"huggingface-cli download intfloat/multilingual-e5-base --local-dir {model_dir}")
