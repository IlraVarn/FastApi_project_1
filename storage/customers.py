#helper functions that talk to the DB
#router->service->storage->DB

from sqlmodel import Session, select

from models import Customer



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