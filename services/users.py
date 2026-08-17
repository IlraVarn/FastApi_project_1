from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from errors import DataIntegrityError
from models import User
from storage.users import add_user_record


def create_user_service(
    *,
    name: str,
    email: str,
    session: Session,
) -> User:

    db_user = add_user_record(
        name=name,
        email=email,
        session=session,
    )

    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    session.refresh(db_user)

    if db_user.id is None:
        raise DataIntegrityError()

    return db_user


