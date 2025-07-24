# Zstandard methodology

Ingestion stats only, no search

**Version:** v1.4.9

## Setup

The benchmark image builds atop the public [**CLP core Ubuntu-Jammy**](https://github.com/y-scope/clp/pkgs/container/clp%2Fclp-core-dependencies-x86-ubuntu-jammy) docker container, adding `zstd` (v1.4.9) via `apt-get`.

We apply zstd compression level 3 to the datasets and compare the result to the decompressed data to gather the ingestion metrics.

Zstd does not have search functionality, so we do not have search metrics for this tool.

