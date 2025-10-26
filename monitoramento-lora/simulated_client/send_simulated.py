
import json
import time
import random
from urllib import request

SERVER_URL = "http://localhost:3000/api/data" 

def send(measure):
    data = json.dumps(measure).encode("utf-8")
    req = request.Request(SERVER_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=5) as resp:
        print("Resposta:", resp.status, resp.read().decode())

def random_measure(sala="rack1"):
    return {
        "sala": sala,
        "temp": round(20 + random.random()*10, 2),
        "umid": round(30 + random.random()*50, 2),
        "poeira": round(random.random()*100, 2),
        "timestamp": None
    }

if __name__ == "__main__":
    for i in range(5):
        m = random_measure("rack1")
        print("Enviando:", m)
        send(m)
        time.sleep(1)
