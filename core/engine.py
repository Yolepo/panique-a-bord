"""
Moteur de simulation et télémétrie - Panique à Bord
Gestion de flotte de drones, boucle temps réel et algorithme de dispatch RG-02
"""

import math
from typing import List, Dict, Optional, Tuple, Any, Union


class SimulationEngine:
    def __init__(
        self,
        drones: Optional[List[Dict[str, Any]]] = None,
        incidents: Optional[List[Dict[str, Any]]] = None,
        speed: float = 5.0,
    ) -> None:
        if drones is None:
            self.drones: List[Dict[str, Any]] = [
                {
                    "id": "PAB-01",
                    "nom": "PAB-01",
                    "name": "PAB-01",
                    "x": 20.0,
                    "y": 30.0,
                    "statut": "IDLE",
                    "status": "IDLE",
                    "batterie": 100.0,
                    "battery": 100.0,
                    "target_id": None,
                },
                {
                    "id": "PAB-02",
                    "nom": "PAB-02",
                    "name": "PAB-02",
                    "x": 70.0,
                    "y": 40.0,
                    "statut": "IDLE",
                    "status": "IDLE",
                    "batterie": 85.0,
                    "battery": 85.0,
                    "target_id": None,
                },
                {
                    "id": "PAB-03",
                    "nom": "PAB-03",
                    "name": "PAB-03",
                    "x": 40.0,
                    "y": 80.0,
                    "statut": "IDLE",
                    "status": "IDLE",
                    "batterie": 92.0,
                    "battery": 92.0,
                    "target_id": None,
                },
                {
                    "id": "PAB-04",
                    "nom": "PAB-04",
                    "name": "PAB-04",
                    "x": 80.0,
                    "y": 85.0,
                    "statut": "IDLE",
                    "status": "IDLE",
                    "batterie": 78.0,
                    "battery": 78.0,
                    "target_id": None,
                },
            ]
        else:
            self.drones = drones

        if incidents is None:
            self.incidents: List[Dict[str, Any]] = [
                {
                    "id": "INC-01",
                    "titre": "Alerte intrusion nord",
                    "title": "Alerte intrusion nord",
                    "x": 25.0,
                    "y": 35.0,
                    "severite": "CRITIQUE",
                    "severity": "CRITICAL",
                    "statut": "DETECTED",
                    "status": "DETECTED",
                },
                {
                    "id": "INC-02",
                    "titre": "Fumée suspecte hangar",
                    "title": "Fumée suspecte hangar",
                    "x": 65.0,
                    "y": 50.0,
                    "severite": "MOYENNE",
                    "severity": "MEDIUM",
                    "statut": "DETECTED",
                    "status": "DETECTED",
                },
            ]
        else:
            self.incidents = incidents

        self.speed: float = speed
        self.incident_counter: int = len(self.incidents)

    def calculate_distance(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
        """
        Calcule la distance euclidienne entre deux entités selon la règle métier RG-02.

        Formule mathématique RG-02 :
            d = sqrt((x2 - x1)^2 + (y2 - y1)^2)

        Paramètres :
            p1 (Dict[str, Any]): Première entité contenant au minimum les coordonnées 'x' et 'y'.
            p2 (Dict[str, Any]): Seconde entité contenant au minimum les coordonnées 'x' et 'y'.

        Retour :
            float: La distance euclidienne calculée.
                   Retourne float('inf') comme valeur de repli sécurisée en cas d'erreur
                   de conversion numérique ou de coordonnées manquantes.
        """
        try:
            x1 = float(p1["x"])
            y1 = float(p1["y"])
            x2 = float(p2["x"])
            y2 = float(p2["y"])
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        except (ValueError, TypeError, KeyError):
            return float("inf")

    def find_nearest_available_drone(self, incident: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recherche le drone disponible le plus proche selon la règle métier RG-02.
        Critères d'éligibilité :
        - Statut IDLE
        - Niveau de batterie > 15%
        - Distance euclidienne minimale vers l'incident cible
        """
        available_drones = [
            d for d in self.drones
            if (d.get("statut") == "IDLE" or d.get("status") == "IDLE")
            and (d.get("batterie", 0) > 15 or d.get("battery", 0) > 15)
        ]
        if not available_drones:
            return None

        best_drone: Optional[Dict[str, Any]] = None
        min_dist: float = float("inf")
        for drone in available_drones:
            dist = self.calculate_distance(drone, incident)
            if dist < min_dist:
                min_dist = dist
                best_drone = drone
        return best_drone

    def dispatch_incidents(self) -> List[Tuple[str, str]]:
        """
        Affecte automatiquement les incidents en attente (DETECTED) aux drones disponibles.
        Passe le drone en EN_ROUTE et l'incident en ASSIGNED.
        """
        assignments: List[Tuple[str, str]] = []
        for inc in self.incidents:
            if inc.get("statut") == "DETECTED" or inc.get("status") == "DETECTED":
                drone = self.find_nearest_available_drone(inc)
                if drone:
                    drone["statut"] = "EN_ROUTE"
                    drone["status"] = "EN_ROUTE"
                    drone["target_id"] = inc["id"]
                    inc["statut"] = "ASSIGNED"
                    inc["status"] = "ASSIGNED"
                    assignments.append((drone["id"], inc["id"]))
        return assignments

    def add_incident(
        self,
        title: str,
        x: Union[float, int, str],
        y: Union[float, int, str],
        severity: str = "MOYENNE",
    ) -> Dict[str, Any]:
        """
        Ajoute un nouvel incident actif sur la grille opérationnelle.
        """
        self.incident_counter += 1
        inc_id = f"INC-{self.incident_counter:02d}"
        try:
            x_val: Union[float, str] = float(x)
        except (ValueError, TypeError):
            x_val = x
        try:
            y_val: Union[float, str] = float(y)
        except (ValueError, TypeError):
            y_val = y

        incident: Dict[str, Any] = {
            "id": inc_id,
            "titre": title,
            "title": title,
            "x": x_val,
            "y": y_val,
            "severite": severity,
            "severity": severity,
            "statut": "DETECTED",
            "status": "DETECTED",
        }
        self.incidents.append(incident)
        return incident

    def tick(self) -> None:
        """
        Cycle de télémétrie temps réel :
        1. Avancement vectoriel des drones EN_ROUTE vers leur incident cible.
        2. Résolution des incidents lorsque la distance passe sous le seuil de 3.0 unités.
        3. Consommation énergétique en vol et recharge progressive en stationnement IDLE.
        4. Déclenchement du dispatch automatique RG-02.
        """
        # 1. Mise à jour de la position des drones
        for drone in self.drones:
            statut = drone.get("statut") or drone.get("status")
            if statut == "EN_ROUTE" and drone.get("target_id"):
                target = next((i for i in self.incidents if i["id"] == drone["target_id"]), None)
                if not target or target.get("statut") == "RESOLVED" or target.get("status") == "RESOLVED":
                    drone["statut"] = "IDLE"
                    drone["status"] = "IDLE"
                    drone["target_id"] = None
                    continue

                dist = self.calculate_distance(drone, target)
                if dist < 3.0:
                    target["statut"] = "RESOLVED"
                    target["status"] = "RESOLVED"
                    drone["statut"] = "IDLE"
                    drone["status"] = "IDLE"
                    drone["target_id"] = None
                elif dist == float("inf"):
                    continue
                else:
                    try:
                        dx = float(target["x"]) - float(drone["x"])
                        dy = float(target["y"]) - float(drone["y"])
                        if dist <= self.speed:
                            drone["x"] = float(target["x"])
                            drone["y"] = float(target["y"])
                            target["statut"] = "RESOLVED"
                            target["status"] = "RESOLVED"
                            drone["statut"] = "IDLE"
                            drone["status"] = "IDLE"
                            drone["target_id"] = None
                        else:
                            drone["x"] = round(float(drone["x"]) + (dx / dist) * self.speed, 2)
                            drone["y"] = round(float(drone["y"]) + (dy / dist) * self.speed, 2)
                    except (ValueError, TypeError):
                        pass

                    current_bat = drone.get("batterie", 100)
                    new_bat = max(0.0, round(current_bat - 0.2, 1))
                    drone["batterie"] = new_bat
                    drone["battery"] = new_bat
            elif statut == "IDLE":
                current_bat = drone.get("batterie", 100)
                if current_bat < 100.0:
                    new_bat = min(100.0, round(current_bat + 0.1, 1))
                    drone["batterie"] = new_bat
                    drone["battery"] = new_bat

        # 2. Dispatch automatique des incidents actifs
        self.dispatch_incidents()
