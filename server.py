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
import time
from typing import Any, Dict, List
import urllib.parse

from core.engine import SimulationEngine

HOST = "0.0.0.0"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOCS_DIR = BASE_DIR / "docs"

# Moteur télémétrique temps réel et verrou de synchronisation
ENGINE = SimulationEngine()
STATE_LOCK = ENGINE.lock



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
            state_data = ENGINE.get_state()
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

            new_incident = ENGINE.add_incident(data)
            self._send_json(200, {
                "status": "ok",
                "incident": new_incident,
                "incidents": ENGINE.get_incidents(),
            })
            return

        self.send_error(404, f"Route POST non trouvée: {path}")

    def log_message(self, format: str, *args: Any) -> None:
        """Format de log épuré pour la console."""
        print(f"[HTTP] {self.address_string()} - {format % args}")


def simulation_worker(engine: SimulationEngine, interval: float = 1.0) -> None:
    """Boucle d'exécution périodique du moteur de simulation."""
    while True:
        try:
            engine.tick()
        except Exception as exc:
            print(f"[ENGINE ERROR] {exc}")
        time.sleep(interval)


def run_server(host: str = HOST, port: int = PORT) -> None:
    """Démarre le serveur HTTP temps réel."""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Démarrage de la boucle télémétrique en tâche de fond
    sim_thread = threading.Thread(target=simulation_worker, args=(ENGINE, 1.0), daemon=True)
    sim_thread.start()
    print("🛰️ [SimulationEngine] Moteur télémétrique temps réel démarré (1 tick/sec)")

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
