from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import (GateRequirement, 
                  )
from datetime import UTC, datetime



def add_gate_requirement_record(
        *,
        gate_id: int,
        requirement_type: str,
        session: Session
        ) -> GateRequirement:
    db_requirement = GateRequirement(
        gate_id=gate_id,
        requirement_type=requirement_type,
    )
    session.add(db_requirement)

    return db_requirement


def list_requirements_by_gate_id(
        *,
        gate_id: int,
        session: Session
    )-> list[GateRequirement]:
    

    statement = (
        select(GateRequirement)
        .where(GateRequirement.gate_id == gate_id)
        .order_by(col(GateRequirement.id))
    )
    db_requirements = list(session.exec(statement).all())

    return db_requirements



