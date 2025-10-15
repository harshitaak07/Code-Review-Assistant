import os
import pickle
from typing import List

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "microsoft/codebert-base"
DATA_FOLDER = "data/"
FAISS_INDEX_FILE = "faiss_indexes/code_index.faiss"
METADATA_FILE = "faiss_indexes/metadata.pkl"

CHUNK_SIZE = 400
TOP_K = 5
BATCH_SIZE = 256
MAX_BATCHES = 10

model = SentenceTransformer(EMBEDDING_MODEL)

def load_data(data_folder: str = DATA_FOLDER) -> List[str]:
    all_texts = []
    for root, _, files in os.walk(data_folder):
        for f in files:
            file_path = os.path.join(root, f)
            if f.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as file:
                    all_texts.append(file.read())
            elif f.endswith(".parquet"):
                df = pd.read_parquet(file_path)
                all_texts.extend(df["code"].tolist())
    return all_texts

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def load_or_create_index(index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE):
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
        with open(metadata_file, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = None
        metadata = []
    return index, metadata

def save_index(index, metadata, index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE):
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    faiss.write_index(index, index_file)
    with open(metadata_file, "wb") as f:
        pickle.dump(metadata, f)

def embed_and_store(chunks: List[str], batch_size: int = BATCH_SIZE, max_batches: int = MAX_BATCHES):
    index, metadata = load_or_create_index()
    for i in range(0, len(chunks), batch_size):
        batch_number = i // batch_size
        if batch_number >= max_batches:
            break
        batch = chunks[i:i + batch_size]
        batch_emb = np.array(model.encode(batch, show_progress_bar=True)).astype("float32")
        if index is None:
            dim = batch_emb.shape[1]
            index = faiss.IndexFlatL2(dim)
        index.add(batch_emb)
        metadata.extend(batch)
        save_index(index, metadata)
        print(f"Saved batch {batch_number + 1} ({len(batch)} embeddings)")

def embed_code_snippet(code_snippet: str):
    return np.array(model.encode([code_snippet])).astype("float32")

def search_top_k_faiss(code_embedding, index, top_k=TOP_K) -> List[int]:
    D, I = index.search(code_embedding, top_k)
    return I[0].tolist()

def retrieve_context(indices: List[int], metadata: List[str]) -> str:
    return "\n\n".join([metadata[i] for i in indices])

def inspect_faiss(index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE, n=5):
    index, metadata = load_or_create_index(index_file, metadata_file)
    print("Number of vectors in FAISS:", index.ntotal)
    print(f"First {n} metadata entries:")
    for i, text in enumerate(metadata[:n]):
        print(f"--- {i} ---\n{text[:200]}...\n")

if __name__ == "__main__":
    datasets = load_data()
    all_chunks = [chunk for text in datasets for chunk in split_into_chunks(text)]
    print(f"Total chunks: {len(all_chunks)}")
    embed_and_store(all_chunks)
    inspect_faiss(n=3)
    user_code = "def add(a, b): return a+b"
    index, metadata = load_or_create_index()
    user_emb = embed_code_snippet(user_code)
    top_indices = search_top_k_faiss(user_emb, index)
    context = retrieve_context(top_indices, metadata)
    print("Retrieved context for LLM:")
    print(context[:500], "...")