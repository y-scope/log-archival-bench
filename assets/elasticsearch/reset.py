import requests

collection_name = "elasticsearch_bench"

requests.delete(f"http://localhost:9202/{collection_name}")
