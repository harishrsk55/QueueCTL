import argparse
import shlex
from enqueue import enqueue
from worker_cmds import start_workers, stop_workers
from status import status
from list_cmds import handle_list
from dlq import handle_dlq_list, handle_dlq_retry
from config_cmds import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="queuectl", description="QueueCTL: Background Job Queue Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Enqueue
    eparser = subparsers.add_parser("enqueue", help="Add a new job to the queue")
    eparser.add_argument("job", help='Job to enqueue. Example: {id: job1, command: "echo hello"}')
    eparser.set_defaults(func=enqueue)

    # Worker
    wparser = subparsers.add_parser("worker", help="Manage worker processes")
    wsub = wparser.add_subparsers(dest="action")

    start_parser = wsub.add_parser("start", help="Start worker processes")
    start_parser.add_argument("--count", type=int, default=1, help="Number of workers to start")
    start_parser.set_defaults(func=start_workers)

    stop_parser = wsub.add_parser("stop", help="Stop all running workers")
    stop_parser.set_defaults(func=stop_workers)

    # Status
    sparser = subparsers.add_parser("status", help="Show queue and worker status")
    sparser.set_defaults(func=status)

    # List
    lparser = subparsers.add_parser("list", help="List jobs in queue or DLQ")
    lparser.add_argument("--state", choices=["pending","processing","completed","failed","dead"], help="Filter jobs by state")
    lparser.set_defaults(func=handle_list)

    # DLQ
    dparser = subparsers.add_parser("dlq", help="DLQ commands")
    dsub = dparser.add_subparsers(dest="dlq_cmd")

    dlq_list_parser = dsub.add_parser("list", help="List all DLQ jobs")
    dlq_list_parser.set_defaults(func=handle_dlq_list)

    dlq_retry_parser = dsub.add_parser("retry", help="Retry a DLQ job by ID")
    dlq_retry_parser.add_argument("job_id", help="Job ID to retry")
    dlq_retry_parser.set_defaults(func=handle_dlq_retry)

    # Config
    cparser = subparsers.add_parser("config", help="Set queue configuration")
    cparser.add_argument("action", choices=["set"], help="Action to perform")
    cparser.add_argument("dest", choices=["max-retries","base"], help="Configuration key to update")
    cparser.add_argument("count", type=int, help="Value to set")
    cparser.set_defaults(func=config)

    print("Welcome to QueueCTL shell. Type 'exit' to quit.")
    while True:
        try:
            command = input("queuectl> ").strip()
            if command.lower() in ["exit","quit"]:
                print("\nExiting QueueCTL shell.")
                break
            if not command:
                continue
            args = parser.parse_args(shlex.split(command))
            args.func(args)
        except SystemExit:
            continue
        except KeyboardInterrupt:
            print("\nExiting QueueCTL shell.")
            break
        except Exception as e:
            print(f"Error: {e}")
