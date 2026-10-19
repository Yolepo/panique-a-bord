#!/usr/bin/env python3
"""Serveur HTTP temps réel pour la cellule de crise Panique à Bord.

Développé en Python 3 standard (http.server) sans dépendance externe.
Expose le tableau de bord naïf, l'API d'état de la flotte et les endpoints de télémétrie.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import threading
from typing import Any, Dict, List
import urllib.parse

HOST = "0.0.0.0"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

# Verrou de synchronisation pour l'accès concurrent à l'état
STATE_LOCK = threading.Lock()

# État initial de la flotte de drones (au moins 4 : PAB-01 à PAB-04)
DRONES: List[Dict[str, Any]] = [
    {
        "id": "PAB-01",
        "nom": "PAB-01 Alpha",
        "name": "PAB-01 Alpha",
        "x": 20.0,
        "y": 25.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 98,
        "battery": 98,
    },
    {
        "id": "PAB-02",
        "nom": "PAB-02 Bravo",
        "name": "PAB-02 Bravo",
        "x": 75.0,
        "y": 20.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 92,
        "battery": 92,
    },
    {
        "id": "PAB-03",
        "nom": "PAB-03 Charlie",
        "name": "PAB-03 Charlie",
        "x": 30.0,
        "y": 80.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 85,
        "battery": 85,
    },
    {
        "id": "PAB-04",
        "nom": "PAB-04 Delta",
        "name": "PAB-04 Delta",
        "x": 80.0,
        "y": 75.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 95,
        "battery": 95,
    },
]

# Incidents initiaux
INCIDENTS: List[Dict[str, Any]] = [
    {
        "id": "INC-01",
        "titre": "Incendie Zone Portuaire",
        "title": "Incendie Zone Portuaire",
        "x": 50.0,
        "y": 45.0,
        "severite": "HIGH",
        "severity": "HIGH",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
    {
        "id": "INC-02",
        "titre": "Avarie Moteur Pont Principal",
        "title": "Avarie Moteur Pont Principal",
        "x": 25.0,
        "y": 65.0,
        "severite": "MEDIUM",
        "severity": "MEDIUM",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
]

INCIDENT_COUNTER = len(INCIDENTS)


class CrisisHttpHandler(BaseHTTPRequestHandler):
    """Handler HTTP pour l'API REST et le service de fichiers statiques."""

    def _send_json(self, status_code: int, data: Any) -> None:
        """Envoie une réponse JSON avec en-têtes CORS standards."""
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(payload)

    def _serve_file(self, file_path: Path) -> None:
        """Sert un fichier statique de manière sécurisée."""
        if not file_path.is_file():
            self.send_error(404, f"Fichier introuvable: {file_path.name}")
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"
        if mime_type.startswith("text/") or mime_type in ("application/javascript", "application/json"):
            mime_type += "; charset=utf-8"

        try:
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Erreur lecture fichier: {e}")

    def do_OPTIONS(self) -> None:
        """Gère les requêtes préliminaires CORS pre-flight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Traite les requêtes HTTP GET."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Endpoints API REST
        if path == "/api/state":
            with STATE_LOCK:
                state_data = {
                    "drones": list(DRONES),
                    "incidents": list(INCIDENTS),
                }
            self._send_json(200, state_data)
            return

        if path == "/api/docs":
            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            docs_dict: Dict[str, str] = {}
            for doc_file in sorted(DOCS_DIR.glob("*.md")):
                if doc_file.is_file():
                    try:
                        docs_dict[doc_file.name] = doc_file.read_text(encoding="utf-8")
                    except Exception as err:
                        docs_dict[doc_file.name] = f"Erreur de lecture: {err}"
            self._send_json(200, docs_dict)
            return

        # Fichiers statiques
        if path in ("/", "/index.html"):
            index_path = STATIC_DIR / "index.html"
            self._serve_file(index_path)
            return

        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            target_path = (STATIC_DIR / rel_path).resolve()
            # Sécurité anti path traversal
            if STATIC_DIR.resolve() in target_path.parents or target_path == STATIC_DIR.resolve():
                self._serve_file(target_path)
            else:
                self.send_error(403, "Accès interdit")
            return

        # Fichier direct sous static si demandé sans préfixe
        direct_static = (STATIC_DIR / path.lstrip("/")).resolve()
        if (STATIC_DIR.resolve() in direct_static.parents) and direct_static.is_file():
            self._serve_file(direct_static)
            return

        self.send_error(404, f"Route non trouvée: {path}")

    def do_POST(self) -> None:
        """Traite les requêtes HTTP POST."""
        global INCIDENT_COUNTER
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/incidents":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                data = json.loads(raw_body)
            except Exception as e:
                self._send_json(400, {"error": f"JSON invalide: {e}"})
                return

            with STATE_LOCK:
                INCIDENT_COUNTER += 1
                inc_id = data.get("id") or f"INC-{INCIDENT_COUNTER:02d}"
                titre = data.get("titre") or data.get("title") or f"Incident #{INCIDENT_COUNTER}"
                severite = data.get("severite") or data.get("severity") or "MEDIUM"
                statut = data.get("statut") or data.get("status") or "DETECTED"
                
                try:
                    x_val = float(data.get("x", 50.0))
                    y_val = float(data.get("y", 50.0))
                except (ValueError, TypeError):
                    x_val = 50.0
                    y_val = 50.0

                new_incident = {
                    "id": inc_id,
                    "titre": titre,
                    "title": titre,
                    "x": x_val,
                    "y": y_val,
                    "severite": severite,
                    "severity": severite,
                    "statut": statut,
                    "status": statut,
                }
                INCIDENTS.append(new_incident)
                current_incidents = list(INCIDENTS)

            self._send_json(200, {
                "status": "ok",
                "incident": new_incident,
                "incidents": current_incidents,
            })
            return

        self.send_error(404, f"Route POST non trouvée: {path}")

    def log_message(self, format: str, *args: Any) -> None:
        """Format de log épuré pour la console."""
        print(f"[HTTP] {self.address_string()} - {format % args}")


def run_server(host: str = HOST, port: int = PORT) -> None:
    """Démarre le serveur HTTP temps réel."""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, CrisisHttpHandler)
    httpd.allow_reuse_address = True
    print(f"🚀 [Panique à Bord] Serveur actif sur http://127.0.0.1:{port} (Host: {host})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé.")
    finally:
        httpd.server_close()
        print(" Serveur arrêté proprement.")


if __name__ == "__main__":
    run_server()
