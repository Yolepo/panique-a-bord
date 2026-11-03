"""
Tests unitaires pour le moteur de simulation et de télémétrie - Panique à Bord
Couverture fonctionnelle (RG-02) et sécuritaire (RG-04, XSS, Bornes radar, Plafonnement)
"""

import math
import unittest
from core.engine import (
    SimulationEngine,
    InvalidCoordinatesError,
    InvalidSeverityError,
    ActiveIncidentLimitError,
    MAX_ACTIVE_INCIDENTS,
)


class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.drones = [
            {
                "id": "PAB-01",
                "nom": "PAB-01",
                "name": "PAB-01",
                "x": 10.0,
                "y": 10.0,
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
                "x": 80.0,
                "y": 80.0,
                "statut": "IDLE",
                "status": "IDLE",
                "batterie": 50.0,
                "battery": 50.0,
                "target_id": None,
            },
        ]
        self.incidents = [
            {
                "id": "INC-01",
                "titre": "Incident Test",
                "title": "Incident Test",
                "x": 13.0,
                "y": 14.0,
                "severite": "MOYENNE",
                "severity": "MEDIUM",
                "statut": "DETECTED",
                "status": "DETECTED",
            }
        ]
        self.engine = SimulationEngine(drones=self.drones, incidents=self.incidents, speed=5.0)

    def test_calculate_distance(self):
        p1 = {"x": 0.0, "y": 0.0}
        p2 = {"x": 3.0, "y": 4.0}
        dist = self.engine.calculate_distance(p1, p2)
        self.assertAlmostEqual(dist, 5.0, places=5)

    def test_find_nearest_available_drone(self):
        nearest = self.engine.find_nearest_available_drone(self.incidents[0])
        self.assertIsNotNone(nearest)
        self.assertEqual(nearest["id"], "PAB-01")

    def test_battery_threshold_filter(self):
        self.drones[0]["batterie"] = 12.0
        self.drones[0]["battery"] = 12.0

        nearest = self.engine.find_nearest_available_drone(self.incidents[0])
        self.assertIsNotNone(nearest)
        self.assertEqual(nearest["id"], "PAB-02")

    def test_dispatch_incidents(self):
        assignments = self.engine.dispatch_incidents()
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0], ("PAB-01", "INC-01"))
        self.assertEqual(self.drones[0]["statut"], "EN_ROUTE")
        self.assertEqual(self.drones[0]["target_id"], "INC-01")
        self.assertEqual(self.incidents[0]["statut"], "ASSIGNED")

    def test_tick_movement(self):
        self.engine.dispatch_incidents()
        initial_x = self.drones[0]["x"]
        initial_y = self.drones[0]["y"]

        self.engine.tick()

        self.assertGreater(self.drones[0]["x"], initial_x)
        self.assertGreater(self.drones[0]["y"], initial_y)

    def test_tick_resolution(self):
        self.drones[0]["x"] = 12.5
        self.drones[0]["y"] = 13.5
        self.drones[0]["statut"] = "EN_ROUTE"
        self.drones[0]["status"] = "EN_ROUTE"
        self.drones[0]["target_id"] = "INC-01"
        self.incidents[0]["statut"] = "ASSIGNED"
        self.incidents[0]["status"] = "ASSIGNED"

        self.engine.tick()

        self.assertEqual(self.incidents[0]["statut"], "RESOLVED")
        self.assertEqual(self.incidents[0]["status"], "RESOLVED")
        self.assertEqual(self.drones[0]["statut"], "IDLE")
        self.assertEqual(self.drones[0]["status"], "IDLE")
        self.assertIsNone(self.drones[0]["target_id"])

    # --- Tests Sécurité & Robustesse RG-04 ---

    def test_xss_sanitization(self):
        raw_payload = "<img src=x onerror=alert('HACKED')> Intrusion Cyber"
        inc = self.engine.add_incident(raw_payload, 50.0, 50.0, "CRITICAL")
        self.assertNotIn("<img", inc["titre"])
        self.assertNotIn("<img", inc["title"])
        self.assertIn("&lt;img", inc["titre"])
        self.assertIn("&lt;img", inc["title"])

    def test_coordinates_out_of_bounds_rejected(self):
        # Coordonnées négatives
        with self.assertRaises(InvalidCoordinatesError):
            self.engine.add_incident("Hors bornes négatif", -9999.0, 50.0, "CRITICAL")

        # Coordonnées supérieures à 100
        with self.assertRaises(InvalidCoordinatesError):
            self.engine.add_incident("Hors bornes supérieur", 50.0, 88888.0, "CRITICAL")

        # Non numérique
        with self.assertRaises(InvalidCoordinatesError):
            self.engine.add_incident("Texte", "abc", 50.0, "CRITICAL")

        # Booléen
        with self.assertRaises(InvalidCoordinatesError):
            self.engine.add_incident("Bool", True, 50.0, "CRITICAL")

        # Valeur infinie / NaN
        with self.assertRaises(InvalidCoordinatesError):
            self.engine.add_incident("Infini", float("inf"), 50.0, "CRITICAL")

    def test_invalid_severity_rejected(self):
        with self.assertRaises(InvalidSeverityError):
            self.engine.add_incident("Sévérité invalide", 50.0, 50.0, "INVALID_LEVEL")

    def test_valid_severities_accepted(self):
        for sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "FAIBLE", "MOYENNE", "HAUTE", "CRITIQUE"]:
            inc = self.engine.add_incident(f"Incident {sev}", 50.0, 50.0, sev)
            self.assertIn(inc["severite"], ["FAIBLE", "MOYENNE", "HAUTE", "CRITIQUE"])
            self.assertIn(inc["severity"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def test_active_incident_queue_limit(self):
        # Créer des incidents jusqu'au plafond (actuellement 1 initial + ceux ajoutés)
        # On vide la liste d'incidents pour tester précisément
        self.engine.incidents.clear()
        self.engine.incident_counter = 0

        for i in range(MAX_ACTIVE_INCIDENTS):
            self.engine.add_incident(f"Incident #{i+1}", 20.0, 20.0, "MOYENNE")

        # Le 11ème incident actif doit déclencher ActiveIncidentLimitError
        with self.assertRaises(ActiveIncidentLimitError):
            self.engine.add_incident("Incident Excédentaire", 20.0, 20.0, "MOYENNE")


if __name__ == "__main__":
    unittest.main()
