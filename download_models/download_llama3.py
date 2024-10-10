# This file was only used once to download Llama 3 from Hugging Face.
# To do so, we first asked Meta for the permissione, which required a couple of hours to get accepted.

import os

os.system("huggingface-cli login --token $HUGGINGFACE_TOKEN")
os.system("huggingface-cli download --local-dir .")


