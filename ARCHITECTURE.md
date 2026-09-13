# SupplyChain IQ — Ontology & Governed Conversational Analytics
## Complete Snowflake CoCo CLI Hackathon GCC Edition Solution

---

### Executive Overview & Problem Statement
Supply chain data is inherently fragmented across ERP (SAP, Oracle), WMS (Manhattan, Blue Yonder), TMS (delivery partners like Delhivery, FedEx, DHL, Blue Dart), and IoT telemetry. Because each functional team defines metrics locally, asking the same fundamental question produces conflicting answers:
- **Logistics**: Reports **73.32% OTIF** (evaluating carrier transit time against dispatch SLA).
- **Procurement**: Reports **50.36% OTIF** (evaluating supplier dock delivery against purchase order promised dates).
- **Planning**: Reports **22.91% OTIF** (evaluating customer order commit date against proof of delivery with 100% quantity fulfillment).

When executives ask *"What is our On-Time In-Full performance?"*, this lack of shared semantic grounding creates executive friction and operational paralysis.

**SupplyChain IQ** resolves this challenge by building a **Canonical Supply Chain Industry Ontology** expressed as **Snowflake Governed Semantic Views** and queried through **Snowflake Cortex Analyst**. It ensures that every natural language query resolves to a single source of truth while transparently disambiguating component sub-metrics for each persona.

---

### CoCo Full Lifecycle Demonstration

#### 1. Planning Phase
- **Data Discovery & Exploration**: Profiled local datasets:
  - `Delivery_Logistics.csv`: 25,000 real Indian dispatches across 9 logistics partners.
  - `dynamic_supply_chain_logistics_dataset_with_country.csv`: 113,097 multi-tier supplier nodes across 90+ countries with 15,550 Asian/GCC corridor entities.
  - `olist_customers_dataset.csv`: 99,441 customer delivery points.
  - `Leads Report 2021`: 31 Indian states evaluated for road, rail, and warehouse infrastructure quality.
  - `IO Publication 2022`: ADB multi-regional input-output trade matrices.
- **Canonical Ontology Design**:
  $$\text{Supplier} \xrightarrow{\text{supplies}} \text{Part/Product} \xrightarrow{\text{stocked in}} \text{Plant/Warehouse} \xrightarrow{\text{dispatched via}} \text{Shipment/Carrier} \xrightarrow{\text{fulfills}} \text{Customer Order} \xrightarrow{\text{delivered to}} \text{Customer}$$

#### 2. Development Phase
- **Synthetic Data Generation (`scripts/generate_synthetic_bridge.py`)**:
  Synthesizes referentially consistent dimension and fact tables in `data/bridged/`:
  - `dim_supplier.csv` (500 suppliers with reliability and country attributes)
  - `dim_part.csv` (200 SKUs with unit costs and categories)
  - `dim_plant_warehouse.csv` (8 regional distribution plants mapped to Indian zones and GCC hubs, attached to LEADS infrastructure scores)
  - `fact_shipment.csv` (25,000 real TMS dispatches with carrier SLA metrics)
  - `fact_sales_order.csv` (25,000 linked customer orders with canonical OTIF flags)
  - `fact_purchase_order.csv` (15,000 procurement POs with dock arrival dates)
  - `fact_inventory_snapshot.csv` (Warehouse stock levels, safety buffers, and DOI)
  - `fact_landed_cost.csv` (Decomposed base, freight, handling, and tariff costs)
- **Snowflake Lakehouse & Semantic SQL (`snowflake/`)**:
  - `01_ingestion_pipeline.sql`: Bronze raw stages and Silver cleaned tables.
  - `02_semantic_views.sql`: Gold layer governed views (`V_CANONICAL_OTIF`, `V_FILL_RATE`, `V_INVENTORY_HEALTH_DOI`, `V_LANDED_COST_ANALYSIS`, `V_PERSONA_RECONCILIATION`).
  - `03_dynamic_tables_and_tasks.sql`: Dynamic Tables (`DT_CARRIER_PERFORMANCE_REALTIME`, `DT_INVENTORY_STOCKOUT_ALERTS` with 1-minute target lag) and CDC Streams/Tasks.
- **Snowflake Cortex Analyst Semantic Model (`cortex/semantic_model.yaml`)**:
  Official Cortex Analyst YAML specification with logical dimensions, synonyms, time dimensions, measures, and certified verified queries.
- **Governed Multi-Persona Engine (`engine/`)**:
  - `persona_resolver.py`: Mathematical proof of metric reconciliation.
  - `governed_cortex_engine.py`: Natural language compiler to verified Snowflake SQL with evidence attestation.
- **Native Streamlit Application (`app.py`)**:
  Interactive enterprise application featuring Command Center, Persona Inspector, Cortex Conversational Hub, Ontology Lineage, and Disruption Simulator.
- **Reusable CoCo Custom Skill (`.coco/skills/supplychain-ontology-validator/`)**:
  Reusable skill validating data models against canonical supply chain ontology standards with 100% compliance.
- **Model Context Protocol (MCP) Server (`mcp/supplychain_mcp_server.py`)**:
  Enables agents to execute actions: ERP Purchase Order creation, TMS carrier rerouting, and Slack incident broadcasting.

#### 3. Execution Phase
- Orchestrated via `run_pipeline.py`, coordinating bridging, schema audits, persona reconciliation, Cortex simulation, MCP tool calling, and test verification in under 12 seconds.

#### 4. Testing & Validation Phase
- Automated unit test suite (`tests/test_solution.py`):
  - `test_referential_integrity_sales`: PASSED (0 orphan foreign keys)
  - `test_referential_integrity_po`: PASSED (0 orphan foreign keys)
  - `test_persona_reconciliation_exact_grounding`: PASSED (Planning persona matches Canonical OTIF at 22.91%)
  - `test_cortex_semantic_model_yaml`: PASSED (Valid Cortex Analyst syntax)
  - `test_cortex_engine_queries`: PASSED (Zero-drift SQL compilation)
  - `test_mcp_server_actions`: PASSED (Real cross-system tool execution)
  - `test_leads_infra_linking`: PASSED (All warehouses bound to state infrastructure indices)

---

### How to Run the Solution

```bash
# 1. Run the entire pipeline with all validations
python run_pipeline.py

# 2. Run the automated test suite
python -m unittest discover -s tests -p "test_*.py"

# 3. Launch the native Streamlit application
streamlit run app.py
```
