import json
import time
import random
from urllib import request

SERVER_URL = "http://localhost:8080/api/data"

seq_por_sala = {}
last_por_sala = {}

DELTA_TEMP = 0.5
DELTA_UMID = 2.0
DELTA_POEIRA = 5.0

def send(measure):
    data = json.dumps(measure).encode("utf-8")
    req = request.Request(
        SERVER_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    with request.urlopen(req, timeout=5) as resp:
        print("Resposta:", resp.status, resp.read().decode())

def gerar_leituras(sala, forcar_alerta=False, forcar_sem_mudanca=False):
    if sala not in seq_por_sala:
        seq_por_sala[sala] = 0

    if sala not in last_por_sala:
        last_por_sala[sala] = {"temp": None, "umid": None, "poeira": None}

    last = last_por_sala[sala]

    if forcar_alerta:
        temp = 32.0
        umid = 25.0
        poeira = 90.0
    elif forcar_sem_mudanca and last["temp"] is not None:
        temp = round(last["temp"] + random.uniform(-0.1, 0.1), 2)
        umid = round(last["umid"] + random.uniform(-0.5, 0.5), 2)
        poeira = round(last["poeira"] + random.uniform(-1.0, 1.0), 2)
    else:
        temp = round(20 + random.random()*10, 2)
        umid = round(30 + random.random()*50, 2)
        poeira = round(random.random()*100, 2)

    mudouTemp = last["temp"] is None or abs(temp - last["temp"]) >= DELTA_TEMP
    mudouUmid = last["umid"] is None or abs(umid - last["umid"]) >= DELTA_UMID
    mudouPoeira = last["poeira"] is None or abs(poeira - last["poeira"]) >= DELTA_POEIRA

    alerta = temp > 30.0 or umid < 30.0
    precisaEnviar = mudouTemp or mudouUmid or mudouPoeira or alerta

    if not precisaEnviar:
        return None

    seq_envio = seq_por_sala[sala]
    seq_por_sala[sala] += 1

    last_por_sala[sala] = {
        "temp": temp,
        "umid": umid,
        "poeira": poeira
    }

    return {
        "sala": sala,
        "seq": seq_envio,
        "temp": temp,
        "umid": umid,
        "poeira": poeira,
        "timestamp": None
    }

if __name__ == "__main__":
    salas = ["rack1", "rack2", "rack3", "rack4"]

    for i in range(100):
        sala = salas[i % len(salas)]

        if i % 10 == 0:
            medida = gerar_leituras(sala, forcar_alerta=True)
            print("Forçando ALERTA:", medida)
        elif i % 10 == 4:
            medida = gerar_leituras(sala, forcar_sem_mudanca=True)
            print("Forçando SEM MUDANÇA (esperado não enviar):", medida)
        else:
            medida = gerar_leituras(sala)
            print("Normal:", medida)

        if medida is not None:
            send(medida)
        else:
            print("Nenhum envio (variação abaixo dos limiares).")

        time.sleep(1)
