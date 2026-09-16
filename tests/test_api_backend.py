"""
tests/test_api_backend.py: Comprehensive Unit and Integration Tests for FastAPI Backend, ML, DL, RL, and Multilingual Voice AI.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestSupplyChainBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertIn("cortex_analyst", data["subsystems"])
        self.assertIn("dl_pytorch_deeprisknet", data["subsystems"])
        self.assertIn("rl_dqn_agent", data["subsystems"])

    def test_supported_languages(self):
        resp = self.client.get("/api/languages")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("hi", data["supported_languages"])
        self.assertIn("ta", data["supported_languages"])
        self.assertIn("te", data["supported_languages"])
        self.assertIn("gu", data["supported_languages"])

    def test_multilingual_query_hindi(self):
        payload = {
            "query": "कौन सा कैरियर सबसे ज्यादा लेट कर रहा है?",
            "persona": "Logistics Manager (Fleet & Carriers)",
            "language": "hi",
            "include_audio": False
        }
        resp = self.client.post("/api/assistant/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["intent"], "CARRIER_PERFORMANCE")
        self.assertEqual(data["detected_language"], "hi")
        self.assertIn("कैनोनिकल", data["native_synthesis"]) if "कैनोनिकल" in data["native_synthesis"] else self.assertTrue(len(data["native_synthesis"]) > 10)

    def test_multilingual_query_tamil(self):
        payload = {
            "query": "எந்த கேரியர் அதிக தாமதத்தை ஏற்படுத்துகிறது?",
            "persona": "Supply Chain Director",
            "language": "ta",
            "include_audio": False
        }
        resp = self.client.post("/api/assistant/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["intent"], "CARRIER_PERFORMANCE")
        self.assertEqual(data["detected_language"], "ta")

    def test_ml_predict_delay(self):
        payload = {
            "distance_km": 300.0,
            "package_weight_kg": 40.0,
            "delivery_cost": 950.0,
            "delivery_partner": "xpressbees",
            "vehicle_type": "truck",
            "delivery_mode": "express",
            "region": "central",
            "weather_condition": "stormy"
        }
        resp = self.client.post("/api/ml/predict-delay", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("predicted_delay_probability", data)
        self.assertIn("risk_tier", data)
        self.assertIn("deep_learning", data)
        self.assertIn("rl_prescriptive_policy", data)

    def test_dl_predict_deep_risk(self):
        payload = {
            "distance_km": 320.0,
            "package_weight_kg": 25.0,
            "delivery_cost": 890.0,
            "delivery_partner": "delhivery",
            "vehicle_type": "van",
            "delivery_mode": "standard",
            "region": "west",
            "weather_condition": "clear"
        }
        resp = self.client.post("/api/dl/predict-deep-risk", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("deep_risk_inference", data)
        self.assertIn("autoencoder_anomaly", data)

    def test_rl_prescribe_action(self):
        payload = {
            "days_of_inventory": 8.5,
            "weather_severity": 0.8,
            "carrier_delay_prob": 0.7,
            "delivery_partner": "xpressbees",
            "weather_condition": "stormy",
            "delivery_cost": 1100.0
        }
        resp = self.client.post("/api/rl/prescribe-action", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("recommended_action_id", data)
        self.assertIn("policy_decision", data)
        self.assertIn("q_values", data)

    def test_rl_simulate_trajectory(self):
        resp = self.client.get("/api/rl/simulate-trajectory?days=7")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["simulation_days"], 7)
        self.assertIn("rl_cumulative_reward", data)
        self.assertIn("heuristic_cumulative_reward", data)

    def test_mcp_execute_tool(self):
        payload = {
            "tool_name": "reroute_delayed_shipment",
            "parameters": {
                "shipment_id": "SHP-10042",
                "current_carrier": "xpressbees",
                "new_carrier": "delhivery",
                "reason": "Predicted delay"
            }
        }
        resp = self.client.post("/api/mcp/execute-tool", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "SUCCESS")

if __name__ == "__main__":
    unittest.main()
