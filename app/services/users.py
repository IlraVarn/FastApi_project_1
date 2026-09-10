from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.errors import DataIntegrityError
from app.models import User
from app.storage.users import add_user_record


def create_user_service(
    *,
    name: str,
    email: str,
    session: Session,
) -> User:

    try:
        db_user = add_user_record(
            name=name,
            email=email,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_user)

    if db_user.id is None:
        raise DataIntegrityError()

    return db_user


