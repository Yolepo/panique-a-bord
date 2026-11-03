#!/usr/bin/env python3
"""
Serveur HTTP temps réel - Panique à Bord
Prototype Naïf pour l'Issue #1
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

# Verrou de synchronisation pour les données en mémoire
STATE_LOCK = threading.Lock()

# État initial de la flotte de drones
DRONES = [
    {
        "id": "PAB-01",
        "nom": "PAB-01",
        "name": "PAB-01",
        "x": 20.0,
        "y": 30.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 100,
        "battery": 100,
    },
    {
        "id": "PAB-02",
        "nom": "PAB-02",
        "name": "PAB-02",
        "x": 70.0,
        "y": 40.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 85,
        "battery": 85,
    },
    {
        "id": "PAB-03",
        "nom": "PAB-03",
        "name": "PAB-03",
        "x": 40.0,
        "y": 80.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 92,
        "battery": 92,
    },
    {
        "id": "PAB-04",
        "nom": "PAB-04",
        "name": "PAB-04",
        "x": 80.0,
        "y": 85.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 78,
        "battery": 78,
    },
]

# État initial des incidents
INCIDENTS = [
    {
        "id": "INC-01",
        "titre": "Alerte intrusion nord",
        "title": "Alerte intrusion nord",
        "x": 25.0,
        "y": 35.0,
        "severite": "CRITIQUE",
        "severity": "CRITICAL",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
    {
        "id": "INC-02",
        "titre": "Fumée suspecte hangar",
        "title": "Fumée suspecte hangar",
        "x": 65.0,
        "y": 50.0,
        "severite": "MOYENNE",
        "severity": "MEDIUM",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
]

incident_counter = len(INCIDENTS)


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
                    "drones": [dict(d) for d in DRONES],
                    "incidents": [dict(i) for i in INCIDENTS],
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

            global incident_counter
            with STATE_LOCK:
                incident_counter += 1
                inc_id = f"INC-{incident_counter:02d}"

                title_val = data.get("titre") if data.get("titre") is not None else data.get("title", f"Incident #{incident_counter}")
                severity_val = data.get("severite") if data.get("severite") is not None else data.get("severity", "MOYENNE")
                x_val = data.get("x", 50.0)
                y_val = data.get("y", 50.0)

                try:
                    x_num = float(x_val)
                except (ValueError, TypeError):
                    x_num = x_val
                try:
                    y_num = float(y_val)
                except (ValueError, TypeError):
                    y_num = y_val

                # Prototype naïf : stockage sans filtrage XSS ni bornage de coordonnées
                new_incident = {
                    "id": inc_id,
                    "titre": title_val,
                    "title": title_val,
                    "x": x_num,
                    "y": y_num,
                    "severite": severity_val,
                    "severity": severity_val,
                    "statut": "DETECTED",
                    "status": "DETECTED",
                }
                INCIDENTS.append(new_incident)

            self._send_json({"ok": True, "incident": new_incident})
            return

        self.send_error(404, f"Route non trouvée: {url_path}")

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run(host="127.0.0.1", port=8080):
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
