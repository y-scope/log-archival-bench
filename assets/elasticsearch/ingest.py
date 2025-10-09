import json
import logging
import sys

import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk  # type: ignore

collection_name = "elasticsearch_bench"

log_path = sys.argv[1]

def pop_by_path(obj, path):
    keys = path.split('.')
    for key in keys[:-1]:
        obj = obj[key]
    out = obj[keys[-1]]
    del obj[keys[-1]]
    return out

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

            try:
                timestamp_val = pop_by_path(json_line, sys.argv[2])
                json_line["@timestamp"] = timestamp_val
            except KeyError:
                # no such timestamp, ignore
                json_line["@timestamp"] = 0

            yield {
                "_index": collection_name,
                "_op_type": "create",
                "_source": json_line,
            }


def ingest_dataset():
    es = Elasticsearch("http://localhost:9202", request_timeout=1200, retry_on_timeout=True)

    if sys.argv[3] != "no_logsdb":
        template_body = {
            "index_patterns": [collection_name],
            "template": {
                "settings": {
                    "index": {
                        "mode": "logsdb"
                    },
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {
                            "type": "date",
                            "format": "date_optional_time||epoch_second||epoch_millis||yyyy-MM-dd HH:mm:ss.SSS zzz"
                            }
                    }
                }
            },
            "priority": 101
        }
        es.indices.put_index_template(name=collection_name, body=template_body)

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
