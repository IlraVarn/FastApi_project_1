from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from datetime import UTC, datetime
from app.models import IdempotencyRecord 
from sqlalchemy import inspect
from typing import Any, cast


def try_claim_idempotency_record(
    *,
    organization_id: int,
    operation: str,
    idempotency_key: str,
    request_hash: str,
    session: Session,
) -> int | None:

    idempotency_table = cast(
        Any,
        IdempotencyRecord,
    ).__table__

    statement = (
        insert(idempotency_table)
        .values(
            organization_id=organization_id,
            operation=operation,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            created_at=datetime.now(UTC),
        )
        .on_conflict_do_nothing(
            constraint="uq_idempotency_org_operation_key",
        )
        .returning(
            idempotency_table.c.id
        )
    )

    return session.exec(
        statement
    ).scalar_one_or_none()


def get_idempotency_record(
    *,
    organization_id: int,
    operation: str,
    idempotency_key: str,
    session: Session,
) -> IdempotencyRecord | None:

    statement = (
        select(IdempotencyRecord)
        .where(
            IdempotencyRecord.organization_id
            == organization_id,
            IdempotencyRecord.operation
            == operation,
            IdempotencyRecord.idempotency_key
            == idempotency_key,
        )
    )

    return session.exec(statement).first()





def complete_idempotency_record(
    *,
    idempotency_record_id: int,
    session: Session,
    gate_id: int | None = None,
    evidence_id: int | None = None,
    evidence_version_id: int | None = None,
) -> bool:

    db_record = session.get(
        IdempotencyRecord,
        idempotency_record_id,
    )

    if db_record is None:
        return False

    db_record.gate_id = gate_id
    db_record.evidence_id = evidence_id
    db_record.evidence_version_id = (
        evidence_version_id
    )

    session.add(db_record)

    return True


