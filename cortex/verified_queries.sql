-- ====================================================================
-- SNOWFLAKE CORTEX ANALYST CERTIFIED QUERIES & BENCHMARKS
-- ====================================================================

-- Query 1: Cross-Corridor Carrier OTIF vs Cost Benchmark
SELECT 
    carrier_partner,
    SUM(total_orders) AS total_dispatches,
    ROUND(SUM(otif_orders) * 100.0 / SUM(total_orders), 2) AS corridor_otif_pct,
    ROUND(AVG(avg_delivery_cost), 2) AS mean_freight_cost_inr
FROM SUPPLYCHAIN_IQ_DB.GOLD_SEMANTIC.V_CANONICAL_OTIF
GROUP BY carrier_partner
ORDER BY corridor_otif_pct DESC;

-- Query 2: Persona Reconciliation (Proving Identical Canonical Grounding)
SELECT 
    persona_perspective,
    measurement_boundary,
    total_evaluations,
    compliant_evaluations,
    persona_otif_pct,
    governed_canonical_source,
    reconciliation_status
FROM SUPPLYCHAIN_IQ_DB.GOLD_SEMANTIC.V_PERSONA_RECONCILIATION;

-- Query 3: Multi-Regional Stockout Vulnerability (< 14 Days of Supply)
SELECT 
    region,
    warehouse_name,
    COUNT(product_id) AS vulnerable_sku_count,
    ROUND(AVG(days_of_inventory), 1) AS avg_runway_days
FROM SUPPLYCHAIN_IQ_DB.GOLD_SEMANTIC.V_INVENTORY_HEALTH_DOI
WHERE days_of_inventory < 14
GROUP BY region, warehouse_name
ORDER BY vulnerable_sku_count DESC;

-- Query 4: GCC vs South Asia Landed Cost Decomposition
SELECT 
    region,
    destination_country,
    ROUND(AVG(avg_unit_landed_cost), 2) AS avg_unit_landed_cost,
    ROUND(AVG(freight_cost_share_pct), 1) AS freight_share_pct,
    ROUND(AVG(customs_cost_share_pct), 1) AS customs_share_pct
FROM SUPPLYCHAIN_IQ_DB.GOLD_SEMANTIC.V_LANDED_COST_ANALYSIS
GROUP BY region, destination_country
ORDER BY avg_unit_landed_cost DESC;
