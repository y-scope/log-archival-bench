# ClickHouse methodology

## Basics

Version: [23.3.1.2823][download]

## Setup

We start the ClickHouse server in daemon mode.

## Specifics

To store JSON records, we use [native json][native_json] in ClickHouse, eliminating the need
for preprocessing.

## Native JSON Changes
* Queries use cleaner dot syntax instead of the original JSON_VALUE functions.
* SQL command uses FORMAT JSON rather than FORMAT JSONAsString
* Table creation is single-column with column name json and type JSONAsObject

## Parameters

### manual columns / automatic columns
Manual columns has a specialized schema for the mongod dataset, classifying each field into a
"static" field (one in every json line) and a "dynamic" field (one that is not in every json line),
and gives a data type and a column to each static field

Automatic columns has one 'json' column of type JSON that every log is ingested into, and works for
all datasets unless keys or order_by is passed

### keys
The primary key used for sorting. Is concatenated to order_by because clickhouse databases must be
ordered by the primary key. They are passed during table creation to `PRIMARY KEY`

### order_by
Additional columns to order by, passed during table creation to `ORDER BY`

[download]: https://hub.docker.com/layers/clickhouse/clickhouse-server/23.3.1.2823/images/sha256-b88fd8c71b64d3158751337557ff089ff7b0d1ebf81d9c4c7aa1f0b37a31ee64?context=explore
[direct_io]: https://clickhouse.com/docs/en/operations/settings/settings#min_bytes_to_use_direct_io
[jsonasstring]: https://clickhouse.com/docs/en/interfaces/formats#jsonasstring
[native_json]: https://clickhouse.com/docs/interfaces/formats/JSON
