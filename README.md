# Supply-Chain-Ontology-and-Governed-Conversational-Analytics

[![Snowflake](https://img.shields.io/badge/Snowflake-Cortex%20Analyst-29B5E8?logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![CoCo CLI](https://img.shields.io/badge/CoCo-Full%20Lifecycle%20Ready-3B82F6)](https://github.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Native%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ontology Compliance](https://img.shields.io/badge/Ontology-100%25%20Certified-10B981)](#-ontology-validation-coco-skill)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **Snowflake CoCo CLI Hackathon — GCC Edition**  
> **Challenge**: Supply Chain Ontology and Governed Conversational Analytics  
> **Platform**: Enterprise AI Supply Chain Intelligence, Governed Semantic Ontology & Knowledge Graph

---

## 📌 Problem Statement: Eliminating Supply Chain "Metric Chaos"

Supply chain data is inherently fragmented across ERP (SAP, Oracle), WMS (Manhattan, Blue Yonder), TMS (Delhivery, FedEx, DHL, Blue Dart), and IoT telemetry. Because each department calculates metrics within its own operational silo, asking the same fundamental question produces conflicting answers:

```
                            ┌─────────────────────────────────┐
                            │   "What is our OTIF rate?"      │
                            └───────────────┬─────────────────┘
                                            │
            ┌───────────────────────────────┼───────────────────────────────┐
            ▼                               ▼                               ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│   Planning Persona    │       │  Procurement Persona  │       │   Logistics Persona   │
│   (Customer POD)      │       │  (Supplier Dock SLA)  │       │ (Carrier Transit SLA) │
│        22.91%         │       │        50.36%         │       │        73.32%         │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```

- **Logistics** reports **73.32%** (measuring carrier transit timestamp against dispatch SLA).
- **Procurement** reports **50.36%** (measuring supplier dock receipt date against purchase order promised dates).
- **Planning** reports **22.91%** (measuring sales order commit date against customer proof of delivery in full).

When executive leadership asks for overall supply chain performance, this lack of shared semantic grounding creates friction, disputes, and operational paralysis.

---

## ⚡ The Solution: Canonical Supply Chain Ontology

**SupplyChain IQ** unifies fragmented multi-tier supply chain data into an **Industry Canonical Ontology** expressed as **Snowflake Governed Semantic Views** and queried through **Snowflake Cortex Analyst**.

### 1. Canonical Business Entity Flow

$$\text{Supplier} \xrightarrow{\text{supplies}} \text{Part / SKU} \xrightarrow{\text{stocked in}} \text{Plant / Warehouse} \xrightarrow{\text{dispatched via}} \text{Shipment / Carrier} \xrightarrow{\text{fulfills}} \text{Sales Order} \xrightarrow{\text{delivered to}} \text{Customer}$$

### 2. Governed Canonical Metrics

1. **On-Time In-Full (OTIF)**:
   $$\text{OTIF} = \frac{\sum [\text{Delivered On-or-Before Promised Date} \land \text{Delivered Qty} \ge \text{Ordered Qty}]}{\text{Total Orders Completed}} \times 100$$
2. **Fill Rate**:
   $$\text{Fill Rate} = \frac{\sum \text{Delivered Quantity}}{\sum \text{Ordered Quantity}} \times 100$$
3. **Days of Inventory (DOI)**:
   $$\text{DOI} = \frac{\text{Current Warehouse Inventory Level}}{\text{Historical 30-Day Average Daily Demand}}$$
4. **Total Landed Cost**:
   $$\text{Landed Cost} = \text{Base Purchase Cost} + \text{Freight Cost} + \text{Handling Cost} + \text{Customs \& Tariffs}$$

---

## ⚖️ Zero-Drift Cross-Persona Reconciliation Matrix

Our governed views resolve the disparate perspectives with mathematical proof and full lineage:

| Persona Perspective | Measurement Boundary | Local Metric | Governed Canonical Grounding | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Planning Persona** | Sales Order Commit to Customer POD | **22.91%** | **22.91%** (`GOLD_SEMANTIC.V_CANONICAL_OTIF`) | **EXACT_MATCH (100% Grounded)** |
| **Procurement Persona** | Supplier Dock Receipt vs PO Date | **50.36%** | **22.91%** (Component: `procurement_dock_otif`) | **COMPONENT_DISAMBIGUATED** |
| **Logistics Persona** | Dispatch Timestamp vs Carrier SLA | **73.32%** | **22.91%** (Component: `carrier_sla_met`) | **COMPONENT_DISAMBIGUATED** |

---

## 🛠️ CoCo Full Lifecycle Implementation

### Phase 1: Planning
- Data exploration and schema profiling across **25,000 TMS shipments**, **113,097 multi-tier SC nodes**, **99,441 customer orders**, and **LEADS Indian state infrastructure indices**.
- Canonical ontology schema specification ([`ONTOLOGY_SPEC.md`](file:///c:/Users/Victus/OneDrive/Desktop/Snowflake%20CoCo%20CLI%20Hackathon%20-%20GCC%20Edition/ARCHITECTURE.md)).

### Phase 2: Development
- **Synthetic Data Bridging (`scripts/generate_synthetic_bridge.py`)**:
  Referentially links fragmented raw CSVs into 8 clean dimensional tables in `data/bridged/`.
- **Snowflake Medallion Lakehouse Pipeline (`snowflake/`)**:
  - `01_ingestion_pipeline.sql`: Bronze raw stages & Silver cleaned tables.
  - `02_semantic_views.sql`: Gold layer governed views (`V_CANONICAL_OTIF`, `V_FILL_RATE`, `V_INVENTORY_HEALTH_DOI`, `V_LANDED_COST_ANALYSIS`, `V_PERSONA_RECONCILIATION`).
  - `03_dynamic_tables_and_tasks.sql`: Dynamic Tables (`DT_CARRIER_PERFORMANCE_REALTIME`, `DT_INVENTORY_STOCKOUT_ALERTS`) with 1-minute target lag and CDC streams.
- **Snowflake Cortex Analyst Authoring (`cortex/`)**:
  - `semantic_model.yaml`: Official Cortex Analyst YAML specification with logical dimensions, synonyms, time dimensions, and verified queries.
  - `verified_queries.sql`: Certified query benchmark patterns.
- **Governed Multi-Persona Engine (`engine/`)**:
  - `persona_resolver.py`: Computes the mathematical reconciliation matrix across teams.
  - `governed_cortex_engine.py`: Natural language compiler to verified Snowflake SQL with a 5-point proof chain.
- **Native Streamlit Application (`app.py`)**:
  Enterprise web application with 5 interactive tabs.

### Phase 3: Execution
- **Pipeline Runner (`run_pipeline.py`)**: Automated orchestration of bridging, validation, reconciliation, Cortex simulation, and testing.

### Phase 4: Testing & Validation
- **Automated Test Suite (`tests/test_solution.py`)**:
  - `test_referential_integrity_sales`: PASSED (0 orphan foreign keys)
  - `test_referential_integrity_po`: PASSED (0 orphan foreign keys)
  - `test_persona_reconciliation_exact_grounding`: PASSED (Planning persona matches Canonical OTIF at 22.91%)
  - `test_cortex_semantic_model_yaml`: PASSED (Valid syntax & verified queries)
  - `test_cortex_engine_queries`: PASSED (Zero-drift SQL execution)
  - `test_mcp_server_actions`: PASSED (Cross-tool execution verified)
  - `test_leads_infra_linking`: PASSED (All warehouses linked to infrastructure ratings)

---

## 🌟 Standout CoCo Capabilities (Judging Bonuses)

### 1. Reusable CoCo Custom Skill (`.coco/skills/`)
Located in [`.coco/skills/supplychain-ontology-validator/`](file:///c:/Users/Victus/OneDrive/Desktop/Snowflake%20CoCo%20CLI%20Hackathon%20-%20GCC%20Edition/.coco/skills/supplychain-ontology-validator/):
- Reusable CoCo CLI skill with CLI utility `validate_ontology.py` that audits any relational schema against SCOR/GS1 standards.
- Audits required entities, foreign key chains, and canonical metric formulas (**100.0% Certified Compliance**).

### 2. Model Context Protocol (MCP) Server (`mcp/`)
Located in [`mcp/supplychain_mcp_server.py`](file:///c:/Users/Victus/OneDrive/Desktop/Snowflake%20CoCo%20CLI%20Hackathon%20-%20GCC%20Edition/mcp/supplychain_mcp_server.py):
Enables CoCo agents to take real cross-system actions:
- `reroute_delayed_shipment`: Reassigns bottleneck shipments (e.g. XpressBees) to high-reliability carriers (e.g. Delhivery or FedEx).
- `trigger_procurement_reorder`: Automatically generates ERP Purchase Orders when inventory drops below 14-day safety thresholds.
- `broadcast_slack_incident`: Posts attested disruption notices to `#supply-chain-incident-ops`.

---

## 📂 Project Repository Structure

```
├── .coco/
│   └── skills/
│       └── supplychain-ontology-validator/
│           ├── SKILL.md                          # Reusable CoCo Custom Skill
│           └── validate_ontology.py              # CLI validation utility
├── Dataset/                                      # Local Datasets (25k TMS, 113k SC, Olist, LEADS)
├── data/
│   └── bridged/                                  # 8 Canonical Relational Tables (Referentially Aligned)
├── scripts/
│   └── generate_synthetic_bridge.py             # Synthetic Bridging Generator
├── snowflake/
│   ├── 01_ingestion_pipeline.sql                # Bronze & Silver Lakehouse DDL
│   ├── 02_semantic_views.sql                    # Governed Semantic Views (Gold Layer)
│   └── 03_dynamic_tables_and_tasks.sql          # Dynamic Tables & CDC Streams/Tasks
├── cortex/
│   ├── semantic_model.yaml                      # Snowflake Cortex Analyst Semantic Model
│   └── verified_queries.sql                     # Certified Query Benchmark Patterns
├── engine/
│   ├── persona_resolver.py                      # Cross-Persona Metric Reconciler
│   └── governed_cortex_engine.py                # NL-to-Ontology Snowflake SQL Compiler
├── mcp/
│   └── supplychain_mcp_server.py                # Model Context Protocol Server
├── tests/
│   ├── __init__.py
│   └── test_solution.py                         # 7 Automated Validation Tests
├── app.py                                       # Native Snowflake Streamlit Application
├── index.html                                   # Palantir/Databricks-style Standalone HTML Prototype
├── STITCH_UI_PROMPTS.md                         # Google Stitch UI Design Prompts
├── ARCHITECTURE.md                              # Detailed Architecture & Technical Report
├── run_pipeline.py                              # End-to-End Automated Pipeline Orchestrator
└── README.md                                    # Project Readme
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Dependencies: `pandas`, `numpy`, `streamlit`, `pyyaml`, `pydantic`

### 1. Run the Complete Automated Pipeline
```bash
python run_pipeline.py
```

### 2. Run the Verification Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 3. Launch the Streamlit Enterprise Dashboard
```bash
streamlit run app.py
```

### 4. Open the Interactive Standalone UI Prototype
Simply double-click [`index.html`](file:///c:/Users/Victus/OneDrive/Desktop/Snowflake%20CoCo%20CLI%20Hackathon%20-%20GCC%20Edition/index.html) or open it in any modern browser to explore all 5 flagship screens with zero server setup!

---

## 📜 License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.
