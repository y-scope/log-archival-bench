import logging
import sys

from elasticsearch import Elasticsearch

collection_name = "elasticsearch_clp_bench"

es = Elasticsearch(
    "http://localhost:9202", request_timeout=30, max_retries=10, retry_on_timeout=True
)
results = []

query = sys.argv[1]


# Function to execute a query without cache
def execute_query_without_cache(query):
    # Initialize the scroll
    page = es.search(
        index=collection_name,
        scroll="8m",  # Keep the search context open for 2 minutes
        body=query,
        request_cache=False,
    )

    for result in page["hits"]["hits"]:
        results.append(result)

    # Start scrolling
    sid = page["_scroll_id"]
    while True:
        page = es.scroll(scroll_id=sid, scroll="8m")
        if not page["hits"]["hits"]:
            break
        for result in page["hits"]["hits"]:
            results.append(result)


# Execute the query
while True:
    try:
        execute_query_without_cache(query)
        print(len(results))
        break
    except Exception as e:
        logging.error(e)
        continue

