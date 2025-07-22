import os

from elasticsearch import Elasticsearch

collection_name = "elasticsearch_clp_bench"

#es = Elasticsearch("http://localhost:9202", timeout=30, max_retries=10, retry_on_timeout=True)
es = Elasticsearch("http://localhost:9202")
es.indices.clear_cache(index=collection_name)
