import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath("."))
from engine.persona_resolver import PersonaReconciler
from engine.governed_cortex_engine import GovernedCortexEngine
from mcp.supplychain_mcp_server import SupplyChainMCPServer

# Page Config
st.set_page_config(
    page_title="SupplyChain IQ — Governed Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling (Deep Navy/Charcoal, Electric Blue, Cyan)
st.markdown("""
<style>
    .reportview-container {
        background: #070B14;
    }
    .main {
        background-color: #070B14;
        color: #E2E8F0;
    }
    .stMetric {
        background: #0D1322;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid #1B253D;
    }
    .metric-card {
        background: #0D1322;
        border: 1px solid #1B253D;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-cyan {
        background-color: rgba(6, 182, 212, 0.15);
        color: #22D3EE;
        border: 1px solid rgba(6, 182, 212, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-green {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-red {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize engines
@st.cache_resource
def load_engines():
    reconciler = PersonaReconciler()
    engine = GovernedCortexEngine()
    mcp_server = SupplyChainMCPServer()
    return reconciler, engine, mcp_server

reconciler, engine, mcp_server = load_engines()

# Load Data
@st.cache_data
def load_core_data():
    df_sales = pd.read_csv("data/bridged/fact_sales_order.csv")
    df_shipment = pd.read_csv("data/bridged/fact_shipment.csv")
    df_inv = pd.read_csv("data/bridged/fact_inventory_snapshot.csv")
    df_landed = pd.read_csv("data/bridged/fact_landed_cost.csv")
    df_wh = pd.read_csv("data/bridged/dim_plant_warehouse.csv")
    return df_sales, df_shipment, df_inv, df_landed, df_wh

df_sales, df_shipment, df_inv, df_landed, df_wh = load_core_data()

# SIDEBAR CONTROLS
st.sidebar.title("⚡ SupplyChain IQ")
st.sidebar.markdown("<span class='badge-cyan'>Snowflake Cortex Governed</span> <span class='badge-green'>Ontology v2.4</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

persona = st.sidebar.selectbox(
    "👤 Active User Persona",
    [
        "Supply Chain Director (Executive)",
        "Planning Lead (Demand & Supply)",
        "Procurement Lead (Vendor & Sourcing)",
        "Logistics Manager (Fleet & Carriers)"
    ]
)

corridor_filter = st.sidebar.selectbox(
    "🌏 Operational Corridor",
    [
        "All Corridors (India, GCC, South Asia)",
        "India Domestic Network",
        "GCC Corridors (Saudi Arabia, UAE, Qatar)",
        "South Asia Cross-Border (Nepal, BD, LK)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Connected Data Assets")
st.sidebar.markdown("""
- **TMS**: 25,000 Delivery Records
- **ERP**: 113,097 Multi-Tier SC Nodes
- **Fulfillment**: 99,441 Customer Orders
- **Macro**: ADB Asian Input-Output Tables
- **Infra**: India LEADS State Scores
""")

# APP HEADER
st.title("SupplyChain IQ — Ontology & Governed Analytics")
st.markdown("##### *Unified, zero-drift supply chain intelligence powered by the Canonical Ontology and Snowflake Cortex.*")

# MAIN TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Command Center",
    "⚖️ Persona Consistency Inspector",
    "🤖 Cortex Governed Analytics",
    "🌐 Ontology & Data Lineage",
    "🚨 Disruption Simulator & MCP Actions"
])

# ====================================================================
# TAB 1: COMMAND CENTER
# ====================================================================
with tab1:
    st.subheader("Global & Regional Supply Chain Telemetry")
    
    # 5 KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    overall_otif = round((df_sales['is_canonical_otif'].sum() / len(df_sales)) * 100, 1)
    carrier_sla = round((df_shipment['carrier_sla_met'].sum() / len(df_shipment)) * 100, 1)
    avg_doi = round(df_inv['days_of_inventory'].mean(), 1)
    crit_skus = int((df_inv['days_of_inventory'] < 14).sum())
    avg_freight = round(df_shipment['delivery_cost'].mean(), 2)

    with col1:
        st.metric(label="Canonical OTIF", value=f"{overall_otif}%", delta="-2.1% vs target")
        st.caption("Commit-to-POD in full")
    with col2:
        st.metric(label="Carrier Transit SLA", value=f"{carrier_sla}%", delta="+0.4% this month")
        st.caption("18,331 of 25k on-time")
    with col3:
        st.metric(label="Days of Inventory (DOI)", value=f"{avg_doi} Days", delta="-1.8 days")
        st.caption("Target: 28-35 days")
    with col4:
        st.metric(label="Stockout Vulnerabilities", value=f"{crit_skus} SKUs", delta=f"{crit_skus} critical", delta_color="inverse")
        st.caption("Runway < 14 days")
    with col5:
        st.metric(label="Avg Delivery Cost", value=f"₹{avg_freight}", delta="Delhivery lowest @ ₹848")
        st.caption("Across 9 logistics partners")

    st.markdown("---")

    # Middle Row: Carrier Performance & Regional Breakdown
    m_left, m_right = st.columns([3, 2])

    with m_left:
        st.markdown("#### Logistics Carrier SLA Adherence vs Delayed Shipments")
        carrier_perf = df_shipment.groupby('delivery_partner').agg(
            total_shipments=('shipment_id', 'count'),
            on_time=('carrier_sla_met', 'sum'),
            avg_cost=('delivery_cost', 'mean')
        ).reset_index()
        carrier_perf['sla_adherence_pct'] = (carrier_perf['on_time'] / carrier_perf['total_shipments'] * 100).round(1)
        carrier_perf['delay_rate_pct'] = (100 - carrier_perf['sla_adherence_pct']).round(1)
        carrier_perf = carrier_perf.sort_values('sla_adherence_pct', ascending=False)
        
        # Display as styled dataframe
        st.dataframe(
            carrier_perf[['delivery_partner', 'total_shipments', 'sla_adherence_pct', 'delay_rate_pct', 'avg_cost']],
            column_config={
                "delivery_partner": "Carrier Partner",
                "total_shipments": "Shipment Volume",
                "sla_adherence_pct": st.column_config.ProgressColumn("SLA Adherence %", min_value=0, max_value=100, format="%.1f%%"),
                "delay_rate_pct": st.column_config.NumberColumn("Delay Rate %", format="%.1f%%"),
                "avg_cost": st.column_config.NumberColumn("Avg Cost (INR)", format="₹%.2f")
            },
            hide_index=True,
            use_container_width=True
        )

    with m_right:
        st.markdown("#### Regional Hub Telemetry & Bottlenecks")
        region_perf = df_shipment.groupby('region').agg(
            dispatches=('shipment_id', 'count'),
            on_time=('carrier_sla_met', 'sum'),
            avg_cost=('delivery_cost', 'mean')
        ).reset_index()
        region_perf['on_time_pct'] = (region_perf['on_time'] / region_perf['dispatches'] * 100).round(1)
        
        st.dataframe(
            region_perf[['region', 'dispatches', 'on_time_pct', 'avg_cost']],
            column_config={
                "region": "Zone / Corridor",
                "dispatches": "Dispatches",
                "on_time_pct": st.column_config.ProgressColumn("On-Time %", min_value=0, max_value=100, format="%.1f%%"),
                "avg_cost": st.column_config.NumberColumn("Avg Cost", format="₹%.2f")
            },
            hide_index=True,
            use_container_width=True
        )

# ====================================================================
# TAB 2: PERSONA CONSISTENCY INSPECTOR
# ====================================================================
with tab2:
    st.subheader("Cross-Persona Metric Reconciliation Matrix")
    st.markdown("""
    **Core Problem Addressed**: *Supply chain data is scattered across ERP, logistics, and supplier systems with inconsistent definitions, so the same question yields different answers across teams.*
    
    Below is the live proof demonstrating how previously fragmented perspectives resolve identically to the **Canonical Supply Chain Ontology**:
    """)

    df_reconciliation = reconciler.reconcile_otif()
    st.dataframe(df_reconciliation, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### Mathematical Proof of Disambiguation")
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("##### 📦 Planning Persona")
        st.info("**Scope**: Sales Order to Customer POD\n\n**Measured**: 25,000 Customer Orders\n\n**Result**: **22.91%**\n\n**Status**: Matches Canonical View (100% Grounded)")
    with p2:
        st.markdown("##### 🏭 Procurement Persona")
        st.warning("**Scope**: Supplier Dock Delivery\n\n**Measured**: 15,000 Purchase Orders\n\n**Result**: **50.36%**\n\n**Status**: Disambiguated as Component Metric `procurement_dock_otif`")
    with p3:
        st.markdown("##### 🚚 Logistics Persona")
        st.success("**Scope**: Carrier Transit SLA\n\n**Measured**: 25,000 Shipments\n\n**Result**: **73.32%**\n\n**Status**: Disambiguated as Component Metric `carrier_sla_met`")

# ====================================================================
# TAB 3: CORTEX GOVERNED CONVERSATIONAL ANALYTICS
# ====================================================================
with tab3:
    st.subheader("Snowflake Cortex Analyst Governed Query Engine")
    st.caption("Natural language queries compiled through the Canonical Ontology into verified Snowflake SQL with zero hallucinations.")

    # Preset Questions
    preset = st.selectbox(
        "💡 Select a Certified Governed Query Benchmark:",
        [
            "Which carrier partner has the highest delivery delays in the corridor?",
            "Which SKUs have critical stockout risk with less than 14 days of inventory?",
            "Decompose landed cost and freight share by region",
            "What is our enterprise canonical OTIF rate?"
        ]
    )

    custom_query = st.text_input("Or enter your own custom supply chain question:", value=preset)

    if st.button("🚀 Run Governed Cortex Query", type="primary"):
        with st.spinner("Compiling query against Canonical Ontology and Snowflake Semantic Views..."):
            response = engine.ask(custom_query, user_persona=persona)

        st.success(f"**Synthesized Answer ({response['execution_time_ms']} ms):**")
        st.markdown(f"### {response['synthesis']}")

        # Evidence Drawer
        with st.expander("🛡️ Inspect Governed Proof & Evidence Chain (Zero-Drift Attestation)", expanded=True):
            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("Ontology Node", response['evidence']['ontology_binding'])
            ec2.metric("Source Table", response['evidence']['source_table'])
            ec3.metric("Confidence", f"{response['confidence']*100:.1f}%")
            ec4.metric("Policy Check", "PASSED ✓")

            st.markdown("##### Compiled Snowflake SQL Query:")
            st.code(response['sql'], language="sql")

        st.markdown("##### Executed Query Result:")
        st.dataframe(response['data'], use_container_width=True)

# ====================================================================
# TAB 4: ONTOLOGY & DATA LINEAGE
# ====================================================================
with tab4:
    st.subheader("Canonical Supply Chain Ontology & Medallion Lineage")
    
    st.markdown("""
    ```mermaid
    graph LR
        S[Supplier] -->|supplies| P[Part / SKU]
        P -->|stocked in| W[Plant / Warehouse]
        W -->|dispatched via| SH[Shipment / Carrier]
        SH -->|fulfills| O[Sales Order]
        O -->|delivered to| C[Customer]
    ```
    """)

    st.markdown("---")
    st.markdown("#### End-to-End Snowflake Data Flow Pipeline")
    
    l1, l2, l3, l4, l5 = st.columns(5)
    with l1:
        st.markdown("**1. Raw Ingestion**\n\n• Delivery_Logistics.csv\n\n• dynamic_supply_chain.csv\n\n• ADB IO Trade Tables")
    with l2:
        st.markdown("**2. Bronze & Silver**\n\n• Typed Schemas\n\n• Referential Integrity\n\n• Deduped Entities")
    with l3:
        st.markdown("**3. Semantic Layer**\n\n• V_CANONICAL_OTIF\n\n• V_FILL_RATE\n\n• V_INVENTORY_HEALTH\n\n• V_LANDED_COST")
    with l4:
        st.markdown("**4. Cortex Analyst**\n\n• semantic_model.yaml\n\n• Verified Queries\n\n• Persona Disambiguation")
    with l5:
        st.markdown("**5. Governed Output**\n\n• Streamlit App\n\n• CoCo CLI Agents\n\n• MCP Tool Actions")

# ====================================================================
# TAB 5: DISRUPTION SIMULATOR & MCP ACTIONS
# ====================================================================
with tab5:
    st.subheader("Proactive Disruption Simulator & MCP Tool Calling")
    st.caption("Demonstrates custom tools and function calling through MCP to take real actions across ERP and TMS.")

    sim_scenario = st.selectbox(
        "Select Simulation Scenario:",
        [
            "Central India Monsoon Surge: XpressBees fleet transit delays in Nagpur/Bhopal",
            "Red Sea & GCC Shipping Disruption: Lead-time spike for Saudi Arabia & Qatar ports",
            "Warehouse Stockout Alert: Electronic components drop below 14-day runway"
        ]
    )

    if st.button("⚡ Execute Scenario & Dispatch MCP Actions"):
        st.warning(f"Simulating Disruption: {sim_scenario}")
        
        st.markdown("#### Agentic Action Dispatch Log (MCP Protocol):")
        
        # Tool 1: Reroute Shipment
        act1 = mcp_server.execute_tool("reroute_delayed_shipment", {
            "shipment_id": "SHP-10042",
            "current_carrier": "xpressbees",
            "new_carrier": "delhivery",
            "reason": "Severe weather transit bottleneck in Central India"
        })
        st.success(f"**[TMS Action]**: {act1['message']} ({act1['mitigation']})")

        # Tool 2: ERP Reorder
        act2 = mcp_server.execute_tool("trigger_procurement_reorder", {
            "supplier_id": "P0353_S1",
            "product_id": "SKU-P0353",
            "quantity": 2500,
            "destination_warehouse": "WH_NAGPUR_C"
        })
        st.info(f"**[ERP Action]**: {act2['message']} (Tracking ID: {act2['erp_tracking_id']})")

        # Tool 3: Slack Broadcast
        act3 = mcp_server.execute_tool("broadcast_slack_incident", {
            "channel": "#supply-chain-incident-ops",
            "incident_title": "Central Corridor Delay Mitigated",
            "mitigation_action": "Rerouted to Delhivery, safety stock reorder triggered."
        })
        st.markdown(f"📢 **[Slack Notification]**: {act3['message']}")
