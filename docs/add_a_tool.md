# How to Adding a Tool

1. Copy [assets/template](/assets/template/) to `assets/{toolname}`.
2. Edit the `config.yaml` in this new directory to contain your container's name, relevant processes for memory benchmarking, and queries given to your script. 
3. Edit the `Dockerfile` to modify the environment your tool will run in.
4. Modify `main.py` to modify the class name and populate all the functions. 
5. Modify [scripts/benchall.py](/scripts/benchall.py) to import your class and add it to the benchmarks list.