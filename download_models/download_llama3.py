import os

os.system("huggingface-cli login --token $HUGGINGFACE_TOKEN")
os.system("huggingface-cli download --local-dir .")


