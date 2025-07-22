# Presto + Parquet(PyArrow) + Velox(Hive) methodology
**Version:**   
Pyarrow \- [20.0.0](https://arrow.apache.org/docs/python/install.html)   
Presto \-  [presto-server-0.293-SNAPSHOT](https://github.com/anlowee/presto/tree/faae543ae318f0289f5d0b537c5724e1b085a2fc)   
Velox \- [Velox](https://github.com/anlowee/velox/tree/5a55969d5fd21bb4bcb53645b832344ff6bbd634)

**File with Formatted Queries:** [Config File](/assets/parquet/config.yaml)

## Setup

### Docker   
We build on top of one of Presto’s provided docker images, `presto/prestissimo-dependency: ubuntu-22.04`. We install the version of `Presto`, `Velox`, and `Pyarrow` linked above.

### Configuration
We test Parquet in two configurations, which differ mainly by the format JSON objects are processed into. One methodology keeps the JSON object whole and treats it as a string. The other methodology breaks the JSON object into a table of column values. Below we’ll show an example of the JSON processing based on the following example JSON objects as well as examples of how the queries change with the format of the JSON.

We used a similar setup to the one described here, [link](https://prestodb.io/blog/2024/06/24/diving-into-the-presto-native-c-query-engine-presto-2-0/). We made some changes, choosing to use only one Prestissimo instance and connecting to a local database instead of utilizing S3.

**Original data**
```json
{  
 "msg": {  
   "ts": 0,  
   "status": "ok"  
 }  
}

{  
 "msg": {  
   "ts": 1,  
   "status": "error",  
   "thread_num": 4,  
   "backtrace": ""  
 }  
}
```

When configuring the Presto coordinator we set the following option in 
* [include/etc_coordinator/config.properties](/assets/parquet/include/etc_coordinator/config.properties)  
  * `native-execution-enabled = true`

#### JSON String

**Configuration Details:**

* Ingested every JSON log into single varchar column, and parsed them during search  
* zstd(3) compression used  
* This ingestion was done solely with PyArrow generating a parquet file

**Data Structure**

| **String Value** |
| ----- |
| `{"msg": { "ts": 0, "status": "ok" }}` |
| `{"msg": { "ts": 1, "status": "error", "thread\_num": 4, "backtrace": "" }}`  |

**Example Query**  
```sql
SELECT * FROM bench_table WHERE 
json_extract_scalar(json_parse(line), 'msg.status') = "error";
```

#### Pairwise Arrays

**Configuration Details:**

* Parsed every JSON log recursively into array columns. `<variable type>`_columns and
`<variable type>`_values  
* Dot syntax used for child objects  
* zstd(3) compression used  
* This ingestion was done solely with PyArrow generating a parquet file

**Data structure**

| string_columns | string_values | int_columns | int_values |
|-|-|-|-|
| ["msg.status"] | ["ok"] | ["msg.ts"] | [0] |
| ["msg.status", "msg.backtrace"] | ["error", ""] | ["msg.ts", "msg.thread_num"] | [1, 4] |

**Example Query**
```sql
SELECT * FROM table WHERE  
array_position(string_columns, 'msg.status') > 0   
AND element_at(  
  string_values,   
  array_position(string_columns, 'msg.status')  
) = 'error';
```

### Launch & Shutdown 
On launch we start the Presto coordinator and one presto worker running in the background. 

On shutdown we kill the running java processes and the presto server and wait for its open ports to close. 

### Clearing Caches
Before each query we flush the file system buffers and clear the filesystem caches. We also send requests to Hive to clear both its memory and SSD caches.
