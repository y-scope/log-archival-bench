# Elasticsearch methodology

## Basics

Version: [8.6.2][download]

## Setup

We deploy [elasticsearch] in a single-node configuration.

## Specifics

We disable the security feature of [xpack][disabling-xpack]. We use Elasticsearch's Python package for data ingestion 
and search operations.

Some preprocessing is necessary to make the dataset searchable in Elasticsearch. For more details,
refer to the `traverse_data` function in `ingest_script` . This process generally involves
reorganizing specific fields, moving them into outer or inner objects to ensure proper query
functionality.


[download]: https://www.elastic.co/downloads/past-releases/elasticsearch-8-6-2
[disabling-xpack]: https://www.elastic.co/guide/en/elasticsearch/reference/current/security-settings.html
[elasticsearch]: https://www.elastic.co/downloads/elasticsearch

