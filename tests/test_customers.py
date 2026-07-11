


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

    assert response.status_code == 201
    
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

def test_list_customers_filter_by_name_success(client, make_customer):

    first_customer = make_customer(name='Ana', email='ana@x.com')
    second_customer = make_customer(name='Olga', email='olga@x.com')

    response = client.get('/customers',
                          params={
                              'name': 'Olga',
                          })

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == second_customer['id']
    assert data[0]['name'] == second_customer['name']

def test_list_customers_filter_by_email_success(client, make_customer):

    first_customer = make_customer(name='Ana', email='ana@x.com')
    second_customer = make_customer(name='Olga', email='olga@x.com')

    response = client.get('/customers',
                          params={
                              'email': 'olga@x.com',
                          })

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == second_customer['id']
    assert data[0]['email'] == second_customer['email']


def test_sort_by_customer_name_descending_success(client, make_customer):

    first_customer = make_customer(name='Ana', email='ana@x.com')
    second_customer = make_customer(name='Olga', email='olga@x.com')

    response = client.get('/customers',
                          params={
                              'sort_by': 'name',
                          })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['id'] == second_customer['id']


def test_list_customers_paginates_success(client, make_customer):

    first_customer = make_customer(name='Ana', email='ana@x.com')
    second_customer = make_customer(name='Olga', email='olga@x.com')    
    third_customer = make_customer(name='Bob', email='bob@x.com')    

    response = client.get('/customers',
                          params={
                              'offset': 1,
                              'limit': 1
                          })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == third_customer['id']


def test_list_customers_no_matches_returns_empty_list_success(client):

    response = client.get('/customers',
                          params={
                            'offset': 0,
                            'limit': 2
                          })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    


#failure tests
def test_create_customer_duplicate_email_returns_409(client, customer):
    
    response = client.post(
        "/customers",
        json={
            "name": "O",
            "email": "olga@x.com",
        },
    )

    data = response.json()

    assert response.status_code == 409
    assert data == {'detail': 'customer email already exists'}

def test_create_customer_invalid_email_returns_422(client, customer):
    
    response = client.post(
        "/customers",
        json={
            "name": "O",
            "email": "@x.com",
        },
    )

    data = response.json()

    assert response.status_code == 422
    assert 'detail' in data
 
def test_get_customer_missing_returns_404(client):
    
    response = client.get(
        "/customers/999",
    )

    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'customer not found'}
 

