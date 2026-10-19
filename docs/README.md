# Panique à Bord - Système de Gestion de Crise

Bienvenue dans le référentiel opérationnel de **Panique à Bord**.

## Description
Panique à Bord est un système de dispatch automatique et de télémétrie en temps réel pour flotte de drones de surveillance et d'intervention d'urgence.

## Architecture
- **Serveur HTTP (`server.py`)** : Développé en Python 3 standard (aucun framework externe), écoute sur le port `8080`.
- **API REST** :
  - `GET /api/state` : Télémétrie de la flotte et incidents en cours.
  - `POST /api/incidents` : Enregistrement d'un nouvel incident.
  - `GET /api/docs` : Exposition dynamique de la documentation Markdown.
- **Tableau de Bord (`static/index.html`)** : Interface web de supervision.

## Lancement
```bash
python3 server.py
```
Accédez ensuite à [http://127.0.0.1:8080](http://127.0.0.1:8080).
