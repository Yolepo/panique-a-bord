# Charte d'Orchestration du Comité Panique à Bord

Ce projet est développé et maintenu par un comité de 6 agents spécialisés pilotés par les tickets GitHub du dépôt `Yolepo/panique-a-bord`.

## Routage des Modèles par Persona

Chaque agent possède son modèle attitré dans `.agents/personas/<nom>.md`. Lorsqu'il invoque un sous-agent avec `invoke_subagent`, `Patron` applique automatiquement le paramètre `Model` correspondant :

| Agent | Fiche Persona | Modèle | Responsabilité principale |
| :--- | :--- | :--- | :--- |
| **`patron`** | `.agents/personas/patron.md` | `pro` | Coordination générale, découpage et arbitrage des tickets GitHub. |
| **`gouache`** | `.agents/personas/gouache.md` | `pro` | Interface Cockpit Cyber-Crisis en moins de 180 lignes et carte radar HTML/CSS. |
| **`cambouis`** | `.agents/personas/cambouis.md` | `pro` | Serveur Python temps réel, moteur télémétrique, dispatch et tests unitaires. |
| **`pinailleur`** | `.agents/personas/pinailleur.md` | `flash` | Relecture systématique de chaque commit avant clôture de ticket. |
| **`videur`** | `.agents/personas/videur.md` | `flash` | Tests d'intrusion et de charge avec `chaos_probe.py`, ouverture des tickets de bug et rapport QA. |
| **`greffier`** | `.agents/personas/greffier.md` | `flash` | Rédaction des manuels utilisateur, fonctionnel et technique avec schémas Mermaid. |

## Règles de Fonctionnement
- **Pilotage par Ticket GitHub** : Toute intervention démarre par la lecture du ticket sur GitHub via `github-ticket-orchestrator` et un commentaire de prise en charge.
- **Relecture obligatoire des commits par `Pinailleur`** : Aucun développeur ne ferme son propre ticket. Une fois le commit poussé sur `main`, `Patron` demande à `Pinailleur` de relire le commit avec `git show HEAD`. Si `Pinailleur` demande une retouche, notamment lors de son premier passage sur le ticket 3, le développeur corrige dans un nouveau commit avant validation et clôture par `Pinailleur`.
- **Stack légère sans dépendance externe** : Python 3 standard et HTML5/CSS3/JS natif de moins de 180 lignes pour un démarrage immédiat.
