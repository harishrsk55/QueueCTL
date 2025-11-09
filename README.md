# QueueCTL

**QueueCTL** is a lightweight CLI-based background job queue system in Python. It allows enqueuing jobs, running multiple worker processes, retrying failed jobs with exponential backoff, and maintaining a Dead Letter Queue (DLQ). All data is stored as JSON files in a dedicated `data/` folder.

---

## Setup Instructions

1. **Clone the repository:**

```
git clone https://github.com/harishrsk55/QueueCTL.git
cd QueueCTL
```

2. **Install required Python packages**
```
pip install -r requirements.txt
```

3. **Run the QueueCTL shell**
```
python queuectl.py
```

## Usage Examples
**Enqueue a job**
```
enqueue '{id: job1, command: "echo Hello"}'
```
**Output**\
Job added to the queue with job id: job1

---

**Start workers**
```
worker start --count 2
```
**Output**\
Starting 2 worker(s)...\
Workers started and running in background.\
PIDs: [12345, 12346]

---

**Stop workers**
```
worker stop
```
**Output**\
Stopped worker PID 12345\
Stopped worker PID 12346\
All workers stopped.

---

**Check queue and worker status**
```
status
```
**Output**\
Total Jobs: 3\
  Pending     : 1\
  In_progress : 0\
  Completed   : 2\
  Failed      : 0\
  Dead        : 0\
Active Workers: 2\
Worker PIDs: 12345, 12346

---

**List jobs**
```
list --state pending
```
**Output**
```
ID              State      Command
------------------------------------------------------------
job3            pending    python script.py
```

---

**List DLQ jobs**
```
dlq list
```
**Output**
```
ID              Command                       Error
----------------------------------------------------------------------
job2            python fail_script.py         RuntimeError
```

---

**Retry a job from DLQ**
```
dlq retry job2
```

**Output**\
Job 'job2' has been moved back to the main queue for retry.

---

**Configuration**
```
config set max-retries 5
config set base 3
```
```max-retries``` : Maximum retry attempts before moving to DLQ\
```base``` : Base delay (in seconds) for exponential backoff

## Architecture Overview
1. **Job Lifecycle**
```
pending -> in_progress -> completed
        \-> failed (if retries left) -> pending
        \-> dead (if retries exceeded) -> DLQ
```

2. **Worker Logic**
* Workers pick jobs atomically to prevent duplicates
* Retry failed jobs using exponential backoff
* Move jobs exceeding max retries to DLQ

3. **Data Persistence**
* JSON files in ```data/``` folder
  * ```jobs.json``` → main queue
  * ```dlq.json``` → dead letter queue
  * ```config.json``` → max retries, base delay
  * ```worker_pids.json``` → running worker PIDs
* All file operations are locked via FileLock for concurrency safety

4. **Assumptions**
* Only basic shell commands will be executed
* Worker processes run on the same machine

## Testing Instructions
1. **Enqueue sample jobs**
```
enqueue '{id: job1, command: "echo test1"}'
enqueue '{id: job2, command: "sleep 5"}'
```

2. **Start workers**
```
worker start --count 2
```

3. **Verify job execution**
* Confirmation received for completed jobs
* Failed jobs retried according to ```max-retries``` and ```base_delay```
* Jobs exceeding retries moved to DLQ

4. **Check status and list**
```
status
list --state completed
dlq list
```

5. **Retry DLQ jobs and verify they re-enter the main queue**
```
dlq retry job2
status
```

6. **Stop workers after testing**
```
worker stop
```

## Demo Video
[Google drive link](https://drive.google.com/file/d/1bAxgICy_tgg1EMNAHKOokKy6mZAQuC_v/view?usp=sharing)
