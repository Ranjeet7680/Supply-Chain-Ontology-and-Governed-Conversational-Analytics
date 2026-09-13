import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

print('1. Loading raw source datasets...')
delivery_path = 'Dataset/Delivery_Logistics.csv'
dyn_path = 'Dataset/dynamic_supply_chain_logistics_dataset_with_country.csv'
olist_path = 'Dataset/olist_customers_dataset.csv'
leads_path = 'Dataset/Leads Report 2021 Numeric Data - Leads Report 2021 Numeric Data.csv'

df_deliv = pd.read_csv(delivery_path)
df_dyn = pd.read_csv(dyn_path)
df_olist = pd.read_csv(olist_path)
df_leads = pd.read_csv(leads_path)

os.makedirs('data/bridged', exist_ok=True)

print('2. Creating DIM_PLANT_WAREHOUSE...')
warehouses = [
    {'warehouse_id': 'WH_MUMBAI_W', 'warehouse_name': 'Mumbai West Apex Hub', 'region': 'west', 'state': 'Maharashtra', 'country': 'India', 'capacity_units': 500000, 'leads_infra_score': 3.61},
    {'warehouse_id': 'WH_NAGPUR_C', 'warehouse_name': 'Nagpur Central Multi-Modal Hub', 'region': 'central', 'state': 'Madhya Pradesh', 'country': 'India', 'capacity_units': 450000, 'leads_infra_score': 3.11},
    {'warehouse_id': 'WH_BLR_S', 'warehouse_name': 'Bengaluru South Tech Hub', 'region': 'south', 'state': 'Karnataka', 'country': 'India', 'capacity_units': 600000, 'leads_infra_score': 3.65},
    {'warehouse_id': 'WH_DELHI_N', 'warehouse_name': 'Delhi NCR North Mega Hub', 'region': 'north', 'state': 'Haryana', 'country': 'India', 'capacity_units': 750000, 'leads_infra_score': 3.52},
    {'warehouse_id': 'WH_KOLKATA_E', 'warehouse_name': 'Kolkata East Gateway Hub', 'region': 'east', 'state': 'West Bengal', 'country': 'India', 'capacity_units': 400000, 'leads_infra_score': 3.20},
    {'warehouse_id': 'WH_RIYADH_GCC', 'warehouse_name': 'Riyadh GCC Logistics Park', 'region': 'gcc', 'state': 'Riyadh', 'country': 'Saudi Arabia', 'capacity_units': 800000, 'leads_infra_score': 3.90},
    {'warehouse_id': 'WH_DUBAI_GCC', 'warehouse_name': 'Jebel Ali GCC Freezone Hub', 'region': 'gcc', 'state': 'Dubai', 'country': 'UAE', 'capacity_units': 950000, 'leads_infra_score': 4.10},
    {'warehouse_id': 'WH_DOHA_GCC', 'warehouse_name': 'Hamad Port Logistics Zone', 'region': 'gcc', 'state': 'Doha', 'country': 'Qatar', 'capacity_units': 350000, 'leads_infra_score': 3.85}
]
df_wh = pd.DataFrame(warehouses)
df_wh.to_csv('data/bridged/dim_plant_warehouse.csv', index=False)

print('3. Creating DIM_SUPPLIER & DIM_PART...')
supplier_agg = df_dyn.groupby(['supplier_id', 'supplier_country']).agg(
    avg_reliability=('supplier_reliability_score', 'mean'),
    avg_lead_time=('lead_time_days', 'mean'),
    risk_class=('risk_classification', lambda x: x.mode()[0] if len(x) > 0 else 'Moderate Risk')
).reset_index().head(500)

supplier_agg['supplier_name'] = supplier_agg['supplier_id'].apply(lambda s: f'Global Vendor {s}')
supplier_agg['corridor_tier'] = supplier_agg['supplier_country'].apply(
    lambda c: 'GCC' if c in ['Saudi Arabia', 'Qatar', 'Oman', 'UAE'] else ('South Asia' if c in ['India', 'Pakistan', 'Nepal', 'Bangladesh', 'Sri Lanka'] else 'Global')
)
df_supplier = supplier_agg
df_supplier.to_csv('data/bridged/dim_supplier.csv', index=False)

product_ids = df_dyn['product_id'].unique()[:200]
categories = ['Automotive Components', 'Industrial Electronics', 'Precision Machinery', 'Consumer Durables', 'Chemical & Raw Material']
products = []
for p_id in product_ids:
    cat = np.random.choice(categories)
    unit_cost = round(float(np.random.uniform(25.0, 850.0)), 2)
    products.append({
        'product_id': p_id,
        'sku_code': f'SKU-{p_id}',
        'category': cat,
        'unit_base_cost': unit_cost,
        'standard_weight_kg': round(float(np.random.uniform(0.5, 45.0)), 2)
    })
df_parts = pd.DataFrame(products)
df_parts.to_csv('data/bridged/dim_part.csv', index=False)

print('4. Aligning FACT_SHIPMENT with 25,000 Delivery_Logistics rows...')
df_deliv['shipment_id'] = [f'SHP-{i+10001}' for i in range(len(df_deliv))]
region_wh_map = {
    'west': 'WH_MUMBAI_W',
    'central': 'WH_NAGPUR_C',
    'south': 'WH_BLR_S',
    'north': 'WH_DELHI_N',
    'east': 'WH_KOLKATA_E'
}
df_deliv['origin_warehouse_id'] = df_deliv['region'].map(region_wh_map).fillna('WH_MUMBAI_W')

base_date = datetime(2024, 7, 1)
df_deliv['departure_date'] = [base_date + timedelta(days=int(i % 90), hours=int((i*3) % 24)) for i in range(len(df_deliv))]

transit_hours = []
for idx, row in df_deliv.iterrows():
    base_h = float(row['distance_km']) / 45.0 + float(np.random.uniform(1.0, 4.0))
    if str(row['delayed']).lower() == 'yes':
        base_h += float(np.random.uniform(6.0, 24.0))
    transit_hours.append(round(base_h, 2))

df_deliv['actual_transit_hours'] = transit_hours
df_deliv['expected_transit_hours'] = [round(float(d)/45.0 + 2.0, 2) for d in df_deliv['distance_km']]
df_deliv['actual_delivery_date'] = [d + timedelta(hours=h) for d, h in zip(df_deliv['departure_date'], df_deliv['actual_transit_hours'])]
df_deliv['expected_delivery_date'] = [d + timedelta(hours=h) for d, h in zip(df_deliv['departure_date'], df_deliv['expected_transit_hours'])]
df_deliv['carrier_sla_met'] = (df_deliv['delayed'].str.lower() == 'no').astype(int)

df_shipment = df_deliv[[
    'shipment_id', 'delivery_id', 'delivery_partner', 'package_type', 'vehicle_type',
    'delivery_mode', 'region', 'origin_warehouse_id', 'weather_condition', 'delayed',
    'distance_km', 'package_weight_kg', 'departure_date', 'expected_delivery_date',
    'actual_delivery_date', 'carrier_sla_met', 'delivery_status', 'delivery_rating', 'delivery_cost'
]].copy()
df_shipment.to_csv('data/bridged/fact_shipment.csv', index=False)

print('5. Creating FACT_SALES_ORDER (25,000 linked customer orders)...')
olist_sample = df_olist.sample(n=len(df_deliv), replace=True, random_state=42).reset_index(drop=True)
sample_products = df_parts.sample(n=len(df_deliv), replace=True, random_state=42).reset_index(drop=True)

ordered_qtys = np.random.randint(1, 50, size=len(df_deliv))
fill_ratios = np.where(np.random.rand(len(df_deliv)) > 0.05, 1.0, np.random.uniform(0.6, 0.95, size=len(df_deliv)))
fulfilled_qtys = np.floor(ordered_qtys * fill_ratios).astype(int)

promised_dates = df_shipment['expected_delivery_date'].copy()
actual_pod_dates = df_shipment['actual_delivery_date'].copy()

order_statuses = np.where(df_shipment['delivery_status'] == 'failed', 'FAILED',
                 np.where(df_shipment['delayed'].str.lower() == 'yes', 'DELIVERED_LATE', 'DELIVERED_ON_TIME'))

df_sales = pd.DataFrame({
    'order_id': [f'ORD-2024-{i+10001}' for i in range(len(df_deliv))],
    'customer_id': olist_sample['customer_id'],
    'customer_city': olist_sample['customer_city'],
    'customer_state': olist_sample['customer_state'],
    'product_id': sample_products['product_id'],
    'warehouse_id': df_shipment['origin_warehouse_id'],
    'shipment_id': df_shipment['shipment_id'],
    'ordered_qty': ordered_qtys,
    'fulfilled_qty': fulfilled_qtys,
    'order_date': df_shipment['departure_date'] - pd.to_timedelta(np.random.randint(4, 24, size=len(df_deliv)), unit='h'),
    'promised_date': promised_dates,
    'actual_pod_date': actual_pod_dates,
    'order_status': order_statuses
})

df_sales['is_on_time'] = (df_sales['actual_pod_date'] <= df_sales['promised_date']).astype(int)
df_sales['is_in_full'] = (df_sales['fulfilled_qty'] >= df_sales['ordered_qty']).astype(int)
df_sales['is_canonical_otif'] = (df_sales['is_on_time'] & df_sales['is_in_full']).astype(int)
df_sales.to_csv('data/bridged/fact_sales_order.csv', index=False)

print('6. Creating FACT_PURCHASE_ORDER (Procurement persona)...')
n_po = 15000
supplier_samples = df_supplier.sample(n=n_po, replace=True, random_state=42).reset_index(drop=True)
part_samples = df_parts.sample(n=n_po, replace=True, random_state=42).reset_index(drop=True)
wh_samples = df_wh.sample(n=n_po, replace=True, random_state=42).reset_index(drop=True)

po_ordered_qtys = np.random.randint(50, 2000, size=n_po)
po_dates = [datetime(2024, 6, 1) + timedelta(days=int(i % 100)) for i in range(n_po)]
lead_times = supplier_samples['avg_lead_time'].values
po_promised_dates = [d + timedelta(days=max(1, int(lt))) for d, lt in zip(po_dates, lead_times)]

actual_dock_dates = []
received_qtys = []
for i in range(n_po):
    rel = float(supplier_samples.loc[i, 'avg_reliability'])
    if np.random.rand() < rel:
        actual_dock_dates.append(po_promised_dates[i] - timedelta(hours=int(np.random.randint(0, 24))))
        received_qtys.append(po_ordered_qtys[i])
    else:
        delay_days = int(np.random.exponential(scale=3.5)) + 1
        actual_dock_dates.append(po_promised_dates[i] + timedelta(days=delay_days))
        received_qtys.append(po_ordered_qtys[i] if np.random.rand() > 0.1 else int(po_ordered_qtys[i] * np.random.uniform(0.8, 0.98)))

df_po = pd.DataFrame({
    'po_id': [f'PO-2024-{i+50001}' for i in range(n_po)],
    'supplier_id': supplier_samples['supplier_id'],
    'product_id': part_samples['product_id'],
    'plant_warehouse_id': wh_samples['warehouse_id'],
    'ordered_qty': po_ordered_qtys,
    'received_qty': received_qtys,
    'unit_purchase_cost': part_samples['unit_base_cost'],
    'po_order_date': po_dates,
    'po_promised_date': po_promised_dates,
    'po_dock_delivery_date': actual_dock_dates
})
df_po['procurement_on_time'] = (df_po['po_dock_delivery_date'] <= df_po['po_promised_date']).astype(int)
df_po['procurement_in_full'] = (df_po['received_qty'] >= df_po['ordered_qty']).astype(int)
df_po['procurement_otif'] = (df_po['procurement_on_time'] & df_po['procurement_in_full']).astype(int)
df_po.to_csv('data/bridged/fact_purchase_order.csv', index=False)

print('7. Creating FACT_INVENTORY_SNAPSHOT (Days of Inventory / DOI)...')
inv_records = []
for _, wh in df_wh.iterrows():
    for _, prod in df_parts.iterrows():
        daily_demand = round(float(np.random.uniform(15.0, 180.0)), 1)
        doi_target = float(np.random.uniform(10.0, 48.0))
        on_hand = round(daily_demand * doi_target, 0)
        safety_stock = round(daily_demand * 14.0, 0)
        inv_records.append({
            'warehouse_id': wh['warehouse_id'],
            'product_id': prod['product_id'],
            'inventory_on_hand_qty': on_hand,
            'safety_stock_qty': safety_stock,
            'daily_demand_30d_avg': daily_demand,
            'days_of_inventory': round(on_hand / daily_demand, 1),
            'stockout_risk_flag': int(on_hand < safety_stock)
        })
df_inv = pd.DataFrame(inv_records)
df_inv.to_csv('data/bridged/fact_inventory_snapshot.csv', index=False)

print('8. Creating FACT_LANDED_COST...')
sample_landed = df_sales.head(10000).copy()
prod_cost_map = df_parts.set_index('product_id')['unit_base_cost'].to_dict()
shp_cost_map = df_shipment.set_index('shipment_id')['delivery_cost'].to_dict()

sample_landed['base_purchase_cost'] = sample_landed['product_id'].map(prod_cost_map).fillna(120.0) * sample_landed['ordered_qty']
sample_landed['freight_cost'] = sample_landed['shipment_id'].map(shp_cost_map).fillna(850.0)
sample_landed['handling_cost'] = (sample_landed['ordered_qty'] * np.random.uniform(2.5, 6.0)).round(2)
sample_landed['customs_tariff_cost'] = np.where(sample_landed['warehouse_id'].str.contains('GCC'), sample_landed['base_purchase_cost'] * 0.05, 0.0).round(2)
sample_landed['total_landed_cost'] = (
    sample_landed['base_purchase_cost'] + sample_landed['freight_cost'] + 
    sample_landed['handling_cost'] + sample_landed['customs_tariff_cost']
).round(2)
sample_landed['unit_landed_cost'] = (sample_landed['total_landed_cost'] / sample_landed['ordered_qty']).round(2)

df_landed = sample_landed[[
    'order_id', 'product_id', 'warehouse_id', 'ordered_qty',
    'base_purchase_cost', 'freight_cost', 'handling_cost', 'customs_tariff_cost',
    'total_landed_cost', 'unit_landed_cost'
]]
df_landed.to_csv('data/bridged/fact_landed_cost.csv', index=False)

print('SUCCESS: All 7 canonical tables generated referentially in data/bridged/!')
