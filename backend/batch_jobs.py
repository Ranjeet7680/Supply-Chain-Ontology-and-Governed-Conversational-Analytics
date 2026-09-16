"""
backend/batch_jobs.py: Asynchronous Batch Job Queue & Execution Engine.
Enables high-throughput multi-model batch inference (Random Forest, PyTorch DeepRisk,
Autoencoder Anomaly, and XAI Attributions) over hundreds of shipments without blocking the API.
"""

import uuid
import time
import threading
from typing import Dict, List, Any, Optional

from ml.predictor import SupplyChainMLPredictor
from ml.dl_model import SupplyChainDLPredictor
from ml.xai_engine import SupplyChainXAIEngine
from ml.drift_detector import DriftDetector


class BatchJobManager:
    """
    In-memory asynchronous batch processing coordinator with thread workers,
    progress tracking, and job lifecycle state management.
    """
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.ml_predictor = SupplyChainMLPredictor()
        self.dl_predictor = SupplyChainDLPredictor()
        self.xai_engine = SupplyChainXAIEngine()
        self.drift_detector = DriftDetector()

    def submit_batch(self, items: List[Dict[str, Any]], model_suite: str = "all") -> str:
        job_id = f"batch-{uuid.uuid4().hex[:8]}"
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "QUEUED",
            "total_records": len(items),
            "processed_records": 0,
            "progress_pct": 0.0,
            "created_at": time.time(),
            "completed_at": None,
            "model_suite": model_suite,
            "results": [],
            "summary_metrics": {},
            "drift_audit": {},
            "error": None
        }

        # Spawn background processing thread
        worker = threading.Thread(target=self._run_job, args=(job_id, items, model_suite), daemon=True)
        worker.start()

        return job_id

    def _run_job(self, job_id: str, items: List[Dict[str, Any]], model_suite: str):
        job = self.jobs[job_id]
        job["status"] = "PROCESSING"
        results = []
        total = len(items)

        try:
            high_risk_count = 0
            anomaly_count = 0
            total_cost = 0.0

            for idx, item in enumerate(items):
                # 1. Classical ML prediction
                ml_res = self.ml_predictor.predict_shipment_delay(item)
                # 2. PyTorch Deep Learning
                dl_res = self.dl_predictor.predict_deep_risk(item)
                # 3. Autoencoder Anomaly Detection
                ae_res = self.dl_predictor.detect_anomaly(item)
                
                # Check metrics
                if dl_res.get("predicted_risk_level") in ["HIGH", "CRITICAL"]:
                    high_risk_count += 1
                if ae_res.get("is_anomaly", False):
                    anomaly_count += 1
                total_cost += float(item.get("delivery_cost", 500.0))

                results.append({
                    "record_index": idx,
                    "item_id": item.get("shipment_id", f"SHP-{1000 + idx}"),
                    "ml_delay_probability": ml_res.get("predicted_delay_probability", 0.0),
                    "dl_risk_level": dl_res.get("predicted_risk_level", "LOW"),
                    "dl_risk_score": dl_res.get("risk_score", 0.0),
                    "is_cost_anomaly": ae_res.get("is_anomaly", False),
                    "anomaly_reconstruction_loss": ae_res.get("reconstruction_loss", 0.0)
                })

                job["processed_records"] = idx + 1
                job["progress_pct"] = round(((idx + 1) / total) * 100, 1)
                # Brief sleep to simulate large-scale micro-batch pacing
                if total > 50 and idx % 25 == 0:
                    time.sleep(0.01)

            # Evaluate batch drift
            drift_audit = self.drift_detector.evaluate_payload_drift(items)

            job["results"] = results
            job["summary_metrics"] = {
                "total_analyzed": total,
                "high_risk_shipments": high_risk_count,
                "high_risk_rate_pct": round((high_risk_count / max(1, total)) * 100, 2),
                "anomalous_cost_spikes": anomaly_count,
                "cumulative_freight_usd": round(total_cost, 2),
                "throughput_per_sec": round(total / max(0.01, time.time() - job["created_at"]), 1)
            }
            job["drift_audit"] = drift_audit
            job["status"] = "COMPLETED"
            job["completed_at"] = time.time()

        except Exception as e:
            job["status"] = "FAILED"
            job["error"] = str(e)

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "total_records": job["total_records"],
            "processed_records": job["processed_records"],
            "progress_pct": job["progress_pct"],
            "elapsed_seconds": round((job["completed_at"] or time.time()) - job["created_at"], 2),
            "summary_metrics": job["summary_metrics"],
            "error": job["error"]
        }

    def get_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        return job


# Global Singleton Instance
batch_manager = BatchJobManager()
