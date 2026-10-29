from sqlmodel import Session, select, col
from sqlalchemy import asc, desc, func
from datetime import UTC, datetime
from app.models import (
    WorkflowRecord
    )


from typing import Any


def add_workflow_record(
    *,
    organization_id: int,
    name: str,
    created_by_user_id: int,
    session: Session,
) -> WorkflowRecord:
    """Create and stage a new WorkflowRecord for persistence.

    WorkflowRecord model defaults initialize created_at and updated_at.
    Does not commit, rollback, or refresh.
    """
    db_workflow_record = WorkflowRecord(
        organization_id=organization_id,
        created_by_user_id=created_by_user_id,
        name=name,
    )

    session.add(db_workflow_record)

    return db_workflow_record



def get_active_workflow_record_by_id(
    *,
    workflow_record_id: int,
    organization_id: int,
    session: Session,
) -> WorkflowRecord | None:

    """Return an active WorkflowRecord by ID, or None if missing or archived."""

    statement = (
        select(WorkflowRecord)
        .where(
        col(WorkflowRecord.id) == workflow_record_id,
            WorkflowRecord.organization_id == organization_id,
            col(WorkflowRecord.archived_at).is_(None),
        ))

    return session.exec(statement).first()


