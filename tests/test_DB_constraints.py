import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC

from models import (
    User,
    Membership,
    Organization,
    Gate,
    GateType,
    GateRequirement,
    GateEvidence,
    )



def test_user_email_unique_constraint(db_session):
    first_user= User(
        name="Olga",
        email="x.com",
    )

    second_user = User(
        name="Ana",
        email="x.com",
    )

    db_session.add(first_user)
    db_session.commit()

    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    

def test_user_email_non_empty_constraint(db_session):
    user = User(
        name="Olga",
        email="",
    )

    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_organization_name_non_empty_constraint(db_session):
    db_organization= Organization(
        name="",
    )

    db_session.add(db_organization)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_membership_user_id_foreign_key_constraint(db_session):

    db_organization= Organization(
        name="Test Organization",
    )
    db_session.add(db_organization)
    db_session.flush()

    assert db_organization.id is not None

    db_membership= Membership(
        user_id=999,
        organization_id=db_organization.id
    )

    db_session.add(db_membership)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_gate_status_check_constraint(db_session):

    db_organization= Organization(
        name="Test Organization",
    )
    db_session.add(db_organization)
    db_session.flush()

    assert db_organization.id is not None
    
    db_gate= Gate(
        organization_id=db_organization.id,
        gate_type=GateType.CLOSEOUT_HANDOFF.value,
        status='wrong_status'
    )

    db_session.add(db_gate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


