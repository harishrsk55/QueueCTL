import re
import time, json
from utils import load, save
from config_cmds import load_config

file = "data/jobs.json"
file_lock = "data/jobs.lock"

def enqueue_parse(job_str):
    fix = re.sub(r'([{,]\s*)(\w+)\s*:', r'\1"\2":', job_str)
    fix = re.sub(r':\s*([\w\s./-]+)([,}])', r': "\1"\2', fix)
    try:
        return json.loads(fix)
    except json.JSONDecodeError:
        raise ValueError("Invalid job format. Use valid JSON pairs")

def enqueue_validation(job):
    required_keys = {"id", "command"}
    missing = required_keys - job.keys()
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")
    return job

def enqueue(args):
    job = enqueue_parse(args.job)
    job = enqueue_validation(job)
    jobs = load(file, file_lock)
    cfg = load_config()

    existing_ids = {j["id"] for j in jobs}
    if job["id"] in existing_ids:
        print(f"Job with ID '{job['id']}' already exists. Use a unique ID.")
        return

    job["status"] = "pending"
    job["attempts"] = 0
    job["max_retries"] = cfg.get("max_retries", 3)
    job["created_at"] = time.time()
    job["updated_at"] = time.time()
    jobs.append(job)
    save(jobs, file, file_lock)
    print(f"Job added to the queue with job id: {job['id']}")
