


#happy path tests
def test_create_customer_success(client):
    response = client.post(
        "/customers",
        json={
            "name": "Ana",
            "email": "ana@example.com",
        },
    )

    #transform json to python dict
    data = response.json()

    assert response.status_code == 200
    
    assert data["id"] is not None
    assert data["name"] == "Ana"
    assert data["email"] == "ana@example.com"
    assert "internal_note" not in data


def test_get_customer_success(client, customer):

    customer_id = customer['id']

    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200

    data = response.json()
    
    assert data['id'] == customer_id
    assert data['name'] == customer['name']
    assert data['email'] == customer['email']
    assert 'internal note' not in data


#failure tests
def test_create_customer_duplicate_email_returns_409(client, customer):
    
    response = client.post(
        "/customers",
        json={
            "name": "Ana",
            "email": "x.com",
        },
    )

    data = response.json()

    assert response.status_code == 409
    assert data == {'detail': 'customer email already exists'}
 
def test_get_customer_missing_returns_404(client):
    
    response = client.get(
        "/customers/999",
    )

    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'customer not found'}
 
  