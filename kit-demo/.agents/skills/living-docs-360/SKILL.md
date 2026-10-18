---
name: living-docs-360
description: >-
  Génère la documentation officielle complète à partir du code réel et des tickets GitHub :
  Manuel Utilisateur (docs/MANUEL_UTILISATEUR.md), Documentation Fonctionnelle
  (docs/DOC_FONCTIONNELLE.md) et Documentation Technique (docs/DOC_TECHNIQUE.md) avec schémas Mermaid.
---

# Skill : Usine Documentaire 360° (`living-docs-360`)

Ce skill est utilisé par **Greffier** en fin de cycle pour produire les 3 piliers documentaires du projet, synchronisés avec le code réel et accessibles directement depuis l'interface de **Panique à Bord**.

## 1. `docs/MANUEL_UTILISATEUR.md` (Cible : Opérateurs de Salle de Crise)
Structure obligatoire :
1. **Présentation du Cockpit Panique à Bord** (Vue d'ensemble et objectifs opérationnels).
2. **Lecture du Radar Tactique & Code Couleur** (Unités de secours en cyan/émeraude, niveaux d'alerte ambre/cramoisi, vecteurs d'intervention).
3. **Guide Pas-à-Pas des Opérations** :
   - Déclencher ou déclarer un incident sur la grille.
   - Observer et superviser le dispatch automatique des drones.
   - Activer le mode Simulation de Crise / Stress-Test.
   - Consulter le journal d'audit sécurité et le centre documentaire intégré.
4. **FAQ & Résolution des situations d'urgence (DEFCON)**.

## 2. `docs/DOC_FONCTIONNELLE.md` (Cible : Product Owners & Experts Métier)
Structure obligatoire :
1. **Vision Produit & Personas Métiers**.
2. **Catalogue des Règles de Gestion (RG)** :
   - `RG-01` : Calcul de priorité et niveaux de criticité (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
   - `RG-02` : Algorithme d'affectation automatique de l'unité disponible la plus proche (distance euclidienne pondérée par la batterie et la vitesse).
   - `RG-03` : Cycle de vie d'un incident (`DETECTED` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED`) avec diagramme d'états Mermaid (`stateDiagram-v2`).
   - `RG-04` : Règles de protection anti-injection et plafonnement de la file d'incidents actifs.
3. **Matrice de Couverture Fonctionnelle par Ticket GitHub (`#1` à `#5`)**.

## 3. `docs/DOC_TECHNIQUE.md` (Cible : Architectes & Développeurs)
Structure obligatoire :
1. **Architecture Globale** avec diagramme Mermaid (`flowchart LR` ou `flowchart TD`).
2. **Flux Temps Réel & API REST** avec diagramme de séquence Mermaid (`sequenceDiagram`) illustrant la boucle de simulation, l'API et le rafraîchissement temps réel.
3. **Contrat des Endpoints API** (`GET /api/state`, `POST /api/incidents`, `POST /api/simulate`, `GET /api/docs`).
4. **Sécurité & Durcissement (Hardening)** : Détail des filtres anti-XSS, validation stricte des schémas et bornage des coordonnées mis en place suite à l'audit de **Videur**.
5. **Guide d'Installation, Exécution Locale et Tests Automatisés**.
