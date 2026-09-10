
from app.models import (EvidenceUploadStatus, 
                    Evidence,
                    EvidenceVersion,
                    )

from sqlmodel import Session, col, select




def add_evidence_record(
    *,
    organization_id: int,
    name: str,
    session: Session,
) -> Evidence:
    db_evidence = Evidence(
        organization_id=organization_id,
        name=name,
    )

    session.add(db_evidence)

    return db_evidence


def add_evidence_version_record(
    *,
    evidence_id: int,
    version_number: int,
    storage_key: str,
    original_filename: str,
    content_type: str,
    size_bytes: int,
    created_by_user_id: int,
    session: Session,
) -> EvidenceVersion:
    db_version = EvidenceVersion(
        evidence_id=evidence_id,
        version_number=version_number,
        storage_key=storage_key,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        checksum_sha256=None,
        upload_status=(
            EvidenceUploadStatus.PENDING.value
        ),
        created_by_user_id=created_by_user_id,
    )

    session.add(db_version)

    return db_version



def get_evidence_record_for_update(
    *,
    evidence_id: int,
    organization_id: int,
    session: Session,
) -> Evidence | None:
    statement = (
        select(Evidence)
        .where(
            Evidence.id == evidence_id,
            Evidence.organization_id == organization_id,
        )
        .with_for_update()
    )

    return session.exec(statement).first()


def get_latest_evidence_version_record(
    *,
    evidence_id: int,
    session: Session,
) -> EvidenceVersion | None:
    statement = (
        select(EvidenceVersion)
        .where(
            EvidenceVersion.evidence_id == evidence_id,
        )
        .order_by(
            col(EvidenceVersion.version_number).desc(),
        )
        .limit(1)
    )

    return session.exec(statement).first()


