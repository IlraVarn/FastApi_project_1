from sqlmodel import Session, select, col
from sqlalchemy import asc, desc, func
from datetime import UTC, datetime
from app.models import (
    Gate, 
    GateStatusChange,
    GateSubmission,
    EvidenceUse,
    GateRequirement, 
    GateSubmissionEvidence,
    )

from app.enums import GateStatusType, GateType
from app.schemas import GateSortBy, GateSortDirection

from typing import Any



    # no previous submissions → 1
    # highest is 1           → 2
    # highest is 2           → 3
def get_next_gate_submission_number(
    *,
    gate_id: int,
    session: Session,
) -> int:
    """Return the next submission number for one Gate."""

    statement = (
        select(func.max(GateSubmission.submission_number))
        .where(GateSubmission.gate_id == gate_id)
    )

    current_max = session.exec(statement).one()

    return (current_max or 0) + 1


def add_gate_submission(
    *,
    gate_id: int,
    submission_number: int,
    submitted_by_user_id: int,
    session: Session,
) -> GateSubmission:
    """Create and stage one GateSubmission."""

    db_submission = GateSubmission(
        gate_id=gate_id,
        submission_number=submission_number,
        submitted_by_user_id=submitted_by_user_id,
    )

    session.add(db_submission)

    return db_submission


def list_evidence_uses_by_gate_id(
    *,
    gate_id: int,
    session: Session,
) -> list[EvidenceUse]:
    """Return current EvidenceUse rows belonging to one Gate."""

    statement = (
        select(EvidenceUse)
        .join(GateRequirement)
        .where(
            col(GateRequirement.gate_id) == gate_id,
        )
    )

    return list(session.exec(statement).all())


def add_gate_submission_evidence(
    *,
    gate_submission_id: int,
    gate_requirement_id: int,
    evidence_version_id: int,
    session: Session,
) -> GateSubmissionEvidence:
    
    """Stage one evidence assignment in a GateSubmission snapshot."""

    db_snapshot = GateSubmissionEvidence(
        gate_submission_id=gate_submission_id,
        gate_requirement_id=gate_requirement_id,
        evidence_version_id=evidence_version_id,
    )

    session.add(db_snapshot)

    return db_snapshot