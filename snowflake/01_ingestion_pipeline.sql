-- ====================================================================
-- SNOWFLAKE COCO HACKATHON - GCC EDITION
-- SCRIPT 01: BRONZE & SILVER LAKEHOUSE INGESTION PIPELINE
-- ====================================================================

CREATE DATABASE IF NOT EXISTS SUPPLYCHAIN_IQ_DB;
USE DATABASE SUPPLYCHAIN_IQ_DB;

CREATE SCHEMA IF NOT EXISTS BRONZE_RAW;
CREATE SCHEMA IF NOT EXISTS SILVER_CLEAN;
CREATE SCHEMA IF NOT EXISTS GOLD_SEMANTIC;

CREATE OR REPLACE FILE FORMAT BRONZE_RAW.CSV_INGEST_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    NULL_IF = ('', 'NULL', 'NaN', 'nan');

CREATE OR REPLACE TABLE SILVER_CLEAN.DIM_SUPPLIER (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(150),
    supplier_country VARCHAR(100),
    corridor_tier VARCHAR(50),
    avg_reliability FLOAT,
    avg_lead_time FLOAT,
    risk_class VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.DIM_PART (
    product_id VARCHAR(50) PRIMARY KEY,
    sku_code VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    unit_base_cost NUMERIC(12, 2),
    standard_weight_kg FLOAT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.DIM_PLANT_WAREHOUSE (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    warehouse_name VARCHAR(150),
    region VARCHAR(50),
    state VARCHAR(100),
    country VARCHAR(100),
    capacity_units INT,
    leads_infra_score FLOAT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.FACT_SHIPMENT (
    shipment_id VARCHAR(50) PRIMARY KEY,
    delivery_id VARCHAR(50),
    delivery_partner VARCHAR(100),
    package_type VARCHAR(100),
    vehicle_type VARCHAR(50),
    delivery_mode VARCHAR(50),
    region VARCHAR(50),
    origin_warehouse_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PLANT_WAREHOUSE(warehouse_id),
    weather_condition VARCHAR(50),
    delayed VARCHAR(10),
    distance_km FLOAT,
    package_weight_kg FLOAT,
    departure_date TIMESTAMP_NTZ,
    expected_delivery_date TIMESTAMP_NTZ,
    actual_delivery_date TIMESTAMP_NTZ,
    carrier_sla_met INT,
    delivery_status VARCHAR(50),
    delivery_rating INT,
    delivery_cost NUMERIC(10, 2),
    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.FACT_SALES_ORDER (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(100),
    customer_city VARCHAR(100),
    customer_state VARCHAR(100),
    product_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PART(product_id),
    warehouse_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PLANT_WAREHOUSE(warehouse_id),
    shipment_id VARCHAR(50) REFERENCES SILVER_CLEAN.FACT_SHIPMENT(shipment_id),
    ordered_qty INT,
    fulfilled_qty INT,
    order_date TIMESTAMP_NTZ,
    promised_date TIMESTAMP_NTZ,
    actual_pod_date TIMESTAMP_NTZ,
    order_status VARCHAR(50),
    is_on_time INT,
    is_in_full INT,
    is_canonical_otif INT,
    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.FACT_PURCHASE_ORDER (
    po_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_SUPPLIER(supplier_id),
    product_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PART(product_id),
    plant_warehouse_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PLANT_WAREHOUSE(warehouse_id),
    ordered_qty INT,
    received_qty INT,
    unit_purchase_cost NUMERIC(12, 2),
    po_order_date TIMESTAMP_NTZ,
    po_promised_date TIMESTAMP_NTZ,
    po_dock_delivery_date TIMESTAMP_NTZ,
    procurement_on_time INT,
    procurement_in_full INT,
    procurement_otif INT,
    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.FACT_INVENTORY_SNAPSHOT (
    warehouse_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PLANT_WAREHOUSE(warehouse_id),
    product_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PART(product_id),
    inventory_on_hand_qty FLOAT,
    safety_stock_qty FLOAT,
    daily_demand_30d_avg FLOAT,
    days_of_inventory FLOAT,
    stockout_risk_flag INT,
    snapshot_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE SILVER_CLEAN.FACT_LANDED_COST (
    order_id VARCHAR(50) REFERENCES SILVER_CLEAN.FACT_SALES_ORDER(order_id),
    product_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PART(product_id),
    warehouse_id VARCHAR(50) REFERENCES SILVER_CLEAN.DIM_PLANT_WAREHOUSE(warehouse_id),
    ordered_qty INT,
    base_purchase_cost NUMERIC(14, 2),
    freight_cost NUMERIC(14, 2),
    handling_cost NUMERIC(14, 2),
    customs_tariff_cost NUMERIC(14, 2),
    total_landed_cost NUMERIC(14, 2),
    unit_landed_cost NUMERIC(10, 2),
    computed_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
