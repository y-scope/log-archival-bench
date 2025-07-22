import json
import logging
import sys

import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk  # type: ignore

collection_name = "elasticsearch_clp_bench"

log_path = sys.argv[1]

def traverse_data(collection_name):
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            json_line = json.loads(line)
            if "attr" in json_line:
                attr = json_line["attr"]
                if "uuid" in attr and isinstance(attr["uuid"], dict):
                    uuid = attr["uuid"]["uuid"]["$uuid"]
                    json_line["attr"]["uuid"] = uuid
                if "error" in attr and isinstance(attr["error"], str):
                    error_msg = attr["error"]
                    json_line["attr"]["error"] = {}
                    json_line["attr"]["error"]["errmsg"] = error_msg
                if "command" in attr:
                    command = attr["command"]
                    if isinstance(command, str):
                        json_line["attr"]["command"] = {}
                        json_line["attr"]["command"]["command"] = command
                    if (
                        isinstance(command, dict)
                        and "q" in command
                        and isinstance(command["q"], dict)
                        and "_id" in command["q"]
                        and not isinstance(command["q"]["_id"], dict)
                    ):
                        id_value = str(command["q"]["_id"])
                        json_line["attr"]["command"]["q"]["_id"] = {}
                        json_line["attr"]["command"]["q"]["_id"]["_ooid"] = id_value
                if (
                    "writeConcern" in attr
                    and isinstance(attr["writeConcern"], dict)
                    and "w" in attr["writeConcern"]
                    and isinstance(attr["writeConcern"]["w"], int)
                ):
                    w = attr["writeConcern"]["w"]
                    json_line["attr"]["writeConcern"]["w"] = str(w)
                if (
                    "query" in attr
                    and isinstance(attr["query"], dict)
                    and "_id" in attr["query"]
                    and not isinstance(attr["query"]["_id"], dict)
                ):
                    id_value = str(attr["query"]["_id"])
                    json_line["attr"]["query"]["_id"] = {}
                    json_line["attr"]["query"]["_id"]["_ooid"] = id_value
            yield {
                "_index": collection_name,
                "_source": json_line,
            }


def ingest_dataset():
    es = Elasticsearch("http://localhost:9202", request_timeout=1200, retry_on_timeout=True)

    count = 0
    for success, info in streaming_bulk(
        es,
        traverse_data(collection_name),
        raise_on_error=False,
        raise_on_exception=False,
        chunk_size=10000,
        #request_timeout=120,
    ):
        if success:
            count += 1
        else:
            logging.error(f"Failed to index document at {count}: {info}")
        if count % 100000 == 0:
            logging.info(f"Index {count} logs")

    requests.post(f"http://localhost:9202/{collection_name}/_flush/")


if __name__ == "__main__":
    try:
        ingest_dataset()
    except Exception as e:
        print(e)
