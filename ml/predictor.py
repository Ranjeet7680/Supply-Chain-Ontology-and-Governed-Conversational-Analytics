"""
SupplyChainMLPredictor: Real-time inference & explainability engine for SupplyChain IQ.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

class SupplyChainMLPredictor:
    def __init__(self, models_dir="ml/models"):
        self.models_dir = models_dir
        self.classifier_path = os.path.join(models_dir, "delay_classifier.joblib")
        self.regressor_path = os.path.join(models_dir, "leadtime_regressor.joblib")
        
        self.clf = joblib.load(self.classifier_path) if os.path.exists(self.classifier_path) else None
        self.reg = joblib.load(self.regressor_path) if os.path.exists(self.regressor_path) else None
        
        # Load metadata
        self.clf_metrics = {}
        clf_meta_path = os.path.join(models_dir, "delay_classifier_metrics.json")
        if os.path.exists(clf_meta_path):
            with open(clf_meta_path, "r", encoding="utf-8") as f:
                self.clf_metrics = json.load(f)

    def predict_shipment_delay(self, features: dict) -> dict:
        """
        Predict probability of delay for an individual dispatch.
        features keys: distance_km, package_weight_kg, delivery_cost, delivery_partner, 
                       vehicle_type, delivery_mode, region, weather_condition
        """
        if self.clf is None:
            return {"error": "Classifier model not loaded"}
            
        df = pd.DataFrame([features])
        prob = float(self.clf.predict_proba(df)[0, 1])
        pred_label = int(prob >= 0.5)
        
        if prob >= 0.70:
            risk_tier = "CRITICAL_RISK"
            action = "Recommend immediate reroute to Delhivery or FedEx Express"
        elif prob >= 0.40:
            risk_tier = "ELEVATED_RISK"
            action = "Add transit buffer (+4 hours) and monitor milestone tracking"
        else:
            risk_tier = "LOW_RISK"
            action = "Standard dispatch schedule approved"
            
        # Top contributing drivers
        drivers = []
        if features.get("weather_condition") in ["rainy", "stormy", "foggy"]:
            drivers.append(f"Adverse weather condition ({features.get('weather_condition')})")
        if features.get("distance_km", 0) > 200:
            drivers.append(f"Long haul distance ({features.get('distance_km')} km)")
        if features.get("delivery_partner") in ["xpressbees", "ekart"]:
            drivers.append(f"Carrier partner historical latency ({features.get('delivery_partner')})")
        if not drivers:
            drivers.append("Optimal route and vehicle parameters")

        return {
            "predicted_delay_probability": round(prob * 100, 1),
            "predicted_delayed": bool(pred_label),
            "risk_tier": risk_tier,
            "recommended_action": action,
            "key_risk_drivers": drivers,
            "model_confidence": round(float(np.max(self.clf.predict_proba(df)[0])), 3)
        }

    def batch_predict(self, df_shipments: pd.DataFrame) -> pd.DataFrame:
        """
        Score a batch of shipments and return enriched DataFrame.
        """
        req_cols = ["distance_km", "package_weight_kg", "delivery_cost", "delivery_partner", 
                    "vehicle_type", "delivery_mode", "region", "weather_condition"]
        X = df_shipments[req_cols].copy()
        probs = self.clf.predict_proba(X)[:, 1]
        
        df_out = df_shipments.copy()
        df_out["ml_delay_probability"] = (probs * 100).round(1)
        df_out["ml_risk_tier"] = np.where(probs >= 0.70, "CRITICAL", np.where(probs >= 0.40, "ELEVATED", "LOW"))
        return df_out

    def get_feature_importances(self):
        return self.clf_metrics.get("top_feature_importances", [])

if __name__ == "__main__":
    predictor = SupplyChainMLPredictor()
    sample = {
        "distance_km": 280.0,
        "package_weight_kg": 35.0,
        "delivery_cost": 920.0,
        "delivery_partner": "xpressbees",
        "vehicle_type": "bike",
        "delivery_mode": "same day",
        "region": "central",
        "weather_condition": "rainy"
    }
    res = predictor.predict_shipment_delay(sample)
    print("--- SAMPLE INFERENCE ---")
    print(json.dumps(res, indent=2))
