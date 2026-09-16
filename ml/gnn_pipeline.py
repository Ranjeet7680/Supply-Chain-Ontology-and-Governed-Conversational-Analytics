"""
ml/gnn_pipeline.py: Multi-Echelon Graph Neural Network (GNN) for Supply Chain Risk Propagation.
Models the multi-tier topology (Suppliers -> Plants -> Hubs -> Cross-Docks -> Retail DCs)
using PyTorch Graph Convolutional layers and message passing to compute bottleneck cascade shocks.
"""

import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Tuple, Optional

# Set reproducible seeds
torch.manual_seed(42)
np.random.seed(42)


class GraphConvolutionLayer(nn.Module):
    """
    Spatial Graph Convolutional Layer with residual skip connection:
    H^{(l+1)} = Activation( \\tilde{D}^{-1/2} \\tilde{A} \\tilde{D}^{-1/2} H^{(l)} W + H^{(l)} W_{skip} )
    """
    def __init__(self, in_features: int, out_features: int, dropout: float = 0.1):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        self.bias = nn.Parameter(torch.FloatTensor(out_features))
        self.skip_weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        self.dropout = nn.Dropout(dropout)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.skip_weight, a=math.sqrt(5))
        fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
        bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0.05
        nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, x: torch.Tensor, norm_adj: torch.Tensor) -> torch.Tensor:
        """
        x: [N, in_features]
        norm_adj: [N, N] normalized adjacency matrix with self-loops
        """
        # Graph convolution: A * X * W
        support = torch.mm(x, self.weight)
        output = torch.spmm(norm_adj, support) + self.bias
        # Residual skip connection
        skip = torch.mm(x, self.skip_weight)
        out = output + skip
        return self.dropout(F.silu(out))


class SupplyChainGNN(nn.Module):
    """
    Multi-layer Graph Neural Network predicting node vulnerability,
    propagation blast radius, and cascade shock index across multi-tier corridors.
    """
    def __init__(self, in_features: int = 6, hidden_dim: int = 32, num_classes: int = 3):
        super().__init__()
        self.gcn1 = GraphConvolutionLayer(in_features, hidden_dim)
        self.gcn2 = GraphConvolutionLayer(hidden_dim, hidden_dim)
        self.gcn3 = GraphConvolutionLayer(hidden_dim, 16)
        
        # Head 1: Node Risk Level (0: Normal, 1: Vulnerable, 2: Critical Bottleneck)
        self.risk_classifier = nn.Linear(16, num_classes)
        # Head 2: Cascade Shock Index (Continuous scalar [0, 1])
        self.shock_regressor = nn.Sequential(
            nn.Linear(16, 8),
            nn.SiLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor, norm_adj: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h1 = self.gcn1(x, norm_adj)
        h2 = self.gcn2(h1, norm_adj)
        h3 = self.gcn3(h2, norm_adj)
        
        logits = self.risk_classifier(h3)
        shock_index = self.shock_regressor(h3)
        return logits, shock_index


class MultiEchelonTopologyEngine:
    """
    Manages the multi-tier supply chain topology graph (nodes, edges, features)
    and orchestrates GNN inference and shock injection simulations.
    """
    def __init__(self):
        # 10 Canonical Multi-Tier Nodes across India & GCC Corridor
        self.nodes = [
            {"id": "T3_GUJ_RAW", "name": "Gujarat Raw Materials (Petrochemicals)", "tier": "Tier-3 Supplier", "region": "Gujarat", "lat": 22.3, "lon": 70.8},
            {"id": "T2_PUN_COMP", "name": "Pune Precision Components", "tier": "Tier-2 Supplier", "region": "Maharashtra", "lat": 18.5, "lon": 73.8},
            {"id": "T2_CHN_ELEC", "name": "Chennai Electronics Sub-Assembly", "tier": "Tier-2 Supplier", "region": "Tamil Nadu", "lat": 13.0, "lon": 80.2},
            {"id": "T1_MUM_PLANT", "name": "Mumbai Primary Assembly Plant", "tier": "Tier-1 Assembly", "region": "Maharashtra", "lat": 19.0, "lon": 72.8},
            {"id": "T1_DEL_PLANT", "name": "NCR Northern Assembly Plant", "tier": "Tier-1 Assembly", "region": "Delhi-NCR", "lat": 28.6, "lon": 77.2},
            {"id": "HUB_NSI_PORT", "name": "Nhava Sheva Maritime Gateway", "tier": "Export Hub", "region": "Navi Mumbai", "lat": 18.9, "lon": 72.9},
            {"id": "HUB_MND_PORT", "name": "Mundra Port Logistics Gateway", "tier": "Export Hub", "region": "Gujarat", "lat": 22.8, "lon": 69.7},
            {"id": "XDK_DXB_JAFZA", "name": "Jebel Ali Cross-Dock (JAFZA)", "tier": "GCC Hub", "region": "Dubai, UAE", "lat": 25.0, "lon": 55.1},
            {"id": "XDK_RUH_DRY", "name": "Riyadh Logistics Dry Port", "tier": "GCC Hub", "region": "Riyadh, KSA", "lat": 24.7, "lon": 46.7},
            {"id": "DC_DOH_CARGO", "name": "Doha Central Fulfillment DC", "tier": "Retail Hub", "region": "Doha, Qatar", "lat": 25.3, "lon": 51.5},
        ]
        
        # Directed edges: (source_idx, target_idx, transit_days, cost_weight)
        self.edges = [
            (0, 1, 1.5, 0.4), # Guj Raw -> Pune Comp
            (0, 3, 2.0, 0.5), # Guj Raw -> Mumbai Plant
            (1, 3, 0.8, 0.3), # Pune Comp -> Mumbai Plant
            (2, 3, 2.5, 0.6), # Chennai Elec -> Mumbai Plant
            (2, 4, 3.0, 0.7), # Chennai Elec -> Delhi Plant
            (3, 5, 0.5, 0.2), # Mumbai Plant -> Nhava Sheva
            (4, 6, 2.0, 0.5), # Delhi Plant -> Mundra Port
            (5, 7, 3.5, 0.8), # Nhava Sheva -> Jebel Ali (Sea)
            (6, 7, 4.0, 0.9), # Mundra Port -> Jebel Ali (Sea)
            (7, 8, 1.2, 0.4), # Jebel Ali -> Riyadh Dry Port (Road/Rail)
            (7, 9, 1.0, 0.3), # Jebel Ali -> Doha Cargo (Road/Sea)
        ]
        
        self.N = len(self.nodes)
        self.adj_matrix, self.norm_adj = self._build_normalized_adjacency()
        
        # Feature dimension = 6:
        # [inventory_buffer_ratio, avg_lead_time_days, congestion_index, disruption_prob, demand_surge_factor, weather_severity]
        self.base_features = torch.tensor([
            [1.20, 2.0, 0.15, 0.10, 1.05, 0.10], # T3_GUJ_RAW
            [1.10, 1.5, 0.20, 0.12, 1.10, 0.15], # T2_PUN_COMP
            [0.95, 2.8, 0.30, 0.18, 1.20, 0.25], # T2_CHN_ELEC
            [1.05, 1.0, 0.25, 0.14, 1.15, 0.20], # T1_MUM_PLANT
            [1.00, 1.8, 0.35, 0.20, 1.10, 0.30], # T1_DEL_PLANT
            [0.85, 3.2, 0.55, 0.28, 1.25, 0.40], # HUB_NSI_PORT
            [0.90, 3.0, 0.45, 0.22, 1.15, 0.35], # HUB_MND_PORT
            [1.15, 2.2, 0.35, 0.15, 1.30, 0.20], # XDK_DXB_JAFZA
            [0.80, 1.5, 0.40, 0.25, 1.25, 0.25], # XDK_RUH_DRY
            [0.75, 1.2, 0.50, 0.30, 1.35, 0.30], # DC_DOH_CARGO
        ], dtype=torch.float32)

        # Initialize GNN Model
        self.model = SupplyChainGNN(in_features=6, hidden_dim=32, num_classes=3)
        self.model.eval()

    def _build_normalized_adjacency(self) -> Tuple[torch.Tensor, torch.Tensor]:
        adj = torch.zeros((self.N, self.N), dtype=torch.float32)
        for u, v, _, weight in self.edges:
            adj[u, v] = 1.0 + weight
            adj[v, u] = 0.5 * (1.0 + weight) # weak upstream reflection

        # Add self-loops: \tilde{A} = A + I
        tilde_A = adj + torch.eye(self.N)
        
        # Degree matrix \tilde{D}
        degrees = torch.sum(tilde_A, dim=1)
        deg_inv_sqrt = torch.pow(degrees, -0.5)
        deg_inv_sqrt[torch.isinf(deg_inv_sqrt)] = 0.0
        D_inv_sqrt = torch.diag(deg_inv_sqrt)
        
        # Symmetric normalization: \tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2}
        norm_adj = torch.mm(torch.mm(D_inv_sqrt, tilde_A), D_inv_sqrt)
        return adj, norm_adj

    def compute_network_risk(self, feature_overrides: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, Any]:
        """
        Runs GNN forward pass over current or overridden network topology.
        """
        features = self.base_features.clone()
        
        if feature_overrides:
            for node_id, values in feature_overrides.items():
                for idx, node in enumerate(self.nodes):
                    if node["id"] == node_id:
                        if "inventory_buffer_ratio" in values:
                            features[idx, 0] = values["inventory_buffer_ratio"]
                        if "congestion_index" in values:
                            features[idx, 2] = values["congestion_index"]
                        if "disruption_prob" in values:
                            features[idx, 3] = values["disruption_prob"]
                        if "weather_severity" in values:
                            features[idx, 5] = values["weather_severity"]

        with torch.no_grad():
            logits, shock_indices = self.model(features, self.norm_adj)
            probs = F.softmax(logits, dim=1)

        risk_labels = ["LOW", "MODERATE", "CRITICAL_BOTTLENECK"]
        node_results = []
        for i, node in enumerate(self.nodes):
            p = probs[i].tolist()
            pred_class = int(torch.argmax(logits[i]).item())
            shock_val = round(float(shock_indices[i].item()), 4)
            
            node_results.append({
                "node_id": node["id"],
                "node_name": node["name"],
                "tier": node["tier"],
                "region": node["region"],
                "lat": node["lat"],
                "lon": node["lon"],
                "vulnerability_class": risk_labels[pred_class],
                "vulnerability_probs": {
                    "low": round(p[0], 4),
                    "moderate": round(p[1], 4),
                    "critical": round(p[2], 4)
                },
                "cascade_shock_index": shock_val,
                "buffer_capacity_ratio": round(float(features[i, 0].item()), 2),
                "congestion_level": round(float(features[i, 2].item()), 2)
            })

        mean_shock = float(shock_indices.mean().item())
        critical_nodes = [n["node_name"] for n in node_results if n["vulnerability_class"] == "CRITICAL_BOTTLENECK"]

        return {
            "network_status": "STABLE" if mean_shock < 0.4 else ("ELEVATED_RISK" if mean_shock < 0.65 else "CRITICAL_CASCADE"),
            "mean_cascade_shock": round(mean_shock, 4),
            "total_nodes": self.N,
            "total_corridor_edges": len(self.edges),
            "critical_bottlenecks": critical_nodes,
            "nodes": node_results
        }

    def simulate_cascade_shock(self, origin_node_id: str, shock_magnitude: float = 0.85) -> Dict[str, Any]:
        """
        Simulates what happens if a specific node (e.g. Mundra Port or Nhava Sheva)
        experiences a sudden shock (e.g. cyclone or port strike).
        Computes the propagation blast radius and downstream impact across the corridor.
        """
        base_state = self.compute_network_risk()
        
        overrides = {
            origin_node_id: {
                "congestion_index": min(1.0, 0.4 + shock_magnitude * 0.6),
                "disruption_prob": min(1.0, 0.3 + shock_magnitude * 0.7),
                "inventory_buffer_ratio": max(0.2, 1.0 - shock_magnitude * 0.75),
                "weather_severity": min(1.0, 0.2 + shock_magnitude * 0.8)
            }
        }
        
        shocked_state = self.compute_network_risk(feature_overrides=overrides)
        
        impact_analysis = []
        for b_node, s_node in zip(base_state["nodes"], shocked_state["nodes"]):
            delta_shock = round(s_node["cascade_shock_index"] - b_node["cascade_shock_index"], 4)
            impact_analysis.append({
                "node_id": s_node["node_id"],
                "node_name": s_node["node_name"],
                "tier": s_node["tier"],
                "baseline_shock": b_node["cascade_shock_index"],
                "shocked_shock": s_node["cascade_shock_index"],
                "shock_delta": delta_shock,
                "is_origin": s_node["node_id"] == origin_node_id,
                "impact_status": "ORIGIN_SHOCK" if s_node["node_id"] == origin_node_id else (
                    "HIGH_DOWNSTREAM_CASCADE" if delta_shock > 0.15 else (
                        "MODERATE_CASCADE" if delta_shock > 0.05 else "INSULATED"
                    )
                )
            })

        blast_radius_nodes = [item["node_name"] for item in impact_analysis if item["shock_delta"] > 0.08]

        return {
            "origin_node_id": origin_node_id,
            "shock_magnitude": shock_magnitude,
            "network_shock_increase_pct": round(((shocked_state["mean_cascade_shock"] - base_state["mean_cascade_shock"]) / max(0.01, base_state["mean_cascade_shock"])) * 100, 2),
            "blast_radius_count": len(blast_radius_nodes),
            "affected_downstream_nodes": blast_radius_nodes,
            "mitigation_prescriptions": [
                f"Activate secondary sea lane routing bypassing {origin_node_id}",
                "Elevate regional safety stock buffer at Jebel Ali Cross-Dock by +35%",
                "Trigger automated supplier advance PO to Tier-2 Pune components"
            ],
            "node_impact_breakdown": impact_analysis
        }


# Global Singleton Instance
gnn_engine = MultiEchelonTopologyEngine()
