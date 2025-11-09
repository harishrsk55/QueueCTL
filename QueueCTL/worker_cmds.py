import time
import subprocess
from multiprocessing import Process, Lock
from utils import load, save
from config_cmds import load_config

# File paths
file = "data/jobs.json"
file_lock = "data/jobs.lock"
dlq_file = "data/dlq.json"
dlq_lock = "data/dlq.lock"
worker_pids_file = "data/worker_pids.json"
worker_pids_lock = "data/worker_pids.lock"

# Move job to DLQ safely
def move_to_dlq(job):
    dead = load(dlq_file, dlq_lock)
    # Ensure job is not already in DLQ
    if not any(j["id"] == job["id"] for j in dead):
        dead.append(job)
        save(dead, dlq_file, dlq_lock)

# Run the shell command
def run(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error while running job: {e}")
        return False

# Worker process
def worker():
    while True:
        job = None

        # 1️⃣ Pick a job atomically inside the lock
        with Lock():
            jobs = load(file, file_lock)
            for j in jobs:
                if j["status"] in ("pending", "failed"):
                    job = j
                    j["status"] = "in_progress"
                    j["updated_at"] = time.time()
                    save(jobs, file, file_lock)
                    break  # Only one job picked per lock

        if not job:
            # No pending jobs, sleep and retry
            time.sleep(2)
            continue

        # 2️⃣ Run job outside the lock
        print(f"Executing job: {job['id']} => {job['command']}")
        success = run(job["command"])

        # 3️⃣ Update job status inside the lock
        with Lock():
            jobs = load(file, file_lock)
            for j in jobs:
                if j["id"] == job["id"]:
                    if success:
                        print(f"Job succeeded: {j['id']}")
                        j["status"] = "completed"
                        j["updated_at"] = time.time()
                        # Remove completed job from queue
                        #jobs = [x for x in jobs if x["id"] != j["id"]]
                    else:
                        j["attempts"] += 1
                        j["updated_at"] = time.time()
                        if j["attempts"] >= j["max_retries"]:
                            print(f"Job {j['id']} moved to DLQ after {j['attempts']} attempts.")
                            j["status"] = "dead"
                            move_to_dlq(j)
                            jobs = [x for x in jobs if x["id"] != j["id"]]
                        else:
                            cfg = load_config()
                            base_delay = cfg.get("base_delay", 2)
                            delay = base_delay ** j["attempts"]
                            j["status"] = "failed"
                            print(f"Retrying job {j['id']} after {delay}s (Attempt {j['attempts']})")
                            save(jobs, file, file_lock)
                            time.sleep(delay)
                    break
            save(jobs, file, file_lock)

        # Small delay before next iteration
        time.sleep(1)

# Start multiple workers
def start_workers(args):
    count = args.count or 1
    processes = []

    print(f"Starting {count} worker(s)...")
    for _ in range(count):
        p = Process(target=worker)
        p.start()
        processes.append(p)

    # Save worker PIDs
    save([p.pid for p in processes], worker_pids_file, worker_pids_lock)
    print("Workers started and running in background.")
    print(f"PIDs: {[p.pid for p in processes]}")

# Stop all workers
def stop_workers(args):
    import os
    import subprocess

    if not os.path.exists(worker_pids_file):
        print("No running workers found.")
        return

    pids = load(worker_pids_file, worker_pids_lock)
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Stopped worker PID {pid}")
        except ProcessLookupError:
            print(f"Worker PID {pid} not found (already stopped).")
    os.remove(worker_pids_file)
    print("All workers stopped.")

