# 🚨 Manuel Utilisateur — Cockpit Panique à Bord

> **Système** : Panique à Bord — Mission Control & Dispatch Tactique  
> **Auteur** : `Greffier` (`Model: flash`) — Usine Documentaire `living-docs-360`  
> **Référence** : Issue GitHub [#4](https://github.com/Yolepo/panique-a-bord/issues/4)  
> **Audience** : Opérateurs de salle de crise, superviseurs d'intervention, coordinateurs de secours  
> **Version** : 1.0.0 (Release Homologuée)  

---

## 1. 🎯 Présentation du Cockpit Panique à Bord

Le cockpit **Panique à Bord** est l'interface opérationnelle unifiée destinée aux opérateurs de cellule de crise. Il permet de superviser en temps réel une flotte de drones d'intervention autonome déployés sur un site sensible et d'orchestrer la réponse immédiate aux incidents détectés.

### Objectifs Opérationnels
- **Visibilité Télémétrique Instantanée** : Surveillance permanente de la position cartésienne $(X, Y)$, de l'état de charge de batterie et du statut opérationnel des drones de secours.
- **Réduction du Temps de Réaction (RTT)** : Détection et affectation automatique des vecteurs de réponse dès la survenue d'une alerte critique.
- **Résilience et Sécurité Renforcée** : Filtrage strict des flux d'événements, neutralisation des tentatives d'injection malveillante et contention de charge en cas de tempête d'alertes.
- **Accès Intégré aux Référentiels** : Consultation en un clic des rapports d'homologation QA, des règles fonctionnelles et de la documentation d'architecture technique.

### Organisation de l'Interface
Le bandeau supérieur offre une navigation rapide entre deux espaces de travail :
1. **🎯 COCKPIT (Vue Opérationnelle)** : Vue active par défaut affichant la carte tactique radar, les compteurs dynamiques d'unités et d'incidents, ainsi que les tableaux de télémétrie de flotte et d'alertes en cours.
2. **📖 CENTRE DOCUMENTAIRE & QA** : Console de consultation in-app des documents techniques et rapports d'audit synchronisés en direct via l'API `/api/docs`.

---

## 2. 🗺️ Lecture du Radar Tactique & Code Couleur

La carte tactique radar modélise un espace d'intervention bidimensionnel orthonormé délimité par des coordonnées cartésiennes allant de `(0, 0)` en haut à gauche jusqu'à `(100, 100)` en bas à droite.

```
(0,0) -------------------------------- (100,0)
  |                                       |
  |         🚁 PAB-01 (IDLE)              |
  |                                       |
  |                    🚨 INC-01 (CRITIQUE)|
  |                                       |
  |         🚁 PAB-02 (EN_ROUTE)          |
  |                                       |
(0,100) ------------------------------ (100,100)
```

### Unités de Secours (Flotte de Drones)
Les drones sont représentés sur le radar par l'icône `🚁 PAB-XX` fluorescente et répertoriés dans la table télémétrique :
- **Cyan Électrique (`#00f0ff`)** : Symbole identifiant les drones en stationnement ou en transit vectoriel avec halo de visibilité.
- **Jauges d'Énergie (Batterie)** :
  - **Émeraude (`#00ff9d`)** : Niveau optimal supérieur à **50%**. L'unité est pleinement opérationnelle pour des missions longue portée.
  - **Ambre (`#ffb800`)** : Niveau intermédiaire compris entre **21% et 50%**. L'unité reste éligible au dispatch mais doit être surveillée.
  - **Cramoisi (`#ff2a5f`)** : Niveau critique inférieur ou égal à **20%**. Conformément à la règle `RG-02`, tout drone dont la batterie est inférieure ou égale à **15%** est automatiquement exclu du dispatch et reste consigné à sa position pour recharge.
- **Statuts Opérationnels** :
  - `IDLE` : Drone en attente à sa position, rechargeant activement sa batterie (+0.1% par pas de temps).
  - `EN_ROUTE` : Drone mobilisé et en vol vectoriel vers un incident cible, consommant son énergie (-0.2% par pas de temps).

### Niveaux d'Alerte des Incidents
Les incidents sont signalés sur la carte radar par l'icône clignotante `🚨 INC-XX` et classés selon leur niveau de criticité :
- **Cramoisi Clignotant (`#ff2a5f` / animation pulse)** :
  - `CRITICAL` / `CRITIQUE` : Péril imminent nécessitant une neutralisation d'urgence (intrusion armée, surcharge réacteur, explosion).
  - `HIGH` / `HAUTE` : Incident majeur (départ de feu, fuite chimique toxique).
- **Ambre Lumineux (`#ffb800`)** :
  - `MEDIUM` / `MOYENNE` : Incident opérationnel standard (fumée suspecte, dysfonctionnement vanne).
  - `LOW` / `FAIBLE` : Anomalie mineure ou contrôle préventif (capteur décalibré).

---

## 3. 📋 Guide Pas-à-Pas des Opérations

### 3.1 Déclencher ou Déclarer un Incident

L'opérateur dispose de trois méthodes pour enregistrer une alerte sur la grille opérationnelle :

#### Méthode A : Clic Direct sur le Radar Tactique (Recommandée)
1. Positionnez le pointeur en forme de réticule (`crosshair`) sur la zone géographique visée dans la boîte radar.
2. Effectuez un simple clic gauche : le cockpit calcule instantanément les coordonnées normalisées du point d'impact (clamping défensif de sécurité entre 10% et 90%).
3. Un incident de criticité `CRITICAL` avec titre d'alerte contextuel est généré et transmis au serveur via l'API `POST /api/incidents`.

#### Méthode B : Bouton d'Urgence « ⚡ Simuler Incident Critique »
1. Cliquez sur le bouton rouge `⚡ Simuler Incident Critique` situé au-dessus de la carte tactique.
2. Une alerte critique est injectée aléatoirement dans le quadrillage sécurisé `[10.0, 90.0]`.

#### Méthode C : Déclaration Manuelle via Appel d'API Externe
Pour interconnecter des capteurs tiers ou injecter un incident précis :
```bash
curl -X POST http://127.0.0.1:8080/api/incidents \
  -H "Content-Type: application/json" \
  -d '{"titre": "Détection thermique anormale", "severite": "CRITICAL", "x": 45.5, "y": 62.0}'
```

### 3.2 Superviser le Dispatch Automatique

Dès qu'un incident passe au statut `DETECTED` :
1. **Élection Euclidienne (`RG-02`)** : Le moteur calcule la distance spatiale vers tous les drones disponibles (`IDLE` et batterie > 15%).
2. **Attribution Immédiate** : Le drone le plus proche bascule au statut `EN_ROUTE`, verrouille l'identifiant de la cible (`target_id = INC-XX`) et l'incident passe à l'état `ASSIGNED`.
3. **Trajectoire Vectorielle** : À chaque pulsation de télémétrie (500 ms), le drone progresse de 5.0 unités de distance vers l'incident.
4. **Neutralisation & Clôture** : Dès que la distance séparant le drone de l'incident devient strictement inférieure à 3.0 unités (zone de contact opérationnel), l'incident passe au statut `RESOLVED` et disparaît du radar actif. Le drone bascule en statut `IDLE` et commence sa recharge énergétique sur place.

### 3.3 Consulter le Centre Documentaire & QA

1. Cliquez sur le bouton de navigation `📖 CENTRE DOCUMENTAIRE & QA` dans l'en-tête du cockpit.
2. La vue affiche la liste des manuels et rapports Markdown disponibles dans le répertoire `docs/` (`MANUEL_UTILISATEUR.md`, `DOC_FONCTIONNELLE.md`, `DOC_TECHNIQUE.md`, `RAPPORT_DE_TESTS.md`).
3. Cliquez sur l'un des boutons pour charger et lire instantanément son contenu complet.
4. Utilisez le bouton `🔄 Rafraîchir Docs` pour recharger les fichiers en cas de mise à jour serveur.

---

## 4. 🚨 Situations d'Urgence & Guide DEFCON

Pour adapter la posture de l'équipe de crise à la criticité de l'environnement, le protocole DEFCON ci-dessous s'applique :

| Niveau | Désignation | Seuil Opérationnel | Actions Immédiates de l'Opérateur |
| :---: | :---: | :---: | :--- |
| **DEFCON 5** | **Nominal** | 0 incident actif, 100% de la flotte opérationnelle | Veille passive, maintien des batteries au repos. |
| **DEFCON 4** | **Vigilance** | 1 à 3 incidents actifs | Supervision visuelle des trajectoires de ralliement des drones. |
| **DEFCON 3** | **Alerte Renforcée** | 4 à 7 incidents actifs | Vérification des réserves de batterie et couverture spatiale des quadrants. |
| **DEFCON 2** | **Crise Majeure** | 8 à 9 incidents actifs | Priorisation des alertes `CRITICAL`, surveillance du seuil de saturation. |
| **DEFCON 1** | **Saturation / Évacuation** | 10 incidents actifs (`Plafond RG-04 atteint`) | Rejet des nouvelles requêtes (HTTP 429). Attendre la résolution des incidents prioritaires. |

### FAQ Opérationnelle

#### Q1 : Un clic sur la carte radar ou un appel API me renvoie une erreur HTTP 429 (« Active incident queue limit reached (RG-04) ») ?
> **Cause** : Le plafond de sécurité de **10 incidents actifs simultanés** (`MAX_ACTIVE_INCIDENTS`) a été atteint afin de prémunir le serveur contre un déni de service (DoS).  
> **Résolution** : Aucun nouvel incident ne peut être enregistré tant qu'au moins une intervention en cours n'est pas finalisée (`RESOLVED`). Laissez les drones converger vers leurs cibles ; la file se débloquera automatiquement dès la libération d'un créneau.

#### Q2 : Pourquoi un incident reste-t-il au statut `DETECTED` sans qu'aucun drone ne parte ?
> **Cause** : Deux explications possibles :
> 1. Tous les drones sont déjà affectés (`EN_ROUTE`) sur d'autres incidents.
> 2. Les drones disponibles ont une réserve de batterie inférieure ou égale à 15% (seuil d'inégibilité `RG-02`).  
> **Résolution** : Attendez la fin d'une intervention ou la recharge passive des batteries (+0.1% par demi-seconde au repos). Le moteur affectera automatiquement l'incident dès qu'un drone refranchit le seuil de 15% et repasse `IDLE`.

#### Q3 : Le radar rejette-t-il les clics sur les bordures extrêmes ?
> **Réponse** : Non, le radar protège l'opérateur en appliquant une projection géométrique avec seuils d'inclusion minimaux de 10% et maximaux de 90%, garantissant que toute cible reste visible et accessible par les drones sans sortir des bornes matérielles.
