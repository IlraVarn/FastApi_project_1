
from app.models import ( 
                    Evidence,
                    EvidenceVersion,
                    )

from app.enums import EvidenceUploadStatusType
from sqlmodel import Session, col, select
from datetime import datetime



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
    checksum_sha256: str,
    created_by_user_id: int,
    session: Session,
) -> EvidenceVersion:
    db_version = EvidenceVersion(
        evidence_id=evidence_id,
        version_number=version_number,
        storage_key=storage_key,
        original_filename=original_filename,
        content_type=content_type,
        checksum_sha256=checksum_sha256,
        size_bytes=size_bytes,
        upload_status=(
            EvidenceUploadStatusType.PENDING.value
        ),
        created_by_user_id=created_by_user_id,
    )

    session.add(db_version)

    return db_version


def get_evidence_by_id_and_organization_for_update(
    *,
    evidence_id: int,
    organization_id: int,
    session: Session,
) -> Evidence | None:
    """Load tenant-scoped Evidence and lock the row for update."""

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


def get_evidence_by_id_and_organization(
    *,
    evidence_id: int,
    organization_id: int,
    session: Session,
) -> Evidence | None:

    statement = (
        select(Evidence)
        .where(
            Evidence.id == evidence_id,
            Evidence.organization_id
            == organization_id,
        )
    )

    return session.exec(statement).first()


def get_evidence_version_by_id_and_evidence(
    *,
    evidence_version_id: int,
    evidence_id: int,
    session: Session,
) -> EvidenceVersion | None:

    statement = (
        select(EvidenceVersion)
        .where(
            EvidenceVersion.id
            == evidence_version_id,
            EvidenceVersion.evidence_id
            == evidence_id,
        )
    )

    return session.exec(statement).first()


#used by complete upload service
def get_evidence_version_by_id_evidence_and_organization(
    *,
    evidence_version_id: int,
    evidence_id: int,
    organization_id: int,
    session: Session,
) -> EvidenceVersion | None:

    statement = (
        select(EvidenceVersion)
        .join(Evidence)
        .where(
            EvidenceVersion.id == evidence_version_id,
            EvidenceVersion.evidence_id == evidence_id,
            Evidence.organization_id == organization_id,
        )
    )

    return session.exec(statement).first()


#completes the upload pending -> available
def mark_evidence_version_available_record(
    *,
    db_version: EvidenceVersion,
    available_at: datetime,
    session: Session,
) -> None:

    db_version.upload_status = (
        EvidenceUploadStatusType.AVAILABLE.value
    )

    db_version.available_at = available_at

    session.add(db_version)

#gets evidence version and locks it for update
def get_evidence_version_by_id_evidence_and_organization_for_update(
    *,
    evidence_version_id: int,
    evidence_id: int,
    organization_id: int,
    session: Session,
) -> EvidenceVersion | None:

    statement = (
        select(EvidenceVersion)
        .join(Evidence)
        .where(
            EvidenceVersion.id
            == evidence_version_id,
            EvidenceVersion.evidence_id
            == evidence_id,
            Evidence.organization_id
            == organization_id,
        )
        .with_for_update()
    )

    return session.exec(statement).first()


# def get_evidence_version_by_id_and_evidence_for_update(
#     *,
#     evidence_version_id: int,
#     evidence_id: int,
#     session: Session,
# ) -> EvidenceVersion | None:

#     statement = (
#         select(EvidenceVersion)
#         .where(
#             EvidenceVersion.id
#             == evidence_version_id,
#             EvidenceVersion.evidence_id
#             == evidence_id,
#         )
#         .with_for_update()
#     )

#     return session.exec(statement).first()


# def set_evidence_version_available(
#     *,
#     db_version: EvidenceVersion,
#     available_at: datetime,
#     session: Session,
# ) -> None:

#     db_version.upload_status = (
#         EvidenceUploadStatusType.AVAILABLE.value
#     )

#     db_version.available_at = available_at

#     session.add(db_version)