# ClickHouse methodology

**Version: [25.6](https://hub.docker.com/layers/clickhouse/clickhouse-server/25.6/images/sha256-77ff1f2054e27bec1b4c5eccbf701b63f8409831fea71f162ae2f25872dee1f4)**

**File with Formatted Queries:** [Config File](/assets/clickhouse/config.yaml)

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

[include/config.xml](/assets/clickhouse/include/config.xml)

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

[include/users.xml](/assets/clickhouse/include/users.xml)

```xml
<date_time_input_format>best_effort</date_time_input_format>  
<enable_json_type>1</enable_json_type>
```
* date_time_input_format: read mongoDB datetime format flexibly  
* enable_json_type: enable native json

**Configuration Considerations:**  
We discuss below some of the configuration choices you have while using ClickHouse. We chose to use automatic columns and to use the timestamp in the various datasets as keys and ordered by that key. We chose to use timestamp because CLP utilizes the timestamp as a parameter and thought it might make the best comparison.

**Manual / automatic columns**  
Manual columns have a specialized schema for the MongoDB dataset, classifying each field into a *static* field (present in every JSON line) and a *dynamic* field (present only in some lines), and assigning a data type and column to each static field.

Automatic columns has one 'json' column of type JSON that every log is ingested into, and works for all datasets unless keys or order_by is passed

**Keys**  
The *keys* form the primary key used for sorting. They are concatenated with the *order_by* columns because ClickHouse tables must be ordered by the primary key. Both are supplied in the `PRIMARY KEY` clause during table creation.

**Order_by**  
Additional columns to order by, passed during table creation to `ORDER BY`

**Launch & Shutdown:**  
On launch we execute ClickHouse’s entrypoint.sh to start ClickHouse in the background and poll ClickHouse until we receive a successful response to a simple query.

On shutdown, we simply send ClickHouse a stop command.

**Clearing Caches:**  
Before starting any queries we ask ClickHouse to drop its UNCOMPRESSED CACHE and MARK CACHE. We also flush the file system buffers and clear the filesystem caches. 
