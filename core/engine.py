"""Moteur télémétrique et algorithme de dispatch pour Panique à Bord."""
import math
import threading
from typing import Any, Dict, List, Optional, Tuple


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


DEFAULT_DRONES = [
    {
        "id": "PAB-01",
        "nom": "PAB-01 Alpha",
        "name": "PAB-01 Alpha",
        "x": 20.0,
        "y": 25.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 98,
        "battery": 98,
    },
    {
        "id": "PAB-02",
        "nom": "PAB-02 Bravo",
        "name": "PAB-02 Bravo",
        "x": 75.0,
        "y": 20.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 92,
        "battery": 92,
    },
    {
        "id": "PAB-03",
        "nom": "PAB-03 Charlie",
        "name": "PAB-03 Charlie",
        "x": 30.0,
        "y": 80.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 85,
        "battery": 85,
    },
    {
        "id": "PAB-04",
        "nom": "PAB-04 Delta",
        "name": "PAB-04 Delta",
        "x": 80.0,
        "y": 75.0,
        "statut": "IDLE",
        "status": "IDLE",
        "batterie": 95,
        "battery": 95,
    },
]

DEFAULT_INCIDENTS = [
    {
        "id": "INC-01",
        "titre": "Incendie Zone Portuaire",
        "title": "Incendie Zone Portuaire",
        "x": 50.0,
        "y": 45.0,
        "severite": "HIGH",
        "severity": "HIGH",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
    {
        "id": "INC-02",
        "titre": "Avarie Moteur Pont Principal",
        "title": "Avarie Moteur Pont Principal",
        "x": 25.0,
        "y": 65.0,
        "severite": "MEDIUM",
        "severity": "MEDIUM",
        "statut": "DETECTED",
        "status": "DETECTED",
    },
]


class Drone:
    """Représentation d'un drone dans la cellule de crise."""

    def __init__(
        self,
        id: str,
        nom: str,
        x: float,
        y: float,
        batterie: int = 100,
        statut: str = "IDLE",
        speed: float = 2.0,
    ) -> None:
        self.id = id
        self.nom = nom
        self.name = nom
        self.x = float(x)
        self.y = float(y)
        self.batterie = int(batterie)
        self.battery = int(batterie)
        self.statut = statut
        self.status = statut
        self.speed = float(speed)
        self.target_incident_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nom": self.nom,
            "name": self.name,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "statut": self.statut,
            "status": self.status,
            "batterie": self.batterie,
            "battery": self.battery,
            "target_incident_id": self.target_incident_id,
            "speed": self.speed,
        }

    def __getitem__(self, item: str) -> Any:
        return self.to_dict()[item]

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ("statut", "status"):
            self.statut = value
            self.status = value
        elif key in ("batterie", "battery"):
            self.batterie = int(value)
            self.battery = int(value)
        elif key in ("nom", "name"):
            self.nom = str(value)
            self.name = str(value)
        elif key in ("x", "y", "speed"):
            setattr(self, key, float(value))
        else:
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)


class Incident:
    """Représentation d'un incident opérationnel."""

    def __init__(
        self,
        id: str,
        titre: str,
        x: float,
        y: float,
        severite: str = "MEDIUM",
        statut: str = "DETECTED",
    ) -> None:
        self.id = id
        self.titre = titre
        self.title = titre
        self.x = float(x)
        self.y = float(y)
        self.severite = severite
        self.severity = severite
        self.statut = statut
        self.status = statut
        self.assigned_drone_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titre": self.titre,
            "title": self.title,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "severite": self.severite,
            "severity": self.severity,
            "statut": self.statut,
            "status": self.status,
            "assigned_drone_id": self.assigned_drone_id,
        }

    def __getitem__(self, item: str) -> Any:
        return self.to_dict()[item]

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ("statut", "status"):
            self.statut = value
            self.status = value
        elif key in ("severite", "severity"):
            self.severite = value
            self.severity = value
        elif key in ("titre", "title"):
            self.titre = str(value)
            self.title = str(value)
        elif key in ("x", "y"):
            setattr(self, key, float(value))
        else:
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)


class SimulationEngine:
    """Moteur de télémétrie et dispatch automatique RG-02."""

    def __init__(
        self,
        drones: Optional[List[Dict[str, Any]]] = None,
        incidents: Optional[List[Dict[str, Any]]] = None,
        speed: float = 2.0,
        resolution_distance: float = 3.0,
        min_battery: int = 15,
    ) -> None:
        self.lock = threading.RLock()
        self.speed = speed
        self.resolution_distance = resolution_distance
        self.min_battery = min_battery
        self.drones: List[Drone] = []
        self.incidents: List[Incident] = []
        self._incident_counter = 0

        if drones is None:
            self.reset_drones()
        else:
            for d in drones:
                self.add_drone(d)

        if incidents is None:
            self.reset_incidents()
        else:
            for inc in incidents:
                self.add_incident(inc)

    def calculate_distance(self, x1, y1, x2, y2):
        return calculate_distance(x1, y1, x2, y2)

    def reset_drones(self) -> None:
        with self.lock:
            self.drones = [
                Drone(
                    id=d["id"],
                    nom=d.get("nom") or d.get("name", d["id"]),
                    x=float(d["x"]),
                    y=float(d["y"]),
                    batterie=int(d.get("batterie", d.get("battery", 100))),
                    statut=d.get("statut", d.get("status", "IDLE")),
                    speed=self.speed,
                )
                for d in DEFAULT_DRONES
            ]

    def reset_incidents(self) -> None:
        with self.lock:
            self.incidents = []
            for inc in DEFAULT_INCIDENTS:
                self.add_incident(inc)

    def add_drone(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            drone = Drone(
                id=str(data["id"]),
                nom=str(data.get("nom") or data.get("name", data["id"])),
                x=float(data.get("x", 0.0)),
                y=float(data.get("y", 0.0)),
                batterie=int(data.get("batterie", data.get("battery", 100))),
                statut=str(data.get("statut", data.get("status", "IDLE"))),
                speed=float(data.get("speed", self.speed)),
            )
            self.drones.append(drone)
            return drone.to_dict()

    def add_incident(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            self._incident_counter += 1
            inc_id = str(data.get("id") or f"INC-{self._incident_counter:02d}")
            titre = str(data.get("titre") or data.get("title") or f"Incident #{self._incident_counter}")
            severite = str(data.get("severite") or data.get("severity") or "MEDIUM")
            statut = str(data.get("statut") or data.get("status") or "DETECTED")

            try:
                x_val = float(data.get("x", 50.0))
                y_val = float(data.get("y", 50.0))
            except (ValueError, TypeError):
                x_val = 50.0
                y_val = 50.0

            incident = Incident(
                id=inc_id,
                titre=titre,
                x=x_val,
                y=y_val,
                severite=severite,
                statut=statut,
            )
            self.incidents.append(incident)
            return incident.to_dict()

    def get_state(self) -> Dict[str, List[Dict[str, Any]]]:
        with self.lock:
            return {
                "drones": [d.to_dict() for d in self.drones],
                "incidents": [i.to_dict() for i in self.incidents],
            }

    def get_drones(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [d.to_dict() for d in self.drones]

    def get_incidents(self) -> List[Dict[str, Any]]:
        with self.lock:
            return [i.to_dict() for i in self.incidents]

    def dispatch(self) -> List[Tuple[str, str]]:
        """Algorithme de dispatch automatique RG-02.

        Assigne l'incident DETECTED au drone IDLE le plus proche ayant > 15% de batterie.
        """
        with self.lock:
            assignments: List[Tuple[str, str]] = []
            detected_incidents = [
                inc for inc in self.incidents
                if (inc.statut == "DETECTED" or inc.status == "DETECTED")
            ]

            for inc in detected_incidents:
                eligible_drones = [
                    d for d in self.drones
                    if (d.statut == "IDLE" or d.status == "IDLE") and d.batterie > self.min_battery
                ]
                if not eligible_drones:
                    continue

                nearest_drone = min(
                    eligible_drones,
                    key=lambda d: calculate_distance(d.x, d.y, inc.x, inc.y),
                )

                nearest_drone.statut = "EN_ROUTE"
                nearest_drone.status = "EN_ROUTE"
                nearest_drone.target_incident_id = inc.id

                inc.statut = "ASSIGNED"
                inc.status = "ASSIGNED"
                inc.assigned_drone_id = nearest_drone.id

                assignments.append((nearest_drone.id, inc.id))

            return assignments

    def tick(self) -> List[str]:
        """Avance la simulation d'un pas temporel."""
        with self.lock:
            # 1. Dispatch automatique
            self.dispatch()

            # 2. Déplacement des drones assignés
            resolved_incidents: List[str] = []
            incidents_map = {inc.id: inc for inc in self.incidents}

            for drone in self.drones:
                if drone.statut != "EN_ROUTE" and drone.status != "EN_ROUTE":
                    continue

                if not drone.target_incident_id or drone.target_incident_id not in incidents_map:
                    drone.statut = "IDLE"
                    drone.status = "IDLE"
                    drone.target_incident_id = None
                    continue

                inc = incidents_map[drone.target_incident_id]
                if inc.statut == "RESOLVED" or inc.status == "RESOLVED":
                    drone.statut = "IDLE"
                    drone.status = "IDLE"
                    drone.target_incident_id = None
                    continue

                dist = calculate_distance(drone.x, drone.y, inc.x, inc.y)

                if dist < self.resolution_distance:
                    inc.statut = "RESOLVED"
                    inc.status = "RESOLVED"
                    drone.statut = "IDLE"
                    drone.status = "IDLE"
                    drone.target_incident_id = None
                    resolved_incidents.append(inc.id)
                else:
                    step = drone.speed
                    if step >= dist:
                        drone.x = inc.x
                        drone.y = inc.y
                    else:
                        dx = inc.x - drone.x
                        dy = inc.y - drone.y
                        drone.x = max(0.0, min(100.0, round(drone.x + (dx / dist) * step, 2)))
                        drone.y = max(0.0, min(100.0, round(drone.y + (dy / dist) * step, 2)))

                    new_dist = calculate_distance(drone.x, drone.y, inc.x, inc.y)
                    if new_dist < self.resolution_distance:
                        inc.statut = "RESOLVED"
                        inc.status = "RESOLVED"
                        drone.statut = "IDLE"
                        drone.status = "IDLE"
                        drone.target_incident_id = None
                        resolved_incidents.append(inc.id)

            return resolved_incidents
