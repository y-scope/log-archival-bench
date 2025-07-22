# Gzip methodology

Ingestion stats only, no search

**Version:** v1.10

## Setup

The benchmark layers on the public [**CLP core Ubuntu-Jammy**](https://github.com/y-scope/clp/pkgs/container/clp%2Fclp-core-dependencies-x86-ubuntu-jammy) docker image, installs `gzip` (v1.10) via `apt-get`, compresses the data with `gzip` and compare the result to the decompressed data to gather the ingestion metrics.

Gzip does not have search functionality, so we do not have search metrics for this tool.