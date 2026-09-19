import datetime
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'HEALTHY'
    assert 'subsystems' in data

def test_dashboard_summary():
    res = client.get('/api/dashboard/summary')
    assert res.status_code == 200
    data = res.json()
    assert 'kpis' in data
    assert 'inventory_value' in data['kpis']
    assert 'otif_rate' in data['kpis']
    assert data['counts']['suppliers'] >= 300

def test_suppliers_list_and_detail():
    res = client.get('/api/suppliers?limit=10')
    assert res.status_code == 200
    data = res.json()
    assert data['total'] >= 300
    assert len(data['items']) == 10
    
    first_id = data['items'][0]['id']
    detail = client.get(f'/api/suppliers/{first_id}')
    assert detail.status_code == 200
    assert 'supplier' in detail.json()

def test_purchase_orders_and_approval():
    res = client.get('/api/orders?limit=5')
    assert res.status_code == 200
    data = res.json()
    assert len(data['items']) == 5
    
    # Test Create PO
    new_po_payload = {
        'supplier_code': 'SUP_0010',
        'destination_warehouse': 'WH_MUMBAI',
        'part_code': 'PRD_001',
        'quantity': 500,
        'unit_price': 45.0
    }
    create_res = client.post('/api/orders', json=new_po_payload)
    assert create_res.status_code == 200
    po_data = create_res.json()
    assert po_data['status'] == 'CREATED'
    
    # Test Approve PO
    approve_res = client.patch(f"/api/orders/{po_data['po_number']}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()['new_status'] == 'Approved'

def test_risk_alerts_and_workflow():
    res = client.get('/api/risks')
    assert res.status_code == 200
    data = res.json()
    assert len(data['items']) >= 4
    
    alert = data['items'][0]
    # Test Acknowledge
    ack_res = client.post(f"/api/risks/{alert['alert_code']}/acknowledge")
    assert ack_res.status_code == 200
    assert ack_res.json()['new_status'] == 'Acknowledged'

def test_ai_playbooks_execution():
    res = client.get('/api/playbooks')
    assert res.status_code == 200
    data = res.json()
    assert len(data['playbooks']) >= 2
    
    pb_id = data['playbooks'][0]['playbook_id']
    run_res = client.post(f'/api/playbooks/{pb_id}/run')
    assert run_res.status_code == 200
    assert run_res.json()['status'] == 'SUCCESS'

def test_ontology_entities_and_relationships():
    ent_res = client.get('/api/ontology/entities')
    assert ent_res.status_code == 200
    assert ent_res.json()['total'] >= 6
    
    rel_res = client.get('/api/ontology/relationships')
    assert rel_res.status_code == 200
    assert rel_res.json()['total'] >= 5

