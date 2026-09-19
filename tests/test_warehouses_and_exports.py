from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_warehouses_list():
    res = client.get('/api/warehouses')
    assert res.status_code == 200
    data = res.json()
    assert data['total'] >= 8
    assert len(data['items']) >= 8

def test_csv_exports():
    for entity in ['suppliers', 'orders', 'inventory', 'shipments']:
        res = client.get(f'/api/export/csv/{entity}')
        assert res.status_code == 200
        assert 'text/csv' in res.headers['content-type']
        assert len(res.text) > 50
