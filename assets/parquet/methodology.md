# Parquet (PyArrow+Presto+Hive) methodology

## Basics

pyarrow 20.0.0
Presto Version: [presto-server-0.293-SNAPSHOT][presto]

## Setup

### Json String
* Ingested every JSON log into single varchar column, and parsed them during search
* zstd(3) compression used
* This ingestion was done solely with PyArrow generating a parquet file

### Columns Values
* Parsed every JSON log recusively into array columns <variable type>_columns and
<variable type>_values
* Dot syntax used for child objects
* zstd(3) compression used
* This ingestion was done solely with PyArrow generating a parquet file


### Coordinator configuration
```
native-execution-enabled = true
```

## Data Structure

Original data:
```
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


### Json String

| line |
|------|
| {"msg": { "ts": 0, "status": "ok" }} |
| {"msg": { "ts": 1, "status": "error", "thread_num": 4, "backtrace": "" }} |
| ... |

### Columns Values
Compressed data structure:
| string_columns | string_values | int_columns | int_values |
|-|-|-|-|
| ["msg.status"] | ["ok"] | ["msg.ts"] | [0] |
| ["msg.status", "msg.backtrace"] | ["error", ""] | ["msg.ts", "msg.thread_num"] | [1, 4] |




## Searching

### Json String

```
SELECT * FROM table WHERE
json_extract_scalar(json_parse(line), 'msg.status') = "error";
```

### Columns Values

```
SELECT * FROM table WHERE
array_position(string_columns, 'msg.status') > 0 
AND element_at(
  string_values, 
  array_position(string_columns, 'msg.status')
) = 'error';
```

[presto]: https://github.com/y-scope/presto/tree/ec3aedb239508ccd91891260ae89e111eb268761
