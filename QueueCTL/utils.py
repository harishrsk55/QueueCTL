import os
import json
from filelock import FileLock

# Generic file load with locking
def load(file, lock_file):
    if not os.path.exists(file):
        return []
    with FileLock(lock_file):
        with open(file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"{file} is corrupted. Resetting.")
                return []

# Generic file save with locking
def save(data, file, lock_file):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with FileLock(lock_file):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
