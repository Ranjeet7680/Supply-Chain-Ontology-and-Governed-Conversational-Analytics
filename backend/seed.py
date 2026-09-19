import os
import sys
import uuid
import pandas as pd
import numpy as np
import datetime
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath('.'))
from backend.database import engine, Base, SessionLocal
from backend.models import (
    User, Supplier, Warehouse, Product, SKUInventory,
    PurchaseOrder, POLineItem, Shipment, ShipmentEvent,
    RiskAlert, OntologyEntity, OntologyRelationship, Playbook, PlaybookRun, Scenario, AuditEvent
)

def seed_database():
    print('Creating database tables if not exist...')
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            print('Seeding enterprise users & personas...')
            users = [
                User(email='director@nexora.com', name='Ranjeet Kumar', role='Supply Chain Director', department='Global Operations', password_hash='hash_director'),
                User(email='procurement@nexora.com', name='Hitali Khachane', role='Procurement Manager', department='Procurement & Sourcing', password_hash='hash_proc'),
                User(email='warehouse@nexora.com', name='Rahul Sangral', role='Warehouse Manager', department='Fulfillment Hubs', password_hash='hash_wh'),
                User(email='analyst@nexora.com', name='Syed Saaduddin', role='Supply Chain Analyst', department='AI & Insights', password_hash='hash_analyst'),
                User(email='admin@nexora.com', name='System Admin', role='Admin', department='IT & Security', password_hash='hash_admin')
            ]
            db.add_all(users)
            db.commit()

        # 2. Seed Warehouses
        if db.query(Warehouse).count() == 0:
            print('Seeding warehouses from bridged data...')
            wh_df = pd.read_csv('data/bridged/dim_plant_warehouse.csv')
            warehouses = []
            for _, r in wh_df.iterrows():
                wh = Warehouse(
                    warehouse_code=str(r['warehouse_id']),
                    warehouse_name=str(r['warehouse_name']),
                    location=f"{r['state']}, {r['country']}",
                    region=str(r['region']),
                    capacity_sqft=float(r.get('capacity_units', 50000.0)),
                    utilization_pct=float(np.random.uniform(65.0, 92.0)),
                    operational_status='Operational'
                )
                warehouses.append(wh)
            db.add_all(warehouses)
            db.commit()

        # 3. Seed Suppliers
        if db.query(Supplier).count() == 0:
            print('Seeding suppliers from bridged data...')
            sup_df = pd.read_csv('data/bridged/dim_supplier.csv')
            suppliers = []
            for _, r in sup_df.iterrows():
                rel = float(r.get('avg_reliability', 0.9))
                risk = 85.0 if str(r.get('risk_class', '')).lower() == 'high' else (45.0 if str(r.get('risk_class', '')).lower() == 'medium' else 15.0)
                sup = Supplier(
                    supplier_code=str(r['supplier_id']),
                    supplier_name=str(r['supplier_name']),
                    category='Components & Raw Materials',
                    country=str(r['supplier_country']),
                    city='Industrial Hub',
                    tier=str(r.get('corridor_tier', 'Tier 1')),
                    otif_score=round(rel * 100, 1),
                    lead_time_days=round(float(r.get('avg_lead_time', 12.0)), 1),
                    quality_score=round(float(np.random.uniform(92.0, 99.5)), 1),
                    risk_score=risk,
                    spend=float(np.random.uniform(120000.0, 1850000.0)),
                    status='Active' if risk < 75 else 'Under Review',
                    last_delivery='2026-03-12',
                    contact_email=f"support@{str(r['supplier_id']).lower()}.supplier.com"
                )
                suppliers.append(sup)
            db.add_all(suppliers)
            db.commit()

        # 4. Seed Products & SKU Inventory
        if db.query(Product).count() == 0:
            print('Seeding products & SKU inventory...')
            part_df = pd.read_csv('data/bridged/dim_part.csv')
            products = []
            skus = []
            for _, r in part_df.iterrows():
                p = Product(
                    part_code=str(r['product_id']),
                    part_name=str(r['sku_code']),
                    category=str(r['category']),
                    unit_cost=float(r['unit_base_cost']),
                    selling_price=round(float(r['unit_base_cost']) * 1.45, 2),
                    safety_stock=int(np.random.randint(200, 800)),
                    reorder_point=int(np.random.randint(150, 400)),
                    lead_time_days=int(np.random.randint(5, 21))
                )
                products.append(p)
                
                # SKU Inventory at WH_MUMBAI and WH_DUBAI
                qty = int(np.random.randint(50, 2000))
                skus.append(SKUInventory(
                    part_code=str(r['product_id']),
                    warehouse_code='WH_MUMBAI',
                    quantity_on_hand=qty,
                    reserved_quantity=int(qty * 0.15),
                    safety_stock=300,
                    stockout_probability=0.28 if qty < 300 else 0.04,
                    demand_forecast_30d=int(np.random.randint(400, 1500)),
                    inventory_value=round(qty * float(r['unit_base_cost']), 2),
                    status='At Risk' if qty < 300 else 'Healthy'
                ))
            db.add_all(products)
            db.add_all(skus)
            db.commit()

        # 5. Seed Purchase Orders
        if db.query(PurchaseOrder).count() == 0:
            print('Seeding purchase orders from bridged data (first 1500)...')
            po_df = pd.read_csv('data/bridged/fact_purchase_order.csv').head(1500)
            pos = []
            lines = []
            for _, r in po_df.iterrows():
                po_num = str(r['po_id'])
                cost = float(r.get('unit_purchase_cost', 50.0))
                ordered = int(r.get('ordered_qty', 100))
                recv = int(r.get('received_qty', ordered))
                otif = int(r.get('procurement_otif', 1))
                status = 'Received' if otif == 1 else ('Delayed' if recv > 0 else 'Pending Approval')
                
                po_uid = str(uuid.uuid4())
                po = PurchaseOrder(
                    id=po_uid,
                    po_number=po_num,
                    supplier_code=str(r['supplier_id']),
                    supplier_name=f"Supplier {r['supplier_id']}",
                    destination_warehouse=str(r.get('plant_warehouse_id', 'WH_MUMBAI')),
                    order_date=str(r.get('po_order_date', '2026-02-01')),
                    expected_delivery_date=str(r.get('po_promised_date', '2026-02-15')),
                    actual_delivery_date=str(r.get('po_dock_delivery_date', '2026-02-15')),
                    total_amount=round(cost * ordered, 2),
                    status=status,
                    variance_days=0 if otif == 1 else 4
                )
                pos.append(po)
                lines.append(POLineItem(
                    id=str(uuid.uuid4()),
                    po_id=po_uid,
                    part_code=str(r.get('product_id', 'PRD_001')),
                    quantity_ordered=ordered,
                    quantity_received=recv,
                    unit_price=cost,
                    line_total=round(cost * ordered, 2)
                ))
            db.add_all(pos)
            db.commit()
            db.add_all(lines)
            db.commit()

        # 6. Seed Shipments
        if db.query(Shipment).count() == 0:
            print('Seeding shipments from bridged data (first 800)...')
            shp_df = pd.read_csv('data/bridged/fact_shipment.csv').head(800)
            shipments = []
            events = []
            for _, r in shp_df.iterrows():
                shp_id = str(r['shipment_id'])
                raw_delayed = str(r.get('delayed', '0')).strip().lower()
                delayed = 1 if raw_delayed in ['1', 'yes', 'true', 'delayed'] else 0
                status = 'Delayed' if delayed == 1 else ('Delivered' if r.get('delivery_status') == 'delivered' else 'In Transit')
                risk = 78.0 if delayed == 1 else 12.0
                
                shp_uid = str(uuid.uuid4())
                shp = Shipment(
                    id=shp_uid,
                    shipment_id=shp_id,
                    carrier=str(r.get('delivery_partner', 'DHL Express')),
                    origin=str(r.get('origin_warehouse_id', 'IN_MAH_WH_01')),
                    destination=f"{r.get('region', 'Central')} Terminal",
                    corridor='India-GCC_Maritime' if 'mumbai' in str(r.get('origin_warehouse_id', '')).lower() else 'Domestic Highway',
                    mode=str(r.get('delivery_mode', 'Express')),
                    status=status,
                    eta=str(r.get('expected_delivery_date', '2026-03-20')),
                    actual_arrival=str(r.get('actual_delivery_date', '')) if delayed == 0 else None,
                    delay_hours=float(np.random.randint(12, 48)) if delayed == 1 else 0.0,
                    risk_score=risk,
                    package_weight_kg=float(r.get('package_weight_kg', 25.0)),
                    delivery_cost=float(r.get('delivery_cost', 450.0)),
                    weather_condition=str(r.get('weather_condition', 'Clear'))
                )
                shipments.append(shp)
                
                events.append(ShipmentEvent(
                    id=str(uuid.uuid4()),
                    shipment_id=shp_uid,
                    event_timestamp=str(r.get('departure_date', '2026-03-10')),
                    checkpoint=shp.origin,
                    event_type='Departure',
                    notes='Consignment cleared dispatch hub'
                ))
            db.add_all(shipments)
            db.commit()
            db.add_all(events)
            db.commit()

        # 7. Seed Risk Alerts
        if db.query(RiskAlert).count() == 0:
            print('Seeding enterprise risk alerts...')
            alerts = [
                RiskAlert(
                    alert_code='ALT-2026-8801',
                    category='Transportation Risk',
                    severity='Critical',
                    entity_type='Shipment',
                    entity_id='SHP_000142',
                    entity_name='Corridor Gateway JNPT Mumbai -> Jebel Ali Dubai',
                    risk_score=88.5,
                    reason='Severe weather disruption and high sea swell near Gulf of Oman corridor causing 36h transit delay.',
                    evidence='IoT buoy sensor data indicates wave height 4.2m exceeding container barge safety protocol.',
                    recommended_action='Reroute vessel to auxiliary berth at Port Sultan Qaboos or switch critical SKU PRD_004 to air cargo charter.',
                    status='Open',
                    owner='Supply Chain Director'
                ),
                RiskAlert(
                    alert_code='ALT-2026-8802',
                    category='Supplier Risk',
                    severity='High',
                    entity_type='Supplier',
                    entity_id='SUP_0028',
                    entity_name='Tata Autocomp Systems',
                    risk_score=76.0,
                    reason='OTIF rate dropped to 72% over last 3 shipments due to raw material component shortages.',
                    evidence='Factory audit report notes furnace maintenance delay at Pune plant.',
                    recommended_action='Split purchase order PO-88219 allocation 50/50 with alternate supplier SUP_0012.',
                    status='Open',
                    owner='Procurement Manager'
                ),
                RiskAlert(
                    alert_code='ALT-2026-8803',
                    category='Inventory Risk',
                    severity='High',
                    entity_type='SKU',
                    entity_id='PRD_0018',
                    entity_name='High-Torque Actuator Assembly',
                    risk_score=82.0,
                    reason='Days of Inventory dropped below 4.5 days against safety threshold of 12 days at WH_DUBAI.',
                    evidence='Sudden surge in regional GCC sales order demand (+34% WoW).',
                    recommended_action='Trigger expedited cross-dock transfer from WH_MUMBAI buffer inventory.',
                    status='Acknowledged',
                    owner='Warehouse Manager'
                ),
                RiskAlert(
                    alert_code='ALT-2026-8804',
                    category='Warehouse Risk',
                    severity='Medium',
                    entity_type='Warehouse',
                    entity_id='WH_DELHI',
                    entity_name='Northern Regional Distribution Center',
                    risk_score=58.0,
                    reason='Inbound dock utilization reached 94.2% causing average truck dwell times of 4.8 hours.',
                    evidence='WMS gate telemetry reports 14 heavy trailers queued at outer yard.',
                    recommended_action='Activate overflow staging bay C and assign 4 additional warehouse associates for offload.',
                    status='Investigating',
                    owner='Warehouse Manager'
                )
            ]
            db.add_all(alerts)
            db.commit()

        # 8. Seed Playbooks
        if db.query(Playbook).count() == 0:
            print('Seeding autonomous AI Playbooks...')
            playbooks = [
                Playbook(
                    playbook_id='PB-OTIF-MITIGATE',
                    title='Autonomous Low-OTIF Supplier Mitigation',
                    description='Detects suppliers whose 30-day OTIF drops below 80% and automatically identifies pre-qualified alternate suppliers, checks buffer inventory, and prepares approval briefs.',
                    trigger_condition='Supplier.otif_score < 80.0 AND Supplier.open_pos > 0',
                    actions=['Query alternate qualified vendors in corridor', 'Simulate reallocation cost delta', 'Draft split PO recommendation', 'Notify Procurement Lead in Slack/Teams'],
                    requires_approval=True,
                    status='Active',
                    owner='Procurement Operations'
                ),
                Playbook(
                    playbook_id='PB-PORT-SHUTDOWN',
                    title='GCC Maritime Corridor Reroute Protocol',
                    description='Activated during severe weather, port congestion, or canal blockages to automatically divert in-transit freight to alternate hubs and adjust downstream customer SLAs.',
                    trigger_condition='Shipment.corridor == India-GCC_Maritime AND Weather.severity > 0.8',
                    actions=['Identify at-risk containers', 'Reroute to Port of Fujairah / Dammam', 'Dispatch MCP API call to carrier TMS', 'Update downstream delivery promises'],
                    requires_approval=False,
                    status='Active',
                    owner='Logistics Operations'
                )
            ]
            db.add_all(playbooks)
            db.commit()

        # 9. Seed Ontology Entities & Relationships
        if db.query(OntologyEntity).count() == 0:
            print('Seeding supply chain ontology knowledge graph...')
            nodes = [
                ('ENT_SUP_01', 'Supplier', 'Global Semi & Micro Electronics', {'country': 'India', 'tier': 'Tier 1', 'rating': 'A+'}),
                ('ENT_PRD_01', 'Product', 'Microcontroller MCU-32X', {'category': 'Semiconductors', 'cost': 18.5}),
                ('ENT_WH_01', 'Warehouse', 'JNPT Logistics Terminal Mumbai', {'region': 'India West', 'capacity': 120000}),
                ('ENT_SHP_01', 'Shipment', 'SHP-GCC-9902 Maritime Express', {'carrier': 'Maersk Line', 'eta': '2026-03-24'}),
                ('ENT_CAR_01', 'Carrier', 'Maersk Ocean Logistics', {'mode': 'Maritime', 'sla_pct': 94.2}),
                ('ENT_CUS_01', 'Customer', 'Emirates Industrial Solutions Dubai', {'market': 'UAE', 'tier': 'Enterprise Strategic'})
            ]
            for nid, ntype, name, attrs in nodes:
                db.add(OntologyEntity(entity_id=nid, entity_type=ntype, name=name, attributes=attrs))
            db.commit()

            edges = [
                ('ENT_SUP_01', 'ENT_PRD_01', 'SUPPLIES', {'lead_days': 12}),
                ('ENT_PRD_01', 'ENT_WH_01', 'STORED_IN', {'min_buffer': 500}),
                ('ENT_WH_01', 'ENT_SHP_01', 'DISPATCHED_VIA', {'dock': 'Bay-04'}),
                ('ENT_SHP_01', 'ENT_CAR_01', 'HANDLED_BY', {'contract_id': 'CTR-MAE-2026'}),
                ('ENT_CAR_01', 'ENT_CUS_01', 'DELIVERS_TO', {'terminal': 'Jebel Ali'})
            ]
            for src, tgt, rel, props in edges:
                db.add(OntologyRelationship(source_entity_id=src, target_entity_id=tgt, relation_type=rel, properties=props))
            db.commit()

        # 10. Seed Initial Audit Event
        if db.query(AuditEvent).count() == 0:
            db.add(AuditEvent(
                event_type='SYSTEM_INITIALIZED',
                actor='System Bootstrapper',
                actor_role='System',
                details={'event': 'SupplyChain IQ v2.4 Enterprise Database Seeded with 15,000+ Canonical Records'}
            ))
            db.commit()

        print('=== SupplyChain IQ Enterprise Database Seed Complete ===')
        print(f'Suppliers: {db.query(Supplier).count()}')
        print(f'Warehouses: {db.query(Warehouse).count()}')
        print(f'Products: {db.query(Product).count()}')
        print(f'Purchase Orders: {db.query(PurchaseOrder).count()}')
        print(f'Shipments: {db.query(Shipment).count()}')
        print(f'Risk Alerts: {db.query(RiskAlert).count()}')
        print(f'Playbooks: {db.query(Playbook).count()}')
        print(f'Ontology Nodes: {db.query(OntologyEntity).count()}')

    except Exception as e:
        db.rollback()
        print('Error during database seed:', e)
        raise e
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()

