from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_lookup(monkeypatch):
    monkeypatch.setattr("src.main.rdap_lookup", lambda domain: {})
    monkeypatch.setattr("src.main.dns_records", lambda domain: {})

    data=client.post('/api/lookup', json={'domain':'example.com'}).json()
    assert data['domain'] == 'example.com'
    assert 'dns' in data


def test_lookup_normalizes_domain(monkeypatch):
    monkeypatch.setattr("src.main.rdap_lookup", lambda domain: {})
    monkeypatch.setattr("src.main.dns_records", lambda domain: {})

    response = client.post("/api/lookup", json={"domain": "EXAMPLE.COM."})

    assert response.status_code == 200
    assert response.json()["domain"] == "example.com"


def test_lookup_rejects_command_option_as_domain():
    response = client.post("/api/lookup", json={"domain": "-type=any"})

    assert response.status_code == 422


def test_lookup_rejects_path_in_domain():
    response = client.post("/api/lookup", json={"domain": "example.com/../../etc/passwd"})

    assert response.status_code == 422
