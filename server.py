#!/usr/bin/env python3
"""
Serveur HTTP temps réel - Panique à Bord
Moteur télémétrique et API de gestion de crise
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import random
import sys
import time
import threading
from pathlib import Path

from core.engine import SimulationEngine

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

# Verrou de synchronisation pour l'état en mémoire
STATE_LOCK = threading.Lock()

# Initialisation du moteur de simulation
ENGINE = SimulationEngine()


class PaniqueHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, content: bytes, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        url_path = self.path.split("?")[0]

        if url_path in ("/", "/index.html"):
            index_path = STATIC_DIR / "index.html"
            if index_path.exists():
                with open(index_path, "rb") as f:
                    self._send_html(f.read())
            else:
                self.send_error(404, "index.html introuvable")
            return

        if url_path == "/api/state":
            with STATE_LOCK:
                payload = {
                    "drones": [dict(d) for d in ENGINE.drones],
                    "incidents": [dict(i) for i in ENGINE.incidents],
                }
            self._send_json(payload)
            return

        if url_path == "/api/docs":
            docs = {}
            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            for file_path in DOCS_DIR.glob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        docs[file_path.name] = f.read()
                except Exception:
                    pass
            self._send_json({"docs": docs})
            return

        if url_path.startswith("/static/"):
            relative = url_path[len("/static/"):]
            file_path = (STATIC_DIR / relative).resolve()
            if STATIC_DIR in file_path.parents and file_path.is_file():
                content_type = "text/plain; charset=utf-8"
                if file_path.suffix == ".html":
                    content_type = "text/html; charset=utf-8"
                elif file_path.suffix == ".css":
                    content_type = "text/css; charset=utf-8"
                elif file_path.suffix == ".js":
                    content_type = "application/javascript; charset=utf-8"
                with open(file_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        self.send_error(404, f"Route non trouvée: {url_path}")

    def do_POST(self):
        url_path = self.path.split("?")[0]

        if url_path == "/api/incidents":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                data = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except Exception:
                data = {}

            title_val = data.get("titre") if data.get("titre") is not None else data.get("title", "Incident Signalé")
            severity_val = data.get("severite") if data.get("severite") is not None else data.get("severity", "MOYENNE")
            x_val = data.get("x", 50.0)
            y_val = data.get("y", 50.0)

            with STATE_LOCK:
                new_incident = ENGINE.add_incident(title_val, x_val, y_val, severity_val)
                new_incident["title"] = title_val
                new_incident["severity"] = severity_val

            self._send_json({"ok": True, "incident": new_incident})
            return

        if url_path == "/api/simulate":
            with STATE_LOCK:
                created = []
                samples = [
                    ("Alerte Panne Électrique", "CRITIQUE"),
                    ("Fuite Chimique Cuve B", "MOYENNE"),
                    ("Anomalie Détecteur Infrarouge", "INFO"),
                ]
                for title, sev in samples:
                    x = round(random.uniform(10.0, 90.0), 1)
                    y = round(random.uniform(10.0, 90.0), 1)
                    inc = ENGINE.add_incident(title, x, y, sev)
                    created.append(inc)
            self._send_json({"ok": True, "generated": created})
            return

        self.send_error(404, f"Route non trouvée: {url_path}")

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def start_engine_loop(interval=0.5):
    def loop():
        while True:
            time.sleep(interval)
            with STATE_LOCK:
                try:
                    ENGINE.tick()
                except Exception as e:
                    sys.stderr.write(f"Erreur boucle télémétrie: {e}\n")

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t


def run(host="127.0.0.1", port=8080):
    start_engine_loop(interval=0.5)
    ThreadingHTTPServer.allow_reuse_address = True
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, PaniqueHandler)
    print(f"Serveur Panique à Bord démarré sur http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port=port)
