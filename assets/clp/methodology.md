# CLP methodology

**Version:** [clp-0.5.1]

**File with Formatted Queries:** [Config File]

## Setup

The benchmark builds on the public [CLP core Ubuntu-Jammy] Docker image.

We use the `clp-s` binary, which is a variant of CLP optimized for semi-structured logs like JSON.
We run `clp-s` with a target encoded size of 256 MB, balancing compression ratio with search speed.
Increasing the target encoded size can yield even better compression results. Additional tuning
options are documented in the [user docs].

Before calling `clp-s`, create a directory for its output files and pass it as a parameter to the
ingestion and search commands.

CLP doesn’t maintain any internal caches, so we only flush the filesystem buffers and clear the
filesystem caches before each query.

[CLP core Ubuntu-Jammy]: https://ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy
[clp-0.5.1]: https://github.com/y-scope/clp/releases/tag/v0.5.1
[Config File]: /assets/clp/config.yaml
[user docs]: https://docs.yscope.com/clp/v0.5.1/user-docs/core-clp-s.html
