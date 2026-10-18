# 🎻 Kit du Chef d'Orchestre — Conducteur Live, Personas, Modèles & Skills

> [!TIP]
> **Le Ticket GitHub est la Seule Source de Vérité !**
> * **D'où viennent les détails des tickets lors de leur création ?** Du fichier [backlog_specs.json](.agents/skills/github-ticket-orchestrator/references/backlog_specs.json) intégré au skill `github-ticket-orchestrator`.
> * **Pourquoi c'est magique en live ?**
>   1. Au **Prompt 1**, `Patron` exécute `init-backlog` qui pousse sur GitHub 4 Issues complètes (User Story, Persona assigné, Skill requis, Spécifications détaillées et Critères d'acceptation `- [ ]`).
>   2. Aux **Prompts 2 à 6**, vous n'avez plus besoin d'expliquer quoi coder dans le chat ! Vous dites simplement : **« Patron, lis et traite les Issues #2 et #3 sur GitHub »**. `Patron` interroge l'API GitHub (`get-issue`), lit le cahier des charges directement sur GitHub et délègue aux bons agents !
>   3. *Bonus interactif avec la salle* : Vous pouvez même modifier le texte d'un ticket directement sur GitHub.com devant le public avant de lancer un prompt : `Patron` lira votre modification en direct !

---

## 1. Aperçu du Cahier des Charges Embarqué dans les Tickets GitHub ([backlog_specs.json](.agents/skills/github-ticket-orchestrator/references/backlog_specs.json))

Voici ce que `Patron` publie automatiquement sur `https://github.com/Yolepo/panique-a-bord/issues` lors de l'Acte I :

````carousel
```markdown
<!-- ISSUE #1 : [INIT] Socle serveur temps réel & Tableau de bord initial (Prototype Naïf) -->
## 🎯 User Story
En tant qu'opérateur de la cellule de crise Panique à Bord, je souhaite disposer d'un premier serveur web local fonctionnel affichant l'état brut de la flotte de drones et des incidents afin de valider la chaîne de déploiement.

## 👤 Persona Responsable
- **Principal** : `Cambouis` (`Model: pro`)
- **Contrainte Démo** : **NE PAS** activer le skill `mission-control-design` sur ce ticket (doit produire une interface HTML grise/claire basique pour démontrer l'effet Avant/Après au Ticket #2).

## 🔧 Spécifications Techniques
1. Créer un serveur HTTP en Python 3 standard (`server.py`) écoutant sur `http://127.0.0.1:8080`.
2. Exposer `GET /api/state`, `POST /api/incidents`, et `GET /api/docs`.
3. Créer une page `static/index.html` volontairement très sobre (fond gris/blanc, simple tableau HTML `<table>`).
4. Lancer le serveur en tâche de fond sur le port `8080`.
```
<!-- slide -->
```markdown
<!-- ISSUE #2 : [DESIGN] Refonte Cockpit Cyber-Crisis & Carte Radar HTML/CSS -->
## 🎯 User Story
En tant que Commandant de Salle de Crise, je veux remplacer le tableau HTML austère par un Cockpit « Mission Control » sombre et lisible avec une carte radar temps réel légère.

## 👤 Persona Responsable & Skill Obligatoire
- **Persona** : `Gouache` (`Model: pro`)
- **Skill à activer impérativement** : `mission-control-design`
- **Contrainte de Vélocité** : Générer un fichier `static/index.html` **compact (< 180 lignes)** en une seule passe, **sans Canvas 2D complexe**.

## 🎨 Spécifications Visuelles & UX (Version Express)
1. Appliquer la palette Cyber-Crisis (`#060b16`, `#00f0ff`, `#00ff9d`, `#ff2a5f`) et les panneaux **Glassmorphism**.
2. Intégrer une **Carte Radar 100 % HTML/CSS** (drones `🚁` et incidents `🚨` positionnés en `%` avec transition fluide + bouton « ⚡ Simuler Incident Critique »).
3. Intégrer **2 Onglets simples** : `🎯 COCKPIT` et `📖 CENTRE DOCUMENTAIRE & QA` (connecté à `/api/docs`).
```
<!-- slide -->
```markdown
<!-- ISSUE #3 : [CORE] Moteur télémétrique temps réel, Dispatch automatique & Tests unitaires -->
## 🎯 User Story
En tant que système de gestion de crise autonome, je dois déplacer les drones en temps réel sur la grille `[0..100, 0..100]` et affecter automatiquement l'unité disponible la plus proche à chaque nouvel incident.

## 👤 Personas Responsables
- **Réalisation** : `Cambouis` (`Model: pro`)
- **Peer Review Stricte** : `Pinailleur` (`Model: flash`) — *Exige 1 retouche qualité (typage + docstring `RG-02`) au 1er passage avant d'approuver le 2e commit.*

## ⚙️ Spécifications Algorithmiques (`core/engine.py`)
1. Flotte d'au moins 4 drones (`PAB-01` à `PAB-04`) avec états `IDLE`, `EN_ROUTE`, `ON_SITE`.
2. **Algorithme de Dispatch Automatique (RG-02)** par distance euclidienne minimale parmi les drones `IDLE` ayant `battery > 15%`.
3. Boucle télémétrique `tick()` déplaçant les drones et résolvant les incidents à proximité (`distance < 3.0`).
4. Suite de tests unitaires `tests/test_engine.py` via `unittest`.
```
<!-- slide -->
```markdown
<!-- ISSUE #4 : [RELEASE] Campagne QA/Chaos, Rapport de Tests & Documentation 360° -->
## 👥 Personas Responsables (En Parallèle) & Peer Review
- **Persona QA** : `Videur` (`Model: flash`) avec le skill `chaos-and-test-runner`
- **Persona Doc** : `Greffier` (`Model: flash`) avec le skill `living-docs-360`
- **Peer Review Finale** : `Pinailleur` (`Model: flash`)

## 📚 Livrables Attendus dans `docs/`
1. `docs/RAPPORT_DE_TESTS.md` (Matrice de couverture des Tickets #1 à #5, sortie `unittest`, comparatif Avant/Après Chaos Probe).
2. `docs/MANUEL_UTILISATEUR.md` (Guide opérateur pas-à-pas).
3. `docs/DOC_FONCTIONNELLE.md` (Règles `RG-01` à `RG-04` + diagramme d'états Mermaid).
4. `docs/DOC_TECHNIQUE.md` (Architecture & Séquence en Mermaid, API REST, sécurité).
```
````

---

## 2. Les 6 Personas & 4 Skills Pré-installés dans `orchestre/` (À Parcourir Pendant l'Exécution des Prompts)

Tous les fichiers de configuration (`.agents/personas/`, `.agents/skills/` et `AGENTS.md`) sont déjà en place dans le dossier `orchestre/`. Vous n'avez rien à saisir ni copier à la main : **pendant que les agents travaillent sur chaque prompt**, ouvrez les fichiers correspondants dans l'IDE pour les commenter au public (zéro temps mort !).

| Persona | Fichier | Modèle | Rôle & Moment idéal pour le montrer à l'écran |
| :--- | :--- | :--- | :--- |
| **`Patron`** | [patron.md](.agents/personas/patron.md) | **`pro`** | **Pendant le Prompt 1** : Montrer l'interdiction de coder seul, le routage `pro`/`flash` et la règle de relecture par `Pinailleur`. |
| **`Cambouis`** | [cambouis.md](.agents/personas/cambouis.md) | **`pro`** | **Pendant le Prompt 2** : Montrer ses consignes backend Python standard, l'algorithme `RG-02` et l'interdiction de fermer ses propres tickets. |
| **`Pinailleur`** | [pinailleur.md](.agents/personas/pinailleur.md) | **`flash`** | **Pendant les Prompts 2 & 3** : Montrer ses consignes courtes et humaines, l'inspection `git show HEAD` et le retour exigé au 1er passage sur le ticket 3. |
| **`Gouache`** | [gouache.md](.agents/personas/gouache.md) | **`pro`** | **Pendant le Prompt 3** : Montrer le contraste sans/avec le skill [mission-control-design](.agents/skills/mission-control-design/SKILL.md) (< 180 lignes, radar HTML/CSS). |
| **`Videur`** | [videur.md](.agents/personas/videur.md) | **`flash`** | **Pendant les Prompts 4 & 5** : Montrer le skill [chaos-and-test-runner](.agents/skills/chaos-and-test-runner/SKILL.md) et l'ouverture automatique d'un ticket `[BUG/SEC]`. |
| **`Greffier`** | [greffier.md](.agents/personas/greffier.md) | **`flash`** | **Pendant le Prompt 6** : Montrer le skill [living-docs-360](.agents/skills/living-docs-360/SKILL.md) qui structure les 3 manuels et schémas Mermaid. |

---

## 3. Le Conducteur de Prompts Ultra-Concis (Piloté par les Tickets + Peer Review Systématique)

Puisque **les Personas et Skills sont déjà dans le workspace** et que **tout le détail technique est dans les Issues GitHub**, vos 6 prompts en live sont courts, fluides et directs :

### 🎬 Prompt 1 — Acte I : Enregistrement du Comité, Création du Dépôt GitHub & Publication du Backlog

```text
Nous démarrons la démonstration dans le répertoire courant.
1. Lis AGENTS.md ainsi que les 6 fiches de .agents/personas/ (patron, gouache, cambouis, pinailleur, videur, greffier) et enregistre les sous-agents (gouache, cambouis, pinailleur, videur, greffier) via define_subagent.
2. En tant que Patron, active le skill github-ticket-orchestrator :
   - Crée le dépôt public "panique-a-bord" sur le compte GitHub Yolepo, initialise git localement et configure le remote origin.
   - Exécute la commande "init-backlog Yolepo/panique-a-bord" du skill pour publier les 4 Tickets GitHub détaillés.
3. Affiche le tableau de notre comité des 6 agents (Persona, Modèle, Rôle) et les liens cliquables vers les 4 Issues GitHub créées.
```
*👉 **Pendant l'exécution (~20s)** : Ouvrez `AGENTS.md` et `.agents/personas/patron.md` à l'écran pour expliquer le routage `pro`/`flash`. Dès que le prompt termine, cliquez sur l'Issue #2 ou #3 sur GitHub devant le public !*

---

### 🎬 Prompt 2 — Acte II.A : Traitement de l'Issue #1 + 1re Peer Review de `Pinailleur`

```text
Patron, consulte les spécifications complètes de l'Issue #1 sur GitHub (Yolepo/panique-a-bord via get-issue), fais-la réaliser et commiter par Cambouis, puis fais relire le commit et clôturer le ticket par Pinailleur.
```
*👉 **Pendant l'exécution** : Parcourez `.agents/personas/cambouis.md` et `.agents/personas/pinailleur.md` avec le public. Puis ouvrez `http://127.0.0.1:8080` à droite de l'écran pour montrer le prototype « naïf » (sans le skill design) et la validation de `Pinailleur` sur l'Issue #1.*

---

### 🎬 Prompt 3 — Acte II.B : Traitement en Parallèle des Issues #2 et #3 + Retour de Peer Review sur #3

```text
Patron, récupère sur GitHub le cahier des charges des Issues #2 et #3 (via get-issue), lance leur implémentation en PARALLÈLE par Gouache et Cambouis, puis fais passer Pinailleur en Peer Review sur chaque commit (si Pinailleur demande une retouche sur l'Issue #3, fais-la corriger par Cambouis avant l'approbation finale et la clôture).
```
*👉 **Pendant l'exécution** : Parcourez `.agents/personas/gouache.md` et `.agents/skills/mission-control-design/SKILL.md`. Montrez ensuite le double effet :*
1. *Le navigateur bascule en **Cockpit Cyber-Crisis** avec radar HTML/CSS et l'Issue #2 est validée et fermée par `Pinailleur`.*
2. *Sur l'Issue #3, **`Pinailleur` refuse de fermer le ticket au 1er passage** et demande en commentaire le typage Python et la docstring `RG-02`. `Cambouis` repasse aussitôt en 2e commit, que `Pinailleur` valide et clôture !*

---

### 🎬 Prompt 4 — Acte III.A : Audit Chaos par `Videur` & Ouverture Automatique de l'Issue #5 (`[BUG/SEC]`)

```text
Patron, mobilise Videur avec son skill "chaos-and-test-runner" pour auditer et attaquer l'application locale (http://127.0.0.1:8080). S'il détecte une faille, il doit ouvrir immédiatement un Ticket de Bug détaillé sur GitHub.
```
*👉 **Pendant l'exécution** : Ouvrez `.agents/personas/videur.md` et `.agents/skills/chaos-and-test-runner/SKILL.md`. Montrez ensuite l'Issue #5 `[BUG/SEC]` créée automatiquement sur GitHub par `Videur` !*

---

### 🎬 Prompt 5 — Acte III.B : Résolution de l'Issue #5 (`[BUG/SEC]`) + Peer Review + Contre-Audit

```text
Patron, consulte sur GitHub le nouveau Ticket de Bug [BUG/SEC] ouvert par Videur, fais corriger les vulnérabilités et ajouter les tests unitaires par Cambouis, fais relire le commit de correctif par Pinailleur, puis fais re-valider (tests + sonde chaos_probe.py) et clôturer le ticket par Videur.
```

---

### 🎬 Prompt 6 — Acte IV : Traitement en Parallèle de l'Issue #4 (`[RELEASE]`) + Peer Review Finale

```text
Patron, consulte sur GitHub le cahier des charges de l'Issue #4 ([RELEASE]), lance en PARALLÈLE Videur et Greffier pour générer le Rapport de Tests et les 3 documentations (Manuel Utilisateur, Doc Fonctionnelle, Doc Technique), puis fais relire le commit final et clôturer l'Issue #4 par Pinailleur.
```
*👉 **Pendant l'exécution** : Parcourez `.agents/personas/greffier.md` et `.agents/skills/living-docs-360/SKILL.md`, puis cliquez sur l'onglet **`📖 CENTRE DOCUMENTAIRE & QA`** dans `http://127.0.0.1:8080` pour admirer les 4 livrables !*
