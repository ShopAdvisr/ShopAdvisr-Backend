import requests
import base64

f = open("thanksgiving.mp3", "rb")
encoded = base64.b64encode(f.read())
requests.get("http://127.0.0.1:5000/suggestions",
             data=encoded,
             headers={"Content-Type": 'application/octet-stream'})
f.close()
