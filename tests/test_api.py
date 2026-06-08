from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_lookup():
    data=client.post('/api/lookup', json={'domain':'example.com'}).json()
    assert data['domain'] == 'example.com'
    assert 'dns' in data
