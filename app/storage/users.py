
from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from app.models import User

#DEV ONLY
def add_user_record(
    *,
    name: str,
    email: str,
    session: Session,
) -> User:
    """dev only for self serve onboarding"""

    db_user = User(
        name=name,
        email=email,
    )

    session.add(db_user)

    return db_user



def get_user_by_id(
    *,
    user_id: int,
    session: Session,
) -> User | None:
    
    return session.get(User, user_id)


