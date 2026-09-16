"""
tests/test_advanced_ml_backend.py: Unit and Integration tests for Advanced ML & Backend.
Tests:
- Graph Neural Network (GNN) multi-echelon network risk & shock simulation
- Temporal attention quantile forecasting (P10, P50, P90)
- Explainable AI (XAI) feature attribution & counterfactuals
- Statistical drift governance (PSI & KS tests)
- Sub-millisecond semantic query cache
- Asynchronous batch job queue
- FastAPI REST endpoints & Prometheus metrics
"""

import unittest
import time
from fastapi.testclient import TestClient

from backend.main import app
from ml.gnn_pipeline import gnn_engine
from ml.temporal_forecaster import temporal_forecaster
from ml.xai_engine import xai_engine
from ml.drift_detector import drift_detector
from backend.semantic_cache import semantic_cache
from backend.batch_jobs import batch_manager


class TestAdvancedMLAndBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_gnn_topology_and_risk(self):
        """Test GNN 10-node network risk forward pass"""
        res = gnn_engine.compute_network_risk()
        self.assertIn("network_status", res)
        self.assertIn("mean_cascade_shock", res)
        self.assertEqual(res["total_nodes"], 10)
        self.assertEqual(len(res["nodes"]), 10)
        
        first_node = res["nodes"][0]
        self.assertIn("vulnerability_class", first_node)
        self.assertIn("cascade_shock_index", first_node)

    def test_02_gnn_shock_simulation(self):
        """Test GNN cascade shock propagation from Nhava Sheva port"""
        res = gnn_engine.simulate_cascade_shock(origin_node_id="HUB_NSI_PORT", shock_magnitude=0.8)
        self.assertEqual(res["origin_node_id"], "HUB_NSI_PORT")
        self.assertGreater(len(res["node_impact_breakdown"]), 0)
        self.assertIn("mitigation_prescriptions", res)
        self.assertGreater(len(res["mitigation_prescriptions"]), 0)

    def test_03_temporal_forecaster_quantiles(self):
        """Test Multi-Horizon Forecaster and monotonic quantile property: P90 >= P50 >= P10"""
        fc = temporal_forecaster.forecast_corridor(
            corridor_name="India-GCC_Maritime",
            recent_weather_drift=0.3,
            recent_demand_surge=1.2
        )
        self.assertEqual(fc["forecast_horizon_days"], 7)
        self.assertIn("governed_safety_stock_recommendation", fc)
        self.assertGreater(fc["governed_safety_stock_recommendation"]["dynamic_buffer_days"], 0)
        
        for day in fc["daily_horizon"]:
            p10 = day["lead_time_days_p10_optimistic"]
            p50 = day["lead_time_days_p50_expected"]
            p90 = day["lead_time_days_p90_worst_case"]
            self.assertLessEqual(p10, p50)
            self.assertLessEqual(p50, p90)

    def test_04_xai_attribution_and_counterfactuals(self):
        """Test Explainable AI waterfall attributions and counterfactual advice"""
        features = {
            "distance_km": 350.0,
            "package_weight_kg": 40.0,
            "delivery_cost": 950.0,
            "delivery_partner": "xpressbees",
            "vehicle_type": "bike",
            "delivery_mode": "same day",
            "region": "central",
            "weather_condition": "stormy",
            "days_of_inventory": 8.0
        }
        res = xai_engine.explain_prediction(features, predicted_risk_prob=0.82, language="en")
        self.assertIn("waterfall_attributions", res)
        self.assertGreater(len(res["waterfall_attributions"]), 0)
        self.assertIn("top_risk_driver", res)
        self.assertIn("counterfactual_prescriptions", res)
        self.assertGreater(len(res["counterfactual_prescriptions"]), 0)

    def test_05_drift_detector_psi_and_ks(self):
        """Test automated statistical drift detection across batch records"""
        sample_batch = [
            {"distance_km": 180.0, "package_weight_kg": 15.0, "delivery_cost": 500.0},
            {"distance_km": 210.0, "package_weight_kg": 20.0, "delivery_cost": 580.0},
            {"distance_km": 195.0, "package_weight_kg": 18.0, "delivery_cost": 530.0}
        ]
        audit = drift_detector.evaluate_payload_drift(sample_batch)
        self.assertIn("overall_drift_status", audit)
        self.assertEqual(audit["inspected_records"], 3)
        self.assertIn("distance_km", audit["features_evaluated"])

    def test_06_semantic_cache_hit_and_miss(self):
        """Test sub-millisecond semantic query caching"""
        # Miss
        miss_res = semantic_cache.get("non-existent random query 12345 xyz")
        self.assertIsNone(miss_res)

        # Put
        test_query = "What is the carrier delay rate for urgent express cargo?"
        test_payload = {"intent": "carrier_delay", "synthesis": "Express delay rate is 18.5%"}
        semantic_cache.put(test_query, test_payload)

        # Hit
        hit_res = semantic_cache.get("What is the carrier delay rate for urgent express cargo?")
        self.assertIsNotNone(hit_res)
        self.assertTrue(hit_res.get("cache_hit"))

        # Check metrics
        metrics = semantic_cache.get_metrics()
        self.assertGreater(metrics["cache_hits"], 0)

    def test_07_batch_job_processing(self):
        """Test asynchronous batch processing and job lifecycle"""
        shipments = [
            {"shipment_id": f"TEST-{i}", "distance_km": 120 + i * 10, "package_weight_kg": 10 + i,
             "delivery_cost": 400 + i * 20, "delivery_partner": "delhivery", "vehicle_type": "van",
             "delivery_mode": "standard", "region": "north", "weather_condition": "clear"}
            for i in range(10)
        ]
        job_id = batch_manager.submit_batch(shipments)
        self.assertTrue(job_id.startswith("batch-"))

        # Wait briefly for worker thread
        time.sleep(0.3)
        status = batch_manager.get_status(job_id)
        self.assertIn(status["status"], ["PROCESSING", "COMPLETED"])

        # Wait for completion
        for _ in range(20):
            status = batch_manager.get_status(job_id)
            if status["status"] == "COMPLETED":
                break
            time.sleep(0.1)

        self.assertEqual(status["status"], "COMPLETED")
        results = batch_manager.get_results(job_id)
        self.assertEqual(len(results["results"]), 10)
        self.assertIn("summary_metrics", results)

    def test_08_fastapi_advanced_endpoints(self):
        """Test all newly added FastAPI advanced REST endpoints"""
        # 1. Health check includes all advanced subsystems
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        data = res_health.json()
        self.assertIn("gnn_topology_engine", data["subsystems"])
        self.assertIn("temporal_forecaster", data["subsystems"])
        self.assertIn("xai_engine", data["subsystems"])
        self.assertIn("semantic_cache", data["subsystems"])

        # 2. System metrics
        res_sys = self.client.get("/api/system/metrics")
        self.assertEqual(res_sys.status_code, 200)
        self.assertIn("semantic_cache", res_sys.json())

        # 3. Prometheus metrics endpoint
        res_prom = self.client.get("/metrics")
        self.assertEqual(res_prom.status_code, 200)
        self.assertIn("supplychain_cache_hit_ratio_pct", res_prom.text)

        # 4. GNN topology
        res_gnn = self.client.get("/api/gnn/network-topology")
        self.assertEqual(res_gnn.status_code, 200)
        self.assertEqual(res_gnn.json()["total_nodes"], 10)

        # 5. GNN Shock simulation
        res_shock = self.client.post("/api/gnn/simulate-shock", json={
            "origin_node_id": "HUB_NSI_PORT",
            "shock_magnitude": 0.75
        })
        self.assertEqual(res_shock.status_code, 200)

        # 6. Temporal Forecasting
        res_fc = self.client.get("/api/forecasting/corridor-horizon?corridor=India-GCC_Maritime&weather_drift=0.2")
        self.assertEqual(res_fc.status_code, 200)
        self.assertEqual(len(res_fc.json()["daily_horizon"]), 7)

        # 7. XAI Explanation
        res_xai = self.client.post("/api/ml/explain-prediction", json={
            "features": {
                "distance_km": 280.0,
                "package_weight_kg": 35.0,
                "delivery_cost": 880.0,
                "delivery_partner": "xpressbees",
                "vehicle_type": "bike",
                "delivery_mode": "same day",
                "region": "central",
                "weather_condition": "stormy",
                "days_of_inventory": 12.0
            },
            "language": "en"
        })
        self.assertEqual(res_xai.status_code, 200)
        self.assertIn("xai_explanation", res_xai.json())

        # 8. Batch Submit
        res_batch = self.client.post("/api/batch/submit", json={
            "shipments": [
                {"distance_km": 150.0, "package_weight_kg": 12.0, "delivery_cost": 420.0,
                 "delivery_partner": "delhivery", "vehicle_type": "truck", "delivery_mode": "standard",
                 "region": "west", "weather_condition": "clear"}
            ]
        })
        self.assertEqual(res_batch.status_code, 200)
        b_job_id = res_batch.json()["job_id"]

        # 9. Batch Status Poll
        res_poll = self.client.get(f"/api/batch/status/{b_job_id}")
        self.assertEqual(res_poll.status_code, 200)


if __name__ == "__main__":
    unittest.main()
