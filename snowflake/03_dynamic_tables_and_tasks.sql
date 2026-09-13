-- ====================================================================
-- SNOWFLAKE COCO HACKATHON - GCC EDITION
-- SCRIPT 03: DYNAMIC TABLES, STREAMS & AUTOMATED TASKS
-- Focus: Automated Pipeline Orchestration & Near-Real-Time Materialization
-- ====================================================================

USE DATABASE SUPPLYCHAIN_IQ_DB;
USE SCHEMA GOLD_SEMANTIC;

-- 1. Snowflake Dynamic Table: Real-Time Carrier Performance Aggregation
-- Materializes live metrics with 1-minute target lag
CREATE OR REPLACE DYNAMIC TABLE GOLD_SEMANTIC.DT_CARRIER_PERFORMANCE_REALTIME
    TARGET_LAG = '1 MINUTE'
    WAREHOUSE = COMPUTE_WH
AS
SELECT 
    delivery_partner,
    region,
    COUNT(shipment_id) AS total_shipments,
    SUM(carrier_sla_met) AS on_time_shipments,
    SUM(CASE WHEN carrier_sla_met = 0 THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND(SUM(carrier_sla_met) * 100.0 / COUNT(shipment_id), 2) AS carrier_sla_pct,
    ROUND(AVG(delivery_cost), 2) AS avg_delivery_cost,
    ROUND(AVG(distance_km), 1) AS avg_transit_distance_km
FROM SILVER_CLEAN.FACT_SHIPMENT
GROUP BY delivery_partner, region;

-- 2. Snowflake Dynamic Table: Near-Real-Time Stockout Risk Monitor
CREATE OR REPLACE DYNAMIC TABLE GOLD_SEMANTIC.DT_INVENTORY_STOCKOUT_ALERTS
    TARGET_LAG = '1 MINUTE'
    WAREHOUSE = COMPUTE_WH
AS
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.region,
    p.product_id,
    p.sku_code,
    p.category,
    i.inventory_on_hand_qty,
    i.safety_stock_qty,
    i.days_of_inventory,
    CASE 
        WHEN i.days_of_inventory < 14 THEN 'P1_CRITICAL'
        WHEN i.days_of_inventory < 21 THEN 'P2_HIGH_RISK'
        ELSE 'P3_NORMAL'
    END AS alert_severity,
    CURRENT_TIMESTAMP() AS evaluated_at
FROM SILVER_CLEAN.FACT_INVENTORY_SNAPSHOT i
JOIN SILVER_CLEAN.DIM_PLANT_WAREHOUSE w ON i.warehouse_id = w.warehouse_id
JOIN SILVER_CLEAN.DIM_PART p ON i.product_id = p.product_id
WHERE i.days_of_inventory < 21;

-- 3. Snowflake Stream on Sales Orders for Real-Time SLA Monitoring
CREATE OR REPLACE STREAM SILVER_CLEAN.STR_SALES_ORDER_CDC
    ON TABLE SILVER_CLEAN.FACT_SALES_ORDER;

-- 4. Snowflake Task: Automated Incident Logger for SLA Misses
CREATE OR REPLACE TASK GOLD_SEMANTIC.TSK_PROCESS_SLA_BREACHES
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 * * * * UTC' -- Runs hourly or when stream has data
    WHEN SYSTEM$STREAM_HAS_DATA('SILVER_CLEAN.STR_SALES_ORDER_CDC')
AS
INSERT INTO GOLD_SEMANTIC.FACT_DISRUPTION_INCIDENTS (
    incident_id,
    entity_id,
    entity_type,
    incident_type,
    incident_severity,
    incident_description,
    detected_at
)
SELECT 
    UUID_STRING() AS incident_id,
    order_id AS entity_id,
    'SALES_ORDER' AS entity_type,
    'SLA_BREACH_DETECTED' AS incident_type,
    'HIGH' AS incident_severity,
    CONCAT('Order ', order_id, ' missed promise date with fulfilled qty ', fulfilled_qty, ' of ', ordered_qty),
    CURRENT_TIMESTAMP() AS detected_at
FROM SILVER_CLEAN.STR_SALES_ORDER_CDC
WHERE is_canonical_otif = 0;
