"""Tests unitaires pour le moteur de simulation et l'algorithme RG-02."""
import unittest

from core.engine import (
    Drone,
    Incident,
    SimulationEngine,
    calculate_distance,
)


class TestSimulationEngine(unittest.TestCase):
    """Suite de tests unitaires validant RG-02, la télémétrie et le dispatch."""

    def test_calculate_distance(self):
        """Vérifie le calcul de la distance euclidienne (RG-02)."""
        # Distance nulle
        self.assertEqual(calculate_distance(0.0, 0.0, 0.0, 0.0), 0.0)
        # Triangle 3-4-5
        self.assertAlmostEqual(calculate_distance(0.0, 0.0, 3.0, 4.0), 5.0)
        self.assertAlmostEqual(calculate_distance(10.0, 20.0, 13.0, 24.0), 5.0)
        # Distance symétrique
        self.assertAlmostEqual(
            calculate_distance(5.0, 15.0, 25.0, 35.0),
            calculate_distance(25.0, 35.0, 5.0, 15.0),
        )

    def test_initial_state(self):
        """Vérifie l'état initial par défaut : 4 drones et 2 incidents."""
        engine = SimulationEngine()
        state = engine.get_state()
        self.assertEqual(len(state["drones"]), 4)
        drone_ids = [d["id"] for d in state["drones"]]
        self.assertIn("PAB-01", drone_ids)
        self.assertIn("PAB-04", drone_ids)

        self.assertEqual(len(state["incidents"]), 2)
        for d in state["drones"]:
            self.assertEqual(d["statut"], "IDLE")
            self.assertGreater(d["batterie"], 15)

    def test_dispatch_rg02_nearest_drone(self):
        """Vérifie que RG-02 assigne le drone disponible le plus proche."""
        custom_drones = [
            {"id": "PAB-FAR", "nom": "Far", "x": 90.0, "y": 90.0, "batterie": 90, "statut": "IDLE"},
            {"id": "PAB-NEAR", "nom": "Near", "x": 15.0, "y": 15.0, "batterie": 80, "statut": "IDLE"},
        ]
        custom_incidents = [
            {"id": "INC-TEST", "titre": "Alerte Proche", "x": 16.0, "y": 16.0, "statut": "DETECTED"}
        ]
        engine = SimulationEngine(drones=custom_drones, incidents=custom_incidents)
        assignments = engine.dispatch()

        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0], ("PAB-NEAR", "INC-TEST"))

        state = engine.get_state()
        d_near = next(d for d in state["drones"] if d["id"] == "PAB-NEAR")
        d_far = next(d for d in state["drones"] if d["id"] == "PAB-FAR")
        inc = next(i for i in state["incidents"] if i["id"] == "INC-TEST")

        self.assertEqual(d_near["statut"], "EN_ROUTE")
        self.assertEqual(d_far["statut"], "IDLE")
        self.assertEqual(inc["statut"], "ASSIGNED")
        self.assertEqual(inc["assigned_drone_id"], "PAB-NEAR")

    def test_dispatch_rg02_battery_filter(self):
        """Vérifie qu'un drone avec <= 15% de batterie est ignoré même s'il est plus proche."""
        custom_drones = [
            {"id": "PAB-LOW", "nom": "Low Battery", "x": 11.0, "y": 11.0, "batterie": 10, "statut": "IDLE"},
            {"id": "PAB-OK", "nom": "Normal Battery", "x": 40.0, "y": 40.0, "batterie": 85, "statut": "IDLE"},
        ]
        custom_incidents = [
            {"id": "INC-TEST", "titre": "Urgence", "x": 10.0, "y": 10.0, "statut": "DETECTED"}
        ]
        engine = SimulationEngine(drones=custom_drones, incidents=custom_incidents)
        assignments = engine.dispatch()

        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0], ("PAB-OK", "INC-TEST"))

    def test_dispatch_busy_drone_ignored(self):
        """Vérifie qu'un drone déjà EN_ROUTE n'est pas réassigné."""
        custom_drones = [
            {"id": "PAB-01", "nom": "Occupé", "x": 10.0, "y": 10.0, "batterie": 90, "statut": "EN_ROUTE"},
            {"id": "PAB-02", "nom": "Libre", "x": 50.0, "y": 50.0, "batterie": 90, "statut": "IDLE"},
        ]
        custom_incidents = [
            {"id": "INC-01", "titre": "Nouvel incident", "x": 12.0, "y": 12.0, "statut": "DETECTED"}
        ]
        engine = SimulationEngine(drones=custom_drones, incidents=custom_incidents)
        assignments = engine.dispatch()

        self.assertEqual(assignments, [("PAB-02", "INC-01")])

    def test_tick_vector_movement(self):
        """Vérifie le déplacement vectoriel fluide d'un drone vers sa cible."""
        custom_drones = [
            {"id": "PAB-01", "nom": "Drone 1", "x": 0.0, "y": 0.0, "batterie": 100, "statut": "IDLE", "speed": 2.0}
        ]
        custom_incidents = [
            {"id": "INC-01", "titre": "Cible", "x": 10.0, "y": 0.0, "statut": "DETECTED"}
        ]
        engine = SimulationEngine(drones=custom_drones, incidents=custom_incidents, speed=2.0)

        # Premier tick : dispatch + mouvement de 2.0 unités selon x
        engine.tick()
        drone = engine.get_drones()[0]
        self.assertEqual(drone["statut"], "EN_ROUTE")
        self.assertAlmostEqual(drone["x"], 2.0, places=2)
        self.assertAlmostEqual(drone["y"], 0.0, places=2)

        # Deuxième tick : mouvement supplémentaire de 2.0 unités
        engine.tick()
        drone = engine.get_drones()[0]
        self.assertAlmostEqual(drone["x"], 4.0, places=2)
        self.assertAlmostEqual(drone["y"], 0.0, places=2)

    def test_tick_resolution(self):
        """Vérifie la résolution automatique d'un incident lorsque distance < 3.0."""
        custom_drones = [
            {"id": "PAB-01", "nom": "Drone 1", "x": 8.0, "y": 0.0, "batterie": 100, "statut": "IDLE", "speed": 2.0}
        ]
        custom_incidents = [
            {"id": "INC-01", "titre": "Cible", "x": 10.0, "y": 0.0, "statut": "DETECTED"}
        ]
        engine = SimulationEngine(drones=custom_drones, incidents=custom_incidents, speed=2.0, resolution_distance=3.0)

        # Tick 1 : dispatch (dist = 2.0 < 3.0), résolution immédiate
        resolved = engine.tick()
        self.assertIn("INC-01", resolved)

        drone = engine.get_drones()[0]
        inc = engine.get_incidents()[0]
        self.assertEqual(inc["statut"], "RESOLVED")
        self.assertEqual(drone["statut"], "IDLE")
        self.assertIsNone(drone["target_incident_id"])

    def test_add_incident_dynamically(self):
        """Vérifie l'ajout dynamique d'un incident via add_incident."""
        engine = SimulationEngine()
        new_inc = engine.add_incident({
            "titre": "Alerte Tempête",
            "x": 42.0,
            "y": 42.0,
            "severite": "CRITICAL",
        })
        self.assertEqual(new_inc["titre"], "Alerte Tempête")
        self.assertEqual(new_inc["statut"], "DETECTED")
        self.assertEqual(len(engine.get_incidents()), 3)


if __name__ == "__main__":
    unittest.main()
