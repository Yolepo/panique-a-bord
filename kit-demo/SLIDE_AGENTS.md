# Slide 1 — Le Comité des 6 Agents & L'Architecture Globale

```mermaid
flowchart TD
    GH[("📋 GitHub Issues API\n(Seule Source de Vérité)")] <-->|"init-backlog, get-issue,\ncomment-issue, close-issue"| Patron["👔 Patron (Model: pro)\n(Tech Lead & Coordinateur)"]
    
    subgraph Comité ["⚡ Les 5 Agents Spécialisés"]
        Gouache["🎨 Gouache (Model: pro)\n(Front-end & Carte Radar HTML/CSS)"]
        Cambouis["⚙️ Cambouis (Model: pro)\n(Back-end Python, Moteur & Dispatch)"]
        Pinailleur["🔍 Pinailleur (Model: flash)\n(Peer Reviewer & Gardien des Commits)"]
        Videur["🛡️ Videur (Model: flash)\n(QA, Sécurité & Chaos Probe)"]
        Greffier["📚 Greffier (Model: flash)\n(Rédacteur Technique & Docs)"]
    end

    Patron -->|"Issue #1 (Socle) & Issue #3 (Moteur)\n+ Correctif Issue #5"| Cambouis
    Patron -->|"Issue #2 (Cockpit Radar\n+ skill mission-control-design)"| Gouache
    Patron -->|"Audit Chaos (ouvre Issue #5)\n+ Issue #4 (Rapport QA)"| Videur
    Patron -->|"Issue #4 (3 Docs Markdown\n+ schémas Mermaid)"| Greffier
    Cambouis & Gouache & Greffier -.->|"Chaque commit git"| Pinailleur
    Pinailleur -->|"Peer Review (git show HEAD)\n+ Clôture Issue (ou Retour #3)"| GH
```

| Agent | Modèle | Rôle | Responsabilité principale |
| :--- | :---: | :--- | :--- |
| **Patron** | `pro` | Tech Lead & Coordinateur | Lit les tickets sur GitHub, délègue en parallèle et fait relire chaque commit. |
| **Cambouis** | `pro` | Développeur Back-end Python | Développe `server.py`, le moteur `core/engine.py`, les tests unitaires et les correctifs. |
| **Gouache** | `pro` | Développeur Front-end | Déploie le cockpit *Cyber-Crisis* en moins de 180 lignes avec carte radar HTML/CSS. |
| **Pinailleur** | `flash` | Relecteur de Code | Inspecte chaque commit avec `git show HEAD`, exige des retouches et clôture les tickets. |
| **Videur** | `flash` | Ingénieur QA & Sécurité | Attaque le serveur avec `chaos_probe.py`, ouvre lui-même le bug #5 et valide le correctif. |
| **Greffier** | `flash` | Rédacteur Technique | Rédige les 3 manuels utilisateur, fonctionnel et technique avec schémas Mermaid. |

---

# Slide 2 — Interaction 1 : Initialisation & 1re Peer Review (Ticket #1)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Présentateur
    participant P as Patron (pro)
    participant GH as GitHub Issues (#1)
    participant C as Cambouis (pro)
    participant Pin as Pinailleur (flash)

    Dev->>P: "Traite l'Issue #1"
    P->>GH: get-issue #1 (lit les spécifications)
    P->>C: Délègue le développement du socle (#1)
    C->>C: Code server.py + static/index.html basique & git commit
    C->>GH: comment-issue #1 (livre le commit sans fermer)
    P->>Pin: Demande la Peer Review du commit
    Pin->>Pin: Inspecte le code (git show HEAD)
    Pin->>GH: comment-issue #1 (Approuvé) + close-issue #1
```

* **Ce qu'on montre** :
  * Le prompt ne contient aucune consigne technique : **Patron** va lire l'Issue #1 directement sur GitHub.
  * **Cambouis** livre un prototype volontairement basique (sans skill design) et ne ferme pas son ticket.
  * **Pinailleur** vérifie le commit et clôture l'Issue #1.

---

# Slide 3 — Interaction 2 : Exécution Parallèle & Retour de Peer Review (Tickets #2 & #3)

```mermaid
flowchart TD
    Patron["👔 Patron (pro)"] -->|"En parallèle : Ticket #2"| Gouache["🎨 Gouache (pro)\n+ skill mission-control-design"]
    Patron -->|"En parallèle : Ticket #3"| Cambouis["⚙️ Cambouis (pro)\ncore/engine.py + tests"]

    Gouache -->|"Commit Cockpit Radar"| Pin2["🔍 Pinailleur (flash)"]
    Pin2 -->|"✅ Valide & Ferme l'Issue #2"| GH2[("📋 Issue #2 Closed")]

    Cambouis -->|"1er Commit Moteur"| Pin3["🔍 Pinailleur (flash)"]
    Pin3 -.->|"⚠️ 1er passage : Refuse de fermer\n(Demande typage + docstring RG-02)"| Cambouis
    Cambouis -->|"2e Commit (Retouche appliquée)"| Pin3_OK["🔍 Pinailleur (flash)"]
    Pin3_OK -->|"✅ 2e passage : Valide & Ferme l'Issue #3"| GH3[("📋 Issue #3 Closed")]
```

* **Ce qu'on montre** :
  * **Parallélisme** : **Gouache** refait toute l'interface en Cockpit *Cyber-Crisis* pendant que **Cambouis** code l'algorithme de dispatch.
  * **Vrai aller-retour de Code Review** : Sur le ticket #3, **Pinailleur** refuse le 1er commit de **Cambouis** et poste un commentaire sur GitHub demandant le typage Python et la docstring `RG-02`. **Patron** renvoie **Cambouis** corriger dans un 2e commit avant que **Pinailleur** ne ferme le ticket.

---

# Slide 4 — Interaction 3 : Attaque Chaos, Auto-Bug & Auto-Guérison (Ticket #5)

```mermaid
flowchart LR
    Videur["🛡️ Videur (flash)\n+ chaos_probe.py"] -->|"1. Attaque : détecte XSS\n& coordonnées hors-radar"| Bug[("🚨 Crée lui-même\nl'Issue #5 [BUG/SEC]")]
    Bug -->|"2. Lecture du bug"| Patron["👔 Patron (pro)"]
    Patron -->|"3. Demande de correctif"| Cambouis["⚙️ Cambouis (pro)\nPatch + Tests unitaires"]
    Cambouis -->|"4. Commit du patch"| Pinailleur["🔍 Pinailleur (flash)\nPeer Review du commit"]
    Pinailleur -->|"5. Commit validé"| Videur2["🛡️ Videur (flash)\nContre-audit chaos_probe.py"]
    Videur2 -->|"6. 100% Vert : Ferme l'Issue #5"| Closed[("📋 Issue #5 Closed")]
```

* **Ce qu'on montre** :
  * **Ouverture autonome de ticket** : **Videur** attaque le serveur local, découvre 2 failles et crée de lui-même l'Issue #5 sur GitHub avec les preuves techniques.
  * **Chaîne de résolution complète** : **Cambouis** corrige $\rightarrow$ **Pinailleur** relit le commit $\rightarrow$ **Videur** relance ses sondes d'attaque et clôture le bug.

---

# Slide 5 — Interaction 4 : Release QA & Documentation 360° en Parallèle (Ticket #4)

```mermaid
flowchart TD
    GH4[("📋 Issue #4 [RELEASE]")] -->|"get-issue #4"| Patron["👔 Patron (pro)"]
    
    Patron -->|"En parallèle"| Videur["🛡️ Videur (flash)\ndocs/RAPPORT_DE_TESTS.md"]
    Patron -->|"En parallèle"| Greffier["📚 Greffier (flash)\n+ skill living-docs-360\nMANUEL + FONCTIONNELLE + TECHNIQUE"]

    Videur & Greffier -->|"Commit des 4 livrables dans docs/"| Pinailleur["🔍 Pinailleur (flash)\nPeer Review finale"]
    Pinailleur -->|"Valide & Clôture l'Issue #4"| Done[("🏁 5 Issues sur 5 Closed\nApplication & Docs en ligne")]
```

* **Ce qu'on montre** :
  * **Usine documentaire en parallèle** : **Videur** synthétise la campagne QA pendant que **Greffier** inspecte le code réel pour générer les 3 documentations et leurs schémas Mermaid.
  * **Consultation immédiate** : Les 4 documents apparaissent directement dans le 2e onglet du Cockpit web, et **Pinailleur** clôture le dernier ticket sur GitHub.
