import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.database import get_db
from backend.models import (
    Supplier, Warehouse, Product, SKUInventory,
    PurchaseOrder, POLineItem, Shipment, ShipmentEvent,
    RiskAlert, OntologyEntity, OntologyRelationship, Playbook, PlaybookRun, Scenario, AuditEvent, User
)

router = APIRouter()

# --- Auth & Profile ---
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = 'demo'

@router.post('/auth/login', tags=['Enterprise Auth'])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Default fallback to director if demo
        user = db.query(User).first()
    return {
        'status': 'SUCCESS',
        'token': 'jwt_bearer_' + user.id,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'department': user.department
        }
    }

@router.get('/auth/me', tags=['Enterprise Auth'])
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'department': user.department,
        'permissions': ['VIEW_DASHBOARD', 'MANAGE_SUPPLIERS', 'TRACK_SHIPMENTS', 'EXECUTE_AI', 'RUN_PLAYBOOKS']
    }

# --- Command Center & KPIs ---
@router.get('/dashboard/summary', tags=['Command Center'])
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_suppliers = db.query(Supplier).count()
    active_shipments = db.query(Shipment).filter(Shipment.status.in_(['In Transit', 'Delayed', 'At Risk'])).count()
    open_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_(['Pending Approval', 'Approved', 'Delayed'])).count()
    critical_risks = db.query(RiskAlert).filter(RiskAlert.status == 'Open').count()
    
    # Calculate live OTIF
    total_pos = db.query(PurchaseOrder).count()
    otif_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status == 'Received', PurchaseOrder.variance_days == 0).count()
    live_otif_pct = round((otif_pos / max(total_pos, 1)) * 100, 1) if total_pos > 0 else 94.2

    # Inventory Value
    total_inv_val = db.query(func.sum(SKUInventory.inventory_value)).scalar() or 24850000.0

    return {
        'kpis': {
            'inventory_value': {'value': round(total_inv_val, 2), 'unit': 'USD', 'change_pct': 4.2, 'target': 26000000.0, 'status': 'Healthy'},
            'otif_rate': {'value': live_otif_pct, 'unit': '%', 'change_pct': -1.4, 'target': 96.0, 'status': 'Warning'},
            'supplier_on_time': {'value': 91.8, 'unit': '%', 'change_pct': 2.1, 'target': 92.0, 'status': 'Healthy'},
            'stockout_risk_skus': {'value': db.query(SKUInventory).filter(SKUInventory.status == 'At Risk').count(), 'unit': 'SKUs', 'change_pct': -5.0, 'target': 10, 'status': 'At Risk'},
            'open_purchase_orders': {'value': open_pos, 'unit': 'POs', 'change_pct': 8.5, 'target': 250, 'status': 'Operational'},
            'active_shipments': {'value': active_shipments, 'unit': 'Convoys', 'change_pct': 12.0, 'target': 180, 'status': 'Operational'},
            'inventory_turns': {'value': 6.8, 'unit': 'Turns/Yr', 'change_pct': 0.4, 'target': 7.0, 'status': 'Healthy'},
            'fill_rate': {'value': 97.4, 'unit': '%', 'change_pct': 0.8, 'target': 98.0, 'status': 'Healthy'}
        },
        'counts': {
            'suppliers': total_suppliers,
            'warehouses': db.query(Warehouse).count(),
            'products': db.query(Product).count(),
            'critical_risks': critical_risks
        }
    }

# --- Suppliers ---
@router.get('/suppliers', tags=['Suppliers'])
def list_suppliers(
    search: Optional[str] = None,
    tier: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(Supplier)
    if search:
        q = q.filter(Supplier.supplier_name.ilike(f'%{search}%') | Supplier.supplier_code.ilike(f'%{search}%') | Supplier.country.ilike(f'%{search}%'))
    if tier:
        q = q.filter(Supplier.tier == tier)
    if risk_level == 'High':
        q = q.filter(Supplier.risk_score >= 70)
    elif risk_level == 'Medium':
        q = q.filter(Supplier.risk_score >= 30, Supplier.risk_score < 70)
    elif risk_level == 'Low':
        q = q.filter(Supplier.risk_score < 30)

    total = q.count()
    items = q.order_by(desc(Supplier.spend)).offset(offset).limit(limit).all()
    return {
        'total': total,
        'limit': limit,
        'offset': offset,
        'items': [
            {
                'id': s.id,
                'supplier_code': s.supplier_code,
                'name': s.supplier_name,
                'category': s.category,
                'country': s.country,
                'tier': s.tier,
                'otif_score': s.otif_score,
                'lead_time_days': s.lead_time_days,
                'quality_score': s.quality_score,
                'risk_score': s.risk_score,
                'spend': s.spend,
                'status': s.status,
                'last_delivery': s.last_delivery
            } for s in items
        ]
    }

@router.get('/suppliers/{supplier_id}', tags=['Suppliers'])
def get_supplier_detail(supplier_id: str, db: Session = Depends(get_db)):
    s = db.query(Supplier).filter((Supplier.id == supplier_id) | (Supplier.supplier_code == supplier_id)).first()
    if not s:
        raise HTTPException(status_code=404, detail='Supplier not found')
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.supplier_code == s.supplier_code).limit(10).all()
    return {
        'supplier': {
            'id': s.id,
            'code': s.supplier_code,
            'name': s.supplier_name,
            'country': s.country,
            'tier': s.tier,
            'category': s.category,
            'otif': s.otif_score,
            'lead_time': s.lead_time_days,
            'risk_score': s.risk_score,
            'quality': s.quality_score,
            'spend': s.spend,
            'status': s.status,
            'contact_email': s.contact_email
        },
        'recent_pos': [
            {
                'po_number': p.po_number,
                'amount': p.total_amount,
                'status': p.status,
                'expected_delivery': p.expected_delivery_date
            } for p in pos
        ]
    }

# --- Inventory & SKUs ---
@router.get('/inventory', tags=['Inventory Intelligence'])
def list_inventory(
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(SKUInventory)
    if status:
        q = q.filter(SKUInventory.status == status)
    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return {
        'total': total,
        'items': [
            {
                'id': item.id,
                'part_code': item.part_code,
                'warehouse': item.warehouse_code,
                'quantity_on_hand': item.quantity_on_hand,
                'reserved_quantity': item.reserved_quantity,
                'safety_stock': item.safety_stock,
                'stockout_probability': item.stockout_probability,
                'demand_forecast_30d': item.demand_forecast_30d,
                'inventory_value': item.inventory_value,
                'status': item.status
            } for item in items
        ]
    }

# --- Purchase Orders ---
@router.get('/orders', tags=['Purchase Orders'])
def list_orders(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseOrder)
    if status:
        q = q.filter(PurchaseOrder.status == status)
    total = q.count()
    items = q.order_by(desc(PurchaseOrder.created_at)).offset(offset).limit(limit).all()
    return {
        'total': total,
        'items': [
            {
                'id': po.id,
                'po_number': po.po_number,
                'supplier_code': po.supplier_code,
                'supplier_name': po.supplier_name,
                'warehouse': po.destination_warehouse,
                'order_date': po.order_date,
                'expected_delivery': po.expected_delivery_date,
                'actual_delivery': po.actual_delivery_date,
                'amount': po.total_amount,
                'status': po.status,
                'variance_days': po.variance_days
            } for po in items
        ]
    }

class POCreateRequest(BaseModel):
    supplier_code: str
    destination_warehouse: str
    part_code: str
    quantity: int
    unit_price: float

@router.post('/orders', tags=['Purchase Orders'])
def create_purchase_order(req: POCreateRequest, db: Session = Depends(get_db)):
    po_num = f'PO-2026-{db.query(PurchaseOrder).count() + 1000}'
    sup = db.query(Supplier).filter(Supplier.supplier_code == req.supplier_code).first()
    new_po = PurchaseOrder(
        po_number=po_num,
        supplier_code=req.supplier_code,
        supplier_name=sup.supplier_name if sup else f'Supplier {req.supplier_code}',
        destination_warehouse=req.destination_warehouse,
        order_date=datetime.date.today().strftime('%Y-%m-%d'),
        expected_delivery_date=(datetime.date.today() + datetime.timedelta(days=14)).strftime('%Y-%m-%d'),
        total_amount=round(req.quantity * req.unit_price, 2),
        status='Pending Approval'
    )
    db.add(new_po)
    db.commit()
    db.refresh(new_po)
    
    # Audit log
    db.add(AuditEvent(
        event_type='PO_CREATED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type='PurchaseOrder',
        entity_id=new_po.po_number,
        details={'amount': new_po.total_amount, 'supplier': req.supplier_code}
    ))
    db.commit()
    return {'status': 'CREATED', 'po_number': new_po.po_number, 'id': new_po.id}

@router.patch('/orders/{po_id}/approve', tags=['Purchase Orders'])
def approve_purchase_order(po_id: str, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter((PurchaseOrder.id == po_id) | (PurchaseOrder.po_number == po_id)).first()
    if not po:
        raise HTTPException(status_code=404, detail='PO not found')
    po.status = 'Approved'
    db.commit()
    db.add(AuditEvent(
        event_type='PO_APPROVED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type='PurchaseOrder',
        entity_id=po.po_number,
        details={'approved_status': 'Approved'}
    ))
    db.commit()
    return {'status': 'SUCCESS', 'po_number': po.po_number, 'new_status': 'Approved'}

# --- Shipments ---
@router.get('/shipments', tags=['Shipments'])
def list_shipments(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return {
        'total': total,
        'items': [
            {
                'id': s.id,
                'shipment_id': s.shipment_id,
                'carrier': s.carrier,
                'origin': s.origin,
                'destination': s.destination,
                'corridor': s.corridor,
                'mode': s.mode,
                'status': s.status,
                'eta': s.eta,
                'delay_hours': s.delay_hours,
                'risk_score': s.risk_score,
                'weather': s.weather_condition,
                'cost': s.delivery_cost
            } for s in items
        ]
    }

# --- Risk & Alerts Engine ---
@router.get('/risks', tags=['Risk & Alerts'])
def list_risks(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(RiskAlert)
    if status:
        q = q.filter(RiskAlert.status == status)
    if severity:
        q = q.filter(RiskAlert.severity == severity)
    items = q.order_by(desc(RiskAlert.risk_score)).all()
    return {
        'total': len(items),
        'items': [
            {
                'id': r.id,
                'alert_code': r.alert_code,
                'category': r.category,
                'severity': r.severity,
                'entity_type': r.entity_type,
                'entity_id': r.entity_id,
                'entity_name': r.entity_name,
                'risk_score': r.risk_score,
                'reason': r.reason,
                'evidence': r.evidence,
                'recommended_action': r.recommended_action,
                'status': r.status,
                'owner': r.owner,
                'detection_time': r.detection_time.strftime('%Y-%m-%d %H:%M:%S') if r.detection_time else None
            } for r in items
        ]
    }

@router.post('/risks/{alert_id}/acknowledge', tags=['Risk & Alerts'])
def acknowledge_risk(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(RiskAlert).filter((RiskAlert.id == alert_id) | (RiskAlert.alert_code == alert_id)).first()
    if not alert:
        raise HTTPException(status_code=404, detail='Risk Alert not found')
    alert.status = 'Acknowledged'
    db.commit()
    db.add(AuditEvent(
        event_type='RISK_ACKNOWLEDGED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type='RiskAlert',
        entity_id=alert.alert_code,
        details={'previous_status': 'Open', 'new_status': 'Acknowledged'}
    ))
    db.commit()
    return {'status': 'SUCCESS', 'alert_code': alert.alert_code, 'new_status': 'Acknowledged'}

@router.post('/risks/{alert_id}/resolve', tags=['Risk & Alerts'])
def resolve_risk(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(RiskAlert).filter((RiskAlert.id == alert_id) | (RiskAlert.alert_code == alert_id)).first()
    if not alert:
        raise HTTPException(status_code=404, detail='Risk Alert not found')
    alert.status = 'Resolved'
    alert.resolved_at = datetime.datetime.utcnow()
    db.commit()
    db.add(AuditEvent(
        event_type='RISK_RESOLVED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type='RiskAlert',
        entity_id=alert.alert_code,
        details={'mitigation': 'Resolved by operator intervention'}
    ))
    db.commit()
    return {'status': 'SUCCESS', 'alert_code': alert.alert_code, 'new_status': 'Resolved'}

# --- Supply Chain Ontology & Graph ---
@router.get('/ontology/entities', tags=['Ontology & Knowledge Graph'])
def get_ontology_entities(db: Session = Depends(get_db)):
    entities = db.query(OntologyEntity).all()
    return {
        'total': len(entities),
        'entities': [
            {
                'id': e.entity_id,
                'type': e.entity_type,
                'name': e.name,
                'attributes': e.attributes
            } for e in entities
        ]
    }

@router.get('/ontology/relationships', tags=['Ontology & Knowledge Graph'])
def get_ontology_relationships(db: Session = Depends(get_db)):
    rels = db.query(OntologyRelationship).all()
    return {
        'total': len(rels),
        'relationships': [
            {
                'source': r.source_entity_id,
                'target': r.target_entity_id,
                'type': r.relation_type,
                'properties': r.properties
            } for r in rels
        ]
    }

# --- AI Playbooks & Scenarios ---
@router.get('/playbooks', tags=['AI Playbooks'])
def list_playbooks(db: Session = Depends(get_db)):
    pbs = db.query(Playbook).all()
    return {
        'playbooks': [
            {
                'id': p.id,
                'playbook_id': p.playbook_id,
                'title': p.title,
                'description': p.description,
                'trigger': p.trigger_condition,
                'actions': p.actions,
                'requires_approval': p.requires_approval,
                'status': p.status,
                'owner': p.owner
            } for p in pbs
        ]
    }

@router.post('/playbooks/{playbook_id}/run', tags=['AI Playbooks'])
def run_playbook(playbook_id: str, db: Session = Depends(get_db)):
    pb = db.query(Playbook).filter((Playbook.id == playbook_id) | (Playbook.playbook_id == playbook_id)).first()
    if not pb:
        raise HTTPException(status_code=404, detail='Playbook not found')
    
    run_code = f'RUN-{int(datetime.datetime.utcnow().timestamp())}'
    run = PlaybookRun(
        run_code=run_code,
        playbook_id=pb.id,
        status='COMPLETED',
        executed_by='Cortex Autonomous Agent',
        execution_log=[
            {'step': 1, 'action': 'Scanned corridor network', 'result': 'Identified 3 delayed consignments'},
            {'step': 2, 'action': 'Evaluated alternate route costs', 'result': 'Air freight + vs Sea +'},
            {'step': 3, 'action': 'Dispatched reroute orders via MCP API', 'result': 'Carrier accepted reroute confirmation'},
            {'step': 4, 'action': 'Generated Executive Audit Record', 'result': 'Log recorded in Governance Mart'}
        ],
        result_summary=f'Playbook {pb.title} executed successfully. 3 consignments rerouted with 0 SLA breach.',
        completed_at=datetime.datetime.utcnow()
    )
    db.add(run)
    db.add(AuditEvent(
        event_type='PLAYBOOK_EXECUTED',
        actor='Cortex Autonomous Agent',
        actor_role='Autonomous AI',
        entity_type='Playbook',
        entity_id=pb.playbook_id,
        details={'run_code': run_code, 'summary': run.result_summary}
    ))
    db.commit()
    return {
        'status': 'SUCCESS',
        'run_code': run_code,
        'summary': run.result_summary,
        'execution_log': run.execution_log
    }

# --- Governance & Audit Stream ---
@router.get('/governance/audit', tags=['Governance & Lineage'])
def get_audit_trail(limit: int = 25, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(limit).all()
    return {
        'total': len(events),
        'events': [
            {
                'id': e.id,
                'type': e.event_type,
                'actor': e.actor,
                'role': e.actor_role,
                'entity': f'{e.entity_type}:{e.entity_id}' if e.entity_type else 'System',
                'details': e.details,
                'timestamp': e.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for e in events
        ]
    }


# --- Scenario Simulator ---
class ScenarioRunRequest(BaseModel):
    name: str = '5-Day Rotterdam & Jebel Ali Port Shutdown'
    scenario_type: str = 'Port Shutdown'
    duration_days: int = 5
    region: str = 'GCC'
    demand_increase_pct: float = 0.0
    capacity_reduction_pct: float = 40.0
    transport_disruption_pct: float = 65.0

@router.post('/scenarios/run', tags=['Scenario Simulator'])
def run_scenario(req: ScenarioRunRequest, db: Session = Depends(get_db)):
    baseline = {
        'otif_rate': 94.2,
        'inventory_value_usd': 24850000.0,
        'stockout_skus': 18,
        'average_delay_hours': 4.2,
        'landed_cost_variance_pct': 0.0
    }
    
    # Mathematical simulation model based on input disruptions
    sim_otif = max(45.0, round(baseline['otif_rate'] - (req.duration_days * 2.8) - (req.transport_disruption_pct * 0.25), 1))
    sim_cost_var = round((req.capacity_reduction_pct * 0.35) + (req.transport_disruption_pct * 0.42), 1)
    sim_stockout = int(baseline['stockout_skus'] + (req.duration_days * 4) + int(req.demand_increase_pct * 0.5))
    sim_delays = round(baseline['average_delay_hours'] + (req.duration_days * 7.5), 1)
    
    simulated = {
        'otif_rate': sim_otif,
        'inventory_value_usd': round(baseline['inventory_value_usd'] * (1 - (req.duration_days * 0.03)), 2),
        'stockout_skus': sim_stockout,
        'average_delay_hours': sim_delays,
        'landed_cost_variance_pct': sim_cost_var
    }
    
    impact_summary = f"Simulation '{req.name}' ({req.duration_days} days): OTIF declines by {round(baseline['otif_rate'] - sim_otif, 1)}%, additional {sim_stockout - baseline['stockout_skus']} SKUs face stockout risk, and landed costs increase by +{sim_cost_var}% across {req.region} corridor."
    
    scenario_record = Scenario(
        name=req.name,
        scenario_type=req.scenario_type,
        duration_days=req.duration_days,
        region=req.region,
        parameters=req.model_dump(),
        baseline_kpis=baseline,
        simulated_kpis=simulated,
        impact_summary=impact_summary
    )
    db.add(scenario_record)
    db.add(AuditEvent(
        event_type='SCENARIO_SIMULATED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type='Scenario',
        entity_id=scenario_record.id,
        details={'name': req.name, 'otif_drop': round(baseline['otif_rate'] - sim_otif, 1)}
    ))
    db.commit()
    
    return {
        'scenario_id': scenario_record.id,
        'name': req.name,
        'type': req.scenario_type,
        'duration_days': req.duration_days,
        'baseline': baseline,
        'simulated': simulated,
        'impact_summary': impact_summary,
        'mitigation_recommendation': 'Trigger Playbook PB-PORT-SHUTDOWN to reroute priority cargo to auxiliary berth at Port Sultan Qaboos or switch critical SKU PRD_004 to air charter.'
    }

@router.get('/scenarios/history', tags=['Scenario Simulator'])
def get_scenario_history(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(desc(Scenario.created_at)).limit(10).all()
    return {
        'total': len(scenarios),
        'scenarios': [
            {
                'id': s.id,
                'name': s.name,
                'type': s.scenario_type,
                'duration': s.duration_days,
                'region': s.region,
                'baseline': s.baseline_kpis,
                'simulated': s.simulated_kpis,
                'summary': s.impact_summary,
                'created_at': s.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for s in scenarios
        ]
    }

# --- Global Search API ---
@router.get('/search', tags=['Global Search'])
def global_search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    term = f'%{q}%'
    suppliers = db.query(Supplier).filter(Supplier.supplier_name.ilike(term) | Supplier.supplier_code.ilike(term)).limit(5).all()
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.po_number.ilike(term) | PurchaseOrder.supplier_name.ilike(term)).limit(5).all()
    shipments = db.query(Shipment).filter(Shipment.shipment_id.ilike(term) | Shipment.carrier.ilike(term) | Shipment.origin.ilike(term)).limit(5).all()
    skus = db.query(SKUInventory).filter(SKUInventory.part_code.ilike(term)).limit(5).all()
    risks = db.query(RiskAlert).filter(RiskAlert.alert_code.ilike(term) | RiskAlert.entity_name.ilike(term)).limit(5).all()
    
    return {
        'query': q,
        'results': {
            'suppliers': [{'id': s.id, 'title': s.supplier_name, 'code': s.supplier_code, 'type': 'Supplier'} for s in suppliers],
            'purchase_orders': [{'id': p.id, 'title': p.po_number, 'status': p.status, 'amount': p.total_amount, 'type': 'Purchase Order'} for p in pos],
            'shipments': [{'id': sh.id, 'title': sh.shipment_id, 'carrier': sh.carrier, 'status': sh.status, 'type': 'Shipment'} for sh in shipments],
            'skus': [{'id': sk.id, 'title': sk.part_code, 'warehouse': sk.warehouse_code, 'quantity': sk.quantity_on_hand, 'type': 'SKU'} for sk in skus],
            'risks': [{'id': r.id, 'title': r.entity_name, 'severity': r.severity, 'code': r.alert_code, 'type': 'Risk Alert'} for r in risks]
        }
    }


# --- Warehouses Endpoint ---
@router.get('/warehouses', tags=['Warehouses'])
def list_warehouses(db: Session = Depends(get_db)):
    whs = db.query(Warehouse).all()
    return {
        'total': len(whs),
        'items': [
            {
                'id': w.id,
                'code': w.warehouse_code,
                'name': w.warehouse_name,
                'location': w.location,
                'region': w.region,
                'capacity_sqft': w.capacity_sqft,
                'utilization_pct': w.utilization_pct,
                'status': w.operational_status
            } for w in whs
        ]
    }

# --- CSV Export Endpoint ---
from fastapi.responses import Response

@router.get('/export/csv/{entity_type}', tags=['Exports & Briefs'])
def export_entity_csv(entity_type: str, db: Session = Depends(get_db)):
    entity_type = entity_type.lower()
    if entity_type in ['suppliers', 'supplier']:
        records = db.query(Supplier).limit(500).all()
        lines = ['supplier_code,name,country,tier,otif_score,lead_time_days,quality_score,risk_score,spend,status']
        for s in records:
            lines.append(f"{s.supplier_code},{s.supplier_name},{s.country},{s.tier},{s.otif_score},{s.lead_time_days},{s.quality_score},{s.risk_score},{s.spend},{s.status}")
        content = '\n'.join(lines)
        filename = 'supplychain_iq_suppliers.csv'
    elif entity_type in ['orders', 'purchase_orders', 'pos']:
        records = db.query(PurchaseOrder).limit(500).all()
        lines = ['po_number,supplier_code,warehouse,amount,status,order_date,expected_delivery']
        for p in records:
            lines.append(f"{p.po_number},{p.supplier_code},{p.destination_warehouse},{p.total_amount},{p.status},{p.order_date},{p.expected_delivery_date}")
        content = '\n'.join(lines)
        filename = 'supplychain_iq_purchase_orders.csv'
    elif entity_type in ['inventory', 'skus']:
        records = db.query(SKUInventory).limit(500).all()
        lines = ['part_code,warehouse,quantity_on_hand,reserved,safety_stock,stockout_prob,status']
        for i in records:
            lines.append(f"{i.part_code},{i.warehouse_code},{i.quantity_on_hand},{i.reserved_quantity},{i.safety_stock},{i.stockout_probability},{i.status}")
        content = '\n'.join(lines)
        filename = 'supplychain_iq_inventory.csv'
    elif entity_type in ['shipments', 'shipment']:
        records = db.query(Shipment).limit(500).all()
        lines = ['shipment_id,carrier,origin,destination,status,eta,delay_hours,risk_score,cost']
        for sh in records:
            lines.append(f"{sh.shipment_id},{sh.carrier},{sh.origin},{sh.destination},{sh.status},{sh.eta},{sh.delay_hours},{sh.risk_score},{sh.delivery_cost}")
        content = '\n'.join(lines)
        filename = 'supplychain_iq_shipments.csv'
    else:
        raise HTTPException(status_code=400, detail='Unknown entity export type. Choose from: suppliers, orders, inventory, shipments')

    db.add(AuditEvent(
        event_type='DATA_EXPORTED',
        actor='Ranjeet Kumar',
        actor_role='Supply Chain Director',
        entity_type=entity_type.upper(),
        details={'filename': filename, 'records_count': len(records)}
    ))
    db.commit()

    return Response(
        content=content,
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
