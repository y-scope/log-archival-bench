import base64
import requests
import sys
import json

#https://openobserve.ai/docs/ingestion/logs/python/#python

user = "root@clpbench.com"
password = "password"
bas64encoded_creds = base64.b64encode(bytes(user + ":" + password, "utf-8")).decode("utf-8")

headers = {"Content-type": "application/json", "Authorization": "Basic " + bas64encoded_creds}
org = "default"
stream = "clpbench1"
openobserve_host = "http://localhost:5080"
openobserve_url = openobserve_host + "/api/" + org + "/" + stream + "/_json"

def base32_encode_string(s):
    return base64.b32encode(s.encode()).decode()

def base32_encode_json(obj):
    if isinstance(obj, dict):
        return {
            base32_encode_string(str(key)): value
            for key, value in obj.items()
        }
    else:
        return obj

def ingest_dataset():
    with open(sys.argv[1], 'r') as file:
        data = []

        for line in file:
            linee = line.strip()
            if not linee:
                continue
            #a = base32_encode_json(json.loads(linee))
            #data.append(a)
            data.append(json.loads(linee))

            if len(data)>50000:
                res = requests.post(openobserve_url, headers=headers, data=json.dumps(data))
                data = []
        if data:
            print(len(data))
            res = requests.post(openobserve_url, headers=headers, data=json.dumps(data))

if __name__ == "__main__":
    try:
        ingest_dataset()
    except Exception as e:
        print(e)
