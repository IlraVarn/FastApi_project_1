from sqlmodel import Session, select

from models import Membership

#used for TenantContext
def get_active_membership_record(
    *,
    user_id: int,
    organization_id: int,
    session: Session,
) -> Membership | None:

    statement = (
        select(Membership)
        .where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
            Membership.status == "active",
        )
    )

    return session.exec(statement).first()


def add_membership_record(
    *,
    user_id: int,
    organization_id: int,
    role: str,
    status: str,
    session: Session,
) -> Membership:
    db_membership = Membership(
        user_id=user_id,
        organization_id=organization_id,
        role=role,
        status=status,
    )

    session.add(db_membership)

    return db_membership

