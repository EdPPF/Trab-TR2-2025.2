import json
import sqlite3
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

DB_FILE = "dados.db"
LISTEN_HOST = "0.0.0.0"   #"127.0.0.1" so localmente 
LISTEN_PORT = 3000

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leituras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sala TEXT,
        temperatura REAL,
        umidade REAL,
        poeira REAL,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    server_version = "MonitorLoRa/0.1"

    def _set_json_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/data":
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_error(400, "Empty body")
            return

        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as e:
            logging.exception("JSON decode error")
            self.send_error(400, "Invalid JSON")
            return


        sala = payload.get("sala") or payload.get("room") or payload.get("device")
        temp = payload.get("temp") or payload.get("temperatura") or payload.get("temperature")
        umid = payload.get("umid") or payload.get("umidade") or payload.get("humidity")
        poeira = payload.get("poeira") or payload.get("dust") or payload.get("pm")

        if sala is None or temp is None or umid is None or poeira is None:
            logging.warning("Missing fields in payload: %s", payload)
            self.send_error(400, "Missing fields (sala/temp/umid/poeira)")
            return

        timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO leituras (sala, temperatura, umidade, poeira, timestamp) VALUES (?, ?, ?, ?, ?)",
                (str(sala), float(temp), float(umid), float(poeira), timestamp)
            )
            conn.commit()
            conn.close()
            logging.info("Inserida leitura sala=%s temp=%s umid=%s poeira=%s", sala, temp, umid, poeira)
            self._set_json_headers(201)
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        except Exception as e:
            logging.exception("DB insert error")
            self.send_error(500, "Server error")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/data":

            if parsed.path == "/" or parsed.path == "/index.html":

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Servidor Monitoramento LoRa</h1></body></html>")
                return
            self.send_error(404, "Not found")
            return

        qs = parse_qs(parsed.query)
        sala = qs.get("sala", [None])[0]
        limit = int(qs.get("limit", [100])[0])
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            if sala:
                cur.execute("SELECT id, sala, temperatura, umidade, poeira, timestamp FROM leituras WHERE sala = ? ORDER BY id DESC LIMIT ?", (sala, limit))
            else:
                cur.execute("SELECT id, sala, temperatura, umidade, poeira, timestamp FROM leituras ORDER BY id DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            conn.close()

            items = [
                {"id": r[0], "sala": r[1], "temperatura": r[2], "umidade": r[3], "poeira": r[4], "timestamp": r[5]}
                for r in rows
            ]
            self._set_json_headers(200)
            self.wfile.write(json.dumps(items).encode("utf-8"))
        except Exception as e:
            logging.exception("DB read error")
            self.send_error(500, "Server error")

    def log_message(self, format, *args):

        logging.info("%s - - %s", self.client_address[0], format % args)


if __name__ == "__main__":
    init_db()
    addr = (LISTEN_HOST, LISTEN_PORT)
    server = ThreadingHTTPServer(addr, RequestHandler)
    logging.info("Servidor rodando em http://%s:%d", LISTEN_HOST, LISTEN_PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Finalizando servidor")
        server.server_close()