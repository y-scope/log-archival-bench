# CLP methodology

**Version:** [0.4.0](https://github.com/y-scope/clp/releases/tag/v0.4.0)

**File with Formatted Queries:** [Config File](/assets/clp_s/config.yaml)

## Setup

We use a publicly available docker image we provide for CLP as the base docker image ([clp core ubuntu-jammy docker image](http://ghcr.io/y-scope/clp/clp-core-dependencies-x86-ubuntu-jammy)).

We use the clp-s binary, which is a variant of CLP designed for semi-structured logs like JSON. We run clp-s with a target encoded size of 256MB to balance compression ratio with search speed. You can obtain even higher compression ratios by using larger target encoded sizes. You can look through more ways to configure clp-s in our user guide, [here.](https://docs.yscope.com/clp/v0.4.0/user-guide/core-clp-s)

There is no need to launch clp-s, once built it can just be called on the command line and will be just shut down when it’s completed its command execution. The only thing we do before calling clp-s is to make a directory for its output files. We provide this as one of the parameters to the ingestion and search commands.

CLP doesn’t maintain any internal caches for us to clear, so before each query we flush the file system buffers and clear the filesystem caches. 