import os
import sys
import argparse
import pandas as pd

def validate_supplychain_ontology(data_dir="data/bridged"):
    print(f"[*] Inspecting directory: {data_dir}")
    
    required_entities = {
        "DIM_SUPPLIER": ["supplier_id", "supplier_country"],
        "DIM_PART": ["product_id", "sku_code", "unit_base_cost"],
        "DIM_PLANT_WAREHOUSE": ["warehouse_id", "region"],
        "FACT_SHIPMENT": ["shipment_id", "delivery_partner", "carrier_sla_met"],
        "FACT_SALES_ORDER": ["order_id", "customer_id", "is_canonical_otif"],
        "FACT_PURCHASE_ORDER": ["po_id", "supplier_id", "procurement_otif"],
        "FACT_INVENTORY_SNAPSHOT": ["warehouse_id", "product_id", "days_of_inventory"],
        "FACT_LANDED_COST": ["order_id", "total_landed_cost"]
    }

    files = {
        "DIM_SUPPLIER": "dim_supplier.csv",
        "DIM_PART": "dim_part.csv",
        "DIM_PLANT_WAREHOUSE": "dim_plant_warehouse.csv",
        "FACT_SHIPMENT": "fact_shipment.csv",
        "FACT_SALES_ORDER": "fact_sales_order.csv",
        "FACT_PURCHASE_ORDER": "fact_purchase_order.csv",
        "FACT_INVENTORY_SNAPSHOT": "fact_inventory_snapshot.csv",
        "FACT_LANDED_COST": "fact_landed_cost.csv"
    }

    passed_entities = 0
    total_entities = len(required_entities)

    print("\n--- ONTOLOGY SCHEMA AUDIT ---")
    for entity, fname in files.items():
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath):
            print(f"[-] MISSING: {entity} ({fname})")
            continue

        df = pd.read_csv(fpath, nrows=5)
        missing_cols = [col for col in required_entities[entity] if col not in df.columns]
        if missing_cols:
            print(f"[!] INCOMPLETE: {entity} missing required attributes: {missing_cols}")
        else:
            print(f"[+] VALID: {entity} ({len(df.columns)} columns verified)")
            passed_entities += 1

    coverage_pct = round((passed_entities / total_entities) * 100, 1)
    print(f"\n==========================================")
    print(f"ONTOLOGY COMPLIANCE SCORE: {coverage_pct}%")
    print(f"STATUS: {'CERTIFIED' if coverage_pct >= 90 else 'ACTION_REQUIRED'}")
    print(f"==========================================\n")
    return coverage_pct >= 90

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="data/bridged", help="Path to bridged datasets")
    args = parser.parse_args()
    success = validate_supplychain_ontology(args.dir)
    sys.exit(0 if success else 1)
