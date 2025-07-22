# LogArchivalBench How To
## Setup

Run the following code to setup the virtual environment, add the python files in src to python's
import path, then run the venv

```
python3 -m venv venv
```
```
echo "$(pwd)" > $(find venv/lib -maxdepth 1 -mindepth 1 -type d)/site-packages/project_root.pth
```
```
. venv/bin/activate
```
```
pip3 install -r requirements.txt
```

## Download Datasets

You can download all the datasets we use in the benchmark using the [download\_all.py](scripts/download_all.py) script we provide. 

### Adding A Dataset

The simplest way to add a new dataset is to,

1) Add a new directory under [data](/data) with your dataset's name.   
2) Copy a metadata.yaml file from any other dataset directory under data and fill in the correct information. The number of lines doesn’t matter for the downloading process.You can fill that value in after it is downloaded.  
3) Run the [download\_all.py](scripts/download_all.py) script.

The [download\_all.py](scripts/download_all.py) script will download all datasets into the correct directories the specified names, concentrate multi-file datasets together into a single file, and generate any modified version of the dataset needed for tools like Presto \+ CLP.

## Run Everything

Follow the instructions in above to set up your virtual environment. 

Stay in the [LogArchiveBench](/) directory and run [scripts/benchall.py](/scripts/benchall.py). This script runs the tools \+ parameters in its "benchmarks" variable across all datasets under [data/](/data).

## Run One Tool

Execute `./assets/{tool name}/main.py {path to <dataset name>.log}` to run ingestion and search on that dataset.

## Adding A Tool

1. Copy [assets/template](/assets/template/) to `assets/{toolname}`.
2. Edit the `config.yaml` in this new directory to contain your container's name, relevant processes for memory benchmarking, and queries given to your script. 
3. Edit the `Dockerfile` to modify the environment your tool will run in.
4. Modify `main.py` to modify the class name and populate all the functions. 
5. Modify [scripts/benchall.py](/scripts/benchall.py) to import your class and add it to the benchmarks list.