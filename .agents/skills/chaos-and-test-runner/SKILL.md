---
name: chaos-and-test-runner
description: >-
  Protocole d'audit de sécurité, de stress-test (Chaos Engineering) et de génération
  du Rapport de Tests officiel (docs/RAPPORT_DE_TESTS.md) pour le persona Videur.
---

# Skill : Audit Sécurité, Chaos & Rapport de Tests (`chaos-and-test-runner`)

Ce skill équipe **Videur** pour éprouver la robustesse de l'application locale, ouvrir des tickets d'incident sur GitHub en cas de faille, et générer le **Rapport de Tests (`docs/RAPPORT_DE_TESTS.md`)**.

## 1. Protocole d'Attaque & Stress-Test (`chaos_probe.py`)
Exécuter le script de sonde contre le serveur local (`http://127.0.0.1:8080`) :
```bash
python3 .agents/skills/chaos-and-test-runner/scripts/chaos_probe.py
```
Ce script teste :
1. **Injection XSS / Payload malveillant** dans la création d'incidents (`<script>alert('BREACH')</script>`).
2. **Coordonnées hors-limites / NaN** (`x: -99999, y: 99999, severity: 999`).
3. **Rafale de surcharge (Flood)** : envoi rapide d'incidents simultanés pour vérifier le plafonnement et la résilience mémoire.

## 2. Réaction en cas d'Anomalie Détectée
Si au moins un vecteur d'attaque n'est pas filtré/bloqué par le serveur :
1. **Ouvrir immédiatement un Ticket de Bug sur GitHub** via `github-ticket-orchestrator` :
   - Titre : `[BUG/SEC] Vulnérabilité Injection XSS & Validation Coordonnées hors-radar`
   - Label : `bug`
   - Contenu : Détail des charges utiles envoyées, comportement observé et exigences de remédiation.
2. Après correction par **Cambouis**, relancer `chaos_probe.py` ET la suite de tests unitaires (`python3 -m unittest discover -s tests -v`), puis clôturer le ticket avec les résultats `PASS`.

## 3. Structure Obligatoire de `docs/RAPPORT_DE_TESTS.md`
Le rapport final doit contenir :
- **Résumé Exécutif QA & Sécurité** (Score global, statut `GO POUR PRODUCTION`).
- **Matrice de Traçabilité des Tickets GitHub** (Tableau liant chaque Issue `#1` à `#5` aux tests associés et à leur statut `✅ PASS`).
- **Résultats des Tests Unitaires & Intégration** (Sortie exacte du runner `unittest` : moteur de dispatch, calcul de distance euclidienne, validation des entrées).
- **Bilan de la Campagne Chaos & Sécurité (Avant / Après Remédiation)** :
  - Tableau comparatif des 3 attaques avant et après le Ticket de Bug.
- **Diagramme Mermaid du Flux de Validation QA**.
