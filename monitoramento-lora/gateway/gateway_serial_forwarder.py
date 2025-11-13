#!/usr/bin/env python3
import json
import serial
import serial.tools.list_ports
from urllib import request
from typing import Dict, Any
import argparse
import sys

SERVER_URL = "http://localhost:8080/api/data"
BAUD_RATE = 9600

def find_serial_port():
    print("Procurando portas seriais...")
    ports = serial.tools.list_ports.comports()
    arduino_ports = [p for p in ports if "USB" in p.description or "Arduino" in p.description]

    if arduino_ports:
        print(f"Porta detectada: {arduino_ports[0].device}")
        return arduino_ports[0].device
    elif ports:
        print("Nenhuma porta Arduino detectada, usando a primeira porta disponível.")
        print(f"Porta detectada: {ports[0].device}")
        return ports[0].device
    else:
        print("Nenhuma porta serial encontrada.")
        return None

def parse_serial_line(line):
    """
    Converte a linha serial para o formato JSON.
    
    Formato de entrada: "id=rack1;temp=23.7;umid=55.2;poeira=42.1"

    Formato de saída: {"sala": "rack1", "temp": 23.7, ...}
    """
    try:
        measure: Dict[str, Any] = {
            "sala": None,
            "temp": None,
            "umid": None,
            "poeira": None,
            "timestamp": None
        }

        parts = [p.strip() for p in line.split(';') if p.strip()]
        for part in parts:
            if '=' in part:
                key, value = [x.strip() for x in part.split('=', 1)]
                if key == 'id':
                    measure['sala'] = value
                elif key == 'temp':
                    measure['temp'] = round(float(value), 2)
                elif key == 'umid':
                    measure['umid'] = round(float(value), 2)
                elif key == 'poeira':
                    measure['poeira'] = round(float(value), 2)
        # Verifica se todas as chaves esperadas estão presentes
        if all(measure[k] is not None for k in ['sala', 'temp', 'umid', 'poeira']):
            return measure
        else:
            print(f"[Parser] Erro: Dados incompletos na linha: '{line}'")
            return None

    except Exception as e:
        print(f"[Parser] Erro ao processar linha '{line}': {e}")
        return None

def send_to_server(measure):
    try:
        data = json.dumps(measure).encode("utf-8")
        req = request.Request(SERVER_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=5) as resp:
            print(f"[HTTP] ({resp.status}) {resp.read().decode()}")
    except Exception as e:
        print(f"[HTTP] Erro: {e}")


def read_from_stdin():
    print(f"Iniciando Gateway (modo stdin)...\nServidor: {SERVER_URL}\n")
    print("Digite no formato: id=rack1;temp=25;umid=50;poeira=10")
    print("Digite 'sair' para encerrar.\n")

    for line in sys.stdin:
        line = line.strip()
        if line.lower() == "sair":
            break
        if not line:
            continue

        print(f"[Serial] Dado: {line}")
        measure = parse_serial_line(line)
        if measure:
            send_to_server(measure)


def read_from_serial(port):
    print(f"Iniciando Gateway (modo serial)...")
    print(f"Porta: {port}, Baud: {BAUD_RATE}")
    print(f"Encaminhando para servidor: {SERVER_URL}\n")

    try:
        with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue

                print(f"[Serial] Dado: {line}")
                measure = parse_serial_line(line)
                if measure:
                    send_to_server(measure)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    except Exception as e:
        print(f"[Serial] Erro: {e}")


def main():
    parser = argparse.ArgumentParser(description="Gateway Serial Forwarder")
    parser.add_argument("--stdin", action="store_true", help="Ler dados digitados manualmente (modo teste)")
    parser.add_argument("--serial", type=str, help="Porta serial (ex: /dev/ttyUSB0, COM3, loop://)")
    args = parser.parse_args()

    if args.stdin:
        read_from_stdin()
    else:
        port = args.serial or find_serial_port()
        if not port:
            print("Nenhuma porta detectada e --stdin não foi usado.")
            return
        read_from_serial(port)


if __name__ == "__main__":
    main()