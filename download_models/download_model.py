# File generico per installare un nuovo modello

import os

# Definisci il percorso della cartella dove vuoi scaricare il modello
model_dir = "/leonardo_work/try24_facchian/prove/embedding_model_new"  # Sostituisci con il percorso desiderato

# Crea la cartella se non esiste
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Login in Hugging Face
os.system("huggingface-cli login --token $HUGGINGFACE_TOKEN")

# Scarica il modello nella cartella specificata
os.system(f"huggingface-cli download openbmb/MiniCPM-Embedding --local-dir {model_dir}")

# intfloat/multilingual-e5-base --> quello utilizzato inizialmente
# openbmb/MiniCPM-Embedding --> quello nuovo
