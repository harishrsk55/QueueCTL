from utils import load
import os

file = "data/jobs.json"
dlq_file = "data/dlq.json"
worker_pids_file = "data/worker_pids.json"

def status(args):
    jobs = load(file, "data/jobs.lock")
    dead = load(dlq_file, "data/dlq.lock")
    jobs = jobs + dead
    total_jobs = len(jobs)

    state_counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0, "dead": 0}
    for job in jobs:
        state = job.get("status", "unknown")
        if state in state_counts:
            state_counts[state] += 1

    active_pids = []
    if os.path.exists(worker_pids_file):
        active_pids = load(worker_pids_file, "data/worker_pids.lock")

    print("\n===== QueueCTL Status =====")
    print(f"Total Jobs: {total_jobs}")
    for state, count in state_counts.items():
        print(f"  {state.capitalize():<12}: {count}")
    print("---------------------------")
    if active_pids:
        print(f"Active Workers: {len(active_pids)}")
        print("Worker PIDs:", ", ".join(map(str, active_pids)))
    else:
        print("No active workers.")
    print("===========================\n")
