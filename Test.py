import requests
import base64
import pprint
f = open("pussycat.m4a", "rb")
encoded = base64.b64encode(f.read())
pprint.pprint(requests.get("http://127.0.0.1:5000/suggestions",
             data=encoded,
             headers={"Content-Type": 'application/octet-stream'}).json())
f.close()
