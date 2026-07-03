from models import (Customer, CustomerPublic, 
                    Order, OrderPublic, OrderDetailPublic,
                    OrderItem, OrderItemPublic, OrderDetailWithItemsPublic)

#customer helpers
def to_customer_public(db_customer: Customer)-> CustomerPublic:
    assert db_customer.id is not None

    return CustomerPublic(
        id=db_customer.id,
        name= db_customer.name,
        email=db_customer.email
    )

#order helpers
def to_order_public(db_order: Order) -> OrderPublic:
    assert db_order.id is not None
    
    return OrderPublic(
        id= db_order.id,
        created_at= db_order.created_at,
        customer_id=db_order.customer_id,
        total_cents= db_order.total_cents,
    )

def to_order_detail_public(db_order: Order, db_customer: Customer) -> OrderDetailPublic:
    assert db_order.id is not None

    return OrderDetailPublic(
        id=db_order.id,
        created_at=db_order.created_at,
        customer=to_customer_public(db_customer),
        total_cents=db_order.total_cents, 
    )

def to_order_detail_with_items_public(
    db_order: Order,
    db_customer: Customer,
    db_items: list[OrderItem],
) -> OrderDetailWithItemsPublic:
    
    assert db_order.id is not None

    public_items = []

    for db_item in db_items:
        public_item = to_item_public(db_item)
        public_items.append(public_item)

    return OrderDetailWithItemsPublic(
        id=db_order.id,
        created_at=db_order.created_at,
        customer=to_customer_public(db_customer),
        total_cents=db_order.total_cents,
        items=public_items,
    )

def to_order_public_list(
        db_orders: list[Order]
        )-> list[OrderPublic]:
    
    public_orders=[]
    for db_order in db_orders:
        public_order= to_order_public(db_order)
        public_orders.append(public_order)

    return public_orders


#item helpers
def to_item_public(db_item: OrderItem)-> OrderItemPublic:
    assert db_item.id is not None

    return OrderItemPublic(
        id=db_item.id,
        order_id=db_item.order_id,
        product_name=db_item.product_name,
        quantity=db_item.quantity,
        unit_price_cents=db_item.unit_price_cents

    )


def to_item_public_list(
        db_items: list[OrderItem]
        )-> list[OrderItemPublic]:
    
    public_items=[]
    for db_item in db_items:
        public_item= to_item_public(db_item)
        public_items.append(public_item)

    return public_items