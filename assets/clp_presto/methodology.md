# Presto + CLP methodology

## Basics

Presto Version: [presto-server-0.293][presto]

Velox Version: [Velox][velox]

CLP Version: 0.4.0 (commit 5d4c6769c269a749e33679bc61974324dba612db)

## Setup

### clp-json
* put clp-json somewhere on the host and mount it using `mount_points` in `main.py`
* edit clp-config.yml
* run clp-json/sbin/start-clp.sh, then stop-clp.sh
* copy the database password under clp-json/etc/credentials.yml and paste in:
* * include/etc_coordinator/catalog/clp.properties (as clp.metadata-db-password)
* * main.py (as SQL_PASSWORD)
* run `curl -X GET http://localhost:8080/v1/info` after launching
* * put version info in `include/etc_worker/config.properties` as `presto.version`

### Dataset and Ingestion
* Renamed all keys within dataset that contained a ' ' or a '-' by encoding with base64
* Launched clp-json with sbin/start-clp.sh outside of container
* Ingested using clp-json/sbin/compress outside of container
``` bash
sbin/compress.sh --timestamp-key 't.\$date' ~/clp-bench/mongodb/mongod.log
```
> Caveat: ingestion data for this tool is still collected, although done in a unconstrained
environment, and therefore does not serve as a valid comparision
* assets/ingest.sh must still be called to correct metadata in sql

## Specifics

### Coordinator configuration
```
native-execution-enabled = true
```

[presto]: https://github.com/anlowee/presto/tree/faae543ae318f0289f5d0b537c5724e1b085a2fc
[velox]: https://github.com/anlowee/velox/tree/5a55969d5fd21bb4bcb53645b832344ff6bbd634

