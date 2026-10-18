---
name: github-ticket-orchestrator
description: >-
  Orchestre le cycle de vie complet du développement et de la Peer Review autour des tickets GitHub (Issues)
  du dépôt Yolepo/panique-a-bord via le client Python sans dépendance gh_api.py.
  Contient le backlog détaillé dans references/backlog_specs.json.
  À activer dès qu'il faut initialiser le dépôt, créer le backlog, lire les spécifications
  d'un ticket (get-issue), commenter l'avancement, publier une Peer Review de commit ou clôturer une issue.
---

# Skill : Orchestration & Peer Review par Tickets GitHub (`github-ticket-orchestrator`)

Ce skill permet à **Patron** et à tous les agents du comité (`Gouache`, `Cambouis`, `Pinailleur`, `Videur`, `Greffier`) de travailler en synchronisation totale avec les **Issues GitHub** du dépôt `Yolepo/panique-a-bord`, où **le corps du ticket GitHub est la seule source de vérité fonctionnelle et technique**.

## Outil CLI intégré & Spécifications du Backlog
* Script CLI : `python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py`
* Cahier des charges des 4 tickets initiaux : `.agents/skills/github-ticket-orchestrator/references/backlog_specs.json`

## Commandes de Référence

1. **Créer le dépôt sur GitHub** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py create-repo panique-a-bord --description "Panique à Bord - Tour de Contrôle Temps Réel orchestrée par Agents IA"
   ```
2. **Initialiser tout le Backlog détaillé sur GitHub (Issues #1 à #4 avec User Stories & Critères d'Acceptation)** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py init-backlog Yolepo/panique-a-bord
   ```
3. **Lire le cahier des charges complet d'un Ticket (OBLIGATOIRE avant de coder ou de relire)** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py get-issue Yolepo/panique-a-bord <NUMERO>
   ```
4. **Créer un Ticket de Bug / Sécurité à la volée (ex: par `Videur`)** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py create-issue Yolepo/panique-a-bord --title "[BUG/SEC] ..." --body "Description..." --labels "bug"
   ```
5. **Commenter la prise en charge, la livraison ou une demande de modification (`CHANGES REQUESTED`)** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py comment-issue Yolepo/panique-a-bord <NUMERO> --body "🔍 **[Pinailleur | Modèle: flash]** ..."
   ```
6. **Clôturer un Ticket après Peer Review approuvée par `Pinailleur`** :
   ```bash
   python3 .agents/skills/github-ticket-orchestrator/scripts/gh_api.py close-issue Yolepo/panique-a-bord <NUMERO> --comment "🔍 **[Pinailleur | Modèle: flash] ✅ PEER REVIEW APPROUVÉE** (Commit <SHA>) : ..."
   ```

## Règles Obligatoires du Workflow
1. **Le Ticket GitHub est la seule source de vérité** : Lorsqu'on demande à `Patron` de traiter l'Issue `#N`, il DOIT d'abord exécuter `get-issue Yolepo/panique-a-bord N` pour lire la User Story, le Persona responsable, le Skill éventuel à activer et les Critères d'Acceptation (DoD).
2. **Peer Review Systématique de chaque Commit par `Pinailleur`** :
   - Les agents réalisateurs (`Cambouis`, `Gouache`, `Greffier`) commitent, poussent et commentent leur livraison sur GitHub **sans fermer le ticket**.
   - `Pinailleur` (`Model: flash`) inspecte le commit (`git show HEAD`) et publie sa revue sur l'Issue GitHub avant de la clôturer (avec 1 aller-retour `⚠️ CHANGES REQUESTED` sur l'Issue #3 avant l'approbation finale).
3. **Traçabilité des Personas & Modèles** : Chaque commentaire posté sur GitHub doit commencer par l'icône, le nom du Persona et son modèle (`👔 [Patron | Modèle: pro]`, `🎨 [Gouache | Modèle: pro]`, `⚙️ [Cambouis | Modèle: pro]`, `🔍 [Pinailleur | Modèle: flash]`, `🛡️ [Videur | Modèle: flash]`, `📚 [Greffier | Modèle: flash]`).
4. **Commits liés** : Chaque commit Git doit mentionner le numéro du ticket (`Refs #1`, `Refs #2`, `Refs #3`, etc.).
