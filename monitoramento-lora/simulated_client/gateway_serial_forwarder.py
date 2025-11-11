import json
import random
import time
import serial
import serial.tools.list_ports
from urllib import request
from typing import Dict, Any

SERVER_URL = "http://localhost:8080/api/data"

# Configs da Porta Serial
# None para tentar detectar, ou
# 'COM3' (Windows) || '/dev/ttyUSB0' (Linux)
SERIAL_PORT = None # 'COM3'
BAUD_RATE = 9600

def find_serial_port():
    """Tenta encontrar uma porta serial USB (Arduino) automaticamente."""
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
        # O JSON que o servidor espera (baseado no send_simulated.py)
        measure: Dict[str, Any] = {
            "sala": None,
            "temp": None,
            "umid": None,
            "poeira": None,
            "timestamp": None
        }

        parts = line.split(';')
        for part in parts:
            if '=' in part:
                key, value = part.split('=')
                # Mapeamento do protocolo serial para o JSON do servidor
                if key == 'id':
                    measure['sala'] = value
                elif key == 'temp':
                    measure['temp'] = round(float(value), 2)
                elif key == 'umid':
                    measure['umid'] = round(float(value), 2)
                elif key == 'poeira':
                    measure['poeira'] = round(float(value), 2)
            
        # Verifica se todas as chaves esperadas estão presentes
        required_keys = ['sala', 'temp', 'umid', 'poeira']
        if all(measure[k] is not None for k in required_keys):
            return measure
        else:
            print(f"[Parser] Erro: Dados incompletos na linha: '{line}'")
            return None

    except Exception as e:
        print(f"[Parser] Erro ao processar linha '{line}': {e}")
        return None

def send_to_server(measure):
    """Envia a medição formatada para o servidor."""
    try:
        data = json.dumps(measure).encode("utf-8")
        req = request.Request(SERVER_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
        
        with request.urlopen(req, timeout=5) as resp:
            print(f"[HTTP] Resposta ({resp.status}): {resp.read().decode()}")
    except Exception as e:
        print(f"[HTTP] Erro ao enviar para o servidor: {e}")


def main():
    global SERIAL_PORT
    if SERIAL_PORT is None:
        SERIAL_PORT = find_serial_port()
        if SERIAL_PORT is None:
            print("Erro: Nenhuma porta serial encontrada. Conecte o dispositivo.")
            return

    print(f"Iniciando 'Gateway Serial Forwarder'...")
    print(f"Ouvindo porta serial: {SERIAL_PORT} (Baud: {BAUD_RATE})")
    print(f"Encaminhando para o servidor: {SERVER_URL}")

    ser = None
    while True:
        try:
            # 1. Conectar à porta serial
            if ser is None or not ser.is_open:
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                print(f"Conectado com sucesso à porta {SERIAL_PORT}.")

            # 2. Ler uma linha da porta serial
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"[Serial] Dado recebido: {line}")
                    # 3. Analisar a linha
                    measure = parse_serial_line(line)
                    if measure:
                        # 4. Enviar para o servidor
                        print(f"[HTTP] Enviando para o servidor: {measure}")
                        send_to_server(measure)

        except serial.SerialException as e:
            print(f"Erro serial: {e}. Tentando reconectar em 5s...")
            if ser and ser.is_open:
                ser.close()
            ser = None
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nEncerrando... Fechando porta serial.")
            if ser and ser.is_open:
                ser.close()
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()