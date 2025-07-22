# Zstandard methodology

Ingestion stats only, no search  
**Version:** v1.4.9

## Setup

We use a publicly available docker image we provide for CLP as the base docker image to build on top of ([clp core ubuntu-jammy docker image](https://github.com/y-scope/clp/pkgs/container/clp%2Fclp-core-dependencies-x86-ubuntu-jammy)). We install `zstd` in this docker container using `apt-get`. 

We compress the data with zstd compression level configured to 3 and compare to the decompressed data to gather the ingestion metrics.

Zstd does not have search functionality, so we do not have search metrics for this tool.

