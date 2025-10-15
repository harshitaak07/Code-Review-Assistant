import redis
from rq import Queue
from backend import rag_utils, llm_utils, s3_utils
import sqlite3
import json
import datetime

DB_FILE = "db.sqlite"

redis_conn = redis.Redis(host='localhost', port=6379)
queue = Queue('code-review', connection=redis_conn)

def process_submission(submission_id: int, code: str):
    user_embedding = rag_utils.embed_code_snippet(code)
    index, metadata = rag_utils.load_faiss_index()
    top_indices = rag_utils.search_top_k_faiss(user_embedding, index)
    context = rag_utils.retrieve_context(top_indices, metadata)
    rag_s3_key = s3_utils.upload_text(context, f"rag_cache/submission_{submission_id}.txt")
    feedback = llm_utils.generate_feedback(code, context)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO feedback (submission_id, feedback_json, rag_s3_key) VALUES (?, ?, ?)",
        (submission_id, json.dumps(feedback), rag_s3_key)
    )
    conn.commit()
    conn.close()
    return {"submission_id": submission_id, "feedback": feedback}

