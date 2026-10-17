import hashlib
import json

from sqlmodel import Session

from app.errors import (
    DataIntegrityError,
    IdempotencyConflictError,
)
from app.models.idempotency.idempotency import IdempotencyRecord
from app.storage.idempotency import (
    get_idempotency_record,
    try_claim_idempotency_record,
)


def build_idempotency_request_hash(
    *,
    values: dict[str, object],
) -> str:
    
    #convert into a standardized string
    canonical_json = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    #convert to bytes and fingerprint them
    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

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



#is this request new or retry of an old one?

def resolve_idempotency_attempt(
    *,
    organization_id: int,
    operation: str,
    idempotency_key: str,
    idempotency_request_hash: str,
    session: Session,
) -> tuple[int | None, IdempotencyRecord | None]:

    #Try to create a new idempotency record for this key
    idempotency_record_id = (
        try_claim_idempotency_record(
            organization_id=organization_id,
            operation=operation,
            idempotency_key=idempotency_key,
            idempotency_request_hash=idempotency_request_hash,
            session=session,
        )
    )

    # NEW REQUEST (none means there's no old record)
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

    if existing_record.idempotency_request_hash != idempotency_request_hash:
        raise IdempotencyConflictError()

    return None, existing_record

# resolve_idempotency_attempt() first tries to create a new idempotency record 
# for the key. If that succeeds, it returns (new_record_id, None), meaning 
# this is a new request. If it fails because the key already exists, 
# it fetches that old record, checks that its request_hash matches the current request, 
# and if it matches returns (None, existing_record), meaning this is a retry; 
# if the old record cannot be found it raises DataIntegrityError, 
# and if the same key was reused with different request data it raises IdempotencyConflictError.