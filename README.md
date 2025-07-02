Run the following code to setup the virtual environment, add the python files in src to python's
import path, then run the venv

```
python3 -m venv venv
echo "$(pwd)/src" >> $(find venv/lib -maxdepth 1 -mindepth 1 -type d)/site-packages/project_root.pth

. venv/bin/activate
pip3 install -r requirements.txt
```
