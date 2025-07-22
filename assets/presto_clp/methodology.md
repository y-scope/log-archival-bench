# Presto + CLP methodology

**Version:**   
Presto Version: [Presto](https://github.com/y-scope/presto.git)  
Velox Version: [Velox](https://github.com/y-scope/velox.git)  
CLP Version: [0.4.0](https://github.com/y-scope/clp/releases/tag/v0.4.0)

**File with Formatted Queries:** [Config File](/assets/presto_clp/config.yaml)

## Setup

### Docker  
We build on top of one of Presto’s provided docker images, `presto/prestissimo-dependency: ubuntu-22.04-presto-0.293`. We install the version of Presto, Velox, and CLP linked above. This version of Presto is modified with a connector for CLP. You can find the exact commit we are using for Presto and Velox in the [Dockerfile](/assets/presto_clp/Dockerfile)

### Configuration:

#### CLP  
We use the clp-s variant of CLP.

Build clp-s using the following command after downloading the pre-built clp-json tar.gz, found at the page linked above, and installing core dependencies.  
- run `task clp-json-pkg-tar`
   
You’ll need to unzip the subsequent `clp-json-{version}-dev.tar.gz file`. This can go in your home directory or we’ll explain below how to update [main.py](/assets/presto_clp/main.py). We’ll refer to the unzipped directory as `clp-json` in the following instructions.

* Put `clp-json` somewhere on the host and mount it by modifying  `CLP_PRESTO_HOST_STORAGE` in [main.py](/assets/presto_clp/main.py)  
* Run `clp-json/sbin/start-clp.sh`, then `clp-json/sbin/stop-clp.sh` to populate `clp-json/etc/credentials.yml`.  
* Copy the `database.password` found in `clp-json/etc/credentials.yml` and update the value in:  
  * [include/etc_coordinator/catalog/clp.properties](/assets/presto_clp/include/etc_coordinator/catalog/clp.properties) (as clp.metadata-db-password)  
    * Ex. `clp.metadata-db-password=<password>`  
  * [main.py](/assets/presto_clp/main.py) (as SQL_PASSWORD)  
    * Ex. `SQL_PASSWORD = "<password>"`  
* Run `curl -X GET http://localhost:8080/v1/info` after launching LogArchivalBench  
  * Update version info in [`include/etc_worker/config.properties`](/assets/presto_clp/include/etc_worker/config.properties) (as `presto.version`)  
    * Ex. `presto.version=<version info>`

#### Dataset and Ingestion

* Renamed all keys within dataset that contained a ' ' or a '-' by encoding with base64  
  * We provide [data/cleankeys.py](/data/cleankeys.py) that you can use to clean the datasets. You can read how to manage the datasets in [README.md](/README.md). 
* Note unlike other tools, [main.py](/assets/presto_clp/main.py) launches `clp-s` with `clp-json/sbin/start-clp.sh` outside of container and dataset is ingested using `clp-json/sbin/compress.sh` outside of container.

**Caveat**: Ingestion data for this tool is still collected, although, unlike other tools, our methodology doesn’t allow it to be constrained to four CPU cores. This is because the CLP package starts multiple docker containers, although we could restrict each container to 4 cores, we could constrain them all to the same 4 cores. For fairness we don’t display the values in our interactive graphs. The compression ratio will be the same as running CLP, but the ingestion speed and memory usage will differ.

#### Presto Coordinator configuration

We set the following in [include/etc_coordinator/config.properties](/assets/presto_clp/include/etc_coordinator/config.properties)  
*native-execution-enabled \= true*

**Launch & Shutdown:**  
On launch we start the Presto coordinator and one presto worker running in the background. We also start the CLP package off running in the background to listen for the ingestion commands.

On shutdown we kill the running java processes and the presto server and wait for its open ports to close. We then shut down the CLP package using the provided `stop-clp.sh` script. 

**Clearing Caches:**  
CLP doesn’t maintain any internal caches for us to clear, so before each query we flush the file system buffers and clear the filesystem caches. 