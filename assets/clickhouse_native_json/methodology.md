# ClickHouse methodology

**Version: [23.3.1.2823](https://hub.docker.com/layers/clickhouse/clickhouse-server/23.3.1.2823/images/sha256-b88fd8c71b64d3158751337557ff089ff7b0d1ebf81d9c4c7aa1f0b37a31ee64?context=explore)**

**File with Formatted Queries:** [Config File](/assets/clickhouse_native_json/config.yaml)

## Setup

### Docker   
We benchmark in one of ClickHouse’s provided docker images `clickhouse/clickhouse-server:latest`.

### Configuration  
We utilize ClickHouse’s new [native JSON](https://clickhouse.com/docs/interfaces/formats/JSON) support. ClickHouses native JSON enables interaction with the original JSON object instead of converting the JSON to a string. Key features are,

* Queries use cleaner dot syntax instead of the JSON\_VALUE functions.  
* SQL command uses FORMAT JSON  
* Table creation is single-column with column name json and type JSONAsObject

We start the ClickHouse server in daemon mode.

**Two key configuration files:**

[include/config.xml](/assets/clickhouse_native_json/include/config.xml)

```xml
<compression>  
    <case>  
        <method>zstd</method>    
        <level>3</level>  
    </case>  
</compression> 
<yandex>  
    <merge_tree>  
        <old_parts_lifetime>1</old_parts_lifetime>  
    </merge_tree>  
</yandex>
```
* compression: set to zstd(3)  
* old_parts_lifetime: old parts last for 1 second to allow direct `du` calculation

[include/users.xml](/assets/clickhouse_native_json/include/users.xml)

```xml
<date_time_input_format>best_effort</date_time_input_format>  
<enable_json_type>1</enable_json_type>
```
* date_time_input_format: read mongoDB datetime format flexibly  
* enable_json_type: enable native json

**Configuration Considerations:**  
We discuss below some of the configuration choices you have while using ClickHouse. We chose to use automatic columns and to use the timestamp in the various datasets as keys and ordered by that key. We chose to use timestamp because CLP utilizes the timestamp as a parameter and thought it might make the best comparison.

**Manual / automatic columns**  
Manual columns has a specialized schema for the MongoDB dataset, classifying each field into a "static" field (one in every json line) and a "dynamic" field (one that is not in every json line), and gives a data type and a column to each static field

Automatic columns has one 'json' column of type JSON that every log is ingested into, and works for all datasets unless keys or order_by is passed

**Keys**  
The primary key used for sorting. Is concatenated to order_by because ClickHouse databases must be ordered by the primary key. They are passed during table creation to `PRIMARY KEY`

**Order\_by**  
Additional columns to order by, passed during table creation to `ORDER BY`

**Launch & Shutdown:**  
On launch we execute ClickHouse’s entrypoint.sh to start ClickHouse in the background and poll ClickHouse until we receive a successful response to a simple query.

On shutdown, we simply send ClickHouse a stop command.

**Clearing Caches:**  
Before starting any queries we ask ClickHouse to drop its UNCOMPRESSED CACHE and MARK CACHE. We also flush the file system buffers and clear the filesystem caches. 