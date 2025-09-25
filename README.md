# Log Archival Bench How To

Follow the steps below to develop and contribute to the project.

## Contributing

* [Task] 3.40.0 or higher

## Setup

Initialize and update submodules:

```shell
git submodule update --init --recursive
```

Run the following code to setup the virtual environment, add the python files in src to python's
import path, then run the venv

```
python3 -m venv venv

echo "$(pwd)" > $(find venv/lib -maxdepth 1 -mindepth 1 -type d)/site-packages/project_root.pth

. venv/bin/activate

pip3 install -r requirements.txt
```

## Download Datasets

You can download all the datasets we use in the benchmark using the [download\_all.py](/scripts/download_all.py) script we provide.

The [download\_all.py](/scripts/download_all.py) script will download all datasets into the correct directories **with** the specified names, concentrate multi-file datasets together into a single file, and generate any modified version of the dataset needed for tools like Presto \+ CLP.

## Run Everything

Follow the instructions above to set up your virtual environment.

Stay in the [Log Archival Bench](/) directory and run [scripts/benchall.py](/scripts/benchall.py). This script runs the tools \+ parameters in its "benchmarks" variable across all datasets under [data/](/data).

## Run One Tool

Execute `./assets/{tool name}/main.py {path to <dataset name>.log}` to run ingestion and search on that dataset.

## Linting

Before submitting a pull request, ensure you've run the linting commands below and have fixed all
violations and suppressed all warnings.

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

Look for all tasks under the `lint` namespace (identified by the `lint:` prefix).

[Task]: https://taskfile.dev
