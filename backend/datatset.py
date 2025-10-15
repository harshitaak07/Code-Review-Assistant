import os
import requests
from datasets import load_dataset
from bs4 import BeautifulSoup

LANGUAGES = ["python", "javascript", "java", "go", "php", "ruby"]
DATA_ROOT = "data/code_examples"
CHUNK_SIZE = 400  
SPLIT_CHUNKS = True  

def save_code_file(code: str, folder: str, filename: str):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

for lang in LANGUAGES:
    dataset = load_dataset("claudios/code_search_net", lang)
    lang_folder = os.path.join(DATA_ROOT, lang)
    os.makedirs(lang_folder, exist_ok=True)
    for split in dataset.keys():  
        split_folder = os.path.join(lang_folder, split)
        os.makedirs(split_folder, exist_ok=True)
        for i, item in enumerate(dataset[split]):
            code = item["code"]
            if not code:
                continue 
            docstring = item.get("docstring", "")
            full_code = code
            if docstring:
                full_code = f"# Docstring: {docstring}\n{code}"
            if SPLIT_CHUNKS:
                chunks = split_into_chunks(full_code)
                for j, chunk in enumerate(chunks):
                    filename = f"{split}_{i}_{j}.txt"
                    save_code_file(chunk, split_folder, filename)
            else:
                filename = f"{split}_{i}.txt"
                save_code_file(full_code, split_folder, filename)

STYLE_GUIDE_FOLDER = "data/style_guides"
os.makedirs(STYLE_GUIDE_FOLDER, exist_ok=True)

pep8_url = "https://peps.python.org/pep-0008/"
r = requests.get(pep8_url)
soup = BeautifulSoup(r.text, "html.parser")
pep8_text = soup.get_text(separator="\n")
with open(os.path.join(STYLE_GUIDE_FOLDER, "python_pep8.txt"), "w", encoding="utf-8") as f:
    f.write(pep8_text)

airbnb_url = "https://raw.githubusercontent.com/airbnb/javascript/master/README.md"
r = requests.get(airbnb_url)
with open(os.path.join(STYLE_GUIDE_FOLDER, "js_airbnb.txt"), "w", encoding="utf-8") as f:
    f.write(r.text)
