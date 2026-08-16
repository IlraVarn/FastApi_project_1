from sqlmodel import Session

from models import Organization


def add_organization_record(
    *,
    name: str,
    session: Session,
) -> Organization:
    db_organization = Organization(
        name=name,
    )

    session.add(db_organization)

    return db_organization


