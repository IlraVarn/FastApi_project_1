from datetime import UTC, datetime

from sqlalchemy import desc
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import (Customer, CustomerCreate,
                    Order, OrderCreate, 
                    OrderItem, OrderUpdate)


def create_customer_service(
        customer_create: CustomerCreate, 
        session: Session
    ) -> Customer:
    
    statement = (select(Customer)
                 .where(Customer.email == customer_create.email))
    
    existing_customer = session.exec(statement).first()

    if existing_customer:
        raise ConflictError("customer email already exists")

    db_customer = Customer(
        name= customer_create.name,
        email= customer_create.email, 
        internal_note= None
    )
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)

    return db_customer


def read_customer_service(
    customer_id: int,
    session: Session ,
) -> Customer:
    
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        raise NotFoundError('customer not found')
    return db_customer


