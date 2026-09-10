from fastapi.testclient import TestClient
from app.main import app

#fake client 
client = TestClient(app)

#sends GET/health
def test_app_loads():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'ok' : True}


