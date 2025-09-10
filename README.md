# Log Archival Bench How To
## Setup

Initialize and update submodules:

```shell
./tools/scripts/deps-download/init.sh
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

Follow the instructions in above to set up your virtual environment.

Stay in the [Log Archival Bench](/) directory and run [scripts/benchall.py](/scripts/benchall.py). This script runs the tools \+ parameters in its "benchmarks" variable across all datasets under [data/](/data).

## Run One Tool

Execute `./assets/{tool name}/main.py {path to <dataset name>.log}` to run ingestion and search on that dataset.
