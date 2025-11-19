import json
import time
import random
from urllib import request

SERVER_URL = "http://localhost:8080/api/data"

def send(measure):
    data = json.dumps(measure).encode("utf-8")
    req = request.Request(SERVER_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=5) as resp:
        print("Resposta:", resp.status, resp.read().decode())

def random_measure(sala):
    return {
        "sala": sala,
        "temp": round(20 + random.random()*10, 2),
        "umid": round(30 + random.random()*50, 2),
        "poeira": round(random.random()*100, 2),
        "timestamp": None
    }

if __name__ == "__main__":
    salas = ["rack1", "rack2"]
    for i in range(5):
        sala = salas[i % len(salas)]
        m = random_measure(sala)
        print(f"Enviando ({sala}):", m)
        send(m)
        time.sleep(1)
