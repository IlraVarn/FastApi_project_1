from sqlmodel import select
from app.models import Membership

# #happy path tests


def test_create_organization_success(authenticated_client, db_session, user):
    response = authenticated_client.post(
        "/organizations",
        json={
            "name": "test_organization",
        },
    )
    assert response.status_code == 201

    #transform json response body to python dict
    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "test_organization"

    #query db for membership as it's not included in the public response
    membership = db_session.exec(
        select(Membership).where(
            Membership.user_id == user["user_id"],
            Membership.organization_id == data["id"],
        )
    ).first()

    assert membership is not None
    assert membership.status == "active"
    assert membership.role == "admin"



 #failure tests
def test_create_organization_requires_authentication(client):
    """This does not retest all of authentication. 
    This one only proves:
    POST /organizations is actually connected to get_authenticated_user()."""

    response = client.post(
        "/organizations",
        json={
            "name": "test_organization",
        },
    )

    assert response.status_code == 401



# def test_get_customer_missing_returns_404(client):
    
#     response = client.get(
#         "/customers/999",
#     )

#     data = response.json()

#     assert response.status_code == 404
#     assert data == {'detail': 'customer not found'}
 



# def test_get_customer_success(client, customer):

#     customer_id = customer['id']

#     response = client.get(f"/customers/{customer_id}")
#     assert response.status_code == 200

#     data = response.json()
    
#     assert data['id'] == customer_id
#     assert data['name'] == customer['name']
#     assert data['email'] == customer['email']
#     assert 'internal note' not in data


# def test_get_customer_with_orders_success_returns_200(client, customer, make_order):

#     customer_id = customer['id']
#     first_order = make_order(total_cents=10, status='paid')
#     second_order = make_order(total_cents=20, status='pending')


#     response = client.get(f"/customers/{customer_id}/orders")
#     assert response.status_code == 200

#     data = response.json()
    
#     assert data['id'] == customer_id
#     assert data['name'] == customer['name']
#     assert data['email'] == customer['email']
#     assert 'internal note' not in data

#     assert len(data['orders']) == 2

#     assert data['orders'][0]['id'] == second_order['id']
#     assert data['orders'][0]['created_at'] is not None
#     assert data['orders'][0]['total_cents'] == second_order['total_cents']
#     assert data['orders'][0]['status'] == 'pending'
    

# def test_list_customers_filter_by_name_success(client, make_customer):

#     first_customer = make_customer(name='Ana', email='ana@x.com')
#     second_customer = make_customer(name='Olga', email='olga@x.com')

#     response = client.get('/customers',
#                           params={
#                               'name': 'Olga',
#                           })

#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]['id'] == second_customer['id']
#     assert data[0]['name'] == second_customer['name']


# def test_list_customers_filter_by_email_success(client, make_customer):

#     first_customer = make_customer(name='Ana', email='ana@x.com')
#     second_customer = make_customer(name='Olga', email='olga@x.com')

#     response = client.get('/customers',
#                           params={
#                               'email': 'olga@x.com',
#                           })

#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]['id'] == second_customer['id']
#     assert data[0]['email'] == second_customer['email']


# def test_sort_by_customer_name_descending_success(client, make_customer):

#     first_customer = make_customer(name='Ana', email='ana@x.com')
#     second_customer = make_customer(name='Olga', email='olga@x.com')

#     response = client.get('/customers',
#                           params={
#                               'sort_by': 'name',
#                           })
    
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]['id'] == second_customer['id']


# def test_list_customers_paginates_success(client, make_customer):

#     first_customer = make_customer(name='Ana', email='ana@x.com')
#     second_customer = make_customer(name='Olga', email='olga@x.com')    
#     third_customer = make_customer(name='Bob', email='bob@x.com')    

#     response = client.get('/customers',
#                           params={
#                               'offset': 1,
#                               'limit': 1
#                           })
    
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]['id'] == third_customer['id']


# def test_list_customers_no_matches_returns_empty_list_success(client):

#     response = client.get('/customers',
#                           params={
#                             'offset': 0,
#                             'limit': 2
#                           })
    
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 0

    
# def test_get_customers_with_orders_no_matches_returns_empty_list_success(client, customer):

#     response = client.get(f"/customers/{customer['id']}/orders")

#     assert response.status_code == 200
#     data = response.json()

#     assert data['id'] == customer['id']
#     assert data['name'] == customer['name']
#     assert data['email'] == customer['email']
#     assert 'internal note' not in data

#     assert data['orders'] ==[]


# #failure tests

# def test_get_customer_with_orders_customer_not_found_returns_404(client):

#         response = client.get(f"/customers/{999}/orders")
#         assert response.status_code == 404

#         data = response.json()
#         assert data == {'detail': 'customer not found'}


# def test_create_customer_duplicate_email_returns_409(client, customer):
    
#     response = client.post(
#         "/customers",
#         json={
#             "name": "O",
#             "email": "olga@x.com",
#         },
#     )

#     data = response.json()

#     assert response.status_code == 409
#     assert data == {'detail': 'customer email already exists'}


# def test_create_customer_invalid_email_returns_422(client, customer):
    
#     response = client.post(
#         "/customers",
#         json={
#             "name": "O",
#             "email": "@x.com",
#         },
#     )

#     data = response.json()

#     assert response.status_code == 422
#     assert 'detail' in data
 

# def test_get_customer_missing_returns_404(client):
    
#     response = client.get(
#         "/customers/999",
#     )

#     data = response.json()

#     assert response.status_code == 404
#     assert data == {'detail': 'customer not found'}
 



        


 