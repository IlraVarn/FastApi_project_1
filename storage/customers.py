#helper functions that talk to the DB
#router->service->storage->DB

from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import Customer
from models import CustomerSortBy, CustomerSortDirection

CUSTOMER_SORT_COLUMNS = {
        'name': col(Customer.name),
        'email': col(Customer.email),
        'id': col(Customer.id)
    }


def get_customer_by_email(
    *,
    email: str,
    session: Session,
) -> Customer | None:
    
    statement = select(Customer).where(Customer.email == email)
    return session.exec(statement).first()


def get_customer_by_id(
    *,
    customer_id: int,
    session: Session,
) -> Customer | None:
    
    return session.get(Customer, customer_id)


def add_customer_record(
    *,
    name: str,
    email: str,
    session: Session,
) -> Customer:
    
    db_customer = Customer(
        name=name,
        email=email,
        internal_note=None,
    )

    session.add(db_customer)
    return db_customer


def list_customer_records(
    *,
    name: str | None,
    email: str | None,
    sort_by: CustomerSortBy,
    sort_dir: CustomerSortDirection ,
    offset: int,
    limit: int,
    session: Session
    ) -> list[Customer]:

    statement = select(Customer)

    if name is not None:
        statement = statement.where(Customer.name == name)

    if email is not None:
        statement = statement.where(Customer.email == email)

    sort_column = CUSTOMER_SORT_COLUMNS[sort_by]
    

    if sort_dir == 'desc':
        primary_sort = desc(sort_column)
        tie_breaker = desc(col(Customer.id))
    else:
        primary_sort = asc(sort_column)
        tie_breaker = asc(col(Customer.id))

    if sort_by == 'id':
        statement = statement.order_by(primary_sort)
    else:
        statement = statement.order_by(primary_sort, tie_breaker)
    

    statement = statement.offset(offset).limit(limit)

    return list(session.exec(statement).all())