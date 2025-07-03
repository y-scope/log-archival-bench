# Openobserve methodology

> Note: Maybe because the ingestion is being done through a HTTP interface, some characters in keys
in the JSON doesn't work. This causes no output in several alternate test cases. A possible solution
is to base64 (or hash) each key

## Basics

> Note: running queries immediately after a reset causes errors since reset returns when deleting
the stream but the stream still shows up undeleted for an amount of time

Version 0.15.0-rc1
https://gallery.ecr.aws/zinclabs/openobserve

## Setup

* Setting the openobserve data location
* Starting the openobserve daemon

## Specifics

Ingestion is done in 50000 line batches through an HTTP API: the software is designed for streams
of data, not compressing large amounts

Searching is similarly done through an HTTP API in pages of 1000 due to maximum number of returned
rows

The size of /home/data/openobserve/stream/files/default/logs is used to measure the compressed size,
as openobserve does not seem to offer an API for querying this information. The size of this folder
after ingesting the same dataset seems to be fairly consistent
