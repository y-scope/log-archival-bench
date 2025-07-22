# SparkSQL methodology

**Version:** [4.0.0](https://hub.docker.com/_/spark)

**File with Formatted Queries:** [Config File](/assets/sparksql/config.yaml)

## Setup

### Docker  
We use SparkSQL’s public `spark:4.0.0` base docker image and use the python `pyspark` library to interact with SparkSQL.

### Configuration 
Set "spark.sql.caseSensitive" to True

### Launch & Shutdown 
For this benchmark we ran SparkSQL as a cluster. On launch we start the master and 1 worker and wait for response on the correct ports before starting the benchmark. 

To shutdown SparkSQL we kill all running java processes with path `/opt/java/openjdk/bin/java` and wait for confirmation of closure on the correct ports.

### Clearing Caches  
SparkSQL doesn’t expose any caches for us to clear, but we flush the file system buffers and clear the filesystem caches. 
