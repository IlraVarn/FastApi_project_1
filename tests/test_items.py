
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
    assert response.status_code == 200
    assert data['id'] is not None
    assert data['order_id'] == order['id']
    assert data['product_name'] == 'toy'
    assert data['quantity'] == 10
    assert data['unit_price_cents'] == 50


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

