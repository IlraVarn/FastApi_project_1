import hashlib
import json

from sqlmodel import Session

from app.errors import (
    DataIntegrityError,
    IdempotencyConflictError,
)
from app.models.idempotency import IdempotencyRecord
from app.storage.idempotency import (
    get_idempotency_record,
    try_claim_idempotency_record,
)


def build_idempotency_request_hash(
    *,
    values: dict[str, object],
) -> str:

    canonical_json = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def resolve_idempotency_attempt(
    *,
    organization_id: int,
    operation: str,
    idempotency_key: str,
    request_hash: str,
    session: Session,
) -> tuple[int | None, IdempotencyRecord | None]:

    idempotency_record_id = (
        try_claim_idempotency_record(
            organization_id=organization_id,
            operation=operation,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            session=session,
        )
    )

    # NEW REQUEST
    if idempotency_record_id is not None:
        return idempotency_record_id, None

    # EXISTING KEY
    existing_record = get_idempotency_record(
        organization_id=organization_id,
        operation=operation,
        idempotency_key=idempotency_key,
        session=session,
    )

    if existing_record is None:
        raise DataIntegrityError()

    if existing_record.request_hash != request_hash:
        raise IdempotencyConflictError()

    return None, existing_record

# What this does
# Input:
# {
#     "evidence_id": 10,
#     "original_filename": "report.pdf",
#     "size_bytes": 5000,
# }
# gets converted into one stable string, then SHA-256:
# request
# ↓
# stable representation
# ↓
# SHA-256
# ↓
# 64-character request_hash
# The ordering of dictionary keys cannot accidentally change the hash because:
# sort_keys=True