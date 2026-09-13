# SupplyChain IQ — Ontology & Governed Conversational Analytics
## Complete Google Stitch UI Design Prompts & Architecture Specification
**Hackathon Target**: Snowflake CoCo CLI Hackathon — GCC Edition  
**Platform Concept**: Enterprise AI Supply Chain Intelligence, Governed Semantic Ontology & Knowledge Graph  
**Visual Benchmark**: Palantir Foundry, Databricks Lakehouse, Microsoft Fabric, Snowflake Cortex  

---

## 1. Executive Summary & Data Grounding

This specification provides the production-grade **Google Stitch UI Design Prompts** for **SupplyChain IQ**, grounded in real data extracted from the local project datasets:

| Local Dataset | Entity Count | Real Data Metrics & Key Attributes Grounded in UI |
| :--- | :--- | :--- |
| **`Delivery_Logistics.csv`** | **25,000** dispatches | 9 Logistics Partners: **Delhivery** (24.8% delay, ₹848.1 avg cost), **FedEx** (25.2% delay, ₹857.4), **DHL** (26.3% delay, ₹872.8), **Blue Dart** (26.9% delay), **Ekart** (27.4% delay), **XpressBees** (28.3% delay). Regions: West, Central, South, North, East. Overall on-time OTIF proxy: **73.3%**. |
| **`dynamic_supply_chain_logistics_dataset_with_country.csv`** | **113,097** SC nodes | **15,550 Asian & GCC Corridor Nodes**: Vietnam (1,896), Bangladesh (1,416), Singapore (1,284), China (1,233), Sri Lanka (1,180), Pakistan (1,169), India (1,089), Saudi Arabia (1,082), Thailand (1,009), Nepal (973), Qatar (872), Oman (826). Risk Classes: High Risk (84,368), Moderate Risk (17,783), Low Risk (10,946). Avg lead time: **5.22 days**. |
| **`IO Publication 2022 - Masterdata.xlsx`** | Multi-regional | ADB Asian Input-Output trade dependency tables for India, Pakistan, Nepal, Bangladesh, Sri Lanka, Bhutan, Maldives. |
| **`olist_customers_dataset.csv`** | **99,441** orders | Customer geographic distribution, fulfillment destinations, zip prefix clusters. |

---

## 2. Master Google Stitch UI Prompt (Paste Directly into Stitch)

Copy and paste the block below directly into Google Stitch:

```text
Design a premium enterprise web application called "SupplyChain IQ — Ontology & Governed Conversational Analytics".
The product is an AI-powered supply-chain intelligence platform built for Snowflake Data Cloud and Cortex AI that connects ERP, WMS, TMS, procurement, multi-carrier logistics, and cross-border trade data through a governed Supply Chain Ontology and Knowledge Graph.

Visual Design System & Enterprise Aesthetic:
- Inspired by high-end enterprise data platforms like Palantir Foundry, Databricks Lakehouse, and Microsoft Fabric, with a unique visual identity.
- Background: Deep navy / charcoal (#070B14 and #090E1A) with soft slate card surfaces (#0D1322 and #111827).
- Borders & Dividers: Subtle slate borders (#1B253D and #1E293B) with 1px hairline dividers.
- Primary Accent: Electric blue (#2563EB / #3B82F6).
- AI & Semantic Highlights: Cyan glow (#06B6D4 / #22D3EE) for ontology nodes, Cortex AI answers, and confidence badges.
- Semantic Status Colors: Emerald green (#10B981) for healthy metrics, Amber (#F59E0B) for risks/warnings, Crimson (#EF4444) strictly for SLA breaches and critical disruptions.
- Surfaces: Rounded 12–16px cards with subtle elevation, backdrop blur (glassmorphism), and dense, highly readable typography (Plus Jakarta Sans + JetBrains Mono for data tokens).
- Responsive desktop-first layout (1440px+ optimized).

Global Navigation:
- Top Bar (Height: 56px):
  - Brand: "SupplyChain IQ" logo with an electric blue / cyan glowing emblem.
  - Active badges: "Ontology v2.4" (cyan pulse) and "Snowflake Cortex Governed".
  - Global omni-search: "Search SKU, Partner, Corridor, PO, or Entity (⌘K)".
  - Telemetry freshness: "Data fresh: 12 min ago (Snowflake Stream Synced)".
  - Global "Ask SupplyChain IQ" action button (electric blue-to-cyan gradient).
  - User role pill: "SC Director (GCC & South Asia)".

- Left Sidebar (Width: 240px, Dark Navy):
  - Section 1 (Analytics & Control):
    * Command Center (Executive Overview)
    * Conversational Analytics (Flagship AI Hub with Evidence Drawer)
    * Ontology Explorer (Interactive Network Canvas)
    * Knowledge Graph (Multi-hop Entity Traversal)
    * Governance & Lineage (Audit Trail & Pipeline)
  - Section 2 (Operational Domains):
    * Suppliers & Partners (Delhivery, FedEx, DHL, Blue Dart, XpressBees)
    * Inventory & Stockout Risk (WMS telemetry)
    * Regional Corridors (India, GCC, South Asia ADB trade flows)
    * Risk & Disruption Center
  - Bottom Status Card: Live ingestion indicators showing 25,000 TMS dispatches and 113,097 multi-tier supplier nodes loaded.

Screen 1 — Supply Chain Command Center:
- Header: "Supply Chain Command Center | Regional Corridor: India, South Asia & GCC"
- Subtitle: "AI-orchestrated, governed operational telemetry across 25,000 domestic dispatches and 113,097 multi-tier supplier nodes."
- 6 Metric KPI Cards (Rounded 14px, dark glass cards):
  1. Corridor OTIF: 73.3% (18,331 on-time / 25k dispatches, amber trend -2.4%).
  2. Avg Lead Time: 5.22 days (emerald trend +0.3d improvement).
  3. Disruption Risk Index: 0.803 (Crimson warning: 84,368 High-Risk Nodes).
  4. Avg Delivery Cost: ₹864.9 (~$10.42 / unit, Delhivery lowest at ₹848.1).
  5. Active Asian & GCC Nodes: 15,550 entities across Vietnam, Bangladesh, Saudi Arabia, India, Pakistan, Nepal, Qatar, Oman.
  6. Governed Ontology Coverage: 94.8% (100% Policy Bound to Snowflake Cortex).
- Main Layout (2 Columns):
  - Left (2/3): Interactive Multi-Carrier Logistics Reliability vs Delay Bar Chart comparing Delhivery (75.2% OTIF, 24.8% delay), FedEx (74.8% OTIF, 25.2% delay), DHL (73.7% OTIF, 26.3% delay), Blue Dart (73.1% OTIF, 26.9% delay), Ekart (72.6% OTIF, 27.4% delay), and XpressBees (71.7% OTIF, 28.3% delay).
  - Right (1/3): Governed AI Alerts Feed with real data insights:
    * High Risk: XpressBees delay rate reached 28.3% across 2,826 shipments with 167 failures.
    * Regional Warning: Nepal & Bangladesh cross-border intermediate transit delay increased lead times to 6.8 days.
    * GCC Opportunity: Saudi Arabia & Qatar route optimization via sea-air hubs yields 12% lower cost.
- Bottom Data Table: Indian Regional Dispatch Telemetry table showing West (5,095 dispatches, 26.9% delay), Central (5,060 dispatches, 27.3% delay bottleneck), South (4,977 dispatches, 26.8% delay), North (4,949 dispatches, 26.6% delay), and East (4,919 dispatches, 25.8% delay).

Screen 2 — Flagship Governed Conversational Analytics:
- Header: "Ask your Supply Chain (Snowflake Cortex Governed Engine)"
- Large chat workspace with multi-turn message stream.
- User Question Card: "Which logistics partners caused the highest delivery delays in the South Asia & India corridor?"
- AI Response Container (Enterprise-grade, NOT generic ChatGPT):
  - Natural Language Synthesis summarizing 25,000 dispatches, 6,669 delays (26.7%), highlighting XpressBees (28.3%) and Ekart (27.4%) vs Delhivery (24.8%).
  - Embedded micro-chart showing partner delay breakdowns and failure counts.
  - Attached Governance Evidence Panel:
    * Ontology Binding: Carrier.delivery_delay & Shipment.status
    * Access Policy: SC_MANAGER_ROLE verified (row-level cost masking applied)
    * Source Tables: TMS_DELIVERY_LOGISTICS & DYNAMIC_SC_MASTER
    * Snowflake Cortex Execution Time: 142 ms
    * Freshness: Synced 12 minutes ago
  - Action toolbar: "View Cortex SQL", "Explain Reasoning", "Open Data Lineage", "Export Governed Proof".
- Quick-query pill suggestions: "Why did delivery performance degrade in Central India?", "Identify high risk suppliers in Vietnam & Saudi Arabia", "Compare lead time volatility between South Asia and GCC".

Screen 3 — Interactive Ontology Explorer:
- Title: "Supply Chain Canonical Ontology (v2.4 Master Schema)"
- Subtitle: "Semantic entity-relationship canvas binding 23,481 entities and 67 relationship types across ERP, TMS, and Macro trade."
- Central Hub Node: "Supply Chain Core Hub".
- Connected Canonical Entity Nodes (arranged in a radial cluster with glowing SVG connectors):
  * Supplier (113,097 nodes, reliability & lead time)
  * Purchase Order (SAP PO lines)
  * Product / SKU (38,410 catalog items)
  * Shipment (25,000 TMS transits)
  * Carrier Partner (Delhivery, Blue Dart, FedEx, DHL, XpressBees)
  * Warehouse & Inventory (84 stock hubs)
  * Country / Corridor (India, GCC, South Asia ADB trade matrices)
  * Governed Metric (OTIF, Lead Time, Cost Deviation)
  * Risk Event (Disruption likelihood & weather impact)
- Right-side Entity Inspector Drawer: Clicking a node displays Entity Details, Attribute Schemas (e.g., delivery_partner VARCHAR, delivery_cost NUMERIC), and Ontology Relationships (e.g., Carrier fulfills Shipment, Carrier triggers SLA Breach).

Screen 4 — Knowledge Graph Workspace:
- Title: "Multi-Hop Knowledge Graph Investigation"
- Search: "Find supplier, purchase order, carrier, or commodity relationship..."
- Multi-Hop Graph Traversal displaying end-to-end causality:
  Tier-1 Supplier (Vietnam: P0353_S1, Reliability 0.986)
  ↓ [issues]
  Purchase Order (PO-2024-8841, Lead Time 2.13d)
  ↓ [dispatches]
  Cross-Border Transit (SHP-VN-IND-409, Disruption Score 0.506)
  ↓ [last-mile handoff]
  Domestic Carrier (Delhivery DEL-IND-25099, Cost ₹848.11, On-Time)
  ↓ [stocks]
  Destination Hub (WH-WEST-MUMBAI, Inv Level 985.7 units)
- Causality Synthesis Card: Explains that upstream supplier reliability is high, but domestic handoff at the Central regional warehouse experienced equipment availability drops (0.481).

Screen 5 — Governance, Data Lineage & Audit:
- Title: "Data Lineage & Governance Integrity (Snowflake Audited)"
- Visual Left-to-Right Pipeline:
  Raw ERP/TMS/ADB Files → Snowflake Bronze Layer → Snowflake Silver (Cleaned) → Snowflake Semantic Layer (Metrics) → Canonical Ontology v2.4 → Snowflake Cortex LLM → Governed UI Insight.
- Governed Metrics Catalog: Table of approved business metrics (OTIF, Lead Time, Disruption Risk, Unit Cost) with SQL logic, business owner, and certification status.
- Immutable AI & Data Audit Log Table:
  Columns: Timestamp | User & Role | Question Asked | Dataset Target | Security Policy | Result Count | Attestation Status (e.g., "Allowed ✓", "Masked", "Blocked ✕").

UX Principle:
The interface must visually articulate the complete chain of trust:
Natural Language → Ontology Validation → Access Control → Snowflake Cortex SQL → Evidence Attestation → Actionable Insight.
```

---

## 3. Screen-by-Screen Stitch Prompts

Use these modular prompts if generating screens individually in Google Stitch:

### Screen 1: Executive Command Center
```text
Design Screen 1 of SupplyChain IQ: "Executive Supply Chain Command Center".
Theme: Deep navy (#070B14) with soft slate cards (#0D1322) and electric blue (#3B82F6) / cyan (#06B6D4) accents.
Top Bar: App name "SupplyChain IQ", active tags "Ontology v2.4", "Snowflake Cortex Governed", global search bar (⌘K), data freshness badge "Synced 12 min ago", and "Ask SupplyChain IQ" gradient button.
KPI Header Grid: 6 cards displaying Corridor OTIF (73.3%, amber -2.4%), Avg Lead Time (5.22 days, emerald), Disruption Risk (0.803, red 84,368 High Risk nodes), Avg Delivery Cost (₹864.9, Delhivery lowest @ ₹848.1), GCC & Asian Corridor Nodes (15,550 entities), and Ontology Coverage (94.8%).
Main Section (Split 2:1):
Left 2/3: Logistics Carrier Reliability vs Delay Rate bar chart comparing Delhivery (75.2% OTIF), FedEx (74.8%), DHL (73.7%), Blue Dart (73.1%), Ekart (72.6%), and XpressBees (71.7% OTIF, 28.3% delay rate).
Right 1/3: Governed AI Alerts card highlighting XpressBees delivery bottlenecks (167 failures), South Asia cross-border trade delays (Nepal/Bangladesh), and GCC export cost optimizations.
Bottom Section: Regional Dispatch Telemetry table for Indian zones (West, Central bottleneck @ 27.3% delay, South, North, East) with total dispatches, on-time counts, and risk badges.
```

### Screen 2: Governed Conversational Analytics (Flagship AI Hub)
```text
Design Screen 2 of SupplyChain IQ: "Governed Conversational Analytics".
Layout: Split view with a flagship AI dialogue feed on the left (75% width) and a Governance Guardrails inspector on the right (25% width).
Theme: Deep slate/navy with electric blue user chat bubbles and dark-card AI response panels accented with cyan highlights.
Conversation Flow:
1. User prompt bubble: "Which logistics partners caused the highest delivery delays in the South Asia & India corridor?"
2. AI Response Container featuring:
   - Analytical summary based on 25,000 TMS shipments and 6,669 delays.
   - Embedded progress bar breakdown of top 3 delay contributors (XpressBees 28.3%, Ekart 27.4%, Blue Dart 26.9%).
   - Governed Proof & Evidence Chain card showing:
     * Ontology Binding: Carrier.delivery_delay & Shipment.status
     * Access Policy: SC_MANAGER_ROLE verified (row-level security active)
     * Source Data: TMS_DELIVERY_LOGISTICS & DYNAMIC_SC_MASTER (Snowflake)
     * Freshness: 12 min ago | Execution: 142ms
     * Action buttons: "View Cortex SQL", "Inspect Lineage", "Explore Ontology".
Bottom Input Bar: Rich query input with "Query" button and suggested prompt pills: "Why did delivery performance degrade in Central India?", "Identify high risk suppliers in Vietnam & Saudi Arabia".
Right Inspector: Displays Active Access Role (GLOBAL_SC_ANALYST), Masking status (Unit cost redacted), Snowflake Cortex LLM zero-hallucination mode, and immutable audit transaction ID TX-9842109.
```

### Screen 3: Interactive Ontology Explorer
```text
Design Screen 3 of SupplyChain IQ: "Supply Chain Canonical Ontology Explorer".
Header: Title "Supply Chain Canonical Ontology (v2.4 Master Schema)" with metadata "23,481 entities, 67 relationship types, 15 linked entity classes".
Main Area: A network graph canvas against a dark charcoal background (#060A12) with glowing SVG nodes and relationship connectors:
- Central Hub: "Supply Chain Core Hub" (Electric blue ring).
- Satellite Nodes:
  * Supplier (113,097 nodes, cyan border)
  * Purchase Order (blue border)
  * Product / SKU (blue border)
  * Shipment (25,000 TMS transits, cyan border)
  * Carrier Partner (Delhivery, DHL, FedEx, cyan border)
  * Warehouse & Inventory (emerald border)
  * Country / Regional Corridor (ADB trade matrices, purple border)
  * Risk & Disruption (crimson border)
  * Governed Metric (emerald border)
Right Inspector Panel (Width: 320px): Shows selected entity details for "Carrier Partner":
- Governed Attributes list: delivery_partner (VARCHAR), delivery_mode (VARCHAR), delivery_cost (NUMERIC), delayed_flag (BOOLEAN).
- Ontology Relationships: fulfills → Shipment, operates_in → Region/Corridor, triggers → SLA Breach.
- Data source origin: TMS_DELIVERY_LOGISTICS.
```

### Screen 4: Multi-Hop Knowledge Graph Investigation Workspace
```text
Design Screen 4 of SupplyChain IQ: "Multi-Hop Knowledge Graph Investigation".
Header: "Multi-Hop Knowledge Graph" with search bar "Find supplier, PO, carrier, or relationship..." and confidence indicator "Confidence: 99.4% Verified".
Main Visual: A multi-hop horizontal node chain illustrating end-to-end supply chain causality:
Node 1 (Tier-1 Supplier): P0353_S1 | Vietnam | Reliability 0.986 | ERP_SUPPLIER_MASTER
↓
Node 2 (Purchase Order): PO-2024-8841 | Product P0353 | Lead Time 2.13 days | SAP_PO_HEADERS
↓
Node 3 (Corridor Transit): SHP-VN-IND-409 | Ocean + Road | Disruption Likelihood 0.506 | TMS_DYNAMIC_LOGISTICS
↓
Node 4 (Domestic Carrier): Delhivery DEL-IND-25099 | Cost ₹848.11 | Status: Delivered Clean | DELIVERY_LOGISTICS_IND
↓
Node 5 (Destination Warehouse): WH-WEST-MUMBAI | Inventory Level 985.7 units | Fulfillment 76.1% | WMS_STOCK_TELEMETRY
Bottom Card: Automated Causality Synthesis box explaining that upstream supplier reliability is high, but intermediate transit disruption risk required rerouting to Delhivery to prevent warehouse stockout.
```

### Screen 5: Data Governance, Lineage & Audit Trail
```text
Design Screen 5 of SupplyChain IQ: "Data Lineage & Governance Integrity".
Header: "Data Lineage & Governance Integrity (Snowflake Audited)" with score card "Governance Score: 98.6%".
Top Section (Pipeline Architecture): A 6-stage left-to-right lineage pipeline diagram:
1. Source Systems (ERP, WMS, TMS, ADB IO Tables)
→ 2. Snowflake Lakehouse (Bronze & Silver Raw Tables)
→ 3. Semantic Layer (Standardized Business Metrics: OTIF, Lead Time)
→ 4. Canonical Ontology (v2.4 Schema & 67 Relationship Types)
→ 5. Snowflake Cortex AI (Governed SQL Generation)
→ 6. Verified UI Insight (Attested Proof Chain)
Bottom Section (Audit Log Table):
Table with columns: Timestamp, User & Role, Governed Question, Dataset Target, Security Policy Executed, Result Count, Attestation Status.
Row 1: 19:14:02 | SC_DIRECTOR | "Show delivery delays by partner" | TMS_DELIVERY (25k) | MASK_FINANCIALS | 9 records | Allowed ✓
Row 2: 18:49:15 | PROCUREMENT_LEAD | "High risk suppliers in Vietnam" | DYNAMIC_SC (113k) | TIER_1_ACCESS | 1,896 records | Allowed ✓
Row 3: 18:12:30 | EXTERNAL_AUDITOR | "Export unmasked contract margins" | ERP_COST_TABLE | ROW_LEVEL_SEC | 0 records | Blocked ✕ (Crimson badge)
```

---

## 4. Canonical Supply Chain Ontology & Snowflake Mapping

Below is the formal schema and mapping connecting your local datasets into the Snowflake Semantic Layer:

```sql
-- ====================================================================
-- SNOWFLAKE SEMANTIC LAYER & CANONICAL ONTOLOGY (v2.4)
-- Database: SNOWFLAKE_SC_DB | Schema: SEMANTIC
-- ====================================================================

-- 1. Carrier & Logistics Semantic Table (Source: Delivery_Logistics.csv)
CREATE OR REPLACE TABLE SEMANTIC.TMS_DELIVERY_LOGISTICS (
    delivery_id VARCHAR(32) PRIMARY KEY,
    delivery_partner VARCHAR(50) NOT NULL, -- Delhivery, FedEx, DHL, Ekart, Blue Dart, XpressBees
    package_type VARCHAR(50),
    vehicle_type VARCHAR(50),
    delivery_mode VARCHAR(50),
    region VARCHAR(30), -- West, Central, South, North, East
    weather_condition VARCHAR(30),
    distance_km FLOAT,
    package_weight_kg FLOAT,
    delayed VARCHAR(5), -- 'yes' / 'no'
    delivery_status VARCHAR(30), -- 'delivered', 'delayed', 'failed'
    delivery_rating INT,
    delivery_cost FLOAT
);

-- 2. Global & Corridor Risk Semantic Table (Source: dynamic_supply_chain_logistics_dataset_with_country.csv)
CREATE OR REPLACE TABLE SEMANTIC.DYNAMIC_SC_MASTER (
    product_id VARCHAR(32),
    supplier_id VARCHAR(32),
    supplier_country VARCHAR(64), -- Vietnam, Bangladesh, Saudi Arabia, India, Pakistan, Nepal, Qatar, Oman
    lead_time_days FLOAT,
    supplier_reliability_score FLOAT, -- 0.0 to 1.0
    disruption_likelihood_score FLOAT,
    delay_probability FLOAT,
    risk_classification VARCHAR(30), -- 'High Risk', 'Moderate Risk', 'Low Risk'
    delivery_time_deviation FLOAT,
    warehouse_inventory_level FLOAT,
    order_fulfillment_status FLOAT
);

-- 3. Governed Semantic Metric Definitions
-- OTIF (On-Time In-Full) Rate:
-- Ratio of shipments delivered with delayed = 'no' and delivery_status = 'delivered'
CREATE OR REPLACE VIEW SEMANTIC.METRIC_CORRIDOR_OTIF AS
SELECT 
    region,
    delivery_partner,
    COUNT(delivery_id) AS total_dispatches,
    SUM(CASE WHEN delayed = 'no' AND delivery_status = 'delivered' THEN 1 ELSE 0 END) AS on_time_in_full,
    ROUND(SUM(CASE WHEN delayed = 'no' AND delivery_status = 'delivered' THEN 1 ELSE 0 END) * 100.0 / COUNT(delivery_id), 1) AS otif_rate,
    ROUND(AVG(delivery_cost), 2) AS avg_cost
FROM SEMANTIC.TMS_DELIVERY_LOGISTICS
GROUP BY region, delivery_partner;
```

---

## 5. Live Interactive Prototype

A fully functional, zero-external-dependency web prototype has been built and saved at:
`C:\Users\Victus\.gemini\antigravity\brain\7e2332af-ceb6-4d63-9faa-4e59797b8f8a\supplychain_iq_prototype.html`

It features:
- Interactive tab navigation across all 5 core screens.
- Real carrier benchmark data from your 25,000 shipment dispatches.
- Conversational AI simulator demonstrating the 5-stage governed evidence flow.
- Interactive SVG Ontology Explorer with clickable nodes and attribute inspectors.
- Multi-hop knowledge graph traversal with confidence scores.
- Snowflake Cortex SQL modal inspector and immutable audit trail.
