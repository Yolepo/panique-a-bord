"""
Tests unitaires pour le moteur de simulation et de télémétrie
"""

import unittest
from core.engine import SimulationEngine


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
        # L'incident est en (13, 14), PAB-01 est en (10, 10) (dist 5.0), PAB-02 est en (80, 80)
        nearest = self.engine.find_nearest_available_drone(self.incidents[0])
        self.assertIsNotNone(nearest)
        self.assertEqual(nearest["id"], "PAB-01")

    def test_battery_threshold_filter(self):
        # PAB-01 est plus proche mais avec batterie critique (<= 15%)
        self.drones[0]["batterie"] = 12.0
        self.drones[0]["battery"] = 12.0

        nearest = self.engine.find_nearest_available_drone(self.incidents[0])
        # PAB-01 doit être ignoré au profit de PAB-02 qui a 50%
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

        # 1er tick : le drone se déplace vers (13, 14)
        self.engine.tick()

        self.assertGreater(self.drones[0]["x"], initial_x)
        self.assertGreater(self.drones[0]["y"], initial_y)

    def test_tick_resolution(self):
        # Positionner le drone tout près de l'incident (distance < 3.0)
        self.drones[0]["x"] = 12.5
        self.drones[0]["y"] = 13.5
        self.drones[0]["statut"] = "EN_ROUTE"
        self.drones[0]["status"] = "EN_ROUTE"
        self.drones[0]["target_id"] = "INC-01"
        self.incidents[0]["statut"] = "ASSIGNED"
        self.incidents[0]["status"] = "ASSIGNED"

        self.engine.tick()

        # L'incident doit être RESOLVED et le drone IDLE
        self.assertEqual(self.incidents[0]["statut"], "RESOLVED")
        self.assertEqual(self.incidents[0]["status"], "RESOLVED")
        self.assertEqual(self.drones[0]["statut"], "IDLE")
        self.assertEqual(self.drones[0]["status"], "IDLE")
        self.assertIsNone(self.drones[0]["target_id"])

    def test_robustness_extreme_coordinates(self):
        # Ajout d'un incident avec coordonnées hors-radar extrêmes
        extreme_inc = self.engine.add_incident("Chaos Out of Bounds", -9999.0, 88888.0, "CRITIQUE")
        self.assertIn(extreme_inc, self.engine.incidents)

        # Un tick ne doit pas lever d'exception
        try:
            self.engine.tick()
        except Exception as e:
            self.fail(f"tick() a levé une exception inattendue: {e}")


if __name__ == "__main__":
    unittest.main()
