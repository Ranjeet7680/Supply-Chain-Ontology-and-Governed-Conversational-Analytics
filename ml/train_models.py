"""
Machine Learning Training Pipeline for SupplyChain IQ.
Trains:
1. Delivery Delay Risk Classifier (LightGBM / RandomForest)
2. Supplier Lead Time Deviation Regressor (XGBoost / RandomForest)
Saves serialized models and metadata to ml/models/
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, mean_absolute_error, r2_score

os.makedirs("ml/models", exist_ok=True)

def train_delivery_delay_classifier():
    print("\n--- 1. Training Delivery Delay Risk Classifier ---")
    data_path = "Dataset/Delivery_Logistics.csv"
    df = pd.read_csv(data_path)
    
    # Target
    y = (df["delayed"].str.lower() == "yes").astype(int)
    
    numeric_features = ["distance_km", "package_weight_kg", "delivery_cost"]
    categorical_features = ["delivery_partner", "vehicle_type", "delivery_mode", "region", "weather_condition"]
    
    X = df[numeric_features + categorical_features].copy()
    
    # Fill any nulls
    for col in numeric_features:
        X[col] = X[col].fillna(X[col].median())
    for col in categorical_features:
        X[col] = X[col].fillna("Unknown")
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )
    
    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    acc = round(accuracy_score(y_test, y_pred), 4)
    roc = round(roc_auc_score(y_test, y_prob), 4)
    f1 = round(f1_score(y_test, y_pred), 4)
    
    print(f"[+] Delivery Delay Classifier Trained successfully!")
    print(f"    - Accuracy: {acc * 100:.2f}%")
    print(f"    - ROC-AUC:  {roc:.4f}")
    print(f"    - F1 Score: {f1:.4f}")
    
    # Feature Importance extraction
    feature_names = numeric_features + list(clf.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features))
    importances = clf.named_steps["classifier"].feature_importances_
    top_indices = np.argsort(importances)[::-1][:10]
    top_features = [{"feature": feature_names[i], "importance": round(float(importances[i]), 4)} for i in top_indices]
    
    # Save Model & Metrics
    model_file = "ml/models/delay_classifier.joblib"
    joblib.dump(clf, model_file)
    
    metrics = {
        "model_name": "Delivery Delay Risk Classifier (RandomForest)",
        "accuracy": acc,
        "roc_auc": roc,
        "f1_score": f1,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "top_feature_importances": top_features
    }
    with open("ml/models/delay_classifier_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return clf, metrics

def train_leadtime_deviation_regressor():
    print("\n--- 2. Training Supplier Lead Time Deviation Regressor ---")
    data_path = "Dataset/dynamic_supply_chain_logistics_dataset_with_country.csv"
    df = pd.read_csv(data_path)
    
    features = [
        "supplier_reliability_score",
        "disruption_likelihood_score",
        "delay_probability",
        "weather_condition_severity",
        "handling_equipment_availability",
        "customs_clearance_time",
        "route_risk_level"
    ]
    
    X = df[features].fillna(df[features].median())
    y = df["delivery_time_deviation"].fillna(df["delivery_time_deviation"].median())
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    reg = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    reg.fit(X_train, y_train)
    
    y_pred = reg.predict(X_test)
    
    mae = round(mean_absolute_error(y_test, y_pred), 4)
    r2 = round(r2_score(y_test, y_pred), 4)
    
    print(f"[+] Lead Time Deviation Regressor Trained successfully!")
    print(f"    - MAE: {mae:.4f} days")
    print(f"    - R2 Score: {r2:.4f}")
    
    model_file = "ml/models/leadtime_regressor.joblib"
    joblib.dump(reg, model_file)
    
    feature_importances = [{"feature": col, "importance": round(float(imp), 4)} for col, imp in zip(features, reg.feature_importances_)]
    feature_importances = sorted(feature_importances, key=lambda x: x["importance"], reverse=True)
    
    metrics = {
        "model_name": "Supplier Lead Time Deviation Regressor (RandomForest)",
        "mae_days": mae,
        "r2_score": r2,
        "features": feature_importances
    }
    with open("ml/models/leadtime_regressor_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return reg, metrics

if __name__ == "__main__":
    train_delivery_delay_classifier()
    train_leadtime_deviation_regressor()
    print("\n[SUCCESS] All ML Models Trained & Exported to ml/models/!")
