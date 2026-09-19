import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default='Supply Chain Director')
    department = Column(String, default='Global Operations')
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(String, primary_key=True, default=gen_uuid)
    supplier_code = Column(String, unique=True, index=True, nullable=False)
    supplier_name = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    country = Column(String, index=True)
    city = Column(String)
    tier = Column(String, default='Tier 1')
    otif_score = Column(Float, default=95.0)
    lead_time_days = Column(Float, default=14.0)
    quality_score = Column(Float, default=98.0)
    risk_score = Column(Float, default=15.0) # 0 to 100
    spend = Column(Float, default=0.0)
    status = Column(String, default='Active')
    last_delivery = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    purchase_orders = relationship('PurchaseOrder', back_populates='supplier')

class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(String, primary_key=True, default=gen_uuid)
    warehouse_code = Column(String, unique=True, index=True, nullable=False)
    warehouse_name = Column(String, nullable=False)
    location = Column(String, index=True)
    region = Column(String, index=True)
    capacity_sqft = Column(Float, default=100000.0)
    utilization_pct = Column(Float, default=78.5)
    operational_status = Column(String, default='Operational')
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    id = Column(String, primary_key=True, default=gen_uuid)
    part_code = Column(String, unique=True, index=True, nullable=False)
    part_name = Column(String, nullable=False)
    category = Column(String, index=True)
    unit_cost = Column(Float, default=10.0)
    selling_price = Column(Float, default=25.0)
    safety_stock = Column(Integer, default=500)
    reorder_point = Column(Integer, default=300)
    lead_time_days = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SKUInventory(Base):
    __tablename__ = 'sku_inventory'
    id = Column(String, primary_key=True, default=gen_uuid)
    part_code = Column(String, index=True, nullable=False)
    warehouse_code = Column(String, index=True, nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    safety_stock = Column(Integer, default=100)
    stockout_probability = Column(Float, default=0.05)
    demand_forecast_30d = Column(Integer, default=500)
    inventory_value = Column(Float, default=0.0)
    status = Column(String, default='Healthy') # Healthy, At Risk, Excess, Stockout
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    id = Column(String, primary_key=True, default=gen_uuid)
    po_number = Column(String, unique=True, index=True, nullable=False)
    supplier_id = Column(String, ForeignKey('suppliers.id'), nullable=True)
    supplier_code = Column(String, index=True, nullable=False)
    supplier_name = Column(String, nullable=True)
    destination_warehouse = Column(String, index=True)
    order_date = Column(String, index=True)
    expected_delivery_date = Column(String, index=True)
    actual_delivery_date = Column(String, nullable=True)
    total_amount = Column(Float, default=0.0)
    currency = Column(String, default='USD')
    status = Column(String, index=True, default='Approved') # Draft, Pending Approval, Approved, Received, Delayed, Cancelled
    variance_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    supplier = relationship('Supplier', back_populates='purchase_orders')
    lines = relationship('POLineItem', back_populates='purchase_order', cascade='all, delete-orphan')

class POLineItem(Base):
    __tablename__ = 'po_line_items'
    id = Column(String, primary_key=True, default=gen_uuid)
    po_id = Column(String, ForeignKey('purchase_orders.id'), nullable=False)
    line_number = Column(Integer, default=1)
    part_code = Column(String, index=True, nullable=False)
    quantity_ordered = Column(Integer, default=1)
    quantity_received = Column(Integer, default=0)
    unit_price = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)

    purchase_order = relationship('PurchaseOrder', back_populates='lines')

class Shipment(Base):
    __tablename__ = 'shipments'
    id = Column(String, primary_key=True, default=gen_uuid)
    shipment_id = Column(String, unique=True, index=True, nullable=False)
    carrier = Column(String, index=True, nullable=False)
    origin = Column(String, index=True, nullable=False)
    destination = Column(String, index=True, nullable=False)
    corridor = Column(String, index=True, default='India-GCC_Maritime')
    mode = Column(String, default='Maritime')
    status = Column(String, index=True, default='In Transit') # Planned, Booked, In Transit, Delayed, At Risk, Delivered, Exception
    eta = Column(String, nullable=False)
    actual_arrival = Column(String, nullable=True)
    delay_hours = Column(Float, default=0.0)
    risk_score = Column(Float, default=10.0)
    package_weight_kg = Column(Float, default=100.0)
    delivery_cost = Column(Float, default=500.0)
    weather_condition = Column(String, default='Clear')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    events = relationship('ShipmentEvent', back_populates='shipment', cascade='all, delete-orphan')

class ShipmentEvent(Base):
    __tablename__ = 'shipment_events'
    id = Column(String, primary_key=True, default=gen_uuid)
    shipment_id = Column(String, ForeignKey('shipments.id'), nullable=False)
    event_timestamp = Column(String, nullable=False)
    checkpoint = Column(String, nullable=False)
    event_type = Column(String, nullable=False) # Departure, Customs Clear, Port Arrival, Handover, Exception
    notes = Column(String, nullable=True)

    shipment = relationship('Shipment', back_populates='events')

class RiskAlert(Base):
    __tablename__ = 'risk_alerts'
    id = Column(String, primary_key=True, default=gen_uuid)
    alert_code = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True, nullable=False) # Supplier Risk, Inventory Risk, Transportation Risk, Geopolitical Risk, etc.
    severity = Column(String, index=True, default='Medium') # Low, Medium, High, Critical
    entity_type = Column(String, nullable=False) # Supplier, SKU, Shipment, Port, Warehouse
    entity_id = Column(String, index=True, nullable=False)
    entity_name = Column(String, nullable=False)
    risk_score = Column(Float, default=50.0)
    reason = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    status = Column(String, index=True, default='Open') # Open, Acknowledged, Investigating, Mitigated, Resolved
    owner = Column(String, default='Supply Chain Director')
    detection_time = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class OntologyEntity(Base):
    __tablename__ = 'ontology_entities'
    id = Column(String, primary_key=True, default=gen_uuid)
    entity_id = Column(String, unique=True, index=True, nullable=False)
    entity_type = Column(String, index=True, nullable=False) # Supplier, Product, Warehouse, Shipment, Carrier, etc.
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class OntologyRelationship(Base):
    __tablename__ = 'ontology_relationships'
    id = Column(String, primary_key=True, default=gen_uuid)
    source_entity_id = Column(String, index=True, nullable=False)
    target_entity_id = Column(String, index=True, nullable=False)
    relation_type = Column(String, index=True, nullable=False) # SUPPLIES, STORED_IN, SHIPPED_TO, ROUTED_BY, etc.
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Playbook(Base):
    __tablename__ = 'playbooks'
    id = Column(String, primary_key=True, default=gen_uuid)
    playbook_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    trigger_condition = Column(Text, nullable=False)
    actions = Column(JSON, default=list)
    requires_approval = Column(Boolean, default=True)
    status = Column(String, default='Active')
    owner = Column(String, default='Supply Chain Ops')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PlaybookRun(Base):
    __tablename__ = 'playbook_runs'
    id = Column(String, primary_key=True, default=gen_uuid)
    run_code = Column(String, unique=True, index=True, nullable=False)
    playbook_id = Column(String, ForeignKey('playbooks.id'), nullable=False)
    status = Column(String, default='COMPLETED') # IN_PROGRESS, COMPLETED, ROLLBACK, FAILED
    executed_by = Column(String, default='Cortex Autonomous Agent')
    execution_log = Column(JSON, default=list)
    result_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Scenario(Base):
    __tablename__ = 'scenarios'
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    scenario_type = Column(String, nullable=False) # Port shutdown, Demand spike, Carrier strike
    duration_days = Column(Integer, default=7)
    region = Column(String, default='GCC')
    parameters = Column(JSON, default=dict)
    baseline_kpis = Column(JSON, default=dict)
    simulated_kpis = Column(JSON, default=dict)
    impact_summary = Column(Text, nullable=True)
    created_by = Column(String, default='Supply Chain Analyst')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id = Column(String, primary_key=True, default=gen_uuid)
    event_type = Column(String, index=True, nullable=False) # AUTH_LOGIN, RISK_ACKNOWLEDGED, PO_APPROVED, AI_QUERY, PLAYBOOK_TRIGGERED
    actor = Column(String, index=True, nullable=False)
    actor_role = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, default='127.0.0.1')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
