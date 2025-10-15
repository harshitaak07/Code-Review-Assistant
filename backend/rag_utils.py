"""
RAG Utilities for Code Review Assistant
Preprocessing:
    - Load datasets (docs, style guides, code examples)
    - Split into chunks
    - Generate embeddings
    - Store embeddings + metadata in FAISS

Runtime:
    - Embed user code snippet
    - Search top-k similar chunks in FAISS
    - Retrieve context
    - Feed code + context to LLM
"""

import os
from typing import List, Dict
import faiss
import pickle
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "codeparrot/code-search-net-embedding"
# microsoft/codebert-base
DATA_FOLDER = "data/"
FAISS_INDEX_FILE = "faiss_indexes/code_index.faiss"
METADATA_FILE = "faiss_indexes/metadata.pkl"
CHUNK_SIZE = 400
TOP_K = 5

model = SentenceTransformer(EMBEDDING_MODEL)

def load_data(data_folder: str = DATA_FOLDER) -> List[str]:
    all_texts = []
    for file_name in os.listdir(data_folder):
        file_path = os.path.join(data_folder, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                all_texts.append(f.read())
    return all_texts

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    embeddings = model.encode(chunks, show_progress_bar = True)
    return embeddings

def store_embeddings(embeddings: List[List[float]], chunks: List[str], index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE):
    dim = embeddings[0].shape[0] if hasattr(embeddings[0], 'shape') else len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    os.makedirs(os.path.dirname(index_file), exist_ok = True)
    faiss.write_index(index, index_file)
    with open(metadata_file, "wb") as f:
        pickle.dump(chunks, f)

def load_faiss_index(index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE):
    index = faiss.read_index(index_file)
    with open(metadata_file, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def embed_code_snippet(code_snippet: str) -> List[float]:
    embedding = model.encode([code_snippet])
    return embedding

def search_top_k_faiss(code_embedding, index, top_k=TOP_K) -> List[int]:
    D, I = index.search(code_embedding, top_k)
    return I[0].tolist()

def retrieve_context(top_k_indices: List[int], metadata: List[str]) -> str:
    context_chunks = [metadata[i] for i in top_k_indices]
    context = "\n\n".join(context_chunks)
    return context

if __name__ == "__main__":
    print("Loading datasets...")
    datasets = load_data()
    all_chunks = []
    for text in datasets:
        all_chunks.extend(split_into_chunks(text))
    print(f"Total chunks: {len(all_chunks)}")
    print("Generating embeddings...")
    embeddings = embed_chunks(all_chunks)
    print("Storing embeddings in FAISS...")
    store_embeddings(embeddings, all_chunks)
    print("Preprocessing done.")
    print("\nSimulating RAG retrieval for a user code snippet...")
    user_code = "def add(a, b): return a+b"
    index, metadata = load_faiss_index()
    user_embedding = embed_code_snippet(user_code)
    top_indices = search_top_k_faiss(user_embedding, index)
    context = retrieve_context(top_indices, metadata)
    print("Retrieved context for LLM:")
    print(context[:500], "...")  