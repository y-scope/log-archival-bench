# Elasticsearch methodology

**Version:** [9.0.3](https://www.elastic.co/downloads/past-releases/elasticsearch-9-0-3)

**File with Formatted Queries:** [Config File](/assets/elasticsearch/config.yaml)

## Setup

### Docker   
We use a publicly available docker image we provide for CLP as the base docker image to build on top of ([clp core ubuntu-jammy docker image](https://github.com/y-scope/clp/pkgs/container/clp%2Fclp-core-dependencies-x86-ubuntu-jammy)). We install `Elasticsearch` in this docker container using `apt-get` and install the corresponding version of the elasticsearch python library using `pip3`.

### Configuration  
We deploy [Elasticsearch](https://www.elastic.co/downloads/elasticsearch) in a single-node configuration.

We disable the [xpack](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-settings.html) security feature. We use Elasticsearch's Python package for data ingestion and search operations.

Some preprocessing is necessary to make the dataset searchable in Elasticsearch. For more details, refer to the `traverse_data` function in [ingest.py](/assets/elasticsearch/ingest.py). This process generally involves reorganizing specific fields, moving them into outer or inner objects to ensure proper query functionality.

We use the [logs data stream](https://www.elastic.co/docs/manage-data/data-store/data-streams/logs-data-stream) which is optimized for timestamped logs

### Launch & Shutdown 
On launch the benchmark framework calls the [launch.sh](/assets/elasticsearch/launch.sh) script. This script automates the configuration of an Elasticsearch instance by modifying its settings to change the HTTP port, disable security features, and ensure it runs in single-node mode. It also updates the `elasticsearch` user settings to allow login and starts the Elasticsearch service in the background.

On shutdown, we `pkill` all Java processes.

### Clearing Caches  
Before starting any of the querying benchmarks, we use elasticsearch's built in function to clear its indice cache. We also flush the file system buffers and clear the filesystem caches. 
