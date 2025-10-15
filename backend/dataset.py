import os
import requests
from datasets import load_dataset
from bs4 import BeautifulSoup
import pandas as pd

LANGUAGES = ["python", "javascript"]
DATA_ROOT = "data/code_examples"
BUG_FIX_ROOT = "data/bug_fixes"
CHUNK_SIZE = 400
SPLIT_CHUNKS = True
MAX_SAMPLES = 5000       
MAX_TSSB_FILES = 5000  
SPLIT_CHUNKS = False      

STYLE_GUIDE_FOLDER = "data/style_guides"
TSSB3M_FOLDER = os.path.join(BUG_FIX_ROOT, "tssb3m_python")

def save_code_file(code: str, folder: str, filename: str):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def process_tssb3m():
    files = [f for f in os.listdir(TSSB3M_FOLDER) if f.endswith(".py")]
    for i, file in enumerate(files):
        if i >= MAX_TSSB_FILES: 
            break
        file_path = os.path.join(TSSB3M_FOLDER, file)
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        filename = f"tssb3m_{i}.txt"
        save_code_file(code, TSSB3M_FOLDER, filename)

def process_codesearchnet():
    for lang in LANGUAGES:
        dataset = load_dataset("claudios/code_search_net", lang)
        lang_folder = os.path.join(DATA_ROOT, lang)
        os.makedirs(lang_folder, exist_ok=True)
        for split in dataset.keys():
            data_list = []
            for i, item in enumerate(dataset[split]):
                if i >= MAX_SAMPLES:
                    break
                code = item.get("func_code_string", "")
                docstring = item.get("func_documentation_string", "")
                if not code and not docstring:
                    continue
                full_code = f"# Docstring: {docstring}\n{code}" if docstring else code
                data_list.append({"code": full_code, "split": split, "language": lang})
            df = pd.DataFrame(data_list)
            df.to_parquet(os.path.join(lang_folder, f"{split}.parquet"), index=False)
            print(f"Saved {len(df)} samples to {lang_folder}/{split}.parquet")



def download_style_guides():
    os.makedirs(STYLE_GUIDE_FOLDER, exist_ok=True)
    pep8_url = "https://peps.python.org/pep-0008/"
    r = requests.get(pep8_url)
    soup = BeautifulSoup(r.text, "html.parser")
    pep8_text = soup.get_text(separator="\n")
    save_code_file(pep8_text, STYLE_GUIDE_FOLDER, "python_pep8.txt")
    airbnb_url = "https://raw.githubusercontent.com/airbnb/javascript/master/README.md"
    r = requests.get(airbnb_url)
    save_code_file(r.text, STYLE_GUIDE_FOLDER, "js_airbnb.txt")

if __name__ == "__main__":
    process_codesearchnet()
    process_tssb3m()
    download_style_guides()
    print("All datasets processed successfully!")