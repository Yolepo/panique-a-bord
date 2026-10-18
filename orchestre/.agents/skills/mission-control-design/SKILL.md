---
name: mission-control-design
description: >-
  Design System Cyber-Crisis "Mission Control" ultra-léger et rapide à générer pour Panique à Bord.
  Utilise uniquement du HTML/CSS pur (grille radar CSS et points positionnés en %) sans Canvas JS complexe,
  pour produire un cockpit sombre/néon en moins de 180 lignes.
---

# Skill : Design System « Mission Control Express » (`mission-control-design`)

Ce skill transforme l'interface HTML basique en un **Cockpit Sombre Cyber-Crisis** avec un effet visuel fort mais **ultra-rapide à générer (< 180 lignes au total)**.

> [!IMPORTANT]
> **Règles de Vélocité Obligatoires pour `Gouache`** :
> 1. **Budget strict : 150 à 180 lignes maximum** pour `static/index.html` (CSS + HTML + JS compris).
> 2. **Zéro Canvas 2D / Zéro CDN externe** : N'écris AUCUN code trigonométrique `<canvas>` et ne charge aucune librairie externe.
> 3. **Carte Radar 100 % HTML/CSS** : Positionne simplement les drones et incidents en `position: absolute; left: ${x}%; top: ${y}%;` avec `transition: all 0.4s linear` dans un conteneur `.radar-box`.
> 4. **Exécution directe en 1 passe** : Ne lis aucun autre skill, ne lance pas de scripts de validation `node`, écris `static/index.html` d'un seul bloc, commite (`Fixes #2`) et ferme le ticket.

## 1. Palette & CSS Clé en Main (Grille Radar + Glassmorphism)

```css
:root {
  --bg: #060b16;
  --panel: rgba(13, 22, 41, 0.85);
  --border: rgba(0, 240, 255, 0.3);
  --cyan: #00f0ff;
  --emerald: #00ff9d;
  --crimson: #ff2a5f;
  --amber: #ffb800;
  --text: #e6f1ff;
}
body { margin: 0; font-family: system-ui, monospace; background: var(--bg); color: var(--text); }
.panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px; backdrop-filter: blur(8px); }
.radar-box {
  position: relative; width: 100%; height: 360px; border-radius: 12px; overflow: hidden;
  background:
    radial-gradient(circle, transparent 28%, rgba(0,240,255,0.12) 29%, transparent 30%),
    radial-gradient(circle, transparent 58%, rgba(0,240,255,0.12) 59%, transparent 60%),
    linear-gradient(rgba(0,240,255,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,240,255,0.06) 1px, transparent 1px), #040811;
  background-size: 100% 100%, 100% 100%, 10% 10%, 10% 10%;
  border: 1px solid var(--cyan);
}
.dot { position: absolute; transform: translate(-50%, -50%); transition: all 0.4s linear; font-size: 12px; font-weight: bold; white-space: nowrap; }
.drone { color: var(--cyan); text-shadow: 0 0 8px var(--cyan); }
.inc { color: var(--crimson); text-shadow: 0 0 10px var(--crimson); animation: pulse 1s infinite alternate; }
@keyframes pulse { from { transform: translate(-50%, -50%) scale(0.9); } to { transform: translate(-50%, -50%) scale(1.2); } }
```

## 2. Architecture Minimaliste à 2 Onglets

1. **En-tête compact** : Titre `🚨 PANIQUE À BORD — MISSION CONTROL`, compteurs rapides (*Drones actifs*, *Incidents*) et 2 boutons d'onglets :
   - `🎯 COCKPIT`
   - `📖 CENTRE DOCUMENTAIRE & QA`
2. **Onglet 1 — `🎯 COCKPIT` (Grille 2 colonnes)** :
   - **Gauche** : La carte `.radar-box` affichant les drones (`🚁 ${d.id}`) et les incidents non résolus (`🚨 ${i.titre || i.title}`) positionnés via `left:${x}%; top:${y}%`, avec clic direct ou bouton **« ⚡ Simuler Incident Critique »** (`POST /api/incidents`).
   - **Droite** : Deux tableaux compacts (Flotte de Drones avec barre/badge de batterie + Liste des Incidents avec statut).
3. **Onglet 2 — `📖 CENTRE DOCUMENTAIRE & QA`** :
   - Charge `GET /api/docs`, affiche un bouton par fichier (`RAPPORT_DE_TESTS.md`, `MANUEL_UTILISATEUR.md`, `DOC_FONCTIONNELLE.md`, `DOC_TECHNIQUE.md`) et affiche le contenu sélectionné dans un bloc `<pre style="white-space:pre-wrap">` propre et lisible.
4. **Rafraîchissement Temps Réel** :
   - Simple `setInterval(fetchState, 1000)` sur `GET /api/state` (compatible avec `drones`/`incidents` et champs FR/EN `titre||title`, `statut||status`, `severite||severity`, `batterie||battery`).
