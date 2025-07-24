#!/usr/bin/env bash

sed -i "s/#http.port: 9200/http.port: 9202/" /etc/elasticsearch/elasticsearch.yml
sed -i "s/xpack.security.enabled: true/xpack.security.enabled: false/" \
    /etc/elasticsearch/elasticsearch.yml
sed -i "/cluster.initial_master_nodes/d" /etc/elasticsearch/elasticsearch.yml
grep -q "discovery.type: single-node" /etc/elasticsearch/elasticsearch.yml \
    || echo "discovery.type: single-node" >>/etc/elasticsearch/elasticsearch.yml

sed -i "/elasticsearch/ s/\/bin\/false/\/bin\/bash/" /etc/passwd
sed -i "/elasticsearch/ s/\/nonexistent/\/usr\/share\/elasticsearch/" /etc/passwd

# It seems the environment variables sometimes does not work, need stop and start the elasticsearch
# in the container manually to ensure it is applied use to check: curl -XGET \
# "http://localhost:9202/_nodes/stats/jvm?pretty"
# ES_JAVA_OPTS="-Xms256m -Xmx256m" su elasticsearch -c \
# "/usr/share/elasticsearch/bin/elasticsearch -d"
su elasticsearch -c "/usr/share/elasticsearch/bin/elasticsearch -d"

curl -X PUT 'http://localhost:9202/_cluster/settings' -H "Content-Type: application/json" -d '{"transient": {"cluster.routing.allocation.disk.watermark.flood_stage": "99%", "cluster.routing.allocation.disk.watermark.high": "98%", "cluster.routing.allocation.disk.watermark.low": "97%"}}'
