from rq.job import Job
import redis
import time
from backend.worker import process_submission

redis_conn = redis.Redis(host='localhost', port=6379)
QUEUE_KEY = "rq:queue:code-review"

print("Windows-safe worker started, polling queue:", QUEUE_KEY)

while True:
    job_id = redis_conn.lpop(QUEUE_KEY)
    if job_id:
        print(f"Got a job from Redis queue! ID = {job_id}")
        try:
            job_id = job_id.decode("utf-8") if isinstance(job_id, bytes) else job_id
            job = Job.fetch(job_id, connection=redis_conn)
            args = job.args or []
            kwargs = job.kwargs or {}
            result = process_submission(*args, **kwargs)
            print("Job finished successfully:", result)
            job.meta["status"] = "completed"
            job.save_meta()
        except Exception as e:
            print("Error processing job:", e)
    else:
        time.sleep(1)
