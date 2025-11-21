import json, sqlite3, logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
DB_FILE = str((Path(__file__).with_name("dados.db")).resolve())

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

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
        timestamp TEXT,
        seq INTEGER
    )
    """)
    conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
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
        except Exception:
            self.send_error(400, "Invalid JSON")
            return

        sala = payload.get("sala")
        temp = payload.get("temp")
        umid = payload.get("umid")
        poeira = payload.get("poeira")
        raw_seq = payload.get("seq")

        if sala is None or temp is None or umid is None or poeira is None:
            self.send_error(400, "Missing fields (sala/temp/umid/poeira)")
            return

        try:
            seq = int(raw_seq) if raw_seq is not None else None
        except (TypeError, ValueError):
            seq = None

        timestamp = payload.get("timestamp") or (datetime.utcnow().isoformat() + "Z")
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO leituras (sala, temperatura, umidade, poeira, timestamp, seq) VALUES (?, ?, ?, ?, ?, ?)",
                (str(sala), float(temp), float(umid), float(poeira), timestamp, seq)
            )
            conn.commit()
            conn.close()
            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        except Exception:
            self.send_error(500, "Server error")

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path in ("/", "/index.html", "/dashboard"):
            try:
                data = HTML_PATH.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                self.send_error(500, "Falha ao servir dashboard")
                return

        if parsed.path != "/api/data":
            self.send_error(404, "Not found")
            return

        qs = parse_qs(parsed.query)
        sala = qs.get("sala", [None])[0]
        limit = int(qs.get("limit", [100])[0])

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            if sala:
                cur.execute(
                    "SELECT id, sala, temperatura, umidade, poeira, timestamp, seq "
                    "FROM leituras WHERE sala = ? ORDER BY id DESC LIMIT ?",
                    (sala, limit)
                )
            else:
                cur.execute(
                    "SELECT id, sala, temperatura, umidade, poeira, timestamp, seq "
                    "FROM leituras ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
            rows = cur.fetchall()
            conn.close()

            items = [
                {
                    "id": r[0],
                    "sala": r[1],
                    "temperatura": r[2],
                    "umidade": r[3],
                    "poeira": r[4],
                    "timestamp": r[5],
                    "seq": r[6],
                }
                for r in rows
            ]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(items).encode("utf-8"))
        except Exception:
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
        server.server_close()
