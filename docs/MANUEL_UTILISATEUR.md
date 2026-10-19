# Manuel Utilisateur — Cockpit Panique à Bord

> **Système Opérationnel de Gestion de Crise et de Télémétrie de Drones**  
> *Référentiel Utilisateur — Version 1.0.0 (Homologation Release #4)*  
> *Auteur : Greffier — Responsable Documentation Technique*

---

## 1. Présentation du Cockpit Panique à Bord

Le système **Panique à Bord** est une plateforme de commandement tactique (*Mission Control*) conçue pour la supervision en temps réel et le dispatch autonome d'une flotte de drones d'intervention rapide sur un théâtre d'opérations spatialisé.

### Objectifs Opérationnels
- **Surveillance Continue** : Visualisation instantanée de la flotte de drones et des incidents déclarés sur une grille tactique normalisée `[0..100, 0..100]`.
- **Réponse Autonome** : Algorithme de routage et d'affectation automatique sans latence humaine, optimisant le temps de réponse d'urgence.
- **Résilience et Légèreté** : Interface web ergonomique sans dépendance logicielle lourde, exploitable depuis n'importe quel poste de crise standard.
- **Accessibilité Documentaire** : Intégration directe du corpus documentaire et des rapports de tests dans le cockpit.

---

## 2. Lecture du Radar Tactique & Codes Couleurs

L'interface principale repose sur un thème visuel **Cyber-Crisis** haute visibilité assurant une lisibilité maximale en ambiance de salle de commandement.

```
+------------------------------------------------------------------------+
| 🚨 PANIQUE À BORD | MISSION CONTROL       [🎯 COCKPIT] [📖 CENTRE DOC] |
+-----------------------------------+------------------------------------+
| 🛰️ CARTE RADAR TACTIQUE          | 🚁 FLOTTE DE DRONES                |
| (Grille 100x100)                  | PAB-01 Alpha [IDLE] 98%            |
|                                   | PAB-02 Bravo [EN_ROUTE] 92%        |
|      🚁 PAB-01                    +------------------------------------+
|            ↘                      | 🚨 INCIDENTS DÉTECTÉS              |
|              🚨 INC-01            | INC-01 Incendie Portuaire [HIGH]   |
+-----------------------------------+------------------------------------+
```

### Grille Radar Tactique
- **Repère spatial** : Coordonnées cartésiennes $(X, Y)$ comprises entre 0 et 100.
  - Le point $(0, 0)$ correspond au coin supérieur gauche du secteur.
  - Le point $(100, 100)$ correspond au coin inférieur droit du secteur.
- **Vecteurs d'intervention** : Les unités en déplacement bénéficient d'une interpolation CSS fluide (`transition: all 0.4s linear`), reflétant le vecteur de convergence vers l'incident assigné.

### Codes Couleurs & Statuts

| Élément | Couleur / Hex | Icône / Badge | Description Opérationnelle |
| :--- | :--- | :---: | :--- |
| **Drone Disponible** | Cyan (`#00f0ff`) | `🚁` `IDLE` | Drone en stationnaire ou patrouille passive, prêt pour une nouvelle assignation. |
| **Drone en Transit** | Ambre (`#ffb800`) | `🚁` `EN_ROUTE` | Unité en acheminement vectoriel actif vers les coordonnées de l'incident. |
| **Drone sur Cible** | Émeraude (`#00ff9d`) | `🚁` `ON_SITE` | Unité positionnée sur zone d'intervention. |
| **Batterie Nominale** | Émeraude (`#00ff9d`) | `XX%` | Capacité énergétique $> 30\%$, unité pleinement opérationnelle. |
| **Batterie Critique** | Cramoisi (`#ff2a5f`) | `XX%` | Capacité $\le 30\%$. Si la batterie tombe à $\le 15\%$, le drone est automatiquement exclu du dispatch (RG-02). |
| **Incident Détecté** | Cramoisi (`#ff2a5f`) | `🚨` `DETECTED` | Alerte active non encore assignée ou en attente d'unité disponible. Pulsation radar active. |
| **Incident Assigné** | Ambre (`#ffb800`) | `🚨` `ASSIGNED` | Unité la plus proche dépêchée sur les lieux. |
| **Incident Résolu** | Archivé / Masqué | `RESOLVED` | Objectif sécurisé. Le drone est automatiquement libéré en statut `IDLE`. |

---

## 3. Guide Pas-à-Pas des Opérations

### 3.1. Accéder au Cockpit de Crise
1. Ouvrir un navigateur moderne (Chrome, Firefox, Safari, Edge).
2. Se connecter sur l'adresse du serveur local :
   ```text
   http://127.0.0.1:8080
   ```
3. L'onglet par défaut `🎯 COCKPIT` s'active immédiatement et initialise la boucle de rafraîchissement télémétrique (1 interrogation par seconde).

### 3.2. Déclencher ou Déclarer un Incident
Deux méthodes sont à la disposition de l'opérateur :

#### Méthode Rapide (Cockpit IHM) :
1. Repérer le bouton d'action d'urgence rouge dans l'en-tête supérieur droit : **« ⚡ Simuler Incident Critique »**.
2. Un clic déclenche l'émission immédiate d'une requête `POST /api/incidents` avec :
   - Titre : `Alerte Critique Brèche Portuaire`
   - Sévérité : `CRITICAL`
   - Coordonnées $X$ et $Y$ générées aléatoirement sur la zone d'intervention $[10..90]$.
3. L'incident apparaît instantanément sur la grille radar sous forme d'une pastille rouge clignotante (`🚨`).

#### Méthode Programmatique (API REST / Terminal de Crise) :
Pour soumettre un incident précis avec description contextuelle, envoyer une requête HTTP standard :
```bash
curl -X POST http://127.0.0.1:8080/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Collision de convoi fluvial",
    "description": "Brèche coque tribord secteur 4",
    "x": 45.0,
    "y": 60.0,
    "severite": "HIGH"
  }'
```

### 3.3. Observer et Superviser le Dispatch Automatique
Dès la prise en compte de l'incident :
1. Le moteur de crise exécute l'algorithme `RG-02` à chaque pas temporel (1 seconde) :
   - Il identifie tous les drones au statut `IDLE` dont la batterie est strictement supérieure à 15%.
   - Il calcule la distance euclidienne séparant chaque drone disponible de l'incident.
   - Il sélectionne l'unité la plus proche et la verrouille en statut `EN_ROUTE`.
2. Sur la carte radar, l'opérateur observe le déplacement fluide de l'icône de drone `🚁` vers l'incident `🚨`.
3. Dès que l'unité franchit le seuil de proximité tactique ($\text{distance} < 3.0$ unités) :
   - L'incident bascule automatiquement au statut `RESOLVED` et disparaît du radar actif.
   - Le drone libéré repasse instantanément au statut `IDLE` et redevient éligible à de nouveaux appels.

### 3.4. Consulter le Centre Documentaire et QA Intégré
1. Cliquer sur l'onglet **`📖 CENTRE DOCUMENTAIRE & QA`** dans la barre de navigation.
2. La vue bascule sans rechargement de page.
3. Des boutons dynamiques générés à partir des fichiers présents dans `docs/` s'affichent :
   - `MANUEL_UTILISATEUR.md`
   - `DOC_FONCTIONNELLE.md`
   - `DOC_TECHNIQUE.md`
   - `RAPPORT_DE_TESTS.md`
   - `README.md`
4. Cliquer sur un bouton pour afficher instantanément l'intégralité du document technique dans la visionneuse intégrée.

---

## 4. FAQ & Procédures d'Urgence (DEFCON)

### Foire Aux Questions (FAQ)

#### Q1 : Pourquoi un incident reste-t-il au statut `DETECTED` sans qu'aucun drone ne bouge ?
**Cause opérationnelle** : Soit l'ensemble des 4 drones sont déjà en mission (`EN_ROUTE`), soit la batterie des unités restantes est inférieure ou égale au seuil de sécurité opérationnelle de 15% (`min_battery`).  
**Action opérateur** : Patienter jusqu'à la résolution d'une intervention en cours ; dès qu'un drone repasse `IDLE`, l'algorithme lui affectera immédiatement l'incident prioritaire au cycle suivant.

#### Q2 : Que se passe-t-il si un opérateur saisit des coordonnées hors de la grille radar ?
**Mesure de protection** : Suite au durcissement de sécurité (Ticket #5), toute requête soumettant des coordonnées hors de l'intervalle $[0..100]$ ou non numériques est immédiatement rejetée avec le code `HTTP 400 Bad Request` et le message `"Coordonnées hors limites [0..100]"`. L'intégrité de la simulation est préservée.

#### Q3 : Les caractères spéciaux ou balises HTML dans les descriptions d'incidents sont-ils dangereux ?
**Mesure de protection** : Le serveur intègre un assainissement systématique via `html.escape`. Tout script ou balise injectée (`<script>`, `<img onerror=...>`) est neutralisé à l'entrée et affiché sous forme textuelle inoffensive.

---

### Grille d'Alerte et Niveaux DEFCON

| Niveau | Seuil Opérationnel | État de la Flotte | Recommandation Tactique |
| :---: | :--- | :--- | :--- |
| **DEFCON 5** | 0 incident actif | 4 drones disponibles (`IDLE`) | Veille standard. Surveillance des niveaux de charge des batteries. |
| **DEFCON 4** | 1 à 2 incidents actifs | Au moins 2 drones en intervention | Opération nominale. Supervision visuelle du bon acheminement des unités. |
| **DEFCON 3** | 3 à 4 incidents actifs | Tous les drones mobilisés | Saturation imminente. Vérifier l'ordre de traitement des priorités. |
| **DEFCON 2** | Incidents en file d'attente | 100% de la flotte engagée + alertes `DETECTED` | Crise majeure. Interdire les simulations de complaisance. Préparer le déploiement d'unités de réserve. |
| **DEFCON 1** | Incident critique non pris en charge + batteries < 20% | Flotte en rupture d'énergie | Alerte rouge absolue. Évacuation des secteurs et bascule sur protocole de secours physique. |
