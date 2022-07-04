import requests

import config

resp = requests.post(config.ENPOINT, json={"key": "value"})