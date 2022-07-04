import requests

import config

resp = requests.post(config.ENDPOINT, json={"key": "value"})