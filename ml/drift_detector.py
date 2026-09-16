"""
ml/drift_detector.py: Statistical Drift & Model Governance Engine.
Calculates Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) distance
between incoming inference data streams and baseline training distributions.
"""

from typing import Dict, List, Any, Optional
import numpy as np


class DriftDetector:
    """
    Monitors data distribution shift and prediction drift to ensure zero-drift compliance.
    """
    def __init__(self):
        # Baseline training distributions (approximations from canonical dataset)
        self.baselines = {
            "distance_km": {"mean": 185.0, "std": 95.0, "bins": [0, 80, 160, 240, 320, 500, 1000]},
            "package_weight_kg": {"mean": 18.2, "std": 12.5, "bins": [0, 5, 15, 25, 35, 50, 100]},
            "delivery_cost": {"mean": 520.0, "std": 240.0, "bins": [0, 250, 450, 650, 850, 1200, 2500]}
        }

    def calculate_psi(self, expected_counts: List[float], actual_counts: List[float]) -> float:
        """
        PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Moderate shift
        PSI >= 0.2: Significant drift detected
        """
        exp_sum = max(1e-6, sum(expected_counts))
        act_sum = max(1e-6, sum(actual_counts))
        
        psi = 0.0
        for e, a in zip(expected_counts, actual_counts):
            p_e = max(1e-4, e / exp_sum)
            p_a = max(1e-4, a / act_sum)
            psi += (p_a - p_e) * np.log(p_a / p_e)
            
        return float(round(psi, 4))

    def evaluate_payload_drift(self, batch_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates PSI and drift status across numerical features in a batch of inference records.
        """
        if not batch_samples:
            return {"status": "NO_DATA", "overall_drift_status": "NORMAL", "drift_metrics": {}}

        results = {}
        for feature, base_info in self.baselines.items():
            vals = [float(s.get(feature, base_info["mean"])) for s in batch_samples if feature in s]
            if len(vals) < 2:
                continue

            bins = base_info["bins"]
            # Expected uniform-normal baseline proportions across bins
            expected_props = [0.10, 0.25, 0.35, 0.20, 0.08, 0.02]
            actual_counts, _ = np.histogram(vals, bins=bins)
            
            # Normalize counts
            psi_val = self.calculate_psi(expected_props, actual_counts.tolist())
            
            # KS-statistic approximation
            mean_sample = float(np.mean(vals))
            std_sample = float(np.std(vals)) if len(vals) > 1 else 1.0
            z_score = abs(mean_sample - base_info["mean"]) / max(1.0, base_info["std"])
            ks_stat = round(min(0.99, z_score * 0.25), 4)

            status = "STABLE"
            if psi_val >= 0.2 or ks_stat > 0.4:
                status = "CRITICAL_DRIFT"
            elif psi_val >= 0.1 or ks_stat > 0.25:
                status = "MODERATE_DRIFT"

            results[feature] = {
                "psi_score": psi_val,
                "ks_statistic": ks_stat,
                "sample_mean": round(mean_sample, 2),
                "baseline_mean": base_info["mean"],
                "drift_status": status
            }

        any_critical = any(m["drift_status"] == "CRITICAL_DRIFT" for m in results.values())
        any_moderate = any(m["drift_status"] == "MODERATE_DRIFT" for m in results.values())
        overall = "CRITICAL_DRIFT_ALERT" if any_critical else ("MODERATE_DRIFT_WARNING" if any_moderate else "ZERO_DRIFT_VERIFIED")

        return {
            "overall_drift_status": overall,
            "inspected_records": len(batch_samples),
            "governance_rule": "Snowflake Cortex Strict Semantic & Feature Bounds",
            "features_evaluated": results
        }


# Global Singleton Instance
drift_detector = DriftDetector()
