# Gzip methodology

Ingestion stats only, no search  
**Version:** v1.10

## Setup

We use a publicly available docker image we provide for CLP as the base docker image to build on top of ([clp core ubuntu-jammy docker image](https://github.com/y-scope/clp/pkgs/container/clp%2Fclp-core-dependencies-x86-ubuntu-jammy)). We install `gzip` in this docker container using `apt-get`. 

We compress the data with `gzip` and compare the result to the decompressed data to gather the ingestion metrics.

Gzip does not have search functionality, so we do not have search metrics for this tool.

