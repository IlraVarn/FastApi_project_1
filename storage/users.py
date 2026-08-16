
from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import User




# def get_customer_by_email(
#     *,
#     email: str,
#     session: Session,
# ) -> Customer | None:
    
#     statement = select(Customer).where(Customer.email == email)
#     return session.exec(statement).first()


def get_user_by_id(
    *,
    user_id: int,
    session: Session,
) -> User | None:
    
    return session.get(User, user_id)
