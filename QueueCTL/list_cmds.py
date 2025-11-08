from utils import load

file = "data/jobs.json"
dlq_file = "data/dlq.json"

def handle_list(args):
    d = load(dlq_file, "data/dlq.lock")
    j = load(file, "data/jobs.lock")
    queue = d + j

    filtered = [job for job in queue if job["status"] == args.state] if args.state else queue
    if not filtered:
        print(f"No jobs found{f' with state {args.state}' if args.state else ''}.")
        return

    print(f"\n{'ID':<15} {'State':<10} {'Command':<30}")
    print("-" * 60)
    for job in filtered:
        print(f"{job['id']:<15} {job['status']:<10} {job['command']:<30}")
    print()
