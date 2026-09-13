-- ====================================================================
-- SNOWFLAKE COCO HACKATHON - GCC EDITION
-- SCRIPT 02: GOVERNED SEMANTIC VIEWS & CANONICAL ONTOLOGY
-- Schema: GOLD_SEMANTIC
-- ====================================================================

USE DATABASE SUPPLYCHAIN_IQ_DB;
USE SCHEMA GOLD_SEMANTIC;

-- 1. CANONICAL ON-TIME IN-FULL (OTIF) GOVERNED VIEW
-- Resolves the fundamental supply chain metric:
-- Delivered on or before Promised Date AND Fulfilled Qty >= Ordered Qty
CREATE OR REPLACE VIEW GOLD_SEMANTIC.V_CANONICAL_OTIF AS
SELECT 
    w.region,
    w.warehouse_name,
    w.country AS fulfillment_country,
    s.delivery_partner AS carrier_partner,
    p.category AS product_category,
    COUNT(o.order_id) AS total_orders,
    SUM(o.is_on_time) AS on_time_orders,
    SUM(o.is_in_full) AS in_full_orders,
    SUM(o.is_canonical_otif) AS otif_orders,
    ROUND(SUM(o.is_on_time) * 100.0 / COUNT(o.order_id), 2) AS on_time_percentage,
    ROUND(SUM(o.is_in_full) * 100.0 / COUNT(o.order_id), 2) AS in_full_percentage,
    ROUND(SUM(o.is_canonical_otif) * 100.0 / COUNT(o.order_id), 2) AS canonical_otif_percentage,
    ROUND(AVG(s.delivery_cost), 2) AS avg_delivery_cost
FROM SILVER_CLEAN.FACT_SALES_ORDER o
JOIN SILVER_CLEAN.DIM_PLANT_WAREHOUSE w ON o.warehouse_id = w.warehouse_id
JOIN SILVER_CLEAN.FACT_SHIPMENT s ON o.shipment_id = s.shipment_id
JOIN SILVER_CLEAN.DIM_PART p ON o.product_id = p.product_id
GROUP BY w.region, w.warehouse_name, w.country, s.delivery_partner, p.category;

-- 2. CANONICAL FILL RATE GOVERNED VIEW
-- Order Fill Rate vs Quantity Fill Rate
CREATE OR REPLACE VIEW GOLD_SEMANTIC.V_FILL_RATE AS
SELECT 
    p.category AS product_category,
    p.sku_code,
    w.region,
    w.warehouse_name,
    SUM(o.ordered_qty) AS total_ordered_qty,
    SUM(o.fulfilled_qty) AS total_fulfilled_qty,
    ROUND(SUM(o.fulfilled_qty) * 100.0 / NULLIF(SUM(o.ordered_qty), 0), 2) AS quantity_fill_rate_pct,
    COUNT(o.order_id) AS total_order_lines,
    SUM(CASE WHEN o.fulfilled_qty >= o.ordered_qty THEN 1 ELSE 0 END) AS fully_filled_orders,
    ROUND(SUM(CASE WHEN o.fulfilled_qty >= o.ordered_qty THEN 1 ELSE 0 END) * 100.0 / COUNT(o.order_id), 2) AS order_fill_rate_pct
FROM SILVER_CLEAN.FACT_SALES_ORDER o
JOIN SILVER_CLEAN.DIM_PART p ON o.product_id = p.product_id
JOIN SILVER_CLEAN.DIM_PLANT_WAREHOUSE w ON o.warehouse_id = w.warehouse_id
GROUP BY p.category, p.sku_code, w.region, w.warehouse_name;

-- 3. INVENTORY HEALTH & DAYS OF INVENTORY (DOI) GOVERNED VIEW
-- Current Stock / Historical Daily Demand
CREATE OR REPLACE VIEW GOLD_SEMANTIC.V_INVENTORY_HEALTH_DOI AS
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.region,
    w.leads_infra_score,
    p.product_id,
    p.sku_code,
    p.category,
    i.inventory_on_hand_qty,
    i.safety_stock_qty,
    i.daily_demand_30d_avg,
    i.days_of_inventory,
    CASE 
        WHEN i.days_of_inventory < 14 THEN 'CRITICAL_STOCKOUT_RISK'
        WHEN i.days_of_inventory BETWEEN 14 AND 25 THEN 'LOW_COVERAGE_WARNING'
        WHEN i.days_of_inventory BETWEEN 26 AND 40 THEN 'HEALTHY_BUFFER'
        ELSE 'EXCESS_INVENTORY'
    END AS inventory_health_status,
    i.stockout_risk_flag
FROM SILVER_CLEAN.FACT_INVENTORY_SNAPSHOT i
JOIN SILVER_CLEAN.DIM_PLANT_WAREHOUSE w ON i.warehouse_id = w.warehouse_id
JOIN SILVER_CLEAN.DIM_PART p ON i.product_id = p.product_id;

-- 4. TOTAL LANDED COST ANALYSIS GOVERNED VIEW
-- Decomposed Landed Cost: Base Purchase + Freight + Handling + Customs/Tariffs
CREATE OR REPLACE VIEW GOLD_SEMANTIC.V_LANDED_COST_ANALYSIS AS
SELECT 
    w.region,
    w.country AS destination_country,
    p.category AS product_category,
    COUNT(l.order_id) AS total_shipment_batches,
    SUM(l.ordered_qty) AS total_units_landed,
    SUM(l.base_purchase_cost) AS total_base_cost,
    SUM(l.freight_cost) AS total_freight_cost,
    SUM(l.handling_cost) AS total_handling_cost,
    SUM(l.customs_tariff_cost) AS total_customs_cost,
    SUM(l.total_landed_cost) AS total_landed_expenditure,
    ROUND(AVG(l.unit_landed_cost), 2) AS avg_unit_landed_cost,
    ROUND(SUM(l.freight_cost) * 100.0 / NULLIF(SUM(l.total_landed_cost), 0), 2) AS freight_cost_share_pct,
    ROUND(SUM(l.customs_tariff_cost) * 100.0 / NULLIF(SUM(l.total_landed_cost), 0), 2) AS customs_cost_share_pct
FROM SILVER_CLEAN.FACT_LANDED_COST l
JOIN SILVER_CLEAN.DIM_PLANT_WAREHOUSE w ON l.warehouse_id = w.warehouse_id
JOIN SILVER_CLEAN.DIM_PART p ON l.product_id = p.product_id
GROUP BY w.region, w.country, p.category;

-- 5. PERSONA RECONCILIATION BENCHMARK VIEW
-- Demonstrates why Planning, Procurement, and Logistics previously disagreed,
-- and how the Governed Ontology provides mathematical consistency and lineage.
CREATE OR REPLACE VIEW GOLD_SEMANTIC.V_PERSONA_RECONCILIATION AS
SELECT 
    'Planning Persona (Customer POD OTIF)' AS persona_perspective,
    'Sales Order Commit to Customer Proof-of-Delivery' AS measurement_boundary,
    COUNT(o.order_id) AS total_evaluations,
    SUM(o.is_canonical_otif) AS compliant_evaluations,
    ROUND(SUM(o.is_canonical_otif) * 100.0 / COUNT(o.order_id), 2) AS persona_otif_pct,
    'GOLD_SEMANTIC.V_CANONICAL_OTIF' AS governed_canonical_source,
    'VERIFIED_MATCH' AS reconciliation_status
FROM SILVER_CLEAN.FACT_SALES_ORDER o

UNION ALL

SELECT 
    'Procurement Persona (Supplier Dock OTIF)' AS persona_perspective,
    'Purchase Order Dock Receipt Date vs Vendor Promise' AS measurement_boundary,
    COUNT(po.po_id) AS total_evaluations,
    SUM(po.procurement_otif) AS compliant_evaluations,
    ROUND(SUM(po.procurement_otif) * 100.0 / COUNT(po.po_id), 2) AS persona_otif_pct,
    'SILVER_CLEAN.FACT_PURCHASE_ORDER.procurement_otif' AS governed_canonical_source,
    'GOVERNED_COMPONENT_ISOLATED' AS reconciliation_status
FROM SILVER_CLEAN.FACT_PURCHASE_ORDER po

UNION ALL

SELECT 
    'Logistics Persona (Carrier Transit SLA)' AS persona_perspective,
    'Dispatch Timestamp to Carrier Hand-off vs Transit SLA' AS measurement_boundary,
    COUNT(s.shipment_id) AS total_evaluations,
    SUM(s.carrier_sla_met) AS compliant_evaluations,
    ROUND(SUM(s.carrier_sla_met) * 100.0 / COUNT(s.shipment_id), 2) AS persona_otif_pct,
    'SILVER_CLEAN.FACT_SHIPMENT.carrier_sla_met' AS governed_canonical_source,
    'GOVERNED_COMPONENT_ISOLATED' AS reconciliation_status
FROM SILVER_CLEAN.FACT_SHIPMENT s;
