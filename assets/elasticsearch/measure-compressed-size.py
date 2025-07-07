import time

import requests

collection_name = "elasticsearch_clp_bench"

time.sleep(5)
response = requests.get(f"http://localhost:9202/{collection_name}/_stats").json()
print(response["_all"]["total"]["store"]["size_in_bytes"])
