import base64
import requests
import sys
import json
import time

#https://openobserve.ai/docs/ingestion/logs/python/#python

user = "root@clpbench.com"
password = "password"
bas64encoded_creds = base64.b64encode(bytes(user + ":" + password, "utf-8")).decode("utf-8")

headers = {"Content-type": "application/json", "Authorization": "Basic " + bas64encoded_creds}
org = "default"
stream = "clpbench1"
openobserve_host = "http://localhost:5080"
openobserve_url = openobserve_host + "/api/" + org + "/_search"

query = sys.argv[1]

pagesize = 1000

i = 0
while True:
    data = {
            "query": {
                "sql": f"SELECT id FROM {stream} WHERE {query}",
                "start_time": int((time.time()-365*24*60*60)*1000000),
                "end_time": int(time.time()*1000000),
                "from": pagesize*i,
                "size": pagesize,
                }
            }
    res = requests.post(openobserve_url, headers=headers, data=json.dumps(data))

    found = json.loads(res.text)["total"]

    if found != pagesize:
        print(found + pagesize*i)
        break
    else:
        i += 1
