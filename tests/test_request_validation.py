import pytest

def test_create_organization_invalid_name_returns_422(authenticated_client):
    
    response = authenticated_client.post(
        "/organizations",
        json={
            "name": " ",
        },
    )

    assert response.status_code == 422
    data = response.json()

    assert 'detail' in data

# def test_create_order_missing_total_cents_returns_422(client):
#     response = client.post(
#         "/orders",
#         json={
#             "customer_id": 999,
#             "status": "paid",
#         },
#     )

#     assert response.status_code == 422
#     assert "detail" in response.json()

# def test_create_order_invalid_body_returns_422_example(client):
#     payload = {"total_cents": 10, "status": "paid"}

#     response = client.post(
#         "/orders",
#         json=payload,
#     )

#     assert response.status_code == 422


# # request body 422 tests
# @pytest.mark.parametrize(
#     "payload",
#        [{'name': '', 'email': 'x.com'},
#         {'name': 'Olga', 'email': ''},
#         {'email': ''},
#         {'name': 'Olga'}
#         ])

# def test_create_customer_invalid_body_returns_422(client, payload):
#     response = client.post('/customers', json = payload)

#     assert response.status_code == 422


# @pytest.mark.parametrize(
#     "payload",
#        [
#         {"total_cents": 10, "status": "paid"},
#         {"customer_id": 999, "status": "paid"},
#         {"customer_id": 999, "total_cents": 10},
#         {"customer_id": "abc", "total_cents": 10, "status": "paid"},
#         {"customer_id": 999, "total_cents": "abc", "status": "paid"},
#         {"customer_id": 0, "total_cents": 10, "status": "paid"},
#         {"customer_id": 999, "total_cents": -10, "status": "paid"},
#         {"customer_id": 999, "total_cents": 10, "status": "garbage"},
#         {"customer_id": 999, "total_cents": 10, "status": 123},
#     ],
#         )

# def test_create_order_invalid_body_returns_422(client, payload):
#     response = client.post(
#         "/orders",
#         json=payload,
#     )

#     assert response.status_code == 422
#     assert "detail" in response.json()


# @pytest.mark.parametrize(
#     "payload",
#        [{
#         'order_id': '0', 
#         'product_name': 'aaa', 
#         'quanity': 0, 
#         'unit_price_cents': 10},
#     {
#         'order_id': '1', 
#         'product_name': '', 
#         'quanity': 0, 
#         'unit_price_cents': 10},
#         {
#         'order_id': '1', 
#         'product_name': 'aaa', 
#         'quanity': -1, 
#         'unit_price_cents': 10},
#         {
#         'order_id': '1', 
#         'product_name': 'aaa', 
#         'quanity': 0, 
#         'unit_price_cents': -1},
#         ])

# def test_create_item_invalid_body_returns_422(client, payload):
#     response = client.post('/orders', json = payload)

#     assert response.status_code == 422

# # query-param 422 test

# @pytest.mark.parametrize(
#     "params",
#     [
#         {"offset": -1, "limit": 10},
#         {"offset": 0, "limit": 0},
#         {"offset": 0, "limit": 101},
#         {"offset": "abc", "limit": 10},
#         {"offset": 0, "limit": "abc"},
#         {"sort_by": "customer_id"},
#         {"sort_dir": "sideways"},
#     ],
# )

# def test_list_orders_invalid_query_params_return_422(client, params):
#     response = client.get(
#         "/orders",
#         params=params,
#     )

#     assert response.status_code == 422
#     assert "detail" in response.json()


# # path-param 422 test

# def test_get_order_invalid_order_id_type_returns_422(client):
#     response = client.get("/orders/not-an-int")

#     assert response.status_code == 422
#     assert "detail" in response.json()


# def test_patch_order_rejects_customer_id(client, make_order):
#     order = make_order(
#         total_cents=5000,
#         status="pending",
#     )


#     order_id = order['id']
#     response = client.patch(
#         f"/orders/{order_id}",
#         json={
#             "customer_id": 999,
#         },
#     )

#     assert response.status_code == 422