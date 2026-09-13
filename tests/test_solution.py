import unittest
import os
import yaml
import json
import pandas as pd
from engine.persona_resolver import PersonaReconciler
from engine.governed_cortex_engine import GovernedCortexEngine
from mcp.supplychain_mcp_server import SupplyChainMCPServer
from ml.predictor import SupplyChainMLPredictor

class TestSupplyChainSolution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_dir = "data/bridged"
        cls.df_sales = pd.read_csv(f"{cls.data_dir}/fact_sales_order.csv")
        cls.df_po = pd.read_csv(f"{cls.data_dir}/fact_purchase_order.csv")
        cls.df_shipment = pd.read_csv(f"{cls.data_dir}/fact_shipment.csv")
        cls.df_wh = pd.read_csv(f"{cls.data_dir}/dim_plant_warehouse.csv")
        cls.df_parts = pd.read_csv(f"{cls.data_dir}/dim_part.csv")
        cls.df_supplier = pd.read_csv(f"{cls.data_dir}/dim_supplier.csv")
        cls.df_inv = pd.read_csv(f"{cls.data_dir}/fact_inventory_snapshot.csv")
        cls.df_landed = pd.read_csv(f"{cls.data_dir}/fact_landed_cost.csv")

    def test_referential_integrity_sales(self):
        """Verify all sales order foreign keys exist in dimension tables."""
        valid_whs = set(self.df_wh["warehouse_id"])
        valid_products = set(self.df_parts["product_id"])
        valid_shipments = set(self.df_shipment["shipment_id"])

        self.assertTrue(set(self.df_sales["warehouse_id"]).issubset(valid_whs), "Orphan warehouse_id in sales orders!")
        self.assertTrue(set(self.df_sales["product_id"]).issubset(valid_products), "Orphan product_id in sales orders!")
        self.assertTrue(set(self.df_sales["shipment_id"]).issubset(valid_shipments), "Orphan shipment_id in sales orders!")

    def test_referential_integrity_po(self):
        """Verify all PO foreign keys exist in dimension tables."""
        valid_suppliers = set(self.df_supplier["supplier_id"])
        valid_products = set(self.df_parts["product_id"])
        valid_whs = set(self.df_wh["warehouse_id"])

        self.assertTrue(set(self.df_po["supplier_id"]).issubset(valid_suppliers), "Orphan supplier_id in purchase orders!")
        self.assertTrue(set(self.df_po["product_id"]).issubset(valid_products), "Orphan product_id in purchase orders!")
        self.assertTrue(set(self.df_po["plant_warehouse_id"]).issubset(valid_whs), "Orphan warehouse_id in purchase orders!")

    def test_persona_reconciliation_exact_grounding(self):
        """Verify Planning Persona resolves to Canonical OTIF with zero mathematical drift."""
        reconciler = PersonaReconciler(data_dir=self.data_dir)
        df_rec = reconciler.reconcile_otif()
        
        planning_row = df_rec[df_rec["Persona"] == "Planning Persona"].iloc[0]
        self.assertEqual(planning_row["Reconciliation Status"], "EXACT_MATCH (100% Grounded)")
        
        total = len(self.df_sales)
        otif_count = self.df_sales["is_canonical_otif"].sum()
        expected_pct = f"{round((otif_count / total) * 100, 2)}%"
        self.assertEqual(planning_row["Local Metric Result"], expected_pct)

    def test_cortex_semantic_model_yaml(self):
        """Verify Snowflake Cortex Analyst YAML specification."""
        self.assertTrue(os.path.exists("cortex/semantic_model.yaml"))
        with open("cortex/semantic_model.yaml", "r", encoding="utf-8") as f:
            model = yaml.safe_load(f)
        
        self.assertIn("name", model)
        self.assertIn("tables", model)
        self.assertIn("verified_queries", model)
        self.assertGreaterEqual(len(model["tables"]), 3)

    def test_cortex_engine_predictive_queries(self):
        """Verify Governed Cortex Engine answers ML predictive queries."""
        engine = GovernedCortexEngine(data_dir=self.data_dir)
        res = engine.ask("Predict which shipments have high delay probability")
        self.assertEqual(res["intent"], "ML_PREDICTIVE_RISK")
        self.assertIn("data", res)
        self.assertIn("evidence", res)

    def test_ml_model_and_inference(self):
        """Verify ML RandomForest Classifier loads and predicts delay risk."""
        self.assertTrue(os.path.exists("ml/models/delay_classifier.joblib"))
        predictor = SupplyChainMLPredictor()
        res = predictor.predict_shipment_delay({
            "distance_km": 300.0,
            "package_weight_kg": 40.0,
            "delivery_cost": 950.0,
            "delivery_partner": "xpressbees",
            "vehicle_type": "bike",
            "delivery_mode": "same day",
            "region": "central",
            "weather_condition": "stormy"
        })
        self.assertIn("predicted_delay_probability", res)
        self.assertIn("risk_tier", res)
        self.assertGreater(res["predicted_delay_probability"], 50.0)

    def test_mcp_server_actions(self):
        """Verify MCP Server functions properly for cross-system and ML actions."""
        mcp = SupplyChainMCPServer(data_dir=self.data_dir)
        tools = mcp.get_available_tools()
        self.assertGreaterEqual(len(tools), 5)

        # Test ML tool
        ml_res = mcp.execute_tool("predict_shipment_delay_risk", {
            "distance_km": 250.0,
            "delivery_partner": "xpressbees",
            "weather_condition": "rainy"
        })
        self.assertEqual(ml_res["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
