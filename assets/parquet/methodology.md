# Parquet (PyArrow+Presto+Hive) methodology

## Basics

pyarrow 20.0.0
Presto Version: [presto-server-0.293-SNAPSHOT][presto]

## Setup

* Ingested every JSON log into single varchar column, and parsed them during search
* zstd(3) compression used
* This ingestion was done solely with PyArrow generating a parquet file

### Coordinator configuration
```
query.max-memory = 1GB
task.max-worker-threads = 1
task.concurrency = 1
native-execution-enabled = true
```

### Worker (native execution) configuration
```
task.max-drivers-per-task=1
```

## Data Structure
| line |
|------|
| {"msg": { "ts": 0, "status": "ok" }} |
| {"msg": { "ts": 1, "status": "error", "thread_num": 4, "backtrace": "" }} |
| ... |

### Searching

Get all error logs
```
SELECT * FROM table WHERE
json_extract_scalar(json_parse(line), 'msg.status') = "error";
```


[presto]: https://github.com/y-scope/presto/tree/ec3aedb239508ccd91891260ae89e111eb268761
