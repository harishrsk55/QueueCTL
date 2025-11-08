from utils import load, save

dlq_file = "data/dlq.json"
dlq_lock = "data/dlq.lock"
jobs_file = "data/jobs.json"
jobs_lock = "data/jobs.lock"

def handle_dlq_list(args):
    dlq = load(dlq_file, dlq_lock)
    if not dlq:
        print("DLQ is empty.")
        return

    print(f"\n{'ID':<15} {'Command':<30} {'Error':<20}")
    print("-" * 70)
    for job in dlq:
        print(f"{job['id']:<15} {job['command']:<30} {job.get('error','N/A'):<20}")
    print()

def handle_dlq_retry(args):
    dlq = load(dlq_file, dlq_lock)
    queue = load(jobs_file, jobs_lock)

    job_id = args.job_id
    job = next((j for j in dlq if j["id"] == job_id), None)
    if not job:
        print(f"No job found in DLQ with ID '{job_id}'.")
        return

    job["status"] = "pending"
    job["attempts"] = 0
    job.pop("error", None)

    queue.append(job)
    dlq.remove(job)

    save(queue, jobs_file, jobs_lock)
    save(dlq, dlq_file, dlq_lock)
    print(f"Job '{job_id}' has been moved back to the main queue for retry.")
