# Log Archival Bench How To
## Setup

Initialize and update submodules:

```shell
git submodule update --init --recursive
```

## Download Datasets

You can download all the datasets we use in the benchmark using the [download\_all.py](/scripts/download_all.py) script we provide.

The [download\_all.py](/scripts/download_all.py) script will download all datasets into the correct directories **with** the specified names, concentrate multi-file datasets together into a single file, and generate any modified version of the dataset needed for tools like Presto \+ CLP.

## Docker Environments

Benchmarks are executed inside Docker containers to ensure reproducible, isolated test environments
with controlled resource limits.

### Build All Docker Images

To build all Docker images concurrently:

```shell
task docker-images:build
```

### Build a Single Docker Images

To build a specific image for a given engine:

```shell
uv run src/log_archival_bench/scripts/docker_images/build.py --engine-name <engine_name>
```

Each image corresponds to a specific engine (e.g. `clp`, `clickhouse`, `elasticsearch`, `sparksql`).

## Run Everything

Follow the instructions above to set up your virtual environment.

Stay in the [Log Archival Bench](/) directory and run [scripts/benchall.py](/scripts/benchall.py). This script runs the tools \+ parameters in its "benchmarks" variable across all datasets under [data/](/data).

## Run One Engine

Execute `./assets/{engine_name}/main.py {path to <dataset_name>.log}` to run ingestion and search on that dataset.

## Contributing

Follow the steps below to develop and contribute to the project.

### Requirements

* [Task] 3.40.0 or higher

### Linting

Before submitting a pull request, ensure you've run the linting commands below and have fixed all
violations and suppressed any benign warnings.

To run all linting checks:

```shell
task lint:check
```

To run all linting checks AND fix some violations:

```shell
task lint:fix
```

To see how to run a subset of linters for a specific file type:

```shell
task -a
```

Look for tasks under the `lint` namespace (identified by the `lint:` prefix).

[Task]: https://taskfile.dev
