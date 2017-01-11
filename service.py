import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import datetime
import hashlib
import time
import signal
import sys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

KUBERNETES_API_URL = "https://kubernetes.default.svc/api/v1/watch/events"
ELASTICSEARCH = "elasticsearch:9200"
TOKEN = None

def get_default_token():
    """
    Returns the value of the default auth token
    """
    path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    with open(path, "rb") as tokenfile:
        token = tokenfile.read()
    return token.strip()

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def archive_event(event):
    # index name from timestamp
    index = "kube-events-%s" % event["object"]["firstTimestamp"][0:10]
    url = "http://{host}/{index}/event/{id}".format(
        host=ELASTICSEARCH,
        index=index,
        id=event_hash(event))
    data = {"_id": id, "_source": event}
    r = requests.put(url, json=event)
    if r.status_code == 201:
        print("Archived event %s" % url)
    else:
        r.raise_for_status()

def event_hash(event):
    h = hashlib.sha256()
    h.update(json.dumps(event, sort_keys=True, indent=0))
    return h.hexdigest()

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)
    TOKEN = get_default_token()
    headers = {
        "Authorization": "Bearer %s" % TOKEN
    }

    time.sleep(10)

    while True:
        r = requests.get(KUBERNETES_API_URL, headers=headers, stream=True, verify=False)
        if r.encoding is None:
            r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if line.strip() != "":
                try:
                    event = json.loads(line)
                    archive_event(event)
                except ValueError as e:
                    print("JSON ValueError:")
                    print("'%s'" % line)
                except Exception as e:
                    print("Error: %s", e)
