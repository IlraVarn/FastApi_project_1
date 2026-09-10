from sqlmodel import Session

from app.models import Organization


def add_organization_record(
    *,
    organization_name: str,
    session: Session,
) -> Organization:
    db_organization = Organization(
        name=organization_name,
    )

    session.add(db_organization)

    return db_organization


