
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from errors import (DataIntegrityError, 
                    UserNotFoundError,
                    )
from models import (Organization)
from sqlalchemy import asc, desc
from storage.users import get_user_by_id

from storage.memberships import(
    add_membership_record, 
)
from storage.organizations import add_organization_record



def create_self_service_organization_service(
    *,
    organization_name: str,
    actor_user_id: int,
    session: Session,
) -> Organization:

    
    #get_user_by_id is redundant for the current architecture
    #since get_authenticated_user already performs this
    # db_user = get_user_by_id(
    #     user_id=actor_user_id,
    #     session=session,
    # )

    # if db_user is None:
    #     raise UserNotFoundError()


    try:
        db_organization = add_organization_record(
            organization_name=organization_name,
            session=session,
        )

        session.flush()

        if db_organization.id is None:
            raise DataIntegrityError()

        add_membership_record(
            user_id=actor_user_id,
            organization_id=db_organization.id,
            role="admin",
            status="active",
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_organization)

    return db_organization


