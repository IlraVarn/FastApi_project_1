#success tests
def test_create_order_success(client, customer,):

    response = client.post(
        "/orders",
        json={
            "customer_id": customer['id'],
            "total_cents": 10,
            "status": "pending"
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["created_at"] is not None
    assert data["customer_id"] == customer['id']
    assert data["total_cents"] == 10


def test_get_order_success(client, customer, order):
    order_id = order['id']

    response = client.get(f"/orders/{order_id}")
    
    data = response.json()
    assert response.status_code == 200

    assert data['id'] == order_id
    assert data['created_at'] is not None
    assert data['total_cents'] == 10
    assert 'status' not in data
    assert 'customer_id' not in data

    assert data['customer']['id'] == order['customer_id']
    assert data['customer']['name'] == customer['name']
    assert data['customer']['email'] == customer['email']
    assert 'internal_note' not in data['customer']


def test_get_order_with_items_success(client, customer, order, item):

    order_id = order['id']
    customer_id = customer['id']
    item_id = item['id']

    response = client.get(f'/orders/{order_id}/items')
    data = response.json()
    assert response.status_code == 200

    assert data['id'] == order_id
    assert data['created_at'] is not None
    assert data['total_cents'] == 10
    assert 'customer_id' not in data
    assert 'status' not in data

    assert data['customer']['id'] == customer_id
    assert data['customer']['name'] == customer['name']
    assert data['customer']['email'] == customer['email']
    assert 'internal_note' not in data['customer']

    assert len(data['items']) == 1
    returned_item = data['items'][0]

    assert returned_item['id'] == item_id
    assert returned_item['order_id'] == order_id
    assert returned_item['product_name'] == item['product_name']
    assert returned_item['unit_price_cents'] ==item['unit_price_cents']
    assert returned_item['quantity'] == item['quantity']


def test_list_list_orders_filter_by_status_success(client, make_order):
    
    paid_order = make_order(total_cents = 20, status = 'paid')
    pending_order = make_order(total_cents = 10, status = 'pending')


    response = client.get(
        '/orders',
        params={
            'status': 'paid',
        })
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1

    assert data[0]['id'] == paid_order['id']
    assert data[0]['created_at'] is not None
    assert data[0]['customer_id'] == paid_order['customer_id']
    assert data[0]['total_cents'] == paid_order['total_cents']
    assert 'status' not in data[0]


def test_list_orders_paginates_success(client, make_order):
    
    first_order = make_order(total_cents = 20, status = 'pending')
    second_order = make_order(total_cents = 10, status = 'pending')
    third_order = make_order(total_cents = 10, status = 'pending')


    response = client.get(
        '/orders',
        params={
            'offset': 1,
            'limit': 1
        })
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1

    assert data[0]['id'] == second_order['id']
    assert data[0]['customer_id'] == second_order['customer_id']
    assert data[0]['total_cents'] == second_order['total_cents']

    assert 'status' not in data


def test_list_orders_no_matches_returns_empty_list(client):
    response = client.get(
        '/orders',
        params={
            'status': 'paid',
            'offset': 0,
            'limit': 2
        })
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 0


def test_update_order_success(client, customer, order):

    order_id = order['id']

    response = client.put(
        f'/orders/{order_id}',
          json={
              'total_cents': 50,
              'status': 'pending'
          })
    
    data = response.json()
    assert response.status_code == 200

    assert data['id'] == order_id
    assert data['created_at'] is not None
    assert data['total_cents'] == 50

    assert data['customer']['id'] == customer['id']
    assert data['customer']['name'] == customer['name']
    assert data['customer']['email'] == customer['email']

    assert 'status' not in data
    assert 'internal_note' not in data['customer']

    list_response = client.get('/orders',
                               params={
                                   'status': 'pending'
                               })
    list_data = list_response.json()

    assert list_response.status_code == 200
    assert len(list_data) == 1
    assert list_data[0]['id'] == order_id


def test_delete_order_success(client, order):

    order_id = order['id']

    response = client.delete(f'/orders/{order_id}')

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    get_response = client.delete(f'/orders/{order_id}')    
    
    assert get_response.status_code == 404

#failure tests
def test_create_order_customer_not_found_returns_404(client):

    response = client.post(
        "/orders",
        json={
            "customer_id": 999,
            "total_cents": 10,
            "status": "pending"
        },
    )

    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'customer not found'}


def test_get_order_missing_returns_404(client):

    response = client.get("/orders/999")
    
    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'order not found'}


def test_get_order_with_items_missing_order_returns_404(client):

    response = client.get("/orders/999/items")
    
    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'order not found'}


def test_update_order_missing_returns_404(client):
    response = client.put(
        f'/orders/999',
          json={
              'total_cents': 50,
              'status': 'pending'
          })
    
    data = response.json()
    assert response.status_code == 404
    assert data == {'detail': 'order not found'}


def test_delete_order_missing_returns_404(client):
    response = client.delete('/orders/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'order not found'}


def test_delete_order_with_items_returns_409(client, order, item):

    order_id = order['id']

    response = client.delete(f'/orders/{order_id}')

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'order cannot be deleted with items'
        }


