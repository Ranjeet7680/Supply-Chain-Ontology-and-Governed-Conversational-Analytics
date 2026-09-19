from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_scenario_simulation():
    res = client.post('/api/scenarios/run', json={
        'name': '5-Day Port Shutdown Test',
        'scenario_type': 'Port Shutdown',
        'duration_days': 5,
        'region': 'GCC',
        'demand_increase_pct': 10.0,
        'capacity_reduction_pct': 40.0,
        'transport_disruption_pct': 60.0
    })
    assert res.status_code == 200
    data = res.json()
    assert 'simulated' in data
    assert 'impact_summary' in data
    assert data['simulated']['otif_rate'] < data['baseline']['otif_rate']

def test_global_search():
    res = client.get('/api/search?q=tata')
    assert res.status_code == 200
    data = res.json()
    assert 'results' in data
    assert 'suppliers' in data['results']

def test_inventory_list():
    res = client.get('/api/inventory?limit=10')
    assert res.status_code == 200
    data = res.json()
    assert data['total'] >= 10
    assert len(data['items']) == 10
