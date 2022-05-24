import requests,json
from requests.structures import CaseInsensitiveDict
import os

def pin(status,no):
    url = os.getenv("RPI_PINS_API")+ status
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = json.dumps({"pin":no})
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code