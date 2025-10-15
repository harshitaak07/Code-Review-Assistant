import datetime
import json
import sqlite3
from flask import Flask, request, jsonify
from rq import Queue
from redis import Redis

from backend import llm_utils, rag_utils, s3_utils
from backend.worker import process_submission

redis_conn = Redis()
queue = Queue("code-review", connection=redis_conn)
app = Flask(__name__)
submissions = {}
index, metadata = rag_utils.load_or_create_index()
DB_FILE = r"backend\db.sqlite"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id INTEGER PRIMARY KEY,
            s3_key TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            submission_id INTEGER PRIMARY KEY,
            feedback_json TEXT,
            rag_s3_key TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

import hashlib

@app.route('/submit-code', methods=['POST'])
def submit_code():
    data = request.get_json()
    code_snippet = data.get('code')
    if not code_snippet:
        return jsonify({"error": "No code provided"}), 400
    code_hash = hashlib.sha256(code_snippet.encode("utf-8")).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT submission_id FROM submissions WHERE code_hash = ?", (code_hash,))
    row = c.fetchone()
    if row:
        submission_id = row[0]
        conn.close()
    c.execute("SELECT MAX(submission_id) FROM submissions")
    row = c.fetchone()
    submission_id = (row[0] or 0) + 1
    s3_key = s3_utils.upload_text(code_snippet, f"submissions/{submission_id}.py")
    timestamp = datetime.datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO submissions (submission_id, s3_key, timestamp, code_hash) VALUES (?, ?, ?, ?)",
        (submission_id, s3_key, timestamp, code_hash)
    )
    conn.commit()
    conn.close()
    queue.enqueue(process_submission, submission_id, code_snippet)
    return jsonify({"submission_id": submission_id, "status": "queued"})


@app.route('/get-feedback/<int:submission_id>', methods=['GET'])
def get_feedback(submission_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT feedback_json FROM feedback WHERE submission_id = ?", (submission_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"status": "processing"}), 202
    feedback = json.loads(row[0])
    return jsonify({"submission_id": submission_id, "status": "done", "feedback": feedback})

if __name__ == '__main__':
    app.run(debug=True)