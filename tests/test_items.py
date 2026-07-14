
def test_create_item_success(client, order):
    response = client.post(
        '/items',
         json= {
            'order_id': order['id'],
            'product_name': 'toy',
            'quantity': 10,
            'unit_price_cents': 50}
         )
    
    data = response.json()
    assert response.status_code == 201
    assert data['id'] is not None
    assert data['order_id'] == order['id']
    assert data['product_name'] == 'toy'
    assert data['quantity'] == 10
    assert data['unit_price_cents'] == 50

def test_list_items_filter_by_min_quantity_success(client, make_item):

    first_item = make_item(product_name = 'toy', quantity= 1, unit_price_cents= 10)
    second_item = make_item(product_name = 'not_toy', quantity= 2, unit_price_cents= 10)

    response = client.get('/items',
                params= {'min_quantity': 2}
                )

    assert response.status_code == 200
    
    data = response.json()
    assert len(data) ==1 
    assert data[0]['id'] == second_item['id']
    assert data[0]['quantity'] == second_item['quantity']

def test_list_items_sort_by_product_name_ascending_success(client, make_item):
    
    first_item = make_item(product_name = 'horse', quantity= 2, unit_price_cents= 10)
    second_item = make_item(product_name = 'cat', quantity= 2, unit_price_cents= 10)
    third_item = make_item(product_name = 'dog', quantity= 2, unit_price_cents= 10)

    response = client.get(
        '/items',
        params={
            'sort_by': 'product_name',
            'sort_dir': 'asc'
        })
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 3

    assert data[0]['product_name'] == second_item['product_name']
    assert data[1]['product_name'] == third_item['product_name']
    assert data[2]['product_name'] == first_item['product_name']

def test_list_items_filter_by_order_id_success(client, make_order):

    first_order = make_order(total_cents = 10, status = 'paid')
    second_order = make_order(total_cents = 10, status = 'pending')

    first_item_response = client.post('/items',
                                      json={
                                          'order_id': first_order['id'],
                                          'product_name': 'toy',
                                          'quantity': 1,
                                          'unit_price_cents': 10
                                      })
    assert first_item_response.status_code == 201
    first_item = first_item_response.json()

    second_item_response = client.post('/items',
                                      json={
                                          'order_id': second_order['id'],
                                          'product_name': 'not_toy',
                                          'quantity': 2,
                                          'unit_price_cents': 20
                                      })
    assert second_item_response.status_code == 201
    second_item = second_item_response.json()

    response = client.get('/items',
                          params={
                              'order_id': first_order['id']
                          })

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1 
    assert data[0]['id'] == first_item['id']
    assert data[0]['order_id'] == first_item['order_id']

def test_list_items_paginates_success(client, make_item):
    first_item = make_item(product_name = 'horse', quantity= 2, unit_price_cents= 10)
    second_item = make_item(product_name = 'cat', quantity= 2, unit_price_cents= 10)
    third_item = make_item(product_name = 'dog', quantity= 2, unit_price_cents= 10)


    response = client.get('/items',
                          params={
                              'offset': 1,
                              'limit': 1
                          })

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]['id'] == third_item['id']
    assert data[0]['product_name'] == 'dog'

def test_list_items_no_matches_returns_empty_list(client):
    response = client.get(
        '/items',
        params={
            'offset': 0,
            'limit': 2
        })
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 0


#failure tests

def test_create_item_missing_order_returns_404(client):
    response = client.post(
        '/items',
            json= {
            'order_id': 999,
            'product_name': 'toy',
            'quantity': 10,
            'unit_price_cents': 50}
         )
    
    assert response.status_code == 404
    data = response.json()
    assert data == {'detail': 'order not found'}




